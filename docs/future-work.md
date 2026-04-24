# Future work, pre-launch polish

Low-prioriteit items buiten de huidige fase-scope. Adresseer wanneer content-pass, launch prep (Fase 5), of budget-ruimte ontstaat. Geen blockers.

## Apu widescreen composite-variant

Huidige Apu composite is 4:3 (1024x768). Op wider-dan-4:3 viewports wordt full-width + bottom-crop gedaan (per commit cbdc650). Dit werkt visueel maar verliest framing-rock in de crop op ultrawide monitors. Een wider-aspect variant (16:9 of 21:9) zou banden boven en onder mogelijk maken met framing-rock zichtbaar. Re-render kost Flux-budget plus 3-5 uur iteratie, visuele ROI beperkt tot ultrawide gebruikers.

## Paracas composite re-render overwegen

Intake Fase 2 substep 1 bevestigde dat Paracas de zwakste van de 6 composites is qua framing-anchor. Het framing-dune-element rechts onderaan is te klein om de frame te dragen, compositie leest als wide-pan landschap ipv immersive-descent. Scrim plus tekst werken functioneel. Re-render overwegen voor stronger framing-anchor, **prioriteit laag**. Pragmatic_acceptance learning gold bij intake, deze flag is voor toekomstige polish-pass als de content-quality op andere biomes hoger ligt.

## Selva teaser: verify binnen 4-6 weken of /cases cases heeft, anders herschrijven zonder binnenkort-claim

De viewport-2 teaser voor Selva (draft in `docs/content-drafts/viewport-2-teasers.md`) sluit met "De eerste landen binnenkort". Die claim is tijdsgebonden: als /cases 4-6 weken post-launch nog leeg staat, wordt "binnenkort" ongeloofwaardig en voelt het onoprecht. Verificatie op dat moment: staat er minstens één case op /cases, dan teaser laten zoals hij is. Is /cases nog leeg, teaser herschrijven naar variant zonder tijdclaim, bijvoorbeeld door de focus te verleggen naar curatie-filosofie in plaats van timing. Low effort wijziging, paar regels tekst, kan meelopen in een post-launch copy-iteratie.

## Fase 2.5 content expansion (viewport 2 content-rich layouts plus SEO pass)

Huidige viewport 2 per biome bevat alleen de teaser-paragraaf uit `docs/content-drafts/viewport-2-teasers.md` plus een CTA. Dat vult niet de volledige `h-[200dvh]` ruimte, vandaar de `mt-32` top-padding hack in substep 6 om de tekst niet aan viewport-top te plakken. Fase 2.5 vult viewport 2 met substantiele content-rijke layouts die de ruimte natuurlijk verdienen.

Per-biome concept:

- **Apu.** Blijft leeg viewport 2, intro biome zonder content. Scroll-chevron placeholder wordt dan een visuele hint voor volgende biome.
- **Puna, `Wie we zijn`.** Founder-photos (Olivier plus Abdul) naast elkaar of gestapeld, 1-zin bio per persoon, visuele markers voor Amsterdam plus Peru (kaart-elementen of subtiele iconografie), CTA onder.
- **Yungas, `Wat we doen`.** 3 kern-diensten als gestructureerde lijst (Websites, Brand Identity, Strategie), 1 zin per dienst plus eventueel startprijs per pakket, CTA naar `/diensten`.
- **Selva, `Wat we maakten`.** 2 tot 3 case-cards, thumbnail plus client-naam plus 1-regel-omschrijving. Placeholder cards als er nog geen echte cases zijn. CTA naar `/cases`.
- **Paracas, `Hoe we werken`.** Proces-stappen als horizontale of verticale timeline (Kennismaking, Strategie, Ontwerp, Bouw, Lancering), typische doorlooptijd per stap of totaal. CTA naar `/proces`.
- **Pacifico, `Laten we praten`.** Email-adres prominent als grote tekst-link, social-icons (LinkedIn, Instagram), CTA naar `/contact` formulier.

SEO-werk in dezelfde fase, content-volume hoort bij Google Dutch-agency search ranking:

