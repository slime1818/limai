# Substep 11 mobile-responsive Puna pilot verify

**Datum**: 2026-04-24
**Commit**: post c26f041 (substep 10)
**Playwright config**: headless chromium, device_scale_factor 1, custom viewports per row

## Test matrix

3 viewports × 3 scroll-positions = 9 positions. Elke positie schiet een screenshot plus probeert DOM-state op 5 criteria: ImageStack fixed-top alignment, dots visibility per md:flex breakpoint, image-decode progressie, h1 visibility op viewport 1, CTA visibility op viewport 2.

| viewport | position | scrollY | ImageStack top | dots visible | expected dots | imgs rendered | h1 visible | CTA visible | status |
|---|---|---|---|---|---|---|---|---|---|
| 390x844 | apu hero | 0 | 0 | false | false | 4 | LimAI | 0 | OK |
| 390x844 | puna hero | 1688 | 0 | false | false | 4 | Wie we zijn | 0 | OK |
| 390x844 | puna v2 | 2532 | 0 | false | false | 4 | - | 1 (Lees ons verhaal) | OK |
| 414x896 | apu hero | 0 | 0 | false | false | 4 | LimAI | 0 | OK |
| 414x896 | puna hero | 1792 | 0 | false | false | 4 | Wie we zijn | 0 | OK |
| 414x896 | puna v2 | 2688 | 0 | false | false | 4 | - | 1 (Lees ons verhaal) | OK |
| 768x1024 | apu hero | 0 | 0 | **true** | true | 4 | LimAI | 0 | OK |
| 768x1024 | puna hero | 2048 | 0 | **true** | true | 4 | Wie we zijn | 0 | OK |
| 768x1024 | puna v2 | 3072 | 0 | **true** | true | 4 | - | 1 (Lees ons verhaal) | OK |

**9/9 positions passed automated checks. 0 console errors cross-viewport.**

## Bevestigd werkend

- `h-[200dvh]` section-height reageert correct op viewport-hoogte. sectionHeight 1688 (390), 1792 (414), 2048 (768).
- ImageStack `fixed inset-0 w-full h-dvh` blijft op viewport-top alignment over alle scroll-posities (top=0 consistent).
- Dots `hidden md:flex` cutoff op exact 768 breakpoint. Op 390 en 414 display:none, op 768 display:flex.
- Vertical F6 scrim (`md:hidden` plus `180deg gradient`) rendert op narrow viewports, dark-top naar less-dark-bottom zichtbaar in Apu 390 en Puna 390 screenshots.
- Horizontal F6 scrim op 768 (md-breakpoint active) rendert als left-gradient.
- Content-layer readability op narrow: `font-display text-6xl md:text-8xl` schaalt naar text-6xl op sub-md. "LimAI" plus "Wie we zijn" Fraunces rendern leesbaar op 390.
- Viewport 2 teaser paragraph (Inter text-base op sub-md) plus CTA "Lees ons verhaal →" readable op 390 met max-w-xl krimp.
- Image lazy-load useInView margin "50%" werkt op kleine viewports, Puna image decoded wanneer user binnen 50% van section nadert.

## iOS-specific concerns, niet Playwright-testbaar

Playwright chromium emuleert geen iOS Safari-specifieke gedragingen. De volgende zijn flags voor manuele verify op een echte iOS device:

1. **iOS toolbar dynamiek plus dvh units.** Op iOS Safari beweegt de address-bar tijdens scroll, wat viewport-height doet veranderen. Onze `h-[200dvh]` en `h-dvh` moeten dit dynamisch volgen. In theorie werkt dvh correct op iOS 15.4+. Bevestigen door op een iPhone zwaar te scrollen en te checken of sections blijven uitlijnen met section-boundaries.

2. **Fixed-position stabiliteit tijdens iOS momentum-scroll.** ImageStack layers zijn `fixed inset-0`. iOS heeft historische issues waar fixed elements "shift" tijdens scroll-momentum. Test door snel flingen plus observeren of layers glued aan viewport blijven.

3. **Sticky-positioning op mobile Safari.** We gebruiken geen sticky meer in 9a+ (alle images zijn fixed in ImageStack), dus geen risico hier. Genoteerd voor de record.

4. **Backdrop-filter plus will-change performance.** Geen backdrop-filter in codebase, `will-change: transform` zit alleen op de pan-wrapper motion.div. Op low-end mobile kan dit memory-druk geven. Flag voor performance-check op oudere iPhone als Olivier die bij heeft.

## Pre-existing known limitation

Per Fase 1 open items (docs/status/2026-04-24-fase-1-start.md): "Mobile-responsive painting-strategy voor portrait-modus, framing-rock valt nu buiten mobile center-crop op aspect-ratio 0.46."

Bevestigd in deze verify: op Apu 390x844 is de framing-rock linkerkant gedeeltelijk gecropt. Dit geldt cross-biome, niet Puna-specifiek. Behouden als Fase 2.5 of Fase 3 polish item (breder painting-strategy denkwerk nodig dan single substep-fix).

## Recommendation

Substep 11 klaar zonder code-changes. Puna pilot mechanica is mobile-responsive op 390, 414, 768 viewports binnen scope wat Playwright-testbaar is.

Voor iOS-device confidence: Olivier op een iPhone de live site op limai-one.vercel.app scrollen en de 3 iOS-concerns bovenaan manueel verifieren. Als daar issues optreden, flag voor substep 11 follow-up.

Pad vooruit: Phase C substep 12 (Yungas scale, pattern-replicatie).
