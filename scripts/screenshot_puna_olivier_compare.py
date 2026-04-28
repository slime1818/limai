"""Capture 4 Olivier foto-varianten en maak een 2x2 vergelijkings-grid.

Pass 2.0 deliverable: visuele data voor Olivier's keuze tussen olivier-a/-b
combinaties met natural en copper-duotone treatment. Geen feature-implementatie,
puur scaffolding via ?olivier=... query-param op de homepage.

Vereist een lopende Next.js dev-server op localhost:3000. Schrijft 4 individuele
PNGs plus 1 grid-PNG naar docs/screenshots/fase-2/.
"""

import urllib.request
from pathlib import Path
from typing import List, Tuple

from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VARIANTS: List[Tuple[str, str]] = [
    ("a-natural", "A natural"),
    ("b-natural", "B natural"),
    ("a-duotone", "A duotone"),
    ("b-duotone", "B duotone"),
]

VIEWPORT_W, VIEWPORT_H = 1440, 900


def prewarm(timeout: float = 120.0) -> None:
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on /")


def capture_variant(variant_id: str) -> Path:
    out = OUT_DIR / f"puna-olivier-{variant_id}.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto(
            f"http://localhost:3000/?olivier={variant_id}",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_selector("h1", state="visible", timeout=15000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=30000,
        )
        # Geef next/font en useEffect-driven variant-switch een moment om te landen.
        page.wait_for_timeout(1500)
        page.evaluate(
            "document.getElementById('puna').scrollIntoView({behavior: 'instant', block: 'start'});"
        )
        page.wait_for_timeout(800)
        page.screenshot(path=str(out), full_page=False)
        browser.close()
    print(f"[{variant_id}] -> {out} ({out.stat().st_size} bytes)")
    return out


def load_label_font(size: int) -> ImageFont.ImageFont:
    """Probeer een systeem-truetype font; val terug op default als geen beschikbaar is."""
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


def assemble_grid(individual_paths: List[Path], labels: List[str]) -> Path:
    cell_w = VIEWPORT_W // 2  # 720
    cell_h = VIEWPORT_H // 2  # 450
    label_h = 60
    gutter = 8
    img_w = cell_w * 2 + gutter * 3
    img_h = (cell_h + label_h) * 2 + gutter * 3
    canvas = Image.new("RGB", (img_w, img_h), (26, 22, 18))
    draw = ImageDraw.Draw(canvas)
    font = load_label_font(28)

    for idx, (path, label) in enumerate(zip(individual_paths, labels)):
        col = idx % 2
        row = idx // 2
        x = gutter + col * (cell_w + gutter)
        y = gutter + row * (cell_h + label_h + gutter)

        with Image.open(path) as img:
            thumb = img.convert("RGB").resize((cell_w, cell_h), Image.LANCZOS)
            canvas.paste(thumb, (x, y))

        # Label-balk onder de thumb in copper op donkere achtergrond.
        label_y = y + cell_h
        draw.rectangle(
            [(x, label_y), (x + cell_w, label_y + label_h)],
            fill=(34, 28, 22),
        )
        # Center-aligned label.
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = x + (cell_w - text_w) // 2
        text_y = label_y + (label_h - text_h) // 2 - bbox[1]
        draw.text((text_x, text_y), label, fill=(212, 154, 106), font=font)

    out = OUT_DIR / "puna-olivier-compare-pass2-0.png"
    canvas.save(out)
    print(f"[grid] -> {out} ({out.stat().st_size} bytes)")
    return out


if __name__ == "__main__":
    prewarm()
    paths: List[Path] = []
    labels: List[str] = []
    for variant_id, label in VARIANTS:
        paths.append(capture_variant(variant_id))
        labels.append(label)
    assemble_grid(paths, labels)
