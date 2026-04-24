"""Substep 9c tuning verify. Crossfade 540px with expected vs measured opacity table."""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# (label, scrollY, expected_opacities_per_biome_by_index)
POSITIONS = [
    ("tune-t1-1260", 1260, {"apu": 1.0, "puna": 0.0}),
    ("tune-t1-1530", 1530, {"apu": 0.5, "puna": 0.5}),
    ("tune-t1-1800", 1800, {"apu": 0.0, "puna": 1.0}),
    ("tune-t1-1950", 1950, {"apu": 0.0, "puna": 1.0}),
    ("tune-t2-3060", 3060, {"puna": 1.0, "yungas": 0.0}),
    ("tune-t2-3330", 3330, {"puna": 0.5, "yungas": 0.5}),
    ("tune-t2-3600", 3600, {"puna": 0.0, "yungas": 1.0}),
    ("tune-t2-3750", 3750, {"puna": 0.0, "yungas": 1.0}),
]

BIOME_ORDER = ["apu", "puna", "yungas", "selva", "paracas", "pacifico"]


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    console_errors: list[str] = []
    rows = []

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

        # Prime lazy-load through Puna and Yungas sections
        for y in [500, 1500, 2500, 3500]:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(500)

        for label, y, expected in POSITIONS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1500)
            opacities_by_idx = page.evaluate(
                """() => {
                    const layers = document.querySelectorAll('.fixed.inset-0 > .absolute.inset-0');
                    return Array.from(layers).map((l, i) => Number(parseFloat(window.getComputedStyle(l).opacity).toFixed(3)));
                }"""
            )
            measured = {BIOME_ORDER[i]: opacities_by_idx[i] for i in range(len(opacities_by_idx))}
            out = OUT_DIR / f"substep-9c-{label}.png"
            page.screenshot(path=str(out), full_page=False)
            for biome, exp_op in expected.items():
                meas_op = measured.get(biome, None)
                diff = abs(exp_op - meas_op) if meas_op is not None else None
                ok = diff is not None and diff < 0.02
                rows.append((label, y, biome, exp_op, meas_op, diff, ok))
            print(f"[{label} at y={y}] -> {out.name}")

        browser.close()

    print()
    print(f"{'label':<18} {'y':>6} {'biome':<10} {'expected':>9} {'measured':>9} {'diff':>6} ok")
    for label, y, biome, exp, meas, diff, ok in rows:
        diff_str = f"{diff:.3f}" if diff is not None else "n/a"
        meas_str = f"{meas:.3f}" if meas is not None else "n/a"
        print(f"{label:<18} {y:>6} {biome:<10} {exp:>9.3f} {meas_str:>9} {diff_str:>6} {'OK' if ok else 'FAIL'}")

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
