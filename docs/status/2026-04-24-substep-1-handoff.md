# Substep 1 handoff: content-drafts compleet

**Datum:** 2026-04-24
**Status:** alle 6 biome-drafts in repo, klaar voor Abdul touchpoint 1
**Asset-status:** alle verplichte assets verzameld, alle beslissingen gemaakt, klaar voor substep 2 implementatie
**Volgende stap:** Abdul reviewt batch, dan substep 2 (per-biome implementatie)

---

## Wat is af

Alle 6 biome-drafts gecommit in `docs/content-drafts/`:

- `apu.md` (biome 1, hero)
- `puna.md` (biome 2, about)
- `yungas.md` (biome 3, services en pricing)
- `selva.md` (biome 4, portfolio)
- `paracas.md` (biome 5, proces)
- `pacifico.md` (biome 6, contact)

Elke draft bevat: layout-wireframe (ASCII), positie-specs, viewport-content (volledige copy), SEO-structuur (semantic HTML voorbeeld), interactie-en-animatie specs, mobile-parking-note, open items, changelog.

### Assets en infrastructuur

- Domain `limaidesign.com` actief op Namecheap
- Resend account verified voor `limaidesign.com` (EU-west-1 region), DKIM en SPF en DMARC DNS records staan
- Google Workspace actief, twee gebruikers: `olivier@limaidesign.com` en `abdul@limaidesign.com`
- Team foto's: `public/team/olivier.webp` en `public/team/abdul.webp`
- RESEND_API_KEY veilig opgeslagen, klaar om in .env.local te plaatsen in substep 2

---

## Locked beslissingen per biome

### Apu (biome 1, hero)

- Variant C hero met metrics-regel
- VP1 left-aligned: eyebrow `01 · Studio uit Amsterdam`, LimAI-titel (Fraunces italic, XXL), tagline `Websites met karakter.`, divider, metrics `6 BIOMES · 2 MAKERS · AMSTERDAM`, scroll-indicator gecentreerd, coordinaten rechtsonder
- VP2 zes-biome route: horizontale copper-lijn met 6 dots (Apu actief vol copper, rest gedimd), italic caption `Zes taferelen.` plus sub `Scroll om ze te ontmoeten.`
- Drager van enige visible H1 op de homepage
- Coordinaten `52°22'N · 12°03'S` (Amsterdam · Lima) als subtiele Peru-hint via getallen, niet via woorden
- Cinematic intro op page-load (eyebrow, letter-per-letter LimAI, tagline, divider, metrics, scroll-indicator, coords met staggered timeline 200ms tot 1500ms)

### Puna (biome 2, about)

- Optie B: duo-viewports, elke founder eigen viewport
- VP1 Olivier (Founder en lead architect), VP2 Abdul (Founder en production lead)
- Per portret: foto, italic naam, copper rol-label, 3 regels body, meta-strip onderaan
- Olivier meta: `18 · Amsterdam · bouwt sinds zijn tienerjaren`
- Abdul meta: `19 · Amsterdam · [TBD]`
- Tilt-on-hover (max 6-8 graden), signature-reveal animatie (clip-path), coordinaten Amsterdam plus Lima
- VP2 CTA `Lees ons verhaal →` naar `/over-ons`

### Yungas (biome 3, services en pricing)

- VP1 drie pricing-cards met Upfront/Per maand toggle:
  - Landing: €400 / €50 (12 termijnen)
  - Compacte site: €700 / €70
  - Volledige site: €1.000 / €100
- VP2 twee maatwerk-cards: `AI in je bedrijf` en `Shoots en socials`
- Bold hover op cards: copper bg-wash 0.15, vol border, copper glow, lift -3px, prijs scale 1.06, pijl-arrow reveal naast prijs, 260ms transitions
- Bij vroegtijdige opzegging: 100% resterende termijnen direct opeisbaar (in AV vastleggen)
- Hosting en onderhoud: "bespreken we bij contact", geen prijzen op site

### Selva (biome 4, portfolio)

- Coming-soon fase, geen echte cases nog
- VP1 scrub-preview van LimAI-site zelf als "eerste case": React `<SitePreview>` component met code-gebouwde mini-site (4 verticaal gestapelde biome-blokken in browser-chrome frame), useScroll koppelt scroll-progress aan translateY van inner stack. Geen assets nodig, puur code
- VP2 drie lege atmospheric cards genummerd 01/02/03 (rgba copper 0.5)
- Copy: `Selva groeit. Onze eerste cases landen hier zodra ze live zijn.`
- Cases-links: alleen externe live links, geen detail-pagina's
- Webarctic mag NIET als case worden gebruikt
- Hover-sync VP2 naar VP1 inbouwen wanneer cases binnen zijn

### Paracas (biome 5, proces)

- Bewust licht ingevuld voor ademruimte
- VP1 vijf-stappen tijdlijn horizontaal: Het gesprek, Het plan, De bouw, De review, De lancering, met copper connector-lijn plus dots
- VP2 2x2 grid van vier service-cards met Lucide-icons: Wrench (Onderhoud), Edit3 (Wijzigingen), MessageCircle (Eén aanspreekpunt), TrendingUp (Meegroeien)
- VP1 connector scroll-sync: stroke-dashoffset gekoppeld aan useScroll progress, dots default rgba 0.35 worden vol copper bij thresholds (0.05/0.275/0.5/0.725/0.95)
- VP2 cards hover: tilt (puna-stijl) plus Bold (yungas-stijl glow + bg-wash + lift), geen pijl, geen price-scale

### Pacífico (biome 6, contact)

