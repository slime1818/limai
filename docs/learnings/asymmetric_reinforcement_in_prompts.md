# Asymmetric reinforcement in Flux prompts

## Lesson
Flux respecteert negatives en compositional directives met voldoende herhaling (3-6x verspreid door prompt), maar absolute pixel-coordinates negeert het grotendeels — zelfs met "non-negotiable" framing. Fractional position language ("one-third from top", "upper-middle") compliance is consistent; absolute pixel specs zijn onvoorspelbaar.

## Validation
Positional:
- Boats v1 "y=220-240 out of 768 pixel height" → Flux interpreted as rough guidance, not pixel-pin
- Boats v2 "one-quarter to one-third down from top, within 60-80 pixels vertical range" → better compliance via fractional primary
- Framing-waves v1 "y=560 to 620 pixel range, non-negotiable for composite pipeline" → 0/10 compliance. Flux ignored pixel spec, crests landed y=330-510. "Non-negotiable" language had zero effect.

Compositional:
- Boats v2 anti-ruler-line reinforcement 6x (4 negatives + 2 main paragraph) → no geometric-line regression
- Pacifico sky-subject anti-water 9+ negatives → 1/10 compliance. Flux prior "sunset sea = horizon line" was stronger than negatives. But the 1/10 that complied, was usable.
- Framing-waves anti-kitsch 10+ negatives spread through prompt → 10/10 muted palette compliance. Palette negatives respected.

## Pattern
For positional constraints:
- Fractional language primary ("upper third", "bottom quarter")
- Pixel ranges as secondary consistency check, not as pin
- Expect 50-80% compliance on fractional, 0-30% on absolute pixel

For compositional negatives:
- Minstens 3x herhaling verspreid door prompt, niet clustered
- "No [X]" phrases work better than "not [X]" phrases
- Palette negatives respect > compositional negatives respect > pixel negatives respect

For Flux-prior fights:
- When asking Flux to override strong prior (sunset-without-horizon, boats-without-water), expect low compliance rate. Plan 2-3 batches, accept 1-2 usable variants.

## Cost-benefit
Repetitive negatives add ~100-300 chars per prompt. Worth it for palette/composition; waste of tokens for pixel specs.
