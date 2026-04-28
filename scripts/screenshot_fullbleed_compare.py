"""Capture drie fullbleed varianten: huidige foto-met-bg, cutout clean, cutout
rim-light. VP1 Olivier, 1440x900.

Pass 2.6 deliverable. Loopt tegen een lopende Next.js dev-server op
localhost:3000.
"""

import urllib.request
from pathlib import Path
from typing import List, Tuple

from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OPTIONS: List[Tuple[str, str]] = [
    ("fullbleed", "Huidig (foto met bg)"),
    ("fullbleed-cutout-clean", "Cutout clean"),
    ("fullbleed-cutout-rim", "Cutout rim-light"),
]
VIEWPORT_W, VIEWPORT_H = 1440, 900


def prewarm(timeout: float = 120.0) -> None:
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on /")


def capture(option_id: str) -> Path:
    out = OUT_DIR / f"_fullbleed-{option_id}-vp1.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto(
            f"http://localhost:3000/?frame={option_id}",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_selector("h1", state="visible", timeout=15000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=30000,
        )
        page.wait_for_timeout(1500)
        page.evaluate(
            "document.getElementById('puna').scrollIntoView({behavior: 'instant', block: 'start'});"
        )
        page.wait_for_timeout(800)
        page.screenshot(path=str(out), full_page=False)
        browser.close()
    print(f"[{option_id}] -> {out} ({out.stat().st_size} bytes)")
    return out


def load_label_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def assemble_grid(captures: List[Tuple[str, str, Path]]) -> Path:
    # Drie cellen op 1/3 horizontale schaal van de source.
    cell_w = VIEWPORT_W // 3
    cell_h = int(VIEWPORT_H * (cell_w / VIEWPORT_W))
    label_h = 56
    gutter = 8

    img_w = cell_w * 3 + gutter * 4
    img_h = cell_h + label_h + gutter * 3
    canvas = Image.new("RGB", (img_w, img_h), (26, 22, 18))
    draw = ImageDraw.Draw(canvas)
    font = load_label_font(22)

    for idx, (_, label, path) in enumerate(captures):
        x = gutter + idx * (cell_w + gutter)
        y = gutter

        with Image.open(path) as img:
            thumb = img.convert("RGB").resize((cell_w, cell_h), Image.LANCZOS)
            canvas.paste(thumb, (x, y))

        label_y = y + cell_h
        draw.rectangle(
            [(x, label_y), (x + cell_w, label_y + label_h)],
            fill=(34, 28, 22),
        )
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = x + (cell_w - text_w) // 2
        text_y = label_y + (label_h - text_h) // 2 - bbox[1]
        draw.text((text_x, text_y), label, fill=(212, 154, 106), font=font)

    out = OUT_DIR / "puna-fullbleed-compare-pass2-6.png"
    canvas.save(out)
    print(f"[grid] -> {out} ({out.stat().st_size} bytes)")
    return out


if __name__ == "__main__":
    prewarm()
    captures: List[Tuple[str, str, Path]] = []
    for option_id, label in OPTIONS:
        captures.append((option_id, label, capture(option_id)))
    assemble_grid(captures)
