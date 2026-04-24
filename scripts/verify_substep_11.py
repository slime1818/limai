"""Substep 11 verification. Mobile-responsive Puna pilot check.

Three viewports: 390x844 (iPhone 14 Pro narrow), 414x896 (iPhone 14 Plus),
768x1024 (iPad portrait, md-breakpoint boundary).

Three scroll-positions per viewport: y=0 (Apu hero), y=sectionHeight (Puna hero),
y=1.5*sectionHeight (Puna viewport 2 teaser).

Generates report markdown at docs/screenshots/fase-2/substep-11-mobile-verify.md
if all checks pass.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("390", 390, 844),
    ("414", 414, 896),
    ("768", 768, 1024),
]


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    all_rows: list[dict] = []
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vlabel, vw, vh in VIEWPORTS:
            context = browser.new_context(
                viewport={"width": vw, "height": vh},
                device_scale_factor=1,
            )
            page = context.new_page()

            def on_console(msg, label=vlabel):
                if msg.type in ("error", "warning"):
                    console_errors.append(f"[{label} {msg.type}] {msg.text}")

            page.on("console", on_console)
            page.on("pageerror", lambda err, label=vlabel: console_errors.append(f"[{label} pageerror] {err}"))

            page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("h1", state="visible", timeout=20000)
            page.wait_for_function(
                "() => { const imgs = document.images; return imgs.length > 0 && imgs[0].complete && imgs[0].naturalWidth > 0; }",
                timeout=30000,
            )
            page.wait_for_timeout(2000)

            section_height = vh * 2  # 200dvh

            # Prime lazy loads by scrolling through Apu+Puna range
            for y in range(0, int(section_height * 2.5), int(vh / 2)):
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(200)

            positions = [
                ("apu", 0),
                ("puna-hero", section_height),
                ("puna-v2", int(section_height * 1.5)),
            ]

            for plabel, y in positions:
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(1500)
                page.wait_for_function(
                    "() => { const imgs = Array.from(document.images).slice(0, 3); return imgs.every(i => i.complete && i.naturalWidth > 0); }",
                    timeout=30000,
                )
                page.wait_for_timeout(800)

                probe = page.evaluate(
                    """() => {
                        const imgs = Array.from(document.images);
                        const rendered = imgs.filter(i => i.complete && i.naturalWidth > 0);
                        // Find ImageStack container (fixed inset-0 z-0)
                        const stackContainer = document.querySelector('.fixed.inset-0.w-full');
                        const stackRect = stackContainer ? stackContainer.getBoundingClientRect() : null;
                        // Find ScrollProgressDots container
                        const dotsContainer = document.querySelector('[aria-hidden="true"].fixed.right-8');
                        const dotsStyle = dotsContainer ? window.getComputedStyle(dotsContainer) : null;
                        const dotsVisible = dotsStyle ? dotsStyle.display !== 'none' : false;
                        // Probe h1 visibility (viewport-1 titles)
                        const h1s = document.querySelectorAll('h1');
                        const visibleH1 = Array.from(h1s).filter(h => {
                            const r = h.getBoundingClientRect();
                            return r.top < window.innerHeight && r.bottom > 0;
                        }).map(h => h.textContent);
                        // Probe paragraphs visibility (taglines + teasers)
                        const visibleP = Array.from(document.querySelectorAll('section p')).filter(pe => {
                            const r = pe.getBoundingClientRect();
                            return r.top < window.innerHeight && r.bottom > 0;
                        }).map(pe => pe.textContent.slice(0, 40));
                        // Probe CTA visibility
                        const visibleCTA = Array.from(document.querySelectorAll('section a')).filter(a => {
                            const r = a.getBoundingClientRect();
                            return r.top < window.innerHeight && r.bottom > 0;
                        }).map(a => a.textContent);
                        return {
                            imgs_rendered: rendered.length,
                            imgs_total: imgs.length,
                            stack_top: stackRect ? stackRect.top : null,
                            stack_height: stackRect ? stackRect.height : null,
                            dots_visible: dotsVisible,
                            viewH: window.innerHeight,
                            viewW: window.innerWidth,
                            visible_h1: visibleH1,
                            visible_p_count: visibleP.length,
                            visible_cta: visibleCTA,
                        };
                    }"""
                )

                out = OUT_DIR / f"substep-11-{vlabel}-{plabel}.png"
                page.screenshot(path=str(out), full_page=False)

                row = {
                    "viewport": f"{vw}x{vh}",
                    "position": plabel,
                    "y": y,
                    **probe,
                    "screenshot": out.name,
                }
                all_rows.append(row)
                print(f"[{vlabel} @ {plabel} y={y}] stack_top={probe['stack_top']} dots={probe['dots_visible']} h1={probe['visible_h1']} -> {out.name}")

            context.close()

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")

    # Evaluate checks
    print("\n--- check report ---")
    issues = []
    for row in all_rows:
        vw = int(row['viewport'].split('x')[0])
        expected_dots = vw >= 768  # md breakpoint
        stack_top_ok = row['stack_top'] == 0  # fixed at viewport top
        dots_ok = row['dots_visible'] == expected_dots
        imgs_ok = row['imgs_rendered'] > 0
        h1_ok = len(row['visible_h1']) > 0 or row['position'] == 'puna-v2'

        if not stack_top_ok:
            issues.append(f"{row['viewport']} @ {row['position']}: ImageStack top not at 0 (={row['stack_top']})")
        if not dots_ok:
            issues.append(f"{row['viewport']} @ {row['position']}: dots visibility mismatch (expected {expected_dots}, got {row['dots_visible']})")
        if not imgs_ok:
            issues.append(f"{row['viewport']} @ {row['position']}: no images rendered")
        if not h1_ok:
            issues.append(f"{row['viewport']} @ {row['position']}: no h1 visible on viewport-1 position")

        status = "OK" if (stack_top_ok and dots_ok and imgs_ok and h1_ok) else "CHECK"
        print(f"{row['viewport']:<10} {row['position']:<12} y={row['y']:<6} stack-top={row['stack_top']} dots={row['dots_visible']}/{expected_dots} imgs={row['imgs_rendered']} h1={len(row['visible_h1'])} cta={len(row['visible_cta'])} [{status}]")

    if issues:
        print(f"\n{len(issues)} issue(s):")
        for i in issues:
            print(f"  - {i}")
    else:
        print("\nAll checks passed.")


if __name__ == "__main__":
    main()
