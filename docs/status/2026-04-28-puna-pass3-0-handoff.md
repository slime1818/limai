# Substep 2.2 Puna desktop pass 3.0 handoff

Datum: 2026-04-28
Pass: 3.0 (cinematic animaties als dev-flag toggles)
Status: deliverables klaar voor visuele review, keuzes nog niet gelockt

## Status Puna desktop

Pass 2.7 ronde productie-staat is gelocked: VP1 Olivier en VP2 Abdul beide
fullbleed-cutout-clean met Allura signaturen en pills. Pass 3.0 voegt drie
animatie-dimensies toe als dev-flag toggles bovenop die productie-staat. De
defaults renderen wat in pass 2.7 is gelocked, plus subtiele intro
animatie A en sig clippath reveal als productie-default.

## Productie-defaults (zonder query-params)

- nameStyle = allura
- skills = pills
- frame = fullbleed-cutout-clean
- intro = A (snel, subtiel)
- hover = none (statische foto)
- sig = clippath (langzame onthulling van naam)
- olivier = b (productie foto)

Dit is wat een eerste-bezoeker zonder query-params ziet.

## Pass 3.0 deliverables

7 WebM recordings voor visuele review op pad
docs/recordings/fase-2/

- puna-pass3-intro-A.webm (353 KB) intro variant A snel subtiel
- puna-pass3-intro-B.webm (339 KB) intro variant B uitgewerkt per element type
- puna-pass3-hover-none.webm (414 KB) statische foto
- puna-pass3-hover-parallax.webm (523 KB) cursor-driven parallax x/y
- puna-pass3-hover-scale.webm (402 KB) hover scale 1.02
- puna-pass3-sig-clippath.webm (264 KB) handtekening reveal van links naar rechts
- puna-pass3-sig-fade.webm (246 KB) handtekening fade-in zonder reveal

17 stills voor frame-level review op pad docs/screenshots/fase-2/
puna-pass3-* (lokaal, niet in git want screenshots dir staat in .gitignore).
Regenereerbaar via python scripts/record_animations.py tegen lopende
dev-server.

## Open keuzes voor pass 3.1

Drie dimensies om te locken:

1. intro: A (snel uniform, ~0.24s per element met stagger 0.08s) versus B
   (uitgewerkt per element type, langere ease-out cubic-bezier)
2. hover: none versus parallax versus scale 1.02
3. sig: clippath (links-naar-rechts onthulling 1.4s) versus fade (0.8s)

Aanbevolen procedure pass 3.1:
- Beoordeel WebM recordings naast elkaar
- Lock per dimensie de winnende variant
- Pas defaults in PunaSection.tsx aan zodat productie-default = gelockte keuze
- Strip dev-flag query-param logic indien gewenst voor productie-cleanup
- Schrijf handoff voor Yungas substep 2.3

## Dev-flag query-params (alle werkend)

Op http://localhost:3000/?param=value#puna

- ?nameStyle=allura|fraunces|fraunces-italic (pass 2.3 toggle)
- ?skills=pills|chips|underlined (pass 2.4 toggle)
- ?frame=fullbleed|fullbleed-cutout-clean|fullbleed-cutout-rim|atmospheric|
  duotone|asymcrop|kinetic|typographic (pass 2.5 en 2.6 toggle)
- ?intro=A|B (pass 3.0 nieuw)
- ?hover=none|parallax|scale (pass 3.0 nieuw)
- ?sig=clippath|fade (pass 3.0 nieuw)
- ?olivier=a|b (pass 2.0 toggle natuurlijke foto versus formele variant)

Combineer met & voor cross-product testen, bijvoorbeeld
?intro=B&hover=parallax&sig=fade

## TODO Abdul cutout

Huidige asset public/team/abdul-cutout-removebg-preview.png heeft
gezicht-artefacten van remove.bg masker. Inline TODO comment staat in
PunaSection.tsx bij ABDUL_CUTOUT_SRC. Vervang zodra een betere foto wordt
aangeleverd, idealiter via Photoroom flow zoals bij Olivier. Tijdelijk
gecompenseerd via cutoutScale 1.7 om Abdul groter te renderen en de
artefacten minder dominant te laten zijn, maar dat is een workaround geen
fix.

## Wat pass 3.1 moet doen

1. Visuele review 7 WebM recordings, kies winnende variant per dimensie
2. Update productie-defaults in PunaSection.tsx naar gelockte keuzes
3. Optioneel: dev-flag query-param logic strippen voor pass 3.0 dimensies
4. Lint plus typecheck check
5. Schrijf substep 2.3 Yungas start-doc op pad
   docs/status/YYYY-MM-DD-substep-2-3-yungas-start.md met spec analoog aan
   substep 2.2 Puna start (founder-grid, biome-context, content-eisen)
6. Commit "Puna substep 2.2 pass 3.1: animatie-keuzes gelockt, dev-flags
   verwijderd"

## Sessie-context

Werkmap C:\Users\odear\projects\limai
Stack Next.js 16.2.4 TS Tailwind v4 motion 12.38.0 Lenis
Schrijfstijl Nederlands geen em-dashes
Tools Claude Code --dangerously-skip-permissions --model claude-opus-4-7

## Locked design-keuzes pass 2.x cumulatief

- Pass 2.0: foto B Olivier natuurlijk (geen formele studio)
- Pass 2.1: copper-glow-soft achter coords backdrop-blur
- Pass 2.2.2: Allura SVG signaturen via fontTools generator
- Pass 2.3: nameStyle = allura
- Pass 2.4: skills = pills, content-extensie body2 plus skills array
- Pass 2.5: frame = fullbleed (fullbleed-cutout-clean follow-up)
- Pass 2.6: frame = fullbleed-cutout-clean met cutout-scale parity per
  founder
- Pass 2.7: VP2 Abdul fullbleed-cutout-clean met scale 1.7
- Pass 3.0: defaults intro A hover none sig clippath, dev-flag toggles
  voor 7 varianten

## Iteratie-leerpunten pass 3.0

- Two-wrapper motion.div nodig wanneer hover en intro animaties op zelfde
  element conflicteren (outer voor hover x/y of scale, inner voor intro
  opacity y)
- IntersectionObserver per founder met margin -25% triggert animatie
  precies wanneer founder card 25% in viewport is, ook bij scrollen tussen
  founders
- useReducedMotion hook strikt respecteren: animaties uitschakelen via
  variants override naar visible state, niet via CSS transitions
- Cubic-bezier 0.22 1 0.36 1 voor B variant geeft cinematic deceleration
  zonder bouncy overshoot
- Playwright record_video_dir heeft geen post-record close hook nodig: het
  context-close commit de WebM automatisch voordat browser sluit
