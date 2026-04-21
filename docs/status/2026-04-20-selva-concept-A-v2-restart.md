# Selva biome-4 Concept A v2 restart — 2026-04-20

## v1 status
Sky-subject B-winner (river + distant trees + mist) + plateau v6 side-frame + canopy Image 4. Composite: feather + clamp + mask stack. Gate 8 PASS 6.13:1 but visually weak: plateau understory reads as stickers, river-bank<->plateau palette break.

## v2 strategy
New sky-subject with palette-continuity zone (lower-middle 20% warm-saturated Palette C matching future plateau). New plateau (simpler than v6 — no side columns, just foreground understory band with organic top). Canopy Image 4 reused with known-good settings: offset (0,0), feather 150-260, luminance clamp 0.65.

## Differentiation preserved
River stays — vs Pacifico ocean teal, vs Paracas desert bronze.

## Retained lessons
- Palette C direction confirmed
- TOP framing geometry works
- No wildlife, sunbeams OK
- Tolerance 130 + relaxed is_pinkish for Selva

## Sky-subject v7 Image 3 palette reference
Pixel analysis of zone y=460..600 (lower-middle 20% of 768-height source), 134,144 non-magenta pixels sampled:

| Role | RGB | Hex |
|------|-----|-----|
| Overall median | (44, 50, 24) | `#2c3218` |
| Leaf-shadow (dark green, low-lum) | (13, 13, 7) | `#0e1007` |
| Dominant green (g>r+5, g>b+5) | (39, 49, 22) | `#273116` |
| Leaf-rim highlight (green, high-lum) | (91, 98, 48) | `#5b6230` |
| Warm highlight (top quartile lum) | (129, 102, 52) | `#816634` |
| Warm undertone (r≥g, r>b+10) | (106, 83, 40) | `#6a5328` |

Top-6 quantized clusters (24-step bins):
1. RGB(12, 12, 12) — 20.8% (deep jungle shadow)
2. RGB(36, 36, 12) — 17.2% (dark warm-olive shadow)
3. RGB(60, 60, 36) — 8.4% (mid-olive)
4. RGB(108, 84, 36) — 8.0% (warm bronze highlight)
5. RGB(132, 108, 60) — 7.0% (warm tobacco accent)
6. RGB(36, 60, 36) — 4.8% (saturated leaf green)

**Palette C signature:** DARK humid dominant — shadows ~40% of pixel mass, greens are desaturated-warm (g and r close, low b), warm bronze threads through highlights NOT cool rim-light. Not "bright saturated jungle green" — dark mossy humid-warm.

Plateau v7 palette-match target = these values. Plateau must extend this palette into the foreground band without visible break.

## Canopy v5 palette reference (from locked sky-subject v7 Image 3 upper zone)
Sky-subject v7 Image 3 + plateau v7 Image 8 integrate clean (palette-match resolved v1 break). Canopy Image 4 is the weak link — reads cartoony vs painterly lower layers. Regenerating canopy only.

Pixel analysis of sky-subject upper 30% atmospheric zone (y=0..230, combined 235,520 non-magenta pixels):

| Role | RGB | Hex |
|------|-----|-----|
| Atmospheric mid (median) | (87, 90, 52) | `#575a34` |
| Dominant leaf-green | (71, 77, 45) | `#474d2d` |
| Dark shadow silhouette | (20, 21, 12) | `#14150c` |
| Trunk-silhouette (Q5 lum) | (12, 14, 9) | `#0c0e09` |
| Leaf-rim highlight (Q75 lum) | (151, 152, 105) | `#979869` |
| Warm bark undertone | (120, 117, 70) | `#787546` |

Sub-zone breakdown:

**Yungas-handoff mist (top 15%, y=0..115):** median #434527, dominant green #272d1a, warm undertone #726d3e, highlight #afae75 — mist rendered WARM not cool (warm Andean transition from Yungas cold khaki into Selva humid warm).

**Canopy-emerging (y=115..230):** median #66693f, dominant green #555c36, warm undertone #7d7c4f, highlight #949569 — lighter than mist above, less saturated than plateau below, mid-atmospheric.

**Feather blend zone (y=170..280, where canopy alpha fades into sky-subject):** median #525634, dominant green #4c5230, 47% green-dominant pixel density — anchors canopy LOWER EDGE palette target.

Compared to plateau (locked, foreground darker): plateau dominant green #273116 vs canopy target #474d2d — canopy sits 2 Euclidean steps lighter in Z-order, producing natural atmospheric perspective.

Canopy v5 palette-match target = these values. Canopy must extend sky-subject's upper atmospheric palette upward into the TOP 20-30% framing zone without visible style break, with painterly-humid shading matching the locked lower layers (NOT cartoony flat).
