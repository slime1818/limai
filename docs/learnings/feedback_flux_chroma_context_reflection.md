# Flux chroma-context reflection — lesson and fix pattern

## The problem

When an element layer is prompt-engineered as a stylized scene where the "background" is the chroma color (e.g., "boats on magenta ocean" instead of "boats on flat magenta isolation"), Flux paints the element WITH hue-reflection from the chroma environment. The rendered element pixels carry the chroma's color influence even though they're clearly distinct from pure chroma.

**Pacifico boats v3 example (2026-04-22):** prompted as "boats on stylized magenta ocean" (leveraging Flux's ocean-scene training for natural hull-waterline placement — lesson from `feedback_flux_no_chroma_key_training`). Source hull silhouettes came out at median RGB(178, 43, 107) `#b22b6b` — heavily magenta-pink-tinted, NOT the prompted warm-brown target RGB(40-70, 30-55, 25-45).

## Why standard chroma extraction misses it

Tolerance-based extraction (e.g., tolerance 80 from detected magenta RGB(216, 48, 133)) catches pixels within Euclidean distance of the detected target magenta. Magenta-tinted hulls have Euclidean distance ~150+ from pure magenta, so they stay opaque. Post-extraction hulls retain the pink tint.

Pacifico post-extraction: hull median RGB(98, 36, 63) `#62243f`, R-B gap +35. Still magenta-leaning, just darker than source.

Strict `is_pinkish` bounds also don't help — they catch pure magenta chroma only, not chroma-reflected element pixels.

## The fix pattern (Pacifico follow-up commit)

Two-pass correction applied to the element layer after chroma extraction, before compositing:

### 1. Top-band mask

Zero alpha for all pixels with `y < known_drift_y` where Flux's "sky prior" or similar environment prior creates a lighter color band different from the main scene. In Pacifico boats, y=0..99 had a warm-pink sky prior `#fb77bc` RGB(254, 119, 188) that survived chroma extraction (R-B gap ~66, outside strict `is_pinkish` bounds, outside tolerance 80 from detected chroma).

```python
def mask_top_rows(img, mask_end_y):
    arr = np.array(img).astype(np.float64)
    arr[:mask_end_y, :, 3] = 0
    return Image.fromarray(arr.astype(np.uint8), mode="RGBA")
```

Applied with `mask_end_y=100` for Pacifico boats. 58,373 previously-opaque pink-drift pixels zeroed.

### 2. HSL hue-rotation + desaturation

For pixels where `R > B + threshold` (magenta-leaning), rotate hue toward the intended target hue and reduce saturation. Preserve L (luminance) so element darkness is retained.

```python
def neutralize_pink_hulls(img, r_b_threshold=15, target_hue_deg=25,
                          hue_shift_strength=0.75, sat_reduction=0.65):
    # Convert to HSL, rotate hue toward target, reduce saturation, convert back.
    # See scripts/process_pacifico.py for full vectorized numpy implementation.
```

Parameters that worked for Pacifico boats:
- `r_b_threshold=15` — triggers on any warm-lean pixel
- `target_hue_deg=25` — warm-brown (brown is roughly 20-35° in HSL)
- `hue_shift_strength=0.75` — rotates 75% toward target, preserves some natural variation
- `sat_reduction=0.65` — keeps 35% saturation. Neutralizes pink without going grey.

**Result:** hull median `#62243f` R-B +35 → `#4d3c37` R-B +22 (warm-brown). 30,292 pixels corrected. Spec target was R-B +15 to +25, actual lands at +22 — clean hit.

## When to apply

- Any element layer prompted as "X inside a stylized-color scene" rather than "X on flat color isolation"
- Source element silhouettes show R-B gap > +30 (indicates chroma color-reflection)
- Euclidean distance from detected chroma exceeds tolerance AND element pixels still carry chroma hue

## When NOT to apply

- Elements already rendered with intended warm-scene colors (no chroma-reflection artifact)
- Target element hue is itself close to the chroma color (e.g., if composite target is pink/red, don't correct toward warm-brown)
- Chroma-reflection IS the design intent (rare — usually a bug)

## Companion lesson

This fix pattern is the counterpart to `feedback_flux_no_chroma_key_training` (save memory). That lesson says: frame isolation briefs as stylized scenes to get natural placement. This lesson says: expect chroma color-reflection as the side-effect, and add a post-extraction correction pass.

The two lessons together describe the complete pattern:
1. Prompt-side: stylize the scene ("element in magenta ocean")
2. Pipeline-side: correct the chroma-reflection ("HSL hue-rotate + desaturate pink-leaning pixels")

## Implementation reference

See `scripts/process_pacifico.py`:
- `mask_top_rows()` — alpha mask for sky-prior bands
- `rgb_to_hsl_np()` / `hsl_to_rgb_np()` — vectorized HSL conversion (no scipy/colorsys dependency)
- `neutralize_pink_hulls()` — HSL correction with configurable R-B threshold, target hue, shift strength, saturation reduction
- Wired into the main loop under the `name == "boats"` branch after `process_layer()` and before the webp save

## History

- 2026-04-22 commit 28a892a: Pacifico v1 production-lock (premature — pink boats shipped)
- 2026-04-22 commit [this one]: chroma-context reflection fix implemented, warm-brown hulls restored, REAL production-lock
