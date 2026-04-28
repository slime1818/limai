"""Capture 3 name-style varianten x 2 viewports en assemble 3-rij x 2-kolom grid.

Pass 2.3 vergelijkings-deliverable. Loopt tegen een lopende Next.js dev-server
op localhost:3000. Schrijft 6 individuele PNGs (`_` prefix) plus 1 grid-PNG
naar docs/screenshots/fase-2/.
"""

import urllib.request
from pathlib import Path
from typing import List, Tuple

from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OPTIONS: List[Tuple[str, str]] = [
    ("A", "A · Allura vervangt"),
    ("B", "B · Fraunces + Allura erbij"),
    ("C", "C · Asymmetrisch (Fraunces, Allura)"),
]
VIEWPORT_W, VIEWPORT_H = 1440, 900


def prewarm(timeout: float = 120.0) -> None:
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on /")


def capture_option(option_id: str) -> Tuple[Path, Path]:
    out_vp1 = OUT_DIR / f"_namestyle-{option_id}-vp1.png"
    out_vp2 = OUT_DIR / f"_namestyle-{option_id}-vp2.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto(
            f"http://localhost:3000/?nameStyle={option_id}",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_selector("h1", state="visible", timeout=15000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=30000,
        )
        page.wait_for_timeout(1500)

        # VP1
        page.evaluate(
            "document.getElementById('puna').scrollIntoView({behavior: 'instant', block: 'start'});"
        )
        page.wait_for_timeout(800)
        page.screenshot(path=str(out_vp1), full_page=False)
        print(f"[{option_id} VP1] -> {out_vp1} ({out_vp1.stat().st_size} bytes)")

        # VP2
        page.evaluate("window.scrollBy(0, window.innerHeight);")
        page.wait_for_timeout(800)
        page.screenshot(path=str(out_vp2), full_page=False)
        print(f"[{option_id} VP2] -> {out_vp2} ({out_vp2.stat().st_size} bytes)")

        browser.close()
    return out_vp1, out_vp2


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


def assemble_grid(captures: List[Tuple[str, str, Path, Path]]) -> Path:
    """captures = [(option_id, label, vp1_path, vp2_path), ...]"""
    cell_w = VIEWPORT_W // 2          # 720
    cell_h = VIEWPORT_H // 2           # 450
    row_label_w = 320
    header_h = 56
    gutter = 8

    img_w = row_label_w + 2 * cell_w + 4 * gutter
    img_h = header_h + 3 * cell_h + 5 * gutter

    canvas = Image.new("RGB", (img_w, img_h), (26, 22, 18))
    draw = ImageDraw.Draw(canvas)
    label_font = load_label_font(22)
    header_font = load_label_font(20)

    # Column headers, gecentreerd boven elke kolom van cellen.
    column_x = [
        row_label_w + gutter * 2 + i * (cell_w + gutter) for i in range(2)
    ]
    column_titles = ["VP1 Olivier", "VP2 Abdul"]
    for x, title in zip(column_x, column_titles):
        bbox = draw.textbbox((0, 0), title, font=header_font)
        text_w = bbox[2] - bbox[0]
        text_x = x + (cell_w - text_w) // 2
        draw.text(
            (text_x, gutter + (header_h - bbox[3] - bbox[1]) // 2),
            title,
            fill=(212, 154, 106),
            font=header_font,
        )

    # Per rij: label-cel links, twee thumbs rechts.
    for row_idx, (_, label, vp1_path, vp2_path) in enumerate(captures):
        y = header_h + gutter + row_idx * (cell_h + gutter)

        # Row-label paneel.
        rx = gutter
        draw.rectangle(
            [(rx, y), (rx + row_label_w, y + cell_h)],
            fill=(34, 28, 22),
        )
        # Wrap text als label te lang: split op " · " en zet op meerdere regels.
        parts = label.split(" · ")
        line_height = 30
        total_h = len(parts) * line_height
        start_y = y + (cell_h - total_h) // 2
        for i, part in enumerate(parts):
            bbox = draw.textbbox((0, 0), part, font=label_font)
            text_w = bbox[2] - bbox[0]
            text_x = rx + (row_label_w - text_w) // 2
            text_y = start_y + i * line_height
            draw.text(
                (text_x, text_y),
                part,
                fill=(212, 154, 106) if i == 0 else (245, 237, 224, 200),
                font=label_font,
            )

        # Thumbs.
        for col_idx, path in enumerate([vp1_path, vp2_path]):
            x = column_x[col_idx]
            with Image.open(path) as img:
                thumb = img.convert("RGB").resize((cell_w, cell_h), Image.LANCZOS)
                canvas.paste(thumb, (x, y))

    out = OUT_DIR / "puna-namestyle-compare-pass2-3.png"
    canvas.save(out)
    print(f"[grid] -> {out} ({out.stat().st_size} bytes)")
    return out


if __name__ == "__main__":
    prewarm()
    captures: List[Tuple[str, str, Path, Path]] = []
    for option_id, label in OPTIONS:
        vp1, vp2 = capture_option(option_id)
        captures.append((option_id, label, vp1, vp2))
    assemble_grid(captures)
