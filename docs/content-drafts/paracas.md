# Paracas viewport draft (design + content)

**Layout:** Twee viewports. VP1 toont een 5-stappen-proces als horizontale tijdlijn met cards en scroll-gekoppelde connector-animatie. VP2 toont vier post-launch service-cards met Lucide-icoontjes in een 2x2 grid, met tilt- en Bold-hover-interacties.

**Status:** draft, klaar voor Abdul's batch-review aan het einde van substep 1.

**Opmerking:** Paracas is bewust licht ingevuld qua content om ademruimte te geven voor toekomstige uitbreiding. Proces en post-launch-services zijn beiden SEO-relevant voor zoekopdrachten als "webdesign proces", "website onderhoud Amsterdam", "website lancering mkb". De interactie-laag compenseert de lichte content met visueel leven.

---

## Layout wireframe

### Viewport 1: vijf-stappen-proces (tijdlijn)

```
┌───────────────────────────────────────────────────────────┐
│  ─ 05 · Hoe we werken                                     │
│                                                           │
│  Van eerste gesprek tot live.     (Fraunces, XL)          │
│                                                           │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐             │
│  │ 01  │  │ 02  │  │ 03  │  │ 04  │  │ 05  │             │
│  │     │  │     │  │     │  │     │  │     │             │
│  │Gesp.│  │Plan │  │Bouw │  │Rev. │  │Lanc.│             │
│  │     │  │     │  │     │  │     │  │     │             │
│  │body │  │body │  │body │  │body │  │body │             │
│  └──●──┘──┘──●──└──┘──●──└──┘──●──└──┘──●──┘             │
│     copper connector scrubt mee met scroll                 │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Viewport 2: post-launch services (2x2 grid)

```
┌───────────────────────────────────────────────────────────┐
│  ─ 05 · Na de lancering                                   │
│                                                           │
│  Wat er daarna gebeurt.     (Fraunces, XL)                │
│                                                           │
│  Een website is pas klaar als hij blijft werken.          │
│                                                           │
│   ┌───────────────────┐      ┌───────────────────┐       │
│   │ [icon]            │      │ [icon]            │       │
│   │ Onderhoud         │      │ Wijzigingen       │       │
│   │ body ~~~~~~       │      │ body ~~~~~~       │       │
│   └───────────────────┘      └───────────────────┘       │
│                                                           │
│   ┌───────────────────┐      ┌───────────────────┐       │
│   │ [icon]            │      │ [icon]            │       │
│   │ Aanspreekpunt     │      │ Meegroeien        │       │
│   │ body ~~~~~~       │      │ body ~~~~~~       │       │
│   └───────────────────┘      └───────────────────┘       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Positie-specs

**Viewport 1:**

