"""Substep 13 verify. Selva text-shadow toegepast, non-Selva biomes unchanged."""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        def check(ctx_opts, vlabel: str, section_h: int):
            print(f"\n--- {vlabel} ---")
            ctx = browser.new_context(**ctx_opts)
            page = ctx.new_page()
            page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("section", timeout=20000)
            page.wait_for_timeout(2500)

            # Scroll to prime lazy-load
            for y in range(0, section_h * 6, section_h // 2):
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(200)

            # Check text-shadow on Selva h1 (biome index 3) at its section-start
            selva_y = section_h * 3
            page.evaluate(f"window.scrollTo(0, {selva_y})")
            page.wait_for_timeout(1500)
            probe = page.evaluate(
                """() => {
                    const h1s = Array.from(document.querySelectorAll('section h1'));
                    return h1s.map(h => ({
                        text: h.textContent,
                        textShadow: window.getComputedStyle(h).textShadow,
                    }));
                }"""
            )
            print("h1 text-shadow per biome:")
            for p in probe:
                has_shadow = p['textShadow'] != 'none'
                tag = "SHADOW" if has_shadow else "none"
                print(f"  [{tag:6}] {p['text']:<20} {p['textShadow']}")

            # Screenshot Selva section
            page.screenshot(path=str(OUT_DIR / f"substep-13-{vlabel}-selva.png"), full_page=False)

            # Scroll to Apu (baseline contrast check)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT_DIR / f"substep-13-{vlabel}-apu.png"), full_page=False)

            ctx.close()

        check(
            ctx_opts={"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1},
            vlabel="desktop",
            section_h=1800,
        )
        check(
            ctx_opts={
                "viewport": {"width": 390, "height": 844},
                "device_scale_factor": 1,
                "has_touch": True,
                "is_mobile": True,
            },
            vlabel="mobile",
            section_h=1688,
        )
        browser.close()


if __name__ == "__main__":
    main()
