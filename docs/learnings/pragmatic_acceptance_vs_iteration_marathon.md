# Pragmatic acceptance vs iteration marathon

## Lesson
Na 3-4 iteraties op dezelfde layer met dezelfde failure mode, stop. Accept beste-van-slecht, ga door. Iteratie-marathon levert geen proportionele quality-gains en eet budget + tijd + motivatie. Als iteration N+1 dezelfde failure mode vertoont als iteration N, is het fundamental prompt issue of Flux-limit, niet variance.

## Validation
Failure modes (stop signals):
- Selva v1 + v2 + v3 compositor tweaks → same "stickers on scene" read → fresh restart needed (Concept B)
- Pacifico boats v1 (silhouettes on magenta) + v2 (silhouettes with organic variation) → same "objects hanging against pink" read → fundamental approach wrong, v3 reframe needed
- Pacifico framing-waves 10/10 variants failed absolute y-pixel spec → Flux limitation on pixel-pin compliance, accepted best y-range (Image 4) with compositor shift

Success modes (non-marathon):
- Pacifico sky-subject 1/10 compliant (Image 2) → accepted, didn't retry. Result: clean seam pattern for whole Pacifico stack.
- Pacifico plateau v2 10/10 no-boats compliance → picked Image 3, single-batch.

## Pattern
Stop signals (each = hard stop on current approach):
1. Two consecutive iterations with same failure mode on same axis
2. All variants in a single batch fail same critical axis
3. Flux prior clearly overriding prompt intent (e.g. "sunset scene = horizon line drawn" priors in sky-subject variants)
4. Iteration count 4+ on a single prompt variant

Restart options:
- Concept shift: fundamentally different visual approach (Selva Concept A → B)
- Approach reframe: different technical framing of same goal (boats "silhouettes on magenta" → "boats on magenta ocean")
- Pragmatic accept: best-of-bad + compositor compensation (framing-waves y-shift)

## Budget impact
Average marathon cost: 3-5 iterations = $0.72 - $1.20 + 2-4 uur real time. Average restart cost: 1 new prompt + 1-2 iterations = $0.24 - $0.48 + 1 uur. Restart economics are almost always better.
