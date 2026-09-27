from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/Users/chengwuxue/projects/resume-template")
OUT = ROOT / "marketing/social/assets"
PREVIEWS = ROOT / "assets/template-previews"
LOGO = ROOT / "assets/brand/resume-now-mark-v2-512.png"

NAVY = "#0B223D"
BLUE = "#0A66E8"
INK = "#121826"
MUTED = "#667085"
PALE = "#F4F7FB"
PALE_BLUE = "#EAF3FF"
WHITE = "#FFFFFF"
GREEN = "#1C8A5A"
RED = "#F04438"

FONT_REG = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size=size)


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def contain(img, size, color=WHITE):
    canvas = Image.new("RGB", size, color)
    copy = img.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def paste_card(canvas, path, box, radius=22, shadow=18, crop=False):
    x, y, w, h = box
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow_layer).rounded_rectangle((x, y + 10, x + w, y + h + 10), radius=radius, fill=(11, 34, 61, 42))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow))
    layer.alpha_composite(shadow_layer)
    src = Image.open(path).convert("RGB")
    if crop:
        ratio = max(w / src.width, h / src.height)
        src = src.resize((int(src.width * ratio), int(src.height * ratio)), Image.Resampling.LANCZOS)
        left = (src.width - w) // 2
        top = (src.height - h) // 2
        src = src.crop((left, top, left + w, top + h))
    else:
        src = contain(src, (w, h))
    card = Image.new("RGBA", (w, h), WHITE)
    card.paste(src, (0, 0))
    card.putalpha(rounded_mask((w, h), radius))
    layer.alpha_composite(card, (x, y))
    canvas.alpha_composite(layer)


