"""Substep 12 regression pass, desktop batch. 11 scroll-positions, DOM-probes plus screenshots.

Saves to docs/screenshots/fase-2/regression-pass/ at 1440x900.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2/regression-pass")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POSITIONS = [
    ("apu-hero", 0, 0, "Apu"),
    ("apu-puna-T1", 1530, 1, "Apu/Puna crossfade midpoint"),
    ("puna-hero", 1800, 1, "Puna"),
    ("puna-yungas-T2", 3330, 2, "Puna/Yungas crossfade midpoint"),
    ("yungas-hero", 3600, 2, "Yungas"),
    ("yungas-selva-T3", 5130, 3, "Yungas/Selva crossfade midpoint"),
    ("selva-hero", 5400, 3, "Selva (no scrim, text-shadow)"),
    ("selva-paracas-T4", 6930, 4, "Selva/Paracas crossfade midpoint"),
    ("paracas-hero", 7200, 4, "Paracas"),
    ("paracas-pacifico-T5", 8730, 5, "Paracas/Pacifico crossfade midpoint"),
    ("pacifico-hero", 9000, 5, "Pacifico"),
]

EXPECTED_TITLES = ["LimAI", "Wie we zijn", "Wat we doen", "Wat we maakten", "Hoe we werken", "Laten we praten"]
EXPECTED_ACCENTS = {
    "apu": "rgb(168, 200, 212)",     # #a8c8d4
    "puna": "rgb(184, 164, 122)",    # #b8a47a
    "yungas": "rgb(107, 142, 107)",  # #6b8e6b
    "selva": "rgb(58, 95, 58)",      # #3a5f3a
    "paracas": "rgb(184, 127, 74)",  # #b87f4a
    "pacifico": "rgb(90, 138, 148)", # #5a8a94
}
BIOME_ORDER = ["apu", "puna", "yungas", "selva", "paracas", "pacifico"]


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = ctx.new_page()
        page.on("console", lambda m: console_errors.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: console_errors.append(f"[pageerror] {e}"))

        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("section", timeout=20000)
        page.wait_for_timeout(2500)

        # Prime lazy-load
        for y in [1500, 3500, 5500, 7500, 9500]:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(300)

        results = []
        for label, y, expected_active, notes in POSITIONS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1800)  # allow transitions to settle

            probe = page.evaluate(
                """() => {
                    const h1s = Array.from(document.querySelectorAll('section h1'));
                    const dotsContainer = document.querySelector('[aria-hidden=\"true\"].fixed.right-8');
                    const dots = dotsContainer ? Array.from(dotsContainer.children) : [];
                    const dotsStyle = dotsContainer ? window.getComputedStyle(dotsContainer) : null;
                    // Active dot is a bar (h > 15px) per substep 10 spec.
                    const activeDotIdx = dots.findIndex(d => d.getBoundingClientRect().height > 15);
                    const activeDotColor = activeDotIdx >= 0 ? window.getComputedStyle(dots[activeDotIdx]).backgroundColor : null;
                    const layers = Array.from(document.querySelectorAll('.fixed.inset-0.w-full.h-screen > .absolute.inset-0'));
                    const layerOpacities = layers.map(l => Number(parseFloat(window.getComputedStyle(l).opacity).toFixed(3)));
                    const textShadows = h1s.map(h => window.getComputedStyle(h).textShadow);
                    return {
                        dotsVisible: dotsStyle ? dotsStyle.display !== 'none' : false,
                        dotsCount: dots.length,
                        activeDotIdx,
                        activeDotColor,
                        layerOpacities,
                        h1Titles: h1s.map(h => h.textContent),
                        h1TextShadows: textShadows,
                    };
                }"""
            )
            out = OUT_DIR / f"{label}.png"
            page.screenshot(path=str(out), full_page=False)

            active_color_ok = False
            if expected_active >= 0 and expected_active < len(BIOME_ORDER):
                expected_color = EXPECTED_ACCENTS[BIOME_ORDER[expected_active]]
                active_color_ok = probe["activeDotColor"] == expected_color
            title_ok = probe["h1Titles"] == EXPECTED_TITLES
            shadow_ok = all(
                (t != "none") if BIOME_ORDER[i] == "selva" else (t == "none")
                for i, t in enumerate(probe["h1TextShadows"])
            )
            dots_ok = probe["dotsVisible"] and probe["dotsCount"] == 6

            results.append({
                "label": label,
                "scrollY": y,
                "notes": notes,
                "probe": probe,
                "title_ok": title_ok,
                "shadow_ok": shadow_ok,
                "dots_ok": dots_ok,
                "active_ok": probe["activeDotIdx"] == expected_active,
                "active_color_ok": active_color_ok,
            })
            print(
                f"[{label:<26} y={y:<6}] active={probe['activeDotIdx']}/expected={expected_active} "
                f"color_ok={active_color_ok} titles_ok={title_ok} shadows_ok={shadow_ok} "
                f"dots_ok={dots_ok} opacities={probe['layerOpacities']}"
            )

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")

    print("\n--- summary ---")
    all_pass = all(
        r["title_ok"] and r["shadow_ok"] and r["dots_ok"] and r["active_ok"] and r["active_color_ok"]
        for r in results
    )
    print(f"Total positions: {len(results)}, all PASS: {all_pass}")
    failed = [r for r in results if not (r["title_ok"] and r["shadow_ok"] and r["dots_ok"] and r["active_ok"] and r["active_color_ok"])]
    if failed:
        for r in failed:
            print(f"  FAIL {r['label']}: title={r['title_ok']} shadow={r['shadow_ok']} dots={r['dots_ok']} active={r['active_ok']} color={r['active_color_ok']}")


if __name__ == "__main__":
    main()
