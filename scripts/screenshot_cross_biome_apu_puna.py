"""Cross-biome viewer Apu + Puna: capture beide hero-VP1's en assemble naast
elkaar in een 2-cel grid.

Doel: drift detecteren tussen Apu en Puna op warmte-stack, copper-tokens,
typografie-schaal, Fraunces uitlijning. Loopt tegen een lopende Next.js
dev-server op localhost:3000.
"""

import urllib.request
from pathlib import Path
from typing import List, Tuple

from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORT_W, VIEWPORT_H = 1440, 900


def prewarm(timeout: float = 120.0) -> None:
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on /")


def capture_biome(biome_id: str) -> Path:
    """Capture VP1 van een biome op localhost:3000. biome_id = 'apu' of 'puna'."""
    out = OUT_DIR / f"_cross-biome-{biome_id}-vp1.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto(
            "http://localhost:3000/",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_selector("h1", state="visible", timeout=15000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=30000,
        )
        page.wait_for_timeout(1500)

        if biome_id == "apu":
            # Apu is de eerste biome, scrollY 0 toont VP1.
            page.evaluate("window.scrollTo(0, 0);")
        else:
            page.evaluate(
                f"document.getElementById('{biome_id}').scrollIntoView({{behavior: 'instant', block: 'start'}});"
            )
        page.wait_for_timeout(800)
        page.screenshot(path=str(out), full_page=False)
        print(f"[{biome_id}] {VIEWPORT_W}x{VIEWPORT_H} -> {out} ({out.stat().st_size} bytes)")
        browser.close()
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


def assemble_grid(cells: List[Tuple[Path, str]]) -> Path:
    # Houd elke cel op volle 1440x900 voor maximale visuele detail bij side-by-
    # side drift-check. Schaal 50% horizontaal naar 720x900 zodat het totaal
    # 1440 breed blijft op standard schermen.
    cell_w = VIEWPORT_W // 2  # 720
    cell_h = VIEWPORT_H        # 900
    label_h = 60
    gutter = 8
    img_w = cell_w * 2 + gutter * 3
    img_h = cell_h + label_h + gutter * 3
    canvas = Image.new("RGB", (img_w, img_h), (26, 22, 18))
    draw = ImageDraw.Draw(canvas)
    font = load_label_font(28)

    for idx, (path, label) in enumerate(cells):
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

    out = OUT_DIR / "cross-biome-apu-puna-pass2-1.png"
    canvas.save(out)
    print(f"[grid] -> {out} ({out.stat().st_size} bytes)")
    return out


if __name__ == "__main__":
    prewarm()
    apu_path = capture_biome("apu")
    puna_path = capture_biome("puna")
    assemble_grid([(apu_path, "Apu hero VP1"), (puna_path, "Puna VP1 — Olivier")])
