"""Capture Fase 2 intake screenshots for the 5 remaining biomes.

Renders /intake?biome=<id> for each of puna, yungas, selva, paracas, pacifico
at 1903x915, saves PNGs to docs/screenshots/fase-2/intake/.

Assumes a Next.js dev server is already running on localhost:3000.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2/intake")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BIOMES = ["puna", "yungas", "selva", "paracas", "pacifico"]

VIEWPORT = {"width": 1903, "height": 915}


def prewarm(path: str, timeout: float = 180.0) -> None:
    url = f"http://localhost:3000{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on {path}")


def capture(biome: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=1,
        )
        page = context.new_page()
        url = f"http://localhost:3000/intake?biome={biome}"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=30000,
        )
        page.wait_for_timeout(1500)
        out = OUT_DIR / f"{biome}-composite.png"
        page.screenshot(path=str(out), full_page=False)
        print(f"[{biome}] {VIEWPORT['width']}x{VIEWPORT['height']} -> {out} ({out.stat().st_size} bytes)")
        browser.close()


if __name__ == "__main__":
    prewarm("/intake?biome=puna")
    for biome in BIOMES:
        capture(biome)