- VP1 vier-veld formulier (Naam, Email, Type project dropdown met 6 opties, Bericht textarea), verstuur-knop rechtsonder
- Type project opties: Landing page, Compacte site, Volledige site, AI in je bedrijf, Shoots en socials, Bespreken met ons
- VP2 drie genummerde stappen `Wat er daarna gebeurt`: Binnen 2 werkdagen, Kennismakingsgesprek, Offerte en start
- Backend: Resend SDK, API route `/app/api/contact/route.ts`, env var `CONTACT_EMAIL` (huidige waarde `o.dearmenteras1@gmail.com`, later business-email zonder code-wijziging)
- Spam-protection: honeypot field, rate-limiting later
- Geen alt-kanalen in VP2, die komen in globale footer onder de hele site

---

## Asset-checklist (blocking voor substep 2)

### Verplicht (zonder dit kan implementatie niet starten)

1. **Foto Olivier:** [DONE] foto's op `public/team/olivier.webp` en `public/team/abdul.webp`
2. **Foto Abdul:** [DONE] foto's op `public/team/olivier.webp` en `public/team/abdul.webp`
3. **Resend account:** [DONE] Resend account aangemaakt
4. **`RESEND_API_KEY`:** [DONE] RESEND_API_KEY gegenereerd, API key privaat opgeslagen buiten de repo
5. **`CONTACT_EMAIL`:** [DONE] CONTACT_EMAIL value bepaald: olivier@limaidesign.com (vervangt gmail)

### Beslissingen om te bevestigen vóór substep 2

6. **Abdul's derde feit voor Puna meta-strip:** [DONE] designer
7. **`/over-ons` link in Puna VP2:** [DONE] /over-ons krijgt placeholder pagina (optie B), regel uitgebreid: elke toekomstige interne link naar een niet-bestaande subpagina krijgt een placeholder pagina met minimale content

### Optioneel (niet blokkerend)

8. **Domain:** [DONE] limaidesign.com actief, DNS geconfigureerd voor Resend (EU region) en Google Workspace
9. **LimAI logo:** waarschijnlijk al in `public/`. Niet kritisch voor homepage, want LimAI is al de hero-titel

---

## Open items per biome (geparkeerd voor later)

- **Apu:** scroll-indicator copy A/B-test, caption `Zes taferelen` vs `Zes biomes` beslissen voor launch, JSON-LD Organization schema inbouwen, OG-image genereren met Playwright
- **Puna:** foto-treatment beslissen (met/zonder duotone), illustrator-richting nog overwegen, biome-illustratie achtergrond verfijning
- **Yungas:** prijzen later mogelijk omhoog richting professional bandbreedte, AV opstellen met 12-termijnen-clausule, hosting/onderhoud-tarieven intern bepalen
- **Selva:** hover-sync VP2 naar VP1 inbouwen wanneer cases binnen zijn, eerste echte cases binnenhalen, scrub-preview component performance-test
- **Paracas:** iconen-keuze finetune, connector-path-shape (recht vs bezier-curve), dot-pulse bij activering inbouwen en evalueren
- **Pacífico:** success-state copy warmer maken, email-subject format uitbreiden bij groei, rate-limiting bij eerste spam-golf, Cloudflare Turnstile als alternatief

---

## Volgende stappen

1. **Abdul touchpoint 1:** Abdul leest alle 6 drafts in `docs/content-drafts/` en geeft feedback
2. **Iteraties:** per-biome aanpassen op feedback, drafts updaten in repo
3. **Olivier verzamelt assets:** foto's, Resend setup, beslissingen Abdul-feit en /over-ons
4. **Substep 2 start:** per-biome implementatie, volgorde:
   - Apu (eerst, want al deels production-locked en geen externe dependencies)
   - Puna (heeft foto's nodig)
   - Yungas (geen externe deps)
   - Selva (puur code, geen assets)
   - Paracas (geen externe deps)
   - Pacífico (heeft Resend nodig)
5. **Mobile-pass** na alle 6 desktop-implementaties klaar (aparte sessie)

---

## Mobile

- **Bewust geparkeerd** voor aparte sessie na desktop-implementatie van alle 6 biomes
- **Dual-tree pattern locked** uit Fase 1: aparte fork voor mobile, 100vh per biome, eigen content-keuze per biome, geen sticky/fixed/motion
- Per-biome mobile-overwegingen al genoteerd in elke draft onder `## Mobile`

---

## Referenties

- `docs/content-drafts/apu.md` t/m `docs/content-drafts/pacifico.md` (6 drafts)
- `docs/DESIGN.md` (locked design decisions uit Fase 0 en Fase 1)
- `docs/learnings/` (pattern library uit asset-gen fase)
- `docs/status/2026-04-20-selva-handoff.md` (vorige session handoff, asset-gen fase)

---

## Sessie-context (voor restart in nieuwe chat)

- **Project:** LimAI, painterly Firewatch-geïnspireerde Next.js scroll-site, 6 Peruviaanse biomes als secties
- **Tech:** Next.js 14+ App Router, TypeScript, Tailwind CSS, GSAP, React Three Fiber, Lenis smooth scroll, Resend voor contact-form
- **Stack:** fal.ai flux-2-pro voor asset-gen (klaar), Claude Code voor implementatie (volgende fase)
- **Team:** Olivier (technisch, 18, Amsterdam, Peruviaanse achtergrond), Abdul (design en outreach, 19, Amsterdam)
- **Schrijfstijl:** geen em-dashes, gebruik komma's of haakjes
- **Communicatietaal:** Nederlands

---

## Changelog

- 2026-04-24: handoff doc aangemaakt na completion van substep 1 (alle 6 content-drafts in repo)
