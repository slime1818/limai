# Visual read calibration

## Lesson
Visual-intuition readings van user en Claude differ vaak op specifieke axes. Claude Code's diagnostic sampling is de belangrijke correctie op beide. Visual intuition is trigger voor aandacht; diagnostic data is bron voor decisions.

## Validation
User ↔ Claude disagreements resolved by diagnostic:
- Pacifico sky-subject Image 2 palette: Claude said "warm peach fringe + teal-grey base" → diagnostic showed "neutral grey all bands, warm only in left quintile x=204-409." User's initial description was calibrated to expected-sunset imagery, not actual muted Peruvian coast.
- Pacifico boats Image 5 cluster y-range: user visual read y=130-440 → diagnostic y=131-520. 80px deeper than visual, due to wake/reflection painting below hull counted as dark pixels.
- Pacifico composite hulls post-extraction: both Claude and user described boats as "warm brown" after commit 28a892a → diagnostic found hulls at #62243f (pink-lean R-B +35). Visual read was relative (compared to magenta background, hulls looked brown), diagnostic was absolute (R-B ratio indicates pink influence).

Pattern held consistently: visual agreement is weak evidence, diagnostic cijfers are strong evidence.

## Pattern
Workflow for palette-match or offset-planning:
1. User + Claude visually scan for trigger (something looks off, or palette-continuity needs verification)
2. Claude Code diagnostic: sample target zone, report RGB medians, detect offsets, confirm stddev ranges
3. Compare diagnostic to expected values
4. If diagnostic disagrees significantly with expectations, trust diagnostic over intuition
5. Next prompt/composite operation anchored to diagnostic numbers, not visual impression

Specific diagnostic triggers:
- Before writing palette-match block → sample previous layer
- Before setting compositor offset → diagnostic y-range of layer content
- After chroma extraction → sample result pixels for residual color-drift
- Before production-lock → visual verify in viewer AND diagnostic cross-check

## Anti-pattern
Visual-only production locks are unsafe. Pacifico 28a892a was visually approved in viewer but had pink-hull regression that diagnostic would have caught. Added visual-verify + diagnostic-cross-check as required gate going forward.
