# Yungas viewport draft (design + content)

**Layout:** Twee viewports. VP1 heeft drie pricing-cards met toggle Upfront / Per maand. VP2 heeft twee losse service-cards voor maatwerk.

**Status:** draft, klaar voor Abdul's batch-review aan het einde van substep 1.

---

## Layout wireframe

### Viewport 1: drie pakketten

```
┌─────────────────────────────────────────────────────┐
│  ─ 03 · Wat we bouwen                               │
│                                                     │
│  Drie manieren om te beginnen.     (Fraunces, XL)   │
│                                                     │
│              [ Upfront ] [ Per maand ]              │
│       Per maand: 12 termijnen, rest direct          │
│                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ Landing  │    │ Compacte │    │ Volledige│      │
│  │          │    │          │    │          │      │
│  │  €400    │    │  €700    │    │  €1.000  │      │
│  │          │    │          │    │          │      │
│  │  body    │    │  body    │    │  body    │      │
│  │  ~~      │    │  ~~      │    │  ~~      │      │
│  │          │    │          │    │          │      │
│  │ footnote │    │ footnote │    │ footnote │      │
│  └──────────┘    └──────────┘    └──────────┘      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Viewport 2: twee maatwerk-cards

```
┌─────────────────────────────────────────────────────┐
│  ─ 03 · Meer dan een website                        │
│                                                     │
│  Of iets groters.              (Fraunces, XL)       │
│                                                     │
│   ┌──────────────────┐    ┌──────────────────┐     │
│   │ AI in je bedrijf │    │ Shoots en socials│     │
│   │                  │    │                  │     │
│   │  body ~~~~~~     │    │  body ~~~~~~     │     │
│   │  ~~~~~~          │    │  ~~~~~~          │     │
│   │                  │    │                  │     │
│   │                  │    │                  │     │
│   │ Neem contact op →│    │ Neem contact op →│     │
│   └──────────────────┘    └──────────────────┘     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Positie-specs

**Viewport 1:**

