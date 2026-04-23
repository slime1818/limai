# Flux has no backend concepts

## Lesson
Flux is niet getraind op chroma-key briefs, alpha channels, isolation layers, parallax pipelines, compositing stages, mask generation, of enige andere engineering-backend terminologie. Alle technical intent moet verpakt worden in visuele vocabulary die Flux wél kent — natural scene descriptions, lighting terminology, compositional conventions.

## Validation
- Boats v1: "silhouettes isolated against flat magenta background for chroma-key extraction, this is a parallax isolation layer for a composite pipeline" → Flux painted boats against pink "wall", tiny ground-shadows, rigid horizon alignment. Backend vocabulary gaf geen signal aan Flux over wat het resultaat moest zijn.
- Boats v2: added "organic wave-bobbing variation" but kept "silhouette layer" framing → same failure mode, boats still detached from water context.
- Boats v3: "painterly digital illustration of Peruvian fishing boats at sea, ocean water painted as flat saturated magenta color" → 10/10 natural placement, hulls in water, wave interaction, scale-by-distance. Flux understood "boats on water" native; magenta was just water-color.

Related: sky-subject v2 45-50% magenta strip worked because painted as "flat bottom painting zone" within a real sky composition, not as "alpha extraction region."

## Pattern
If prompt contains any of these backend concepts:
- "chroma key", "isolation", "alpha extraction"
- "layer", "composite", "pipeline", "mask"
- "parallax layer", "compositor pass"
- "silhouette on [color]" (treating color as non-medium)

Reframe to visual concept Flux knows:
- "[objects] in stylized [color]-tinted [natural medium]"
- "painting of [scene] with [color] [element] instead of natural [element-color]"
- Extraction happens downstream via tolerance, never via Flux-intent

## Cost of skipping
Boats v1 + v2 = $0.48 wasted on fundamentally wrong framing. Boats v3 first-try = clean approach. Reframe cost = zero (just rewriting prompt), savings = $0.24+ per avoided bad iteration.
