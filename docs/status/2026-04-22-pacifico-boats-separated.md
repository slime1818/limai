# Pacifico architecture correction — 2026-04-22

## What changed
User caught architecture error after plateau v1 batch: boats cannot be baked into plateau painting if they need to parallax independently in Next.js phase 4. Baking them into plateau locks them to plateau motion — defeats purpose.

## Before
3-layer composite:
- sky-subject (no boats) ✓
- plateau (water + boats)
- framing-waves

## After
4-layer composite:
- sky-subject (no boats) ✓ LOCKED
- plateau v2 (water ONLY, no boats)
- boats v1 (NEW separate layer — silhouettes on full magenta)
- framing-waves

## Retained from plateau v1 batch
1. Palette-match pattern validated at plateau stage (8/10 muted coast compliance)
2. Top-edge seam handling approach from Image 2: soft airbrushed transition, NOT hard horizon line
3. Glint depth-split (Tweak 2) validated — closer glints warmer and brighter, distant glints softer and cooler
4. Asymmetric center-left warmth weighting validated

## Applied to plateau v2
Same palette anchors + same 4-zone structure, but upper-middle zone describes the IMPLIED horizon as empty ocean plane — no boats. Everything else carries over.

## Applied to boats v1
New prompt: silhouettes on full magenta background, no water, no sky, no context. Boats sized and positioned to drop cleanly onto plateau v2's implied horizon line in compositor.
