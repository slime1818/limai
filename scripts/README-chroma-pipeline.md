# Chroma extraction pipeline — per-biome tolerance policy

## Key principle

**Chroma extraction tolerance is NOT architecturally shared cross-biome.** Each biome's painterly palette determines its own safe tolerance. Blind cross-biome consistency breaks on palettes whose painted content falls within the chroma-distance radius.

## Locked per-biome configuration (2026-04-20)

| Biome | Palette character | `CHROMA_TOLERANCE` | `is_pinkish` bounds |
|-------|-------------------|---------------------|---------------------|
| Apu | Cool grey rock + snow + warm bronze plateau | **55** | Strict `r>180, b>120, g<90` |
| Puna | Altiplano warm-bronze + ichu tussocks + khaki earth | **55** | Relaxed `r>160, b>80, g<150` |
| Yungas | Warm jungle greens + wet cloud-forest + moss | **130** | Relaxed `r>160, b>80, g<150` |
| Selva | Deep saturated warm greens + humid wet browns | **130** | Relaxed `r>160, b>80, g<150` |
| Paracas | TBD | TBD at prompt time | TBD |
| Pacífico | TBD | TBD at prompt time | TBD |

## Why tolerance 130 breaks Apu + Puna

Apu + Puna palettes contain warm-bronze rim-light + warm-brown earth pixels at Euclidean distance ~65-90 from their detected chroma targets. Tolerance 130 falsely extracts these legitimate painted pixels as chroma:

- **Apu regression (observed 2026-04-20):** dark rock-shadow pixels within tolerance 130 of plateau chroma `RGB(218, 57, 150)` got removed → black chunks over mountains
- **Puna regression (observed 2026-04-20):** dark foliage pixels within tolerance 130 of plateau chroma `RGB(217, 0, 113)` got removed → black holes in bushes

At tolerance 55 the radius is tight enough that only near-chroma transition pixels get caught. Painted warm-tones stay opaque. Production baselines for Apu + Puna restored with `git checkout HEAD -- scripts/process_apu.py scripts/process_puna.py`.

## Why Yungas + Selva need tolerance 130

Yungas + Selva palettes are deep-saturated warm greens (RGB ~50/100/40 range) — Euclidean distance from typical pink chroma (~230/30/150) exceeds 180. Tolerance 130 catches pink-transition pixels without touching jungle greens.

At tolerance 55, Yungas + Selva's fern silhouettes on magenta produced anti-aliased pink-haze edges that remained opaque — visible pink residue in the composite. Tolerance 130 catches those transition pixels cleanly.

## Acceptable residue: Puna salmon stripe

Puna composite shows ~4k–7k salmon/pink pixels at `y=460..520` under tolerance 55 (detected via criterion `r > g + 30 AND r > b AND r > 140`). This is **acceptable**:

- Painterly warm-tone pixels are indistinguishable from intended altiplano dawn-light content (bronze rim-light on grass-tips, sunrise warmth on stones)
- F6 gradient covers the text-content zone (left 50% viewport) so residue is outside the critical area
- Tolerance bump to 130 would introduce black-hole regressions in foliage — not worth it

## Acceptable residue: Apu mountain-face bottom chroma

Apu mountain-face source renders `RGB(189, 21, 106)` at the bottom chroma-strip. Strict `is_pinkish` (`b > 120`) fails on `b=106` → mountain-face treated as fully opaque, chroma strip remains visible magenta underneath. This is **acceptable**:

- Plateau layer overlays mountain-face bottom 15% with opaque painted rock/snow content, fully covering the magenta strip in the composite
- Relaxing `is_pinkish` would detect the strip and extract it, but then tolerance 55 matches warm-bronze rim-light → black chunks (the full regression pattern)
- Current production state preserves clean Apu composite

## Rule going forward (for Paracas + Pacífico)

When authoring a new biome:

1. Generate composite at **tolerance 55 first** as safe baseline
2. Visual inspect for pink / salmon transition bleed and black chunk regressions
3. Only bump to 130 IF both conditions hold:
   - No warm-tone painted content at risk of false-positive extraction (no bronze rim-light, no warm earth in chroma-distance range)
   - AND fern/leaf silhouette edges show visible pink haze
4. Consider intermediate tolerance (80–100) for biomes with mixed palette
5. `is_pinkish` bounds: strict for cool-palette biomes, relaxed for warm-palette biomes whose rendered chroma has high `g` component

## History

- 2026-04-18: Yungas tolerance 55 → 130 (fern silhouette pink residue fix)
- 2026-04-18: Selva tolerance 130 baseline
- 2026-04-20 morning: Puna salmon-stripe fix attempted via 55 → 130 bump → black foliage holes → reverted
- 2026-04-20 morning: Apu strict `is_pinkish` relax + 55 → 130 bump → black rock chunks → reverted
- 2026-04-20: This README committed to lock in the lesson
