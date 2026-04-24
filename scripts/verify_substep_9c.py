"""Substep 9c verification. T1 Apu-Puna + T2 Puna-Yungas crossfade screenshots."""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POSITIONS = [
    # T1 Apu -> Puna
    ("t1-crossfade-1260", 1260),
    ("t1-crossfade-1620", 1620),
    ("t1-crossfade-1800", 1800),
    ("t1-crossfade-1950", 1950),
    # T2 Puna -> Yungas
    ("t2-crossfade-3060", 3060),
    ("t2-crossfade-3420", 3420),
    ("t2-crossfade-3600", 3600),
    ("t2-crossfade-3750", 3750),
]


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()

        def on_console(msg):
            if msg.type in ("error", "warning"):
                console_errors.append(f"[{msg.type}] {msg.text}")

        page.on("console", on_console)
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {err}"))

        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_function(
            "() => { const imgs = document.images; return imgs.length > 0 && imgs[0].complete && imgs[0].naturalWidth > 0; }",
            timeout=30000,
        )
        page.wait_for_timeout(2500)

        # Scroll incrementally to populate lazy-load of Yungas before T2 capture
        for y in [500, 1500, 2500, 3200]:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(500)

        for label, y in POSITIONS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1500)

            opacities = page.evaluate(
                """() => {
                    const layers = document.querySelectorAll('.fixed.inset-0 > .absolute.inset-0');
                    return Array.from(layers).map((l, i) => {
                        const op = parseFloat(window.getComputedStyle(l).opacity);
                        return { idx: i, opacity: Number(op.toFixed(3)) };
                    });
                }"""
            )
            out = OUT_DIR / f"substep-9c-{label}.png"
            page.screenshot(path=str(out), full_page=False)
            active = [o for o in opacities if o['opacity'] > 0.01]
            print(f"[{label} at y={y}] active_layers={active} -> {out.name}")

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
