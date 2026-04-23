# Palette match at paint-time

## Lesson
Palette-continuity tussen lagen in een multi-layer composite moet je aan Flux vragen tijdens painting, met expliciete RGB+hex anchors gesampled uit de vorige layer. Post-hoc compositor tricks (feather, alpha-clamp, boundary-mask) kunnen alpha-recession doen maar kunnen materiaal/palette mismatch niet verbergen — ze eten content, ze blenden niet.

## Validation
- Selva v1-v6: 4-5 uur compositor-marathon met feather/clamp/mask stack, Gate 8 PASS 6.13:1 maar visueel unconvincing (plateau understory leest als stickers, river-bank↔plateau palette-break). Fresh restart needed.
- Selva v7: palette-continuity zone lower-middle 20% expliciet in sky-subject prompt met warm Palette C anchors matching future plateau. First-try clean integration.
- Paracas: plateau prompt had sampled sky-subject horizon palette als RGB+hex anchor block. Clean seam without compositor tricks.
- Pacifico plateau v2: gesampled sky-subject mist-horizon met 4 anchors (#6d7577 cool base, #ecc8a1 brightest glint, #d1a78b midtone, #978b80 shoulder). Image 3 produced clean top-edge seam.
- Pacifico framing-waves: gesampled plateau foreground 4 anchors (#43494b top-edge, #474e4f body, #fcdbaf glint, #2d2f30 trough). Image 4 matched plateau exit-palette exactly.

## Pattern
Voordat je prompt voor layer N+1 schrijft, laat Claude Code de boundary-zone van layer N samplen voor 4 anchors:

1. Dominant body tone — median RGB van main band
2. Brightest accent — brightest decile (glint highlight zone)
3. Darkest accent — darkest decile (shadow/trough zone)
4. Asymmetric light direction — warmth-gradient horizontal quintiles to detect left/center/right weighting

Deze anchors worden een `STRICT palette match` block bovenaan de nieuwe layer prompt, geformatteerd als:

```
STRICT palette match with [previous layer] — top edge match
RGB(X,Y,Z) hex #xxxxxx for seam continuity, body dominated by
RGB(X,Y,Z) hex #xxxxxx, brightest highlights anchored to
RGB(X,Y,Z) hex #xxxxxx, darkest shadows to RGB(X,Y,Z) hex
#xxxxxx, warmth concentrated [direction] preserving previous
layer's directional weighting
```

## Cost of skipping
Selva compositor-marathon = 4-5 uur real time + budget voor 3 plateau iterations zonder visual cohesion. Palette-match at paint-time voor Paracas/Pacifico = eerste-poging clean. Break-even is ongeveer 1 sampled palette-block equals 3-4 uur compositor work.
