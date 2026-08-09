#!/usr/bin/env python3
"""Build precise, directly editable text overlays from the original DOCX files."""

from __future__ import annotations

import json
import os
import shutil
import statistics
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pdfplumber
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "template-manifest.js"
OUTPUT = ROOT / "template-overlays.js"
CACHE = ROOT / "assets" / "template-overlays" / ".render-cache"
PAGE_ASSETS = ROOT / "assets" / "template-pages"
PYTHON = Path("/Users/chengwuxue/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")
RENDERER = Path("/Users/chengwuxue/.codex/plugins/cache/openai-primary-runtime/documents/26.805.11740/skills/documents/render_docx.py")
DEPENDENCY_BINS = [
    "/Users/chengwuxue/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override",
    "/Users/chengwuxue/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback",
]


def load_manifest() -> list[dict]:
    payload = MANIFEST.read_text(encoding="utf-8")
    return json.loads(payload[payload.index("[") : payload.rindex("]") + 1])


def render_pdf(item: dict) -> Path:
    source = ROOT / item["source"]
    output_dir = CACHE / item["id"]
    pdf = output_dir / f"{source.stem}.pdf"
    if pdf.exists() and pdf.stat().st_mtime >= source.stat().st_mtime:
        return pdf
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join(DEPENDENCY_BINS + [env.get("PATH", "")])
    subprocess.run(
        [str(PYTHON), str(RENDERER), str(source), "--output_dir", str(output_dir), "--emit_pdf"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=150,
    )
    if not pdf.exists():
        matches = list(output_dir.glob("*.pdf"))
        if not matches:
            raise RuntimeError("renderer did not create a PDF")
        pdf = matches[0]
    return pdf


def color_to_hex(value, fallback="#202124") -> str:
    if value is None:
        return fallback
    if isinstance(value, (int, float)):
        value = (value, value, value)
    if not isinstance(value, (tuple, list)):
        return fallback
    if len(value) == 1:
        value = (value[0], value[0], value[0])
    if len(value) >= 4:  # CMYK is uncommon here; a conservative conversion is enough.
        c, m, y, k = (float(channel) for channel in value[:4])
        rgb = (1 - min(1, c + k), 1 - min(1, m + k), 1 - min(1, y + k))
    else:
        rgb = tuple(float(channel) for channel in value[:3])
    if max(rgb, default=0) <= 1:
        rgb = tuple(channel * 255 for channel in rgb)
    return "#" + "".join(f"{max(0, min(255, round(channel))):02x}" for channel in rgb)


def sample_background(image: Image.Image, box: tuple[float, float, float, float], page_width: float, page_height: float) -> str:
    width, height = image.size
    x0, top, x1, bottom = box
    px0 = max(0, int(x0 / page_width * width) - 4)
    py0 = max(0, int(top / page_height * height) - 3)
    px1 = min(width - 1, int(x1 / page_width * width) + 4)
    py1 = min(height - 1, int(bottom / page_height * height) + 3)
    pixels = []
    for y in range(py0, py1 + 1):
        for x in range(px0, px1 + 1):
            if y in range(py0, min(py0 + 3, py1 + 1)) or y in range(max(py0, py1 - 2), py1 + 1) or x in range(px0, min(px0 + 3, px1 + 1)) or x in range(max(px0, px1 - 2), px1 + 1):
                red, green, blue = image.getpixel((x, y))[:3]
                pixels.append((round(red / 12) * 12, round(green / 12) * 12, round(blue / 12) * 12))
    if not pixels:
        return "#ffffff"
    red, green, blue = Counter(pixels).most_common(1)[0][0]
    return f"#{min(red,255):02x}{min(green,255):02x}{min(blue,255):02x}"


def split_into_visual_lines(words: list[dict]) -> list[list[dict]]:
    rows: list[list[dict]] = []
    for word in sorted(words, key=lambda entry: ((entry["top"] + entry["bottom"]) / 2, entry["x0"])):
        center = (word["top"] + word["bottom"]) / 2
        best_row = None
        best_distance = float("inf")
        for row in rows:
            row_center = statistics.median((item["top"] + item["bottom"]) / 2 for item in row)
            row_height = max(item["bottom"] - item["top"] for item in row)
            tolerance = max(row_height, word["bottom"] - word["top"]) * 0.42
            distance = abs(center - row_center)
            if distance <= tolerance and distance < best_distance:
                best_row, best_distance = row, distance
        if best_row is None:
            rows.append([word])
        else:
            best_row.append(word)

    segments: list[list[dict]] = []
    for row in rows:
        row.sort(key=lambda entry: entry["x0"])
        current = [row[0]]
        for word in row[1:]:
            previous = current[-1]
            median_height = statistics.median(item["bottom"] - item["top"] for item in current)
            gap = word["x0"] - previous["x1"]
            if gap > max(14, min(30, median_height * 2.25)):
                segments.append(current)
                current = [word]
            else:
                current.append(word)
        segments.append(current)
    return segments


def colors_are_close(first: str, second: str, tolerance: int = 22) -> bool:
    try:
        first_rgb = tuple(int(first[index:index + 2], 16) for index in (1, 3, 5))
        second_rgb = tuple(int(second[index:index + 2], 16) for index in (1, 3, 5))
    except (TypeError, ValueError):
        return first == second
    return max(abs(left - right) for left, right in zip(first_rgb, second_rgb)) <= tolerance


def can_merge_lines(group: list[dict], line: dict) -> bool:
    """Join consecutive PDF lines only when they belong to one visual text block."""
    previous = group[-1]
    vertical_gap = line["top"] - previous["bottom"]
    font_size = statistics.median((previous["font_size"], line["font_size"]))
    if vertical_gap < -max(1.2, font_size * 0.22) or vertical_gap > max(5.5, font_size * 0.82):
        return False
    if abs(line["font_size"] - previous["font_size"]) > max(0.8, font_size * 0.1):
        return False
    if line["weight"] != previous["weight"] or line["italic"] != previous["italic"]:
        return False
    if not colors_are_close(line["color"], previous["color"]):
        return False

    tolerance = max(4.5, font_size * 0.72)
    same_left = abs(line["x0"] - previous["x0"]) <= tolerance
    same_right = abs(line["x1"] - previous["x1"]) <= tolerance
    previous_center = (previous["x0"] + previous["x1"]) / 2
    line_center = (line["x0"] + line["x1"]) / 2
    same_center = abs(line_center - previous_center) <= tolerance
    previous_width = previous["x1"] - previous["x0"]
    line_width = line["x1"] - line["x0"]
    width_ratio = min(previous_width, line_width) / max(previous_width, line_width, 1)
    return same_left or same_right or (same_center and width_ratio >= 0.48)


def group_visual_lines(lines: list[dict]) -> list[list[dict]]:
    groups: list[list[dict]] = []
    for line in sorted(lines, key=lambda entry: (entry["top"], entry["x0"])):
        candidates = [group for group in groups if can_merge_lines(group, line)]
        if not candidates:
            groups.append([line])
            continue
        best = min(
            candidates,
            key=lambda group: (
                max(0, line["top"] - group[-1]["bottom"]),
                abs(line["x0"] - group[-1]["x0"]),
            ),
        )
        best.append(line)
    return groups


def detect_photo_region(page, page_number: int) -> dict | None:
    """Find one likely résumé portrait while rejecting icons, banners, and portfolio art."""
    candidates = []
    for image in page.images:
        x0 = float(image.get("x0", 0))
        top = float(image.get("top", 0))
        x1 = float(image.get("x1", x0))
        bottom = float(image.get("bottom", top))
        width = max(0, x1 - x0)
        height = max(0, bottom - top)
        width_ratio = width / page.width
        height_ratio = height / page.height
        area_ratio = width_ratio * height_ratio
        aspect = width / max(height, 1)
        if not (0.018 <= area_ratio <= 0.18):
            continue
        if not (0.1 <= width_ratio <= 0.42 and 0.08 <= height_ratio <= 0.38):
            continue
        if top / page.height > 0.43 or not (0.55 <= aspect <= 1.65):
            continue
        candidates.append((area_ratio * (1.25 - top / page.height), x0, top, width, height, aspect))
    if candidates:
        _, x0, top, width, height, aspect = max(candidates)
    else:
        circle_candidates = []
        for curve in page.curves:
            x0 = float(curve.get("x0", 0))
            top = float(curve.get("top", 0))
            x1 = float(curve.get("x1", x0))
            bottom = float(curve.get("bottom", top))
            width = max(0, x1 - x0)
            height = max(0, bottom - top)
            width_ratio = width / page.width
            height_ratio = height / page.height
            area_ratio = width_ratio * height_ratio
            aspect = width / max(height, 1)
            if not curve.get("fill") or top / page.height > 0.43:
                continue
            if not (0.008 <= area_ratio <= 0.12 and 0.1 <= width_ratio <= 0.36):
                continue
            if not (0.88 <= aspect <= 1.12):
                continue
            circle_candidates.append((area_ratio * (1.2 - top / page.height), x0, top, width, height, aspect))
        if not circle_candidates:
            return None
        _, x0, top, width, height, aspect = max(circle_candidates)
    return {
        "id": f"page-{page_number}-photo-1",
        "x": round(x0 / page.width * 100, 4),
        "y": round(top / page.height * 100, 4),
        "w": round(width / page.width * 100, 4),
        "h": round(height / page.height * 100, 4),
        "shape": "circle" if 0.82 <= aspect <= 1.18 else "rounded",
    }


def page_preview(item: dict, page_number: int) -> tuple[Path, Image.Image]:
    """Publish a lightweight editor image for every rendered Word page."""
    rendered = CACHE / item["id"] / f"page-{page_number}.png"
    if not rendered.exists():
        raise RuntimeError(f"renderer did not create page {page_number}")
    image = Image.open(rendered).convert("RGB")
    output_dir = PAGE_ASSETS / item["id"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"page-{page_number}.jpg"
    published = image.copy()
    published.thumbnail((1100, 1550), Image.Resampling.LANCZOS)
    published.save(output, "JPEG", quality=90, optimize=True, progressive=True)
    published.close()
    return output, image


def build_page(page, preview: Image.Image, page_number: int) -> dict:
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    chars = page.chars
    lines = []
    for index, segment in enumerate(split_into_visual_lines(words)):
        text = " ".join(word["text"] for word in segment).strip()
        if not text or not any(character.isalnum() for character in text):
            continue
        x0 = min(word["x0"] for word in segment)
        top = min(word["top"] for word in segment)
        x1 = max(word["x1"] for word in segment)
        bottom = max(word["bottom"] for word in segment)
        matching_chars = [
            char for char in chars
            if char.get("x1", 0) >= x0 and char.get("x0", 0) <= x1
            and char.get("bottom", 0) >= top and char.get("top", 0) <= bottom
            and char.get("text", "").strip()
        ]
        sizes = [float(char.get("size", bottom - top)) for char in matching_chars]
        fonts = [str(char.get("fontname", "")) for char in matching_chars]
        colors = [color_to_hex(char.get("non_stroking_color")) for char in matching_chars]
        font_size = statistics.median(sizes) if sizes else bottom - top
        font_name = Counter(fonts).most_common(1)[0][0] if fonts else ""
        color = Counter(colors).most_common(1)[0][0] if colors else "#202124"
        lines.append({
            "text": text,
            "x0": x0,
            "top": top,
            "x1": x1,
            "bottom": bottom,
            "font_size": font_size,
            "color": color,
            "weight": 700 if "bold" in font_name.lower() else 400,
            "italic": "italic" in font_name.lower() or "oblique" in font_name.lower(),
        })

    blocks = []
    for index, group in enumerate(group_visual_lines(lines)):
        font_size = statistics.median(line["font_size"] for line in group)
        x0 = min(line["x0"] for line in group)
        top = min(line["top"] for line in group)
        x1 = max(line["x1"] for line in group)
        bottom = max(line["bottom"] for line in group)
        pad_x = max(0.8, font_size * 0.08)
        pad_y = max(0.5, font_size * 0.04)
        box = (max(0, x0 - pad_x), max(0, top - pad_y), min(page.width, x1 + pad_x), min(page.height, bottom + pad_y))
        if len(group) > 1:
            top_steps = [current["top"] - previous["top"] for previous, current in zip(group, group[1:])]
            line_height = max(0.8, min(2, statistics.median(top_steps) / max(font_size, 1)))
            left_spread = max(line["x0"] for line in group) - min(line["x0"] for line in group)
            right_spread = max(line["x1"] for line in group) - min(line["x1"] for line in group)
            centers = [(line["x0"] + line["x1"]) / 2 for line in group]
            center_spread = max(centers) - min(centers)
            if right_spread < left_spread and right_spread <= font_size:
                alignment = "right"
            elif center_spread <= font_size * 0.75 and left_spread > font_size * 0.75:
                alignment = "center"
            else:
                alignment = "left"
        else:
            line_height = 1
            alignment = "left"
        blocks.append({
            "id": f"page-{page_number}-block-{index + 1}",
            "text": "\n".join(line["text"] for line in group),
            "x": round(box[0] / page.width * 100, 4),
            "y": round(box[1] / page.height * 100, 4),
            "w": round((box[2] - box[0]) / page.width * 100, 4),
            "h": round((box[3] - box[1]) / page.height * 100, 4),
            "fontSize": round(font_size / page.width * 100, 4),
            "fontSizePoints": round(font_size, 2),
            "lineHeight": round(line_height, 3),
            "align": alignment,
            "color": Counter(line["color"] for line in group).most_common(1)[0][0],
            "background": sample_background(preview, box, page.width, page.height),
            "weight": Counter(line["weight"] for line in group).most_common(1)[0][0],
            "italic": Counter(line["italic"] for line in group).most_common(1)[0][0],
        })
    photo_region = detect_photo_region(page, page_number)
    return {
        "width": round(float(page.width), 3),
        "height": round(float(page.height), 3),
        "blocks": blocks,
        "photoRegions": [photo_region] if photo_region else [],
    }


def build_overlay(item: dict) -> tuple[str, dict]:
    pdf_path = render_pdf(item)
    pages = []
    with pdfplumber.open(pdf_path) as document:
        for page_number, page in enumerate(document.pages, start=1):
            preview_path, preview = page_preview(item, page_number)
            page_data = build_page(page, preview, page_number)
            page_data["preview"] = preview_path.relative_to(ROOT).as_posix()
            pages.append(page_data)
            preview.close()
    canonical_photo = pages[0]["photoRegions"][0] if pages and pages[0]["photoRegions"] else None
    for page in pages[1:]:
        page["photoRegions"] = [
            region for region in page["photoRegions"]
            if canonical_photo
            and abs(region["x"] - canonical_photo["x"]) < 2.5
            and abs(region["y"] - canonical_photo["y"]) < 2.5
            and abs(region["w"] - canonical_photo["w"]) < 2.5
            and abs(region["h"] - canonical_photo["h"]) < 2.5
        ]
    return item["id"], {"pageCount": len(pages), "pages": pages}


def main() -> int:
    items = [item for item in load_manifest() if not item.get("supportsOnlineEdit")]
    CACHE.mkdir(parents=True, exist_ok=True)
    PAGE_ASSETS.mkdir(parents=True, exist_ok=True)
    overlays: dict[str, dict] = {}
    failures = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(build_overlay, item): item for item in items}
        for completed, future in enumerate(as_completed(futures), start=1):
            item = futures[future]
            try:
                template_id, overlay = future.result()
                overlays[template_id] = overlay
                line_count = sum(len(page["blocks"]) for page in overlay["pages"])
                print(f"[{completed}/{len(items)}] {template_id}: {overlay['pageCount']} pages, {line_count} lines", flush=True)
            except Exception as error:
                failures.append((item["id"], str(error)))
                print(f"[{completed}/{len(items)}] {item['id']}: FAILED {error}", flush=True)
    ordered = {item["id"]: overlays[item["id"]] for item in items if item["id"] in overlays}
    OUTPUT.write_text("window.resumeTemplateOverlays = " + json.dumps(ordered, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Wrote {len(ordered)} overlays to {OUTPUT}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
