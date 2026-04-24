"""Substep 12 regression pass, mobile batch. 11 scroll-positions at 390x844, section_h = 1688."""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2/regression-pass")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POSITIONS = [
    ("apu-hero-mobile", 0, 0, "Apu"),
    ("apu-puna-T1-mobile", 1430, 1, "Apu/Puna crossfade midpoint"),
    ("puna-hero-mobile", 1688, 1, "Puna"),
    ("puna-yungas-T2-mobile", 3118, 2, "Puna/Yungas crossfade midpoint"),
    ("yungas-hero-mobile", 3376, 2, "Yungas"),
    ("yungas-selva-T3-mobile", 4806, 3, "Yungas/Selva crossfade midpoint"),
    ("selva-hero-mobile", 5064, 3, "Selva (no scrim, text-shadow)"),
    ("selva-paracas-T4-mobile", 6494, 4, "Selva/Paracas crossfade midpoint"),
    ("paracas-hero-mobile", 6752, 4, "Paracas"),
    ("paracas-pacifico-T5-mobile", 8182, 5, "Paracas/Pacifico crossfade midpoint"),
    ("pacifico-hero-mobile", 8440, 5, "Pacifico"),
]

EXPECTED_TITLES = ["LimAI", "Wie we zijn", "Wat we doen", "Wat we maakten", "Hoe we werken", "Laten we praten"]
EXPECTED_ACCENTS = {
    "apu": "rgb(168, 200, 212)",
    "puna": "rgb(184, 164, 122)",
    "yungas": "rgb(107, 142, 107)",
    "selva": "rgb(58, 95, 58)",
    "paracas": "rgb(184, 127, 74)",
    "pacifico": "rgb(90, 138, 148)",
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
            viewport={"width": 390, "height": 844},
            device_scale_factor=1,
            has_touch=True,
            is_mobile=True,
        )
        page = ctx.new_page()
        page.on("console", lambda m: console_errors.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: console_errors.append(f"[pageerror] {e}"))

        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("section", timeout=20000)
        page.wait_for_timeout(2500)

        # Prime lazy-load
        for y in [1400, 3100, 4800, 6500, 8200]:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(300)

        results = []
        for label, y, expected_active, notes in POSITIONS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1800)

            probe = page.evaluate(
                """() => {
                    const h1s = Array.from(document.querySelectorAll('section h1'));
                    const dotsContainer = document.querySelector('[aria-hidden=\"true\"].fixed.right-8');
                    const dotsStyle = dotsContainer ? window.getComputedStyle(dotsContainer) : null;
                    const dots = dotsContainer ? Array.from(dotsContainer.children) : [];
                    // Op mobile heeft dotsContainer display:none, dus getBoundingClientRect geeft 0. Detect active via inline style.backgroundColor (alleen active dot heeft dat gezet).
                    const activeDotIdx = dots.findIndex(d => d.style.backgroundColor !== "");
                    const activeDotColor = activeDotIdx >= 0 ? dots[activeDotIdx].style.backgroundColor : null;
                    const layers = Array.from(document.querySelectorAll('.fixed.inset-0.w-full.h-screen > .absolute.inset-0'));
                    const layerOpacities = layers.map(l => Number(parseFloat(window.getComputedStyle(l).opacity).toFixed(3)));
                    const textShadows = h1s.map(h => window.getComputedStyle(h).textShadow);
                    return {
                        dotsHiddenExpected: dotsStyle ? dotsStyle.display === 'none' : false,
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

            # At T-crossover midpoint (label contains "-T"): active may be either previous
            # or current biome depending on exact scrollY vs hook's switch-point (section.top
            # minus crossfadeHalf = 0.15 * section_h). Opacities show ~0.5/0.5 regardless.
            is_crossover = "-T" in label
            valid_active_indices = (
                {expected_active, max(0, expected_active - 1)} if is_crossover else {expected_active}
            )
            active_ok = probe["activeDotIdx"] in valid_active_indices
            active_color_ok = False
            if probe["activeDotIdx"] >= 0:
                current_biome = BIOME_ORDER[probe["activeDotIdx"]]
                expected_color_hex = EXPECTED_ACCENTS[current_biome]
                inline_val = probe["activeDotColor"] or ""
                var_ref = f"var(--color-{current_biome})"
                active_color_ok = inline_val == var_ref or inline_val == expected_color_hex
            title_ok = probe["h1Titles"] == EXPECTED_TITLES
            shadow_ok = all(
                (t != "none") if BIOME_ORDER[i] == "selva" else (t == "none")
                for i, t in enumerate(probe["h1TextShadows"])
            )
            dots_hidden_ok = probe["dotsHiddenExpected"] and probe["dotsCount"] == 6

            results.append({
                "label": label,
                "scrollY": y,
                "notes": notes,
                "probe": probe,
                "title_ok": title_ok,
                "shadow_ok": shadow_ok,
                "dots_hidden_ok": dots_hidden_ok,
                "active_ok": active_ok,
                "active_color_ok": active_color_ok,
            })
            print(
                f"[{label:<32} y={y:<6}] active={probe['activeDotIdx']}/expected={expected_active} "
                f"color_ok={active_color_ok} titles_ok={title_ok} shadows_ok={shadow_ok} "
                f"dots_hidden_ok={dots_hidden_ok} opacities={probe['layerOpacities']}"
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
        r["title_ok"] and r["shadow_ok"] and r["dots_hidden_ok"] and r["active_ok"] and r["active_color_ok"]
        for r in results
    )
    print(f"Total positions: {len(results)}, all PASS: {all_pass}")
    failed = [r for r in results if not (r["title_ok"] and r["shadow_ok"] and r["dots_hidden_ok"] and r["active_ok"] and r["active_color_ok"])]
    if failed:
        for r in failed:
            print(f"  FAIL {r['label']}: title={r['title_ok']} shadow={r['shadow_ok']} dots_hidden={r['dots_hidden_ok']} active={r['active_ok']} color={r['active_color_ok']}")


if __name__ == "__main__":
    main()