- Meta descriptions per biome-sectie via route segment metadata of een centrale biome-meta config.
- JSON-LD `Organization` structured data op root layout voor rich-results.
- `og:image` per biome voor social-sharing previews (use composite thumbnails).
- Dutch-localized `hreflang` tags voor nl-NL targeting.
- Content-volume-boost voor Google pickup, huidige site heeft weinig indexable copy buiten de taglines.

Dependency: Abdul plus Olivier content-sessie nodig voor de echte founder-bios, service-copy, case-omschrijvingen. Niet puur dev-werk. Minimaal halve dag gezamenlijke content-sprint voor alle 5 biomes.

Timing: tussen Fase 2 (mechanica af) en Fase 3 (particles). Idealiter pre-launch zodat de site bij launch al content-volume heeft voor SEO.

## Paracas scroll-triggered sandstorm intensification

Cinematic escalatie op de baseline Paracas sand-particles die in Fase 3 worden geimplementeerd. DESIGN.md noemt voor Paracas "stochastic intensifications" zonder specifieke trigger-conditie. Deze entry concretiseert wat stochastic hier betekent: niet random-timer, maar scroll-progress getriggerd voor cinematic payoff.

Mechanica:

- Baseline particles, Fase 3 default. Rustig zand-drift in de lucht, laag-density, warme bronze-tinten matchend Paracas palette.
- Trigger punt op scroll-progress `> 0.4` binnen de Paracas section (ongeveer wanneer viewport 2 in beeld komt).
- Intensificatie bij threshold overshoot: particle density vermenigvuldigd x3 tot x5, wind-vectors krijgen acceleratie-boost, kleur-saturatie bump voor dramatiek, eventueel subtle motion-blur hint op snelle deeltjes.
- Payoff-moment na storm-piek: nieuwe tekst-layer fade-in bovenop de storm, bijvoorbeeld "In de storm vinden we helderheid" of equivalent Andes-storytelling-regel in lijn met de ensemble-toon.
- Return to baseline bij scroll-progress terug onder threshold. Wind kalmeert graceful via easing, deeltjes drijven weer rustig.

Implementatie: R3F particle system uit Fase 3 (particle scope voor alle 6 biomes) plus een scroll-triggered intensity GSAP timeline gekoppeld aan `useScroll` progress of aan een dedicated motion-value. Lenis smooth-scroll zorgt ervoor dat de intensification-curve smooth volgt, niet per wheel-tick snapt.

Timing: Fase 3 particles implementation plus polish. Niet Fase 4 (daar zit T4 authored drama voor Selva naar Paracas transition, ander mechaniek).

## Layered parallax per biome

Sky-subject, plateau, en framing-rock (of biome-equivalent zoals framing-canopy voor Selva, framing-waves plus boats voor Pacifico) als aparte image-layers stacken in BiomeSection, met individueel verschillende translateY ranges voor cinematic depth-illusion. Near-layer pant meer dan far-layer, klassieke parallax.

Assets zijn al beschikbaar, gesplitst in `public/Backdrops/[biome]/processed/`:
- `sky-subject.webp`, `plateau.webp`, `framing-rock.webp` voor Apu, Puna, Yungas, Paracas.
- `framing-canopy.webp` ipv framing-rock voor Selva (TOP-framing).
- `framing-waves.webp` plus aparte `boats.webp` voor Pacifico (boten zijn eigen parallax-layer).

Complexity-impact:

- Asset-loading verdubbelt van 1 composite naar 3 plus 4 files per biome, image-optimizer caching moet dat aankunnen.
- BiomeSection markup wordt complexer, 3 motion.divs ipv 1, elk met eigen useTransform output met verschillende translateY range (bijvoorbeeld sky -4%, plateau -8%, framing-rock -12% voor progressieve diepte).
- Substep 9 alpha-crossfade moet per layer werken, niet op 1 composite. Crossfade-timing wordt layer-gesynchroniseerd anders valt de scene uit elkaar tijdens transitie.
- Mobile-performance: 3x image-decode per biome op sub-md kan LCP schaden, potentieel conditional naar 1 composite op mobile-breakpoint.

Timing: Fase 3+ polish, niet Fase 2. Demo-bar goal voor Fase 2 is simpler model (1 composite per biome) die al acceptabel leest. Layered parallax is een "next level" polish voor wanneer Fase 3 R3F-infra er staat en performance-headroom duidelijk is.
