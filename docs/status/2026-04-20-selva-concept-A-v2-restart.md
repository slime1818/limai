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