- **Eyebrow:** top-left, Inter monospace 11-12px, copper (#b87f4a), letter-spacing 0.08em
- **Headline:** onder eyebrow, Fraunces display, groot (40-56px op desktop)
- **Vijf cards:** horizontaal naast elkaar, gelijke breedte, ongeveer 160-180px per card
  - Card border: 0.5px rgba(184,127,74,0.25), border-radius 10px
  - Padding: 1.25rem intern
  - Interne structuur: nummer bovenaan (Fraunces, groot, copper), titel (Fraunces, medium), body 2-3 regels (Inter, small)
  - Niet interactief: geen hover-effect, geen cursor-pointer
- **Tijdlijn-connector:** copper-kleurige horizontale lijn onder de cards, met dots op het centerpoint van elke card
  - Line-asset: een SVG-path met 5 punten, totale breedte gelijk aan afstand van card-1-center tot card-5-center
  - Dots: 8px diameter cirkels, gecentreerd op elke card
  - Wordt als aparte SVG-laag gerenderd achter of onder de cards

**Viewport 2:**

- **Eyebrow en headline:** zelfde styling als VP1
- **Body-regel** onder headline: Inter body, 16-18px, secondary kleur, één zin
- **2x2 grid:** gelijke breedte, 2 kolommen, 2 rijen, gap ongeveer 1rem
  - Card border: 0.5px rgba(184,127,74,0.25), border-radius 10px
  - Baseline achtergrond: transparant
  - Padding: 1.5rem intern
  - Interne structuur: Lucide-icon bovenaan (24px, copper), titel (Fraunces, medium), body 2-3 regels (Inter, small)
  - Interactief: combinatie tilt-on-hover plus Bold hover-feedback (zie animatie-sectie)

---

## Viewport 1: Het proces (content)

- **Eyebrow:** 05 · Hoe we werken
- **Headline** (Fraunces, display): Van eerste gesprek tot live.

### Stap 01: Het gesprek

- **Titel:** Het gesprek
- **Body:** We starten met een gesprek om te begrijpen wat je wilt bereiken, niet wat je denkt dat je nodig hebt. Vaak is de eerste vraag anders dan de uiteindelijke oplossing.

### Stap 02: Het plan

- **Titel:** Het plan
- **Body:** We zetten op papier wat er gebouwd wordt en wat het kost. Geen uren-achteraf-verrassingen, geen scope-creep zonder gesprek.

### Stap 03: De bouw

- **Titel:** De bouw
- **Body:** We bouwen in sprints en laten je onderweg zien hoe het ervoor staat, zodat niks pas op het einde verrast.

### Stap 04: De review

- **Titel:** De review
- **Body:** Voor oplevering krijg je een staging-link. Je test op je eigen telefoon, loopt teksten na, laat ons weten wat je wilt aanpassen. Daarna pas gaan we live.

### Stap 05: De lancering

- **Titel:** De lancering
- **Body:** We zetten live, testen op echte bezoekers, en blijven de eerste maand actief meekijken. Lanceren is een begin, geen einde.

---

## Viewport 2: Na de lancering (content)

- **Eyebrow:** 05 · Na de lancering
- **Headline** (Fraunces, display): Wat er daarna gebeurt.
- **Body** (Inter, body size): Een website is pas klaar als hij blijft werken.

### Card 1: Onderhoud

- **Icon:** `Wrench` (Lucide)
- **Titel:** Onderhoud
- **Body:** Maandelijks of ad-hoc, jij kiest. Updates, beveiliging, en wat er verder aan de achterkant nodig is.

### Card 2: Wijzigingen

- **Icon:** `Edit3` (Lucide)
- **Titel:** Wijzigingen
- **Body:** Kleine aanpassingen in teksten, afbeeldingen of pagina's zonder telkens een dev-rekening te krijgen.

### Card 3: Aanspreekpunt

- **Icon:** `MessageCircle` (Lucide)
- **Titel:** Eén aanspreekpunt
- **Body:** Abdul is je vaste contact voor vragen, support en bestellingen. Geen ticket-systeem, geen wachtrij.

### Card 4: Meegroeien

- **Icon:** `TrendingUp` (Lucide)
- **Titel:** Meegroeien
- **Body:** Extra pagina's, AI-integraties, of een hele rebuild als je bedrijf groeit. De site groeit met je mee.

---

## SEO-structuur

```html
<section id="paracas" aria-labelledby="paracas-heading">
  <h2 id="paracas-heading" class="sr-only">Hoe we werken</h2>

  <article aria-labelledby="process-heading">
    <p class="eyebrow">05 · Hoe we werken</p>
    <h3 id="process-heading">Van eerste gesprek tot live</h3>

    <ol class="process-timeline">
      <li>
        <h4>01. Het gesprek</h4>
        <p>We starten met een gesprek om te begrijpen ...</p>
      </li>
      <li>
        <h4>02. Het plan</h4>
        <p>We zetten op papier wat er gebouwd wordt ...</p>
      </li>
      <li>
        <h4>03. De bouw</h4>
        <p>We bouwen in sprints en laten je onderweg ...</p>
      </li>
      <li>
        <h4>04. De review</h4>
        <p>Voor oplevering krijg je een staging-link ...</p>
      </li>
      <li>
        <h4>05. De lancering</h4>
        <p>We zetten live, testen op echte bezoekers ...</p>
      </li>
    </ol>
  </article>

  <article aria-labelledby="post-launch-heading">
    <p class="eyebrow">05 · Na de lancering</p>
    <h3 id="post-launch-heading">Wat er daarna gebeurt</h3>
    <p>Een website is pas klaar als hij blijft werken.</p>

    <ul class="post-launch-services">
      <li>
        <h4>Onderhoud</h4>
        <p>Maandelijks of ad-hoc ...</p>
      </li>
      <li>
        <h4>Wijzigingen</h4>
        <p>Kleine aanpassingen zonder ...</p>
      </li>
      <li>
        <h4>Eén aanspreekpunt</h4>
        <p>Abdul is je vaste contact ...</p>
      </li>
      <li>
        <h4>Meegroeien</h4>
        <p>Extra pagina's, AI-integraties ...</p>
      </li>
    </ul>
  </article>
</section>
```

**Hiërarchie-principes:**

- één visible H1 op de homepage, in de Apu hero sectie
- Paracas-sectie krijgt H2 "Hoe we werken", als sr-only boven beide viewports
- VP1 en VP2 krijgen elk een H3
- Stappen als `<ol>` (geordende lijst) met H4's per stap, perfect voor Google en LLMs
- Post-launch-services als `<ul>` met H4's per service
- Lucide-icoontjes krijgen `aria-hidden="true"` want ze zijn puur decoratief naast de titel

---

## Interactie en animatie

### VP1 connector scroll-sync (hoofd-interactie van VP1)

**Concept:** de copper tijdlijn-lijn tekent zichzelf progressief terwijl de bezoeker door Paracas VP1 scrolt. Niet één animatie bij scroll-in, maar continu gekoppeld aan scroll-progress. Dots zijn standaard aanwezig in halftransparant copper en worden vol copper zodra de lijn ze bereikt.

**Techniek:**

- Connector is één SVG-element: een `<path>` (of `<line>`) die alle 5 card-centers verbindt
- Pad-eigenschappen:
  - `stroke: #b87f4a`
  - `stroke-width: 1`
  - `stroke-linecap: round`
  - `stroke-dasharray: <totaleLengte>` (gelijk aan de pad-lengte, bereken met `getTotalLength()` op mount)
  - `stroke-dashoffset: <totaleLengte>` (startwaarde, lijn onzichtbaar)
- Dots als 5 aparte `<circle>` elementen op de card-centers
  - Standaard: `fill: rgba(184,127,74,0.35)` (halftransparant)
  - Actief (lijn is aangekomen): `fill: #b87f4a` (vol copper)

**Scroll-koppeling:**

- `useScroll` hook met target op Paracas VP1 ref, `offset: ["start end", "end start"]`
- `useTransform` van scroll-progress (0-1) naar `stroke-dashoffset`: `offset = totaleLengte * (1 - progress)`
- Dots: elk heeft een `threshold` (progress-waarde waarbij lijn ze bereikt)
  - Dot 1 threshold: 0.05
  - Dot 2 threshold: 0.275
  - Dot 3 threshold: 0.5
  - Dot 4 threshold: 0.725
  - Dot 5 threshold: 0.95
- Elke dot-opacity/fill wordt geswitcht als `progress >= threshold`

**Subtiele pulse op dot-activering:**

- als lijn een dot bereikt, kort schaal-pulse (scale 1 naar 1.25 naar 1) in 220ms
- optioneel, als het niet te druk voelt. Anders weglaten

**Reduce-motion fallback:**

- bij `prefers-reduced-motion: reduce`: geen scroll-sync
- lijn is volledig getekend, alle dots volledig zichtbaar, geen animatie

### VP1 cards entrance (lichte ondersteuning)

- Bij scroll-in van VP1: cards faden in met stagger, 80ms per card
- Elke card: opacity 0 naar 1, translateY 8px naar 0
- duur 400ms per card, ease-out
- Bewust korter en minder uitgesproken dan de connector-animatie, anders concurreren ze

### VP2 cards hover (tilt plus Bold)

**Baseline (geen hover):**

- border: `0.5px solid rgba(184,127,74,0.25)`
- border-radius: `10px`
- background: `transparent`
- transform: `rotateX(0) rotateY(0) translateY(0)`
- box-shadow: geen

**Tilt (muis-tracking, zoals Puna):**

- op `mousemove` binnen de card-wrap: bereken muispositie relatief tot card center
- `rotateX = (dy / (height/2)) * -6` (max 6 graden negatief omhoog)
- `rotateY = (dx / (width/2)) * 6` (max 6 graden positief naar rechts)
- `transform-style: preserve-3d` op de card
- `perspective: 1200px` op de wrapping container
- transition op transform: `0.3s cubic-bezier(0.23, 1, 0.32, 1)` (soepele ease-out)
- op `mouseleave`: reset naar `rotateX(0) rotateY(0)`
- lichte implementatie: vanilla JS met requestAnimationFrame, of `react-parallax-tilt` (zelfde library als in Puna)

**Bold hover-feedback (tegelijk met tilt):**

- background: `rgba(184,127,74,0.15)` (copper wash)
- border-color: `#b87f4a` (vol copper)
- translateY: `-3px` (bovenop de tilt-rotation, gewoon optellen in transform)
- box-shadow: `0 10px 32px -8px rgba(184,127,74,0.4)` (copper glow onder de card)
- icon-color: intensiteit van 90% naar 100% opacity, of van `rgba(184,127,74,0.85)` naar `#b87f4a`
- **geen pijl-arrow** (geen prijs, dus geen plek voor die reveal)
- **geen price-scale** (geen prijs)

**Transitions:**

- background, border-color, box-shadow, icon: 260ms ease
- tilt-transform: 300ms cubic-bezier(0.23, 1, 0.32, 1)

**Overige:**

- cursor: pointer
- op touch devices: tilt uit via `@media (hover: hover) and (pointer: fine)`, actieve state bij tap met dezelfde Bold-effecten

---

## Mobile

- **parkeren voor aparte mobile-pass sessie**, na alle 6 biome desktop-drafts klaar
- Mobile-strategie: apart dual-tree fork, 100vh per biome, eigen content-keuze
- Voor Paracas mobile waarschijnlijk: gestapelde cards (niet horizontaal), connector-lijn verticaal ipv horizontaal
- Connector scroll-sync werkt op mobile ook maar moet getest worden of iOS Safari het lekker rendert. Anders fallback naar statische connector
- VP2 2x2 grid wordt waarschijnlijk 1x4 gestapeld
- Tilt uit op mobile (geen pointer-fine)

---

## Open items

- **Paracas bewust licht ingevuld:** ruimte om later uit te breiden zonder hele biome te herschrijven. Mogelijke toekomstige uitbreidingen: klant-quotes per stap, tijdsindicatie per stap (bv. "Stap 01 duurt meestal 1 week"), prijs-indicatie post-launch-services
- **iconen finetune:** huidige Lucide-keuzes (Wrench, Edit3, MessageCircle, TrendingUp) zijn voorlopig. Later eventueel aanpassen als een icon niet goed "klopt" visueel of semantisch
- **connector-path shape:** nu rechte horizontale lijn. Als dat te strak lijkt, kan een subtle bezier-curve tussen dots een zachtere "route" geven. Visuele beslissing voor later
- **dot pulse bij activering:** optioneel. Inbouwen en kijken of het werkt of juist te druk is
- **mobile-pass:** volgt na alle 6 desktop-drafts klaar

---

## Changelog

- 2026-04-24: eerste draft met 5-stappen-tijdlijn en 2x2 post-launch-services
- 2026-04-24: connector-animatie upgegrade naar scroll-sync progressive drawing, VP2 cards krijgen tilt plus Bold hover combinatie