def wrap_text(draw, text, fnt, max_width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            trial = f"{line} {word}".strip()
            if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_wrapped(draw, xy, text, fnt, fill, max_width, spacing=1.12):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    step = int(fnt.size * spacing)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def brand(draw, canvas, x=64, y=56, dark=False, compact=False):
    mark = Image.open(LOGO).convert("RGBA")
    size = 44 if compact else 54
    mark.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas.alpha_composite(mark, (x, y))
    draw.text((x + size + 14, y + (2 if compact else 4)), "ResumeNowOnline", font=font(27 if compact else 31, True), fill=WHITE if dark else NAVY)


def button(draw, xy, label, width=None):
    x, y = xy
    fnt = font(28, True)
    text_w = draw.textbbox((0, 0), label, font=fnt)[2]
    w = width or text_w + 64
    draw.rounded_rectangle((x, y, x + w, y + 68), radius=34, fill=BLUE)
    draw.text((x + (w - text_w) / 2, y + 17), label, font=fnt, fill=WHITE)


def save(canvas, rel):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(path, quality=95)


def linkedin_launch():
    c = Image.new("RGBA", (1200, 1500), PALE)
    d = ImageDraw.Draw(c)
    brand(d, c, 72, 62)
    d.rounded_rectangle((72, 156, 290, 207), radius=25, fill=PALE_BLUE)
    d.text((96, 168), "FREE TO BUILD", font=font(21, True), fill=BLUE)
    y = draw_wrapped(d, (72, 250), "Build your resume.\nKeep it free.", font(80, True), INK, 720, 1.02)
    d.text((76, y + 28), "Choose · edit · preview every page", font=font(31), fill=MUTED)
    button(d, (76, y + 92), "Start free")
    paste_card(c, PREVIEWS / "template-004.jpg", (650, 230, 390, 555), 22)
    paste_card(c, PREVIEWS / "template-012.jpg", (396, 700, 390, 555), 22)
    paste_card(c, PREVIEWS / "template-013.jpg", (746, 820, 390, 555), 22)
    d.rounded_rectangle((72, 1335, 402, 1403), radius=34, fill=WHITE)
    d.text((104, 1351), "105 editable templates", font=font(27, True), fill=NAVY)
    save(c, "linkedin/soc-001-launch-free-resume-builder.png")


def pinterest_template(rel, template, eyebrow, title, cta, background=PALE_BLUE):
    c = Image.new("RGBA", (1000, 1500), background)
    d = ImageDraw.Draw(c)
    brand(d, c, 62, 52, compact=True)
    d.text((62, 152), eyebrow.upper(), font=font(23, True), fill=BLUE)
    y = draw_wrapped(d, (62, 205), title, font(62, True), INK, 850, 1.03)
    d.text((62, y + 18), "Edit the complete resume online", font=font(27), fill=MUTED)
    paste_card(c, PREVIEWS / template, (180, y + 90, 640, 905), 20)
    button(d, (247, 1382), cta, 506)
    save(c, rel)


def reel_cover(rel, title, badge, template, accent=BLUE):
    c = Image.new("RGBA", (1080, 1920), NAVY)
    d = ImageDraw.Draw(c)
    brand(d, c, 64, 64, dark=True)
    d.rounded_rectangle((64, 170, 64 + 300, 228), radius=29, fill=accent)
    d.text((92, 183), badge.upper(), font=font(23, True), fill=WHITE)
    draw_wrapped(d, (64, 285), title, font(79, True), WHITE, 900, 1.02)
    d.text((67, 642), "The actual template. Directly editable.", font=font(31), fill="#BFD5EE")
    paste_card(c, PREVIEWS / template, (174, 735, 732, 1040), 26)
    d.rounded_rectangle((64, 1788, 1016, 1860), radius=36, fill=WHITE)
    d.text((204, 1806), "Choose  →  Edit  →  Preview free", font=font(31, True), fill=NAVY)
    save(c, rel)


def x_evidence():
    c = Image.new("RGBA", (1600, 900), WHITE)
    d = ImageDraw.Draw(c)
    brand(d, c, 70, 55, compact=True)
    d.text((74, 186), "Your resume needs", font=font(50), fill=MUTED)
    d.text((74, 254), "evidence, not adjectives.", font=font(72, True), fill=INK)
    d.rounded_rectangle((74, 394, 718, 508), radius=24, fill="#FFF0EF")
    d.text((112, 428), "results-driven professional", font=font(33, True), fill=RED)
    d.line((108, 454, 675, 454), fill=RED, width=7)
    d.rounded_rectangle((74, 548, 1010, 702), radius=24, fill="#EAF8F1")
    d.text((112, 577), "Automated weekly reporting", font=font(33, True), fill=GREEN)
    d.text((112, 625), "5 hours → 40 minutes", font=font(39, True), fill=INK)
    paste_card(c, PREVIEWS / "template-013.jpg", (1170, 160, 330, 575), 18)
    d.text((75, 805), "Action + context + measurable result", font=font(28, True), fill=BLUE)
    save(c, "x/soc-004-x-evidence-not-adjectives.png")


def ig_length():
    c = Image.new("RGBA", (1080, 1350), PALE)
    d = ImageDraw.Draw(c)
    brand(d, c, 60, 55, compact=True)
    d.text((62, 178), "ONE PAGE OR TWO?", font=font(27, True), fill=BLUE)
    draw_wrapped(d, (62, 238), "Use the space your evidence needs.", font(64, True), INK, 940, 1.03)
    paste_card(c, PREVIEWS / "template-004.jpg", (100, 545, 390, 575), 20)
    paste_card(c, PREVIEWS / "template-001.jpg", (586, 545, 390, 575), 20)
    d.rounded_rectangle((64, 1195, 1016, 1274), radius=39, fill=NAVY)
    d.text((164, 1216), "Never shrink the type to obey a myth.", font=font(31, True), fill=WHITE)
    save(c, "instagram/soc-007-resume-length-cover.png")


def profile_assets():
    c = Image.new("RGBA", (1128, 191), NAVY)
    d = ImageDraw.Draw(c)
    brand(d, c, 45, 38, dark=True, compact=True)
    d.text((622, 54), "Build. Edit. Preview free.", font=font(33, True), fill=WHITE)
    d.text((622, 102), "105 editable resume templates", font=font(24), fill="#BFD5EE")
    save(c, "profile/linkedin-banner.png")

    c = Image.new("RGBA", (1500, 500), PALE_BLUE)
    d = ImageDraw.Draw(c)
    brand(d, c, 80, 60)
    draw_wrapped(d, (80, 180), "A better resume starts free.", font(64, True), INK, 820, 1.03)
    d.text((83, 338), "Choose · edit · preview every page", font=font(30), fill=MUTED)
    paste_card(c, PREVIEWS / "template-004.jpg", (1085, 28, 292, 432), 18)
    save(c, "profile/x-header.png")


if __name__ == "__main__":
    linkedin_launch()
    pinterest_template("pinterest/soc-002-pin-clean-business.png", "template-004.jpg", "Free resume template", "Clean Business Resume", "Edit this template")
    reel_cover("reels/soc-003-reel-direct-edit-cover.png", "A resume you can actually edit.", "Editor demo", "template-004.jpg")
    x_evidence()
    reel_cover("reels/soc-005-tiktok-better-bullets-cover.png", "3 resume lines recruiters skip", "Resume tip", "template-013.jpg", GREEN)
    pinterest_template("pinterest/soc-006-pin-minimal-collection.png", "template-012.jpg", "Minimal templates", "Clean. Focused. Easy to edit.", "Browse free templates", "#F7F1EE")
    ig_length()
    profile_assets()
    print(f"Created assets in {OUT}")
