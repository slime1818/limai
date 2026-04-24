"""Substep 9b tuning fix verify. Buffer -25% to eliminate 9px gap at peak translate."""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POSITIONS = [
    ("tune-fix-apu-pan-progress-50", 900),
    ("tune-fix-apu-pan-progress-75", 1350),
]


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_function(
            "() => { const imgs = document.images; return imgs.length > 0 && imgs[0].complete && imgs[0].naturalWidth > 0; }",
            timeout=30000,
        )
        page.wait_for_timeout(2000)

        for label, y in POSITIONS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1200)
            info = page.evaluate(
                """() => {
                    const w = document.querySelector('.will-change-transform');
                    if (!w) return null;
                    const style = window.getComputedStyle(w);
                    const rect = w.getBoundingClientRect();
                    return {
                        transform: style.transform,
                        top_px: rect.top,
                        bottom_px: rect.bottom,
                        viewH: window.innerHeight,
                    };
                }"""
            )
            out = OUT_DIR / f"substep-9b-{label}.png"
            page.screenshot(path=str(out), full_page=False)
            gap_top = max(0, info['top_px']) if info else 'n/a'
            gap_bottom = max(0, info['viewH'] - info['bottom_px']) if info else 'n/a'
            print(f"[{label} at y={y}] transform={info['transform']} gap_top={gap_top:.1f}px gap_bottom={gap_bottom:.1f}px -> {out.name}")

        browser.close()


if __name__ == "__main__":
    main()
