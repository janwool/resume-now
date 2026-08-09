#!/usr/bin/env python3
"""Render every resume DOCX into a web preview and build a static manifest."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PREVIEW_DIR = ROOT / "assets" / "template-previews"
RENDER_DIR = PREVIEW_DIR / ".render-cache"
MANIFEST_PATH = ROOT / "template-manifest.js"
RENDERER = Path("/Users/chengwuxue/.codex/plugins/cache/openai-primary-runtime/documents/26.805.11740/skills/documents/render_docx.py")
PYTHON = Path("/Users/chengwuxue/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")


TRANSLATIONS = {
    "黑色": "Black", "白色": "White", "蓝色": "Blue", "黄色": "Yellow",
    "绿色": "Green", "橙色": "Orange", "青色": "Coral", "亮蓝": "Bright Blue",
    "深蓝": "Navy", "深灰": "Charcoal", "灰白": "Light Gray", "蓝白": "Blue White",
    "黑白": "Black White", "黑黄": "Black Gold", "黑灰": "Black Gray",
    "黑绿": "Black Green", "白灰": "White Gray", "白绿": "White Green",
    "深绿": "Deep Green", "蓝灰": "Blue Gray", "黑橙": "Black Orange",
    "绿白": "Green White",
}


# Stable, human-readable names for the current collection. Keep these in the
# catalog generator so rebuilding previews never restores opaque folder numbers.
CURATED_SEO_NAMES = [
    "Heritage Executive Resume Template",
    "Editorial Photographer Resume Template",
    "Contemporary Profile Resume Template",
    "Clean Business Resume Template",
    "Bold Sidebar Resume Template",
    "Refined Leadership Resume Template",
    "Modern Timeline Resume Template",
    "Elegant Two-Column Resume Template",
    "Creative Director Resume Template",
    "Minimal Corporate Resume Template",
    "Strategic Professional Resume Template",
    "Blue Accent Professional Resume Template",
    "Classic Executive Resume Template",
    "Blue White Corporate Resume Template",
    "Sophisticated Manager Resume Template",
    "Polished Consultant Resume Template",
    "Modern Analyst Resume Template",
    "Monochrome Professional Resume Template",
    "Clean Timeline Resume Template",
    "Contemporary Manager Resume Template",
    "Black Accent ATS Resume Template",
    "Blue Sidebar ATS Resume Template",
    "Deep Green Executive Resume Template",
    "Navy Executive Resume Template",
    "Light Gray Professional Resume Template",
    "Blue Gray Analyst Resume Template",
    "Royal Blue Corporate Resume Template",
    "Black Modern Resume Template",
    "Structured ATS Resume Template",
    "Black Sidebar Professional Resume Template",
    "Monochrome Career Resume Template",
    "Black Line Executive Resume Template",
    "Soft Gray Minimal Resume Template",
    "Charcoal Modern Resume Template",
    "Green Accent Professional Resume Template",
    "Clean Grid ATS Resume Template",
    "Compact One-Page Resume Template",
    "Modern Two-Column Resume Template",
    "Professional Profile Resume Template",
    "Multi-Page Executive Resume Template",
    "Blue Contact Sidebar Resume Template",
    "Gold Accent Creative Resume Template",
    "Black Classic Resume Template",
    "Borderless Minimal Resume Template",
    "Bordered Executive Resume Template",
    "Black Header ATS Resume Template",
    "Green Sidebar Resume Template",
    "Dark Professional Resume Template",
    "White Gray Minimal Resume Template",
    "Sage Green Creative Resume Template",
    "Charcoal Sidebar Resume Template",
    "Forest Green Executive Resume Template",
    "Clean Professional Resume Template",
    "Charcoal Executive Resume Template",
    "Navy Corporate Resume Template",
    "Classic Career Resume Template",
    "Modern Career Resume Template",
    "Gold Timeline Resume Template",
    "Black Timeline Resume Template",
    "Black White ATS Resume Template",
    "Black Gold Executive Resume Template",
    "Slater Creative CV Resume Template",
    "Denim Blue Professional Resume Template",
    "Ocean Blue Professional Resume Template",
    "Black White Professional Resume Template",
    "Bright Blue Modern Resume Template",
    "Navy Modern Resume Template",
    "Light Gray Clean Resume Template",
    "Black Minimal Resume Template",
    "Orange Flat Designer Resume Template",
    "Green Flat Designer Resume Template",
    "Blue Flat Designer Resume Template",
    "Coral Flat Designer Resume Template",
    "Black Flat Designer Resume Template",
    "Green Contemporary Resume Template",
    "Botanical Editorial Resume Template",
    "Soft Blush Creative Resume Template",
    "Airy Designer Resume Template",
    "Modern Muse Resume Template",
    "Fresh Portfolio Resume Template",
    "Minimal Art Director Resume Template",
    "Quiet Luxury Resume Template",
    "Nordic Minimal Resume Template",
    "Ivory Minimal Resume Template",
    "Modern Serif Minimal Resume Template",
    "Simple Elegant Resume Template",
    "Classic ATS Resume Template",
    "Essential Black White Resume Template",
    "Clean ATS Resume Template",
    "Professional Monochrome Resume Template",
    "Simple Corporate ATS Resume Template",
    "Traditional Executive Resume Template",
    "Recruiter Friendly Resume Template",
    "One-Page ATS Resume Template",
    "Global Professional Resume Template",
    "Modern European Resume Template",
    "Confident Executive Resume Template",
    "International Business Resume Template",
    "Contemporary Global Resume Template",
    "Premium Professional Resume Template",
    "Urban Executive Resume Template",
    "Luxury Minimal Resume Template",
    "Executive Elegance Resume Template",
    "Premium Clean Resume Template",
    "Senior Leadership Resume Template",
]


def seo_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def seo_subtitle(name: str, category: str) -> str:
    lowered = name.lower()
    if "ats" in lowered:
        return "ATS-friendly editable résumé template"
    if any(term in lowered for term in ("creative", "designer", "editorial", "portfolio", "art director")):
        return "Creative editable résumé template"
    if any(term in lowered for term in ("executive", "leadership", "manager")):
        return "Executive résumé template for experienced professionals"
    if any(term in lowered for term in ("minimal", "clean", "simple", "borderless", "ivory", "nordic")):
        return "Clean minimalist résumé template"
    if "one-page" in lowered or "one page" in lowered:
        return "Professional one-page résumé template"
    if "professional" in category:
        return "Professional editable résumé template"
    return "Free editable résumé template"


def is_resume_candidate(path: Path) -> bool:
    name = path.name.lower()
    if any(term in name for term in ("cover letter", "cover_letter", "coverletter", "portfolio", "reference")):
        return False

    siblings = [p.name.lower() for p in path.parent.glob("*.docx") if p != path]
    if any(term in name for term in ("page two", "page 02")) and any("page one" in sibling or "page 01" in sibling for sibling in siblings):
        return False

    if re.search(r"高端模板\s*\([23]\)", path.name) and any(sibling == "高端模板.docx" for sibling in siblings):
        return False
    return True


def natural_key(path: Path):
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", path.as_posix())]


def translate_variant(value: str) -> str:
    value = value.strip()
    if value in TRANSLATIONS:
        return TRANSLATIONS[value]
    value = re.sub(r"^\d+[_\s-]*", "", value)
    value = re.sub(r"\b(resume|a4|color|with border|without border)\b", "", value, flags=re.I)
    value = re.sub(r"[_-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip().title()


def make_name(path: Path) -> tuple[str, str, str]:
    rel = path.relative_to(ROOT)
    if rel.parts[0] == "英文单页":
        stem = path.stem
        number = re.search(r"(\d+)$", stem)
        index = number.group(1) if number else ""
        if "文艺清新" in stem:
            return f"Editorial Fresh {index}", "Creative single-page résumé", "creative"
        if "极简气质" in stem:
            return f"Quiet Minimal {index}", "Minimal single-page résumé", "minimal ats"
        if "标准黑白" in stem:
            return f"Essential Mono {index}", "ATS-friendly monochrome résumé", "minimal professional ats"
        if "欧美大气" in stem:
            return f"Modern International {index}", "Confident international résumé", "professional"
        if "高端简洁" in stem:
            return f"Executive Clean {index}", "Premium clean résumé", "professional minimal"

    family = rel.parts[0].strip("()")
    detail_parts = [translate_variant(part) for part in rel.parts[1:-1]]
    stem_detail = translate_variant(path.stem)
    if stem_detail and stem_detail.lower() not in {"resume", "high end template", "高端模板"}:
        detail_parts.append(stem_detail)
    detail_parts = [part for part in detail_parts if part]
    if family == "118":
        variant = detail_parts[0] if detail_parts else "Flat"
        return f"Flat · {variant}", "Three-column creative résumé", "creative professional"
    suffix = f" · {' · '.join(detail_parts)}" if detail_parts else ""
    return f"Template {family}{suffix}", "Original editable Word résumé", "professional ats"


def render_preview(item: dict) -> tuple[str, str | None]:
    source = ROOT / item["source"]
    preview = ROOT / item["preview"]
    preview.parent.mkdir(parents=True, exist_ok=True)
    if preview.exists() and preview.stat().st_mtime >= source.stat().st_mtime:
        return item["id"], None

    if item.get("originalPreview"):
        image_source = ROOT / item["originalPreview"]
        with Image.open(image_source) as image:
            image.convert("RGB").save(preview, "JPEG", quality=88, optimize=True)
        return item["id"], None

    output_dir = RENDER_DIR / item["id"]
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    dependency_bins = [
        "/Users/chengwuxue/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override",
        "/Users/chengwuxue/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback",
    ]
    env["PATH"] = os.pathsep.join(dependency_bins + [env.get("PATH", "")])
    command = [str(PYTHON), str(RENDERER), str(source), "--output_dir", str(output_dir)]
    try:
        subprocess.run(command, cwd=ROOT, env=env, check=True, capture_output=True, text=True, timeout=120)
        page = output_dir / "page-1.png"
        if not page.exists():
            return item["id"], "renderer did not create page-1.png"
        with Image.open(page) as image:
            image = image.convert("RGB")
            image.thumbnail((900, 1200), Image.Resampling.LANCZOS)
            image.save(preview, "JPEG", quality=86, optimize=True)
        return item["id"], None
    except Exception as error:
        return item["id"], str(error)


def main() -> int:
    paths = sorted((path for path in ROOT.rglob("*.docx") if is_resume_candidate(path)), key=natural_key)
    entries = []
    for index, path in enumerate(paths, start=1):
        fallback_name, _, category = make_name(path)
        name = CURATED_SEO_NAMES[index - 1] if index <= len(CURATED_SEO_NAMES) else fallback_name
        subtitle = seo_subtitle(name, category)
        template_id = f"template-{index:03d}"
        rel = path.relative_to(ROOT).as_posix()
        original_preview = None
        if path.parent.parent.name == "(118)" and "resume" in path.stem.lower():
            candidate = path.with_suffix(".jpg")
            if candidate.exists():
                original_preview = candidate.relative_to(ROOT).as_posix()
        entries.append({
            "id": template_id,
            "name": name,
            "slug": seo_slug(name),
            "subtitle": subtitle,
            "description": f"Use this free editable {name.lower()} for international job applications. Customize every section online and get 3 PDF downloads for $5.",
            "category": category,
            "source": rel,
            "preview": f"assets/template-previews/{template_id}.jpg",
            "editableHtml": f"assets/template-html/{template_id}/index.html" if (ROOT / "assets" / "template-html" / template_id / "index.html").exists() else None,
            "originalPreview": original_preview,
            "supportsOnlineEdit": path.parent.parent.name == "(118)" and "resume" in path.stem.lower(),
            "color": {"黑色": "black", "蓝色": "blue", "绿色": "green", "橙色": "orange", "青色": "cyan"}.get(path.parent.name),
        })

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    failures = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(render_preview, item): item for item in entries}
        for completed, future in enumerate(as_completed(futures), start=1):
            template_id, error = future.result()
            if error:
                failures.append((template_id, error))
            print(f"[{completed}/{len(entries)}] {template_id}{' FAILED' if error else ''}", flush=True)

    successful = [item for item in entries if (ROOT / item["preview"]).exists()]
    payload = "window.resumeTemplateManifest = " + json.dumps(successful, ensure_ascii=False, indent=2) + ";\n"
    MANIFEST_PATH.write_text(payload, encoding="utf-8")
    print(f"Wrote {len(successful)} templates to {MANIFEST_PATH}")
    if failures:
        print("Failures:", file=sys.stderr)
        for template_id, error in failures:
            print(f"  {template_id}: {error}", file=sys.stderr)
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
