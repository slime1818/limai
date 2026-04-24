"""Substep 10 verification. Active-dot shape-shift bar per crossover-based detection.

6 settled states + 5 crossover switch states. Active-dot dimensions assertion (w=4, h=24 px).
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Expected active index per position.
SETTLED = [
    ("active-apu", 900, 0),
    ("active-puna", 2700, 1),
    ("active-yungas", 4500, 2),
    ("active-selva", 6300, 3),
    ("active-paracas", 8100, 4),
    ("active-pacifico", 9900, 5),
]

# Crossover switch moments (10px after exact midpoint).
CROSSOVER = [
    ("cross-1", 1540, 1),  # Apu -> Puna crossover at 1530
    ("cross-2", 3340, 2),
    ("cross-3", 5140, 3),
    ("cross-4", 6940, 4),
    ("cross-5", 8740, 5),
]


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    console_errors: list[str] = []
    results: list[tuple] = []

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
        page.wait_for_timeout(2000)

        # Prime lazy loads by scrolling through the full page
        for y in [1000, 3000, 5000, 7000, 9000, 10500]:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(400)

        def probe_dots():
            return page.evaluate(
                """() => {
                    const dots = document.querySelectorAll('[aria-hidden="true"].fixed.right-8 > div');
                    return Array.from(dots).map((d, i) => {
                        const r = d.getBoundingClientRect();
                        const s = window.getComputedStyle(d);
                        return {
                            idx: i,
                            w: Math.round(r.width * 100) / 100,
                            h: Math.round(r.height * 100) / 100,
                            bg: s.backgroundColor,
                        };
                    });
                }"""
            )

        def test_position(label: str, y: int, expected_active: int):
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1800)  # allow CSS morph transition to settle
            probed = probe_dots()
            # Active = bar (h > 15, w < 6). Inactive = dot (h < 10).
            active_ids = [d['idx'] for d in probed if d['h'] > 15]
            active_match = len(active_ids) == 1 and active_ids[0] == expected_active
            active_dot = probed[expected_active] if 0 <= expected_active < len(probed) else None
            dims_ok = (
                active_dot
                and abs(active_dot['w'] - 4) < 0.5
                and abs(active_dot['h'] - 24) < 0.5
            )
            out = OUT_DIR / f"substep-10-{label}.png"
            page.screenshot(path=str(out), full_page=False)
            results.append((label, y, expected_active, active_ids, active_dot, active_match, dims_ok))
            return out

        print("\n--- settled states ---")
        for label, y, expected in SETTLED:
            out = test_position(label, y, expected)
            last = results[-1]
            print(f"[{label} y={y}] expected_active={expected} measured_active={last[3]} dims_ok={last[6]} -> {out.name}")

        print("\n--- crossover switch states (10px past switch-point) ---")
        for label, y, expected in CROSSOVER:
            out = test_position(label, y, expected)
            last = results[-1]
            print(f"[{label} y={y}] expected_active={expected} measured_active={last[3]} dims_ok={last[6]} -> {out.name}")

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")

    print()
    all_ok = all(r[5] and r[6] for r in results)
    print(f"Summary: {sum(1 for r in results if r[5] and r[6])}/{len(results)} positions OK")
    print(f"Overall: {'ALL PASS' if all_ok else 'SOME FAIL'}")


if __name__ == "__main__":
    main()