- **Eyebrow:** top-left, Inter monospace 11-12px, copper (#b87f4a), met korte streep ervoor (letter-spacing 0.08em)
- **Headline:** onder eyebrow, Fraunces display, groot (40-56px op desktop)
- **Toggle:** horizontaal gecentreerd, pill-stijl met twee segmenten. Actief segment krijgt copper fill-opacity 0.35, inactief segment transparent met copper text
- **Regel onder toggle:** Inter small 12-13px, kleur rgba(255,255,255,0.55), gecentreerd
- **3 cards:** gelijke breedte, horizontaal naast elkaar met gelijke gap, gelijke hoogte
  - Card border: 0.5px rgba(184,127,74,0.4), border-radius 10px
  - Baseline achtergrond: transparant
  - Padding: 1.5rem intern
  - Structuur: naam (Inter mono klein, copper bovenaan, uppercase, letter-spacing 0.1em), prijs (Fraunces XXL, groot, met pijl-arrow ernaast die initieel verborgen is), body (Inter 2-3 regels), inclusief-lijst (kleine bullets), footnote (Inter small secondary onderaan, met border-top in subtle copper)

**Viewport 2:**

- **Eyebrow en headline:** zelfde styling als VP1
- **2 service cards:** groter dan VP1 cards, ongeveer 1.5x zo breed, horizontaal naast elkaar
  - Card border: 0.5px rgba(184,127,74,0.4), border-radius 10px
  - Baseline achtergrond: transparant
  - Padding: 1.5rem intern
  - Structuur: naam bovenaan (Inter mono klein, copper), body 3-4 regels (Inter), CTA links-onder met pijl-arrow
  - Geen prijs

---

## Viewport 1: Pakketten (content)

- **Eyebrow:** 03 · Wat we bouwen
- **Headline** (Fraunces, display): Drie manieren om te beginnen.
- **Toggle** (boven de cards): `Upfront` · `Per maand`
- **Regel onder de toggle** (Inter, small, secondary): Per maand loopt 12 termijnen. Vervroegd opzeggen kan, resterende termijnen worden direct gefactureerd.

### Card 1: Landing page

- **Upfront:** €400
- **Per maand:** €50 / 12 mnd
- **Body:** Eén pagina, één boodschap, één actie. Voor een snel online visitekaartje of campagne-pagina.
- **Inclusief:** responsive design, contactformulier
- **Footnote** (Inter, small, secondary): Hosting en onderhoud bespreken we bij contact.

### Card 2: Compacte site

- **Upfront:** €700
- **Per maand:** €70 / 12 mnd
- **Body:** Drie pagina's (home, diensten, contact) met basis-SEO. Genoeg om gevonden te worden op je eigen bedrijfsnaam en kernwoorden.
- **Inclusief:** alles van Landing, plus SEO-basis en Google Analytics
- **Footnote** (Inter, small, secondary): Hosting en onderhoud bespreken we bij contact.

### Card 3: Volledige site

- **Upfront:** €1.000
- **Per maand:** €100 / 12 mnd
- **Body:** Vijf pagina's, volledige SEO en blog-ready structuur. Groeien zonder opnieuw beginnen.
- **Inclusief:** alles van Compacte, plus uitgebreide SEO en blog-module
- **Footnote** (Inter, small, secondary): Hosting en onderhoud bespreken we bij contact.

---

## Viewport 2: Andere diensten (content)

- **Eyebrow:** 03 · Meer dan een website
- **Headline** (Fraunces, display): Of iets groters.

### Card 4: AI in je bedrijf

- **Body:** Workflows automatiseren, klantmails afhandelen, rapportages genereren, dashboards bouwen. Ook als je (nog) geen site bij ons hebt.
- **CTA:** Neem contact op →

### Card 5: Shoots en socials

- **Body:** Professionele fotoshoot plus het runnen van je TikTok en Instagram. De foto's gebruiken we ook op je website, als je die bij ons bouwt.
- **CTA:** Neem contact op →

---

## SEO-structuur

```html
<section id="yungas" aria-labelledby="yungas-heading">
  <h2 id="yungas-heading" class="sr-only">Wat we bouwen</h2>

  <article aria-labelledby="pricing-heading">
    <p class="eyebrow">03 · Wat we bouwen</p>
    <h3 id="pricing-heading">Drie manieren om te beginnen</h3>

    <div role="tablist" aria-label="Prijsweergave">
      <button role="tab" aria-selected="true">Upfront</button>
      <button role="tab" aria-selected="false">Per maand</button>
    </div>

    <div class="pricing-cards">
      <article>
        <h4>Landing page</h4>
        <p class="price">€400 upfront, of €50 per maand gedurende 12 maanden</p>
        <p>Eén pagina, één boodschap, één actie ...</p>
      </article>
      <article>
        <h4>Compacte site</h4>
        <p class="price">€700 upfront, of €70 per maand gedurende 12 maanden</p>
        <p>Drie pagina's met basis-SEO ...</p>
      </article>
      <article>
        <h4>Volledige site</h4>
        <p class="price">€1.000 upfront, of €100 per maand gedurende 12 maanden</p>
        <p>Vijf pagina's, volledige SEO ...</p>
      </article>
    </div>
  </article>

  <article aria-labelledby="more-heading">
    <p class="eyebrow">03 · Meer dan een website</p>
    <h3 id="more-heading">Of iets groters</h3>

    <article>
      <h4>AI in je bedrijf</h4>
      <p>Workflows automatiseren ...</p>
      <a href="/contact">Neem contact op</a>
    </article>
    <article>
      <h4>Shoots en socials</h4>
      <p>Professionele fotoshoot plus socials ...</p>
      <a href="/contact">Neem contact op</a>
    </article>
  </article>
</section>
```

**Hiërarchie-principes:**

- één visible H1 op de homepage, in de Apu hero sectie
- Yungas-sectie krijgt H2 "Wat we bouwen", als sr-only boven beide viewports
- VP1 en VP2 krijgen elk een H3 (de viewport-headline)
- elke card krijgt een H4 met pakket- of dienstnaam, voor Google en voor LLM-crawlers
- prijzen als `<p class="price">` met leesbare zin en concrete getallen, zodat crawlers en AI ze kunnen oppakken

---

## Interactie en animatie

### Pricing-toggle (Upfront / Per maand)

- twee-state toggle boven de drie pricing-cards
- klikken switcht het zichtbare prijsblok in alle drie cards tegelijk
- animatie: crossfade van het prijsblok, ongeveer 250ms, ease-in-out
- keyboard accessibility: `role="tablist"`, pijltjes wisselen de state
- initiële state: Upfront actief

### Prijs-morph

- bij toggle faden oude cijfers uit en nieuwe cijfers in op dezelfde plek
- alternatief iets spannender: cijfers sliden verticaal (odometer-stijl) van oude naar nieuwe waarde
- duur ongeveer 300ms, cubic-bezier ease-out
- NB: verhoog duur niet, anders voelt het traag bij herhaald klikken

### Card hover-effect (Bold variant, geldt voor alle 5 cards in Yungas)

**Baseline (geen hover):**

- border: `0.5px solid rgba(184,127,74,0.4)`
- border-radius: `10px`
- background: `transparent`
- pijl-arrow naast prijs (alleen VP1 cards): `opacity: 0; transform: translateX(-10px)`

**Hover-effecten (alle tegelijk):**

- background: `rgba(184,127,74,0.15)` (copper wash)
- border-color: `#b87f4a` (vol copper)
- transform: `translateY(-3px)` (subtle lift)
- box-shadow: `0 10px 32px -8px rgba(184,127,74,0.4)` (copper glow onder de card)
- prijs: `transform: scale(1.06)` met `transform-origin: left center`
- pijl-arrow verschijnt naast prijs: `opacity: 1; transform: translateX(0)` (fade-in plus slide-in)

**Transitions:**

- transform en box-shadow: 260ms `cubic-bezier(0.4, 0, 0.2, 1)`
- background-color en border-color: 260ms `ease`
- pijl-arrow opacity en transform: 260ms `ease`

**Overige:**

- cursor: pointer
- tilt-on-hover NIET gebruiken hier (tilt is Puna-specifiek, Yungas houdt het bij lift plus glow)
- op mobile: geen hover, wel actieve state bij tap met dezelfde visuele effecten

### Featured card (optioneel, later)

- nu neutraal gelaten. Alle drie cards gelijkwaardig weergegeven
- later eventueel Compacte site markeren als "meest gekozen" met een lichte copper rand, zodra klantdata dat onderbouwt

---

## Mobile

- dezelfde tekstuele content als desktop, voor content-parity onder mobile-first indexing
- layout: cards onder elkaar gestapeld, toggle bovenaan VP1
- VP2 service-cards ook gestapeld onder elkaar
- hover-lift vervangen door actieve state bij tap
- geen horizontal carousel, gewone verticale scroll

---

## Open items

- **prijzen bevestigen:** nu €400 / €700 / €1.000 upfront en €50 / €70 / €100 per maand. Olivier overweegt later ophogen naar "professional" bandbreedte (€750 / €1.500 / €2.500) als eerste opdrachten binnenlopen
- **Landing +50% dissonantie:** upfront €400 versus €50 x 12 = €600 is +50%, terwijl Compacte en Volledige op +20% zitten. Niet fataal, later eventueel €500 upfront maken of maandprijs op €40 zetten
- **algemene voorwaarden:** 12-termijnen-regel en opzeg-clausule (100% resterende termijnen direct opeisbaar) moeten juridisch in AV staan. Regelen via KvK-template, Ligo, of advocaat. Linken vanuit de toggle-footnote naar een /voorwaarden pagina
- **AI-card body:** huidige tekst is generiek. Later aanscherpen met één of twee concrete cases zodra Olivier en Abdul weten welke AI-integraties ze standaard aanbieden
- **Shoots-card body:** idem. Voorbeeld toevoegen zodra eerste klant klaar is
- **featured card:** beslissing uitgesteld tot klantdata ondersteunt welk pakket "meest gekozen" is
- **glow op painterly biome:** Bold-variant gebruikt een copper glow. Bij dark Yungas-biome werkt dat mooi. Als de biome-art later lichter blijkt, mogelijk glow-intensiteit (rgba alpha) verlagen

---

## Changelog

- 2026-04-24: eerste draft met layout-wireframe, chat-sessie Olivier en Claude
- 2026-04-24: hover-variant gekozen: Bold (glow, pijl-reveal, 10px corners)
