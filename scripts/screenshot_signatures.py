"""Render Olivier en Abdul SVG-handtekeningen op een LimAI noche-andina test-page
en schrijf een screenshot voor visuele verificatie.

Doel: laten zien dat de gegenereerde SVG's leesbaar zijn als script-handtekeningen
in copper kleur, voor pass 2.2 deliverable. Geen integratie in PunaSection.tsx.

Schrijft docs/screenshots/fase-2/signatures-pass2-2.png. Vereist Playwright.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SIG_DIR = ROOT / "public" / "team" / "signatures"
OUT_DIR = ROOT / "docs" / "screenshots" / "fase-2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = OUT_DIR / "signatures-pass2-2.png"

VIEWPORT_W, VIEWPORT_H = 1200, 800


def render() -> None:
    olivier_svg = (SIG_DIR / "olivier.svg").read_text(encoding="utf-8")
    abdul_svg = (SIG_DIR / "abdul.svg").read_text(encoding="utf-8")

    # Inline-SVG zodat we geen lokale http-server nodig hebben. Test-page mirrort
    # LimAI tokens: noche-andina bg, copper-bright accent, Inter-achtige system
    # mono-font voor de label.
    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8" />
<title>Signatures pass 2.2 verify</title>
<style>
  :root {{
    --noche-andina: #1a1612;
    --andes-copper: #b87f4a;
    --andes-copper-bright: #d49a6a;
    --warm-white: #f5ede0;
  }}
  html, body {{
    margin: 0;
    padding: 0;
    background: var(--noche-andina);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  }}
  body {{
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    gap: 64px;
    padding: 64px 96px;
  }}
  .row {{
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }}
  .label {{
    color: var(--andes-copper-bright);
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-feature-settings: 'tnum';
  }}
  .signature {{
    color: var(--andes-copper);
    height: 140px;
  }}
  .signature svg {{
    height: 100%;
    width: auto;
    display: block;
  }}
  .footnote {{
    color: var(--andes-copper-bright);
    opacity: 0.6;
    font-size: 11px;
    letter-spacing: 0.1em;
    margin-top: 32px;
  }}
</style>
</head>
<body>
  <div class="row">
    <div class="label">Olivier</div>
    <div class="signature">{olivier_svg}</div>
  </div>
  <div class="row">
    <div class="label">Abdul</div>
    <div class="signature">{abdul_svg}</div>
  </div>
  <div class="footnote">Allura-Regular, copper #b87f4a op noche-andina #1a1612</div>
</body>
</html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.set_content(html, wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUTPUT), full_page=False)
        browser.close()
    print(f"[signatures] -> {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    render()
