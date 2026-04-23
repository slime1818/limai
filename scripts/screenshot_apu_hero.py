"""Capture Apu hero screenshots at desktop + mobile viewports.

Runs against an already-running Next.js dev server on localhost:3000
(scripts/with_server.py manages the lifecycle). Writes two PNGs to
docs/screenshots/fase-1/.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-1")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def prewarm(timeout: float = 120.0) -> None:
    """Force Turbopack first-compile so Playwright goto isn't blocked on it."""
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on /")

VIEWPORTS = [
    ("desktop", 1440, 900, "apu-hero-desktop.png"),
    ("mobile", 390, 844, "apu-hero-mobile.png"),
]


def capture(label: str, width: int, height: int, filename: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=15000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=20000,
        )
        # Give next/font a beat to swap Fraunces/Inter in after load.
        page.wait_for_timeout(1500)
        out = OUT_DIR / filename
        page.screenshot(path=str(out), full_page=False)
        print(f"[{label}] {width}x{height} -> {out} ({out.stat().st_size} bytes)")
        browser.close()


if __name__ == "__main__":
    prewarm()
    for label, w, h, fn in VIEWPORTS:
        capture(label, w, h, fn)
