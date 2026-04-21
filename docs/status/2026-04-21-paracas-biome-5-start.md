# Paracas biome-5 start — 2026-04-21

## Selva recap
Biome-4 production-locked 2026-04-20. Palette-match paint-time strategy validated. All 4 biomes now locked.

## Paracas user decisions
- Framing: BOTTOM dune (first BOTTOM in project, novel)
- Architecture: 3-layer (sky + plateau + framing-dune curved forward of plateau)
- Character: sand-dunes-dominant, subtle rock silhouettes on horizon, ocean-mist hint beyond
- Palette: Desert Bronze accent #b87f4a, warm late-day atmosphere

## Budget plan
- Sky-subject: $0.24 (8x batch)
- Plateau: $0.12 (4x batch, after sky-subject palette extracted)
- Framing-dune curved: $0.24 (8x batch, novel BOTTOM framing)
- Total: $0.60 of $2.35 remaining

## Open questions (to resolve during build)
- Framing-dune curved shape geometry: how much vertical arc? Will determine offset/feather architecture for process_paracas.py
- T4 golden-dust integration: handled by sky-subject top zone (soft) OR requires dedicated particle overlay in Next.js phase? Assume Next.js handles particles separately — sky-subject only sets atmospheric tone.

## Sky-subject v1 Image 7 palette reference
Pixel analysis of zone y=460..600 (lower-middle 20% of 768-height source), 143,360 pixels (100% opaque — zone sits above the chroma strip):

| Role | RGB | Hex | Density |
|------|-----|-----|---------|
| Warm undertone (dominant) | (165, 125, 100) | `#a57d64` | 67.7% |
| Overall median | (146, 110, 91) | `#926e5b` | — |
| Warm bronze highlight | (197, 155, 120) | `#c59b78` | 25.0% (Q75 lum) |
| Cool lavender shadow | (67, 64, 77) | `#43404d` | 35.4% (cool-drift zone) |
| Warm peach accent | (204, 156, 132) | `#cc9c84` | 6.9% cluster |
| Texture bronze-earth | (180, 132, 108) | `#b4846c` | 10.4% cluster |
| Ichu tussock (sparse) | (114, 105, 95) | `#72695f` | 0.1% |

Top-5 quantized clusters (24-step bins):
1. RGB(60, 60, 84) `#3c3c54` — 12.7% (cool purple shadow)
2. RGB(180, 132, 108) `#b4846c` — 10.4% (warm bronze)
3. RGB(156, 108, 84) `#9c6c54` — 10.1% (warm bronze mid)
4. RGB(204, 156, 132) `#cc9c84` — 6.9% (warm peach highlight)
5. RGB(84, 84, 84) `#545454` — 5.7% (neutral gray)

**Brand accent #b87f4a RGB(184, 127, 74) euclid distances:** vs warm undertone **32.3** (closest — Image 7 tracks brand accent tightly), vs overall median 45.0, vs warm bronze highlight 55.4.

**Paracas signature:** warm bronze dominating (~67% pixel mass) + cool lavender-gray shadow threading (~35%) — Image 7 balances warm-primary + cool-shadow deliberately, executing the user's "cool lavender-gray shadow slopes" prompt constraint. Ichu tussocks under-rendered at 0.1% — plateau can include 2-4 sparse clusters without breaking palette match. Clean warm coastal-desert palette with no Selva-green handoff drift (user rejected green-handoff variants).

Plateau v1 palette-match target = these values. Plateau must extend warm-bronze sand + cool-shadow threading into the foreground band without visible break.

## Plateau Image 5 TOP-zone palette reference
Plateau opaque band came out at 42.3% of canvas (y=442..767) vs target 15-18% — Flux expanded the band, offset tuning will handle it at composite time. Palette analysis of the plateau TOP-edge 100 rows (y=442..542, 97,399 non-magenta pixels):

| Role | RGB | Hex | Density |
|------|-----|-----|---------|
| Warm dune-sand dominant | (199, 161, 154) | `#c7a19a` | 55.3% |
| Painterly neutral median | (144, 119, 131) | `#907783` | — |
| Warm bronze-cream highlight | (233, 187, 173) | `#e9bbad` | 25.0% (Q75) |
| Cool lavender shadow | (85, 78, 101) | `#554e65` | 25.0% (Q25) |
| Cool drift shadow | (96, 88, 111) | `#60586f` | 59.9% |

**Palette integration check (plateau TOP-edge vs sky-subject lower-middle):**
- warm_dominant: euclid **73.3** (plateau drifted warmer-pinker than sky target)
- median: euclid 41.0
- highlight: euclid 71.6 (plateau highlights pinker)
- shadow: euclid 33.1 (close match)

Plateau Image 5 reads visually coherent per user's accepted pick, but RGB-wise drifted toward pink-bronze rather than orange-bronze. This shifts the framing-dune anchor: framing-dune sits DIRECTLY in front of plateau TOP-edge, so its palette target = plateau TOP-edge values (the boundary it will continue), NOT sky-subject ideal.

## Framing-dune v1 palette target
Same as plateau TOP-edge palette above. Slight saturation bump permitted on warm highlights for foreground atmospheric-perspective (closer-to-camera = more saturation), but warm-primary + cool-shadow balance must be preserved. Key anchors fed to prompt:
- warm dune-sand dominant: `#c7a19a`
- neutral median: `#907783`
- warm cream highlight: `#e9bbad`
- cool lavender shadow: `#554e65`
- cool drift shadow: `#60586f`

Architecture: BOTTOM 25-30% opaque content, CURVED ARC top edge (asymmetric dune crest — first curved-edge framing in project), 70-75% magenta. Composite stack: sky → plateau → framing-dune (front).
