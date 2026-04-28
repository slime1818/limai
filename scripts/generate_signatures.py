"""Genereer SVG-handtekeningen via Allura-Regular.ttf.

Doel: leesbare script-handtekeningen voor Olivier en Abdul, klaar voor pass 3
cinematic intro met clip-path writing animatie. Output gebruikt fill="currentColor"
zodat consumers de kleur via CSS color of SVG inheritance kunnen sturen.

Vereist scripts/fonts/Allura-Regular.ttf (gitignored, herhaalbaar via curl uit
google/fonts repo). Geen kerning-handling: Allura is ontworpen om met advance
widths te connecten.
"""

from pathlib import Path
from typing import List, Tuple

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "scripts" / "fonts" / "Allura-Regular.ttf"
SIG_DIR = ROOT / "public" / "team" / "signatures"

# Padding rondom de tight bbox, in font-units (typisch 1000-2048 per em).
PADDING = 40


def generate_signature(text: str, output_path: Path) -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Font ontbreekt: {FONT_PATH}. Download via "
            "https://github.com/google/fonts/raw/main/ofl/allura/Allura-Regular.ttf"
        )

    font = TTFont(str(FONT_PATH))
    cmap = font.getBestCmap()
    glyphSet = font.getGlyphSet()

    # Per glyph: pen-commands plus cumulatieve x-offset binnen TTF-coordinaten.
    glyph_data: List[Tuple[str, float]] = []

    # Globale bbox accumuleert over alle glyphs in flipped TTF-space.
    g_x_min = float("inf")
    g_x_max = float("-inf")
    g_y_min = float("inf")
    g_y_max = float("-inf")

    x_offset = 0.0
    for char in text:
        codepoint = ord(char)
        glyph_name = cmap.get(codepoint)
        if glyph_name is None:
            print(f"  [waarschuwing] geen glyph voor U+{codepoint:04X} ({char!r}), wordt overgeslagen")
            continue
        glyph = glyphSet[glyph_name]

        path_pen = SVGPathPen(glyphSet)
        glyph.draw(path_pen)
        path_d = path_pen.getCommands()

        bounds_pen = BoundsPen(glyphSet)
        glyph.draw(bounds_pen)
        if bounds_pen.bounds is not None:
            x_min, y_min, x_max, y_max = bounds_pen.bounds
            g_x_min = min(g_x_min, x_min + x_offset)
            g_x_max = max(g_x_max, x_max + x_offset)
            g_y_min = min(g_y_min, y_min)
            g_y_max = max(g_y_max, y_max)

        glyph_data.append((path_d, x_offset))
        x_offset += glyph.width

    if g_x_min == float("inf"):
        # Veiligheidsval: text zonder leesbare glyphs.
        units_per_em = font["head"].unitsPerEm
        g_x_min, g_x_max = 0.0, float(x_offset)
        g_y_min, g_y_max = 0.0, float(units_per_em)

    # ViewBox in flipped user-space. Na <g transform="scale(1 -1)"> mapt TTF-y
    # [y_min, y_max] naar SVG-y [-y_max, -y_min]. Padding wordt symmetrisch
    # rondom de tight bbox toegevoegd.
    vb_x = g_x_min - PADDING
    vb_y = -g_y_max - PADDING
    vb_w = (g_x_max - g_x_min) + 2 * PADDING
    vb_h = (g_y_max - g_y_min) + 2 * PADDING

    paths_xml: List[str] = []
    for path_d, x in glyph_data:
        if not path_d.strip():
            continue
        if x == 0:
            paths_xml.append(f'    <path d="{path_d}" fill="currentColor"/>')
        else:
            paths_xml.append(
                f'    <path d="{path_d}" transform="translate({x:.2f} 0)" fill="currentColor"/>'
            )

    paths_block = "\n".join(paths_xml)

    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!-- Allura by Robert Leuschke, OFL license. "
        "Gegenereerd via scripts/generate_signatures.py -->\n"
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vb_x:.2f} {vb_y:.2f} {vb_w:.2f} {vb_h:.2f}" '
        'aria-hidden="true">\n'
        '  <g transform="scale(1 -1)">\n'
        f"{paths_block}\n"
        "  </g>\n"
        "</svg>\n"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    font.close()
    print(
        f"[{text}] -> {output_path} ({output_path.stat().st_size} bytes), "
        f"viewBox=({vb_x:.0f} {vb_y:.0f} {vb_w:.0f} {vb_h:.0f})"
    )


if __name__ == "__main__":
    SIG_DIR.mkdir(parents=True, exist_ok=True)
    generate_signature("Olivier", SIG_DIR / "olivier.svg")
    generate_signature("Abdul", SIG_DIR / "abdul.svg")
