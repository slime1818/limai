# Pacífico viewport draft (design + content)

**Layout:** Twee viewports. VP1 is het contactformulier als centerpiece met vier velden. VP2 toont drie genummerde stappen over wat er na het verzenden gebeurt.

**Status:** draft, klaar voor Abdul's batch-review aan het einde van substep 1.

**Opmerking:** Pacífico is de laatste biome, de landing van de scroll. Alt-contact-kanalen (LinkedIn, direct mail, socials) staan NIET in VP2 maar in de algemene footer onder de hele site.

---

## Layout wireframe

### Viewport 1: contactformulier

```
┌───────────────────────────────────────────────────────────┐
│  ─ 06 · Contact                                           │
│                                                           │
│  Neem contact op.     (Fraunces, XL)                      │
│                                                           │
│  NAAM                                                     │
│  ┌─────────────────────────────────────────────┐          │
│  │                                             │          │
│  └─────────────────────────────────────────────┘          │
│  EMAIL                                                    │
│  ┌─────────────────────────────────────────────┐          │
│  │                                             │          │
│  └─────────────────────────────────────────────┘          │
│  TYPE PROJECT                                             │
│  ┌─────────────────────────────────────────────┐          │
│  │                                           ▾ │          │
│  └─────────────────────────────────────────────┘          │
│  BERICHT                                                  │
│  ┌─────────────────────────────────────────────┐          │
│  │                                             │          │
│  │                                             │          │
│  └─────────────────────────────────────────────┘          │
│                                     [ Versturen ]         │
└───────────────────────────────────────────────────────────┘
```

### Viewport 2: wat er daarna gebeurt

```
┌───────────────────────────────────────────────────────────┐
│  ─ 06 · Wat er daarna gebeurt                             │
│                                                           │
│  Wat er daarna gebeurt.     (Fraunces, XL)                │
│                                                           │
│   ○ 1    Binnen 2 werkdagen                               │
│          body ~~~~~~~~~~                                  │
│                                                           │
│   ○ 2    Kennismakingsgesprek                             │
│          body ~~~~~~~~~~                                  │
│                                                           │
│   ○ 3    Offerte en start                                 │
│          body ~~~~~~~~~~                                  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Positie-specs

**Viewport 1:**

- **Eyebrow:** top-left, Inter monospace 11-12px, copper (#b87f4a), letter-spacing 0.08em
- **Headline:** onder eyebrow, Fraunces display, groot (40-56px op desktop), `Neem contact op.`
- **Formulier:** max-width ongeveer 520px op desktop, links uitgelijnd binnen scrim-zone
  - Label boven elk veld: Inter monospace, 10-11px, copper, uppercase, letter-spacing 0.05em
  - Input border: 0.5px rgba(184,127,74,0.4), border-radius 4px, padding 10-12px
  - Baseline achtergrond: transparant
  - Focus state: border vol copper (#b87f4a), subtle glow box-shadow
  - Textarea voor bericht: hoogte ongeveer 100-120px, resize vertical
  - Gap tussen velden: 1rem
- **Verstuur-knop:** rechts-uitgelijnd onder het laatste veld
  - Background: copper #b87f4a
  - Text: donker (#1a1612), Inter 14px, medium weight
  - Padding: 10px 20px
  - Border-radius: 4px
  - Hover: background iets donkerder copper
  - Disabled (tijdens submit): opacity 0.6, cursor not-allowed

**Viewport 2:**

- **Eyebrow en headline:** zelfde styling als VP1
- **3 stappen:** verticaal gestapeld, gelijke vertical-gap
  - Nummer-cirkel: 24px diameter, copper border 1px, copper cijfer gecentreerd (Fraunces medium)
  - Stap-titel rechts naast cirkel: Fraunces medium (18-22px)
  - Stap-body onder titel: Inter body (15-16px), secondary kleur, 1-2 regels
  - Gap tussen stappen: 1.5rem
  - Geen cards-borders rond stappen, het zijn tekstuele elementen met een iconisch nummer

---

## Viewport 1: Contactformulier (content)

- **Eyebrow:** 06 · Contact
- **Headline** (Fraunces, display): Neem contact op.

### Formulier-velden

**Veld 1: Naam**

- **Label:** NAAM
- **Type:** text
- **Placeholder:** Je naam
- **Required:** ja
- **Validation:** min 1, max 100 karakters

**Veld 2: Email**

- **Label:** EMAIL
- **Type:** email
- **Placeholder:** jouw@email.nl
- **Required:** ja
- **Validation:** standaard email-regex

**Veld 3: Type project**

- **Label:** TYPE PROJECT
- **Type:** select (dropdown)
- **Placeholder/default:** Wat zoek je?
- **Required:** ja
- **Opties** (zes stuks, in deze volgorde):
  1. Landing page
  2. Compacte site
  3. Volledige site
  4. AI in je bedrijf
  5. Shoots en socials
  6. Bespreken met ons

**Veld 4: Bericht**

- **Label:** BERICHT
- **Type:** textarea
- **Placeholder:** Vertel wat je nodig hebt. Geen verplicht format, gewoon in je eigen woorden.
- **Required:** ja
- **Validation:** min 10 karakters, max 2000 karakters

### Verstuur-knop

- **Tekst:** Versturen
- **States:**
  - idle: knop zichtbaar met "Versturen"
  - loading: disabled, tekst "Versturen..." of spinner
  - success: formulier verdwijnt, success-bericht verschijnt op dezelfde plek
  - error: error-bericht boven het formulier, knop weer actief

### Success-bericht

- **Tekst:** `Je bericht is verstuurd. Binnen 2 werkdagen hoor je van ons.`
- **Styling:** zelfde padding/max-width als formulier, copper border-left als accent
- **Optioneel:** subtle animatie bij verschijnen (fade-in + translateY)

### Error-bericht

- **Generiek:** `Er ging iets mis. Probeer het opnieuw of mail direct naar [CONTACT_EMAIL].`
- **Veld-specifiek:** onder het betreffende veld, in red (#d64b4b) of een zachtere variant

---

## Viewport 2: Wat er daarna gebeurt (content)

- **Eyebrow:** 06 · Wat er daarna gebeurt
- **Headline** (Fraunces, display): Wat er daarna gebeurt.

### Stap 1

- **Titel:** Binnen 2 werkdagen
- **Body:** Je krijgt reactie van Olivier, meestal sneller.

### Stap 2

- **Titel:** Kennismakingsgesprek
- **Body:** Online of bij koffie in Amsterdam, jij kiest.

### Stap 3

- **Titel:** Offerte en start
- **Body:** Als het klikt, sturen we een concrete offerte. Daarna beginnen we.

### Géén alt-kanalen in VP2

- LinkedIn, direct mailen, socials komen in de globale footer onder alle biomes, niet in Pacífico zelf
- Bewust: VP2 houdt focus op de reassurance, geen concurrerende calls-to-action

---

## Backend en verzending

### Resend integratie

- **SDK:** `resend` npm package
- **API key:** environment variable `RESEND_API_KEY` in `.env.local` en in Vercel-environment
- **Ontvangend email-adres:** environment variable `CONTACT_EMAIL`
  - **Huidige waarde:** `o.dearmenteras1@gmail.com`
  - **Later vervangen:** door LimAI business-email zodra die bestaat (bijv. `hello@limai.nl`)
  - Wisselen kan zonder code-wijziging, alleen `.env` aanpassen

### API route

- **Path:** `/app/api/contact/route.ts`
- **Method:** POST
- **Body:** JSON met `name`, `email`, `projectType`, `message`
- **Server-side validation:** herhalen van client-validation met Zod schema
- **Spam protection:** honeypot-veld in form (hidden field dat bots invullen, mensen niet), rejection als ingevuld
- **Rate limiting (later):** IP-based rate limit, bv. 3 verzendingen per uur per IP. Voor launch niet kritisch, inbouwen bij eerste spam-golf
- **Email-inhoud (wat LimAI ontvangt):**
  - From: `contact@limai-form.vercel.app` of Resend's default, as-appropriate
  - To: `CONTACT_EMAIL` env-value
  - Subject: `Nieuw bericht van [Naam], type: [projectType]`
  - Body: plain tekst of simpele HTML met alle formuliergegevens

### Error-handling

- network error: "Verbinding mislukt, probeer opnieuw"
- Resend API error: log server-side, toon generieke error aan gebruiker
- validation error: markeer velden, toon inline

---

## SEO-structuur

```html
<section id="pacifico" aria-labelledby="pacifico-heading">
  <h2 id="pacifico-heading" class="sr-only">Contact</h2>

  <article aria-labelledby="contact-form-heading">
    <p class="eyebrow">06 · Contact</p>
    <h3 id="contact-form-heading">Neem contact op</h3>

    <form>
      <label for="name">Naam</label>
      <input id="name" name="name" type="text" required />

      <label for="email">Email</label>
      <input id="email" name="email" type="email" required />

      <label for="project-type">Type project</label>
      <select id="project-type" name="projectType" required>
        <option value="">Wat zoek je?</option>
        <option value="landing">Landing page</option>
        <option value="compact">Compacte site</option>
        <option value="full">Volledige site</option>
        <option value="ai">AI in je bedrijf</option>
        <option value="shoots">Shoots en socials</option>
        <option value="other">Bespreken met ons</option>
      </select>

      <label for="message">Bericht</label>
      <textarea id="message" name="message" required></textarea>

      <button type="submit">Versturen</button>
    </form>
  </article>

  <article aria-labelledby="next-steps-heading">
    <p class="eyebrow">06 · Wat er daarna gebeurt</p>
    <h3 id="next-steps-heading">Wat er daarna gebeurt</h3>

    <ol class="next-steps">
      <li>
        <h4>Binnen 2 werkdagen</h4>
        <p>Je krijgt reactie van Olivier, meestal sneller.</p>
      </li>
      <li>
        <h4>Kennismakingsgesprek</h4>
        <p>Online of bij koffie in Amsterdam, jij kiest.</p>
      </li>
      <li>
        <h4>Offerte en start</h4>
        <p>Als het klikt, sturen we een concrete offerte. Daarna beginnen we.</p>
      </li>
    </ol>
  </article>
</section>
```

**Hiërarchie-principes:**

- één visible H1 op de homepage, in de Apu hero sectie
- Pacífico-sectie krijgt H2 "Contact", als sr-only
- VP1 en VP2 krijgen elk een H3
- stappen in VP2 als `<ol>` met H4's, consistent met Paracas-proces-pattern
- formulier-labels correct verbonden via `for`/`id`, zodat screenreaders velden kunnen associëren
- honeypot-veld met `aria-hidden="true"` en `tabindex="-1"` zodat mensen het niet zien of tabben

---

## Interactie en animatie

### VP1 formulier

**Focus-states op inputs:**

- border-color: rgba(184,127,74,0.4) → #b87f4a
- box-shadow: 0 0 0 3px rgba(184,127,74,0.15) (subtle focus-ring)
- transition: 180ms ease

**Verstuur-knop hover:**

- background: iets donkerder copper (#a67040)
- transition 180ms
- op click: subtle scale-down (0.98) en weer terug

**Loading state:**

- Button content wisselt naar "Versturen..." plus subtle spinner of animated-dots
- Button disabled, alle inputs disabled

**Success-state animatie:**

- Formulier fade-out (opacity 1 → 0, translateY 0 → -8px) in 300ms
- Success-bericht fade-in op dezelfde plek (opacity 0 → 1, translateY 8px → 0) in 400ms met 150ms delay

### VP2 stappen stagger

- Bij scroll-in van VP2: 3 stappen faden in met stagger, 120ms per stap
- Elke stap: opacity 0 naar 1, translateY 10px naar 0
- duur 500ms per stap, ease-out
- Geen hover-effects op stappen: het is informatief, niet interactief

### Géén tilt of Bold hover in Pacífico

- Pacífico is functioneel en direct. Tilt of glow op een formulier voelt misplaatst
- Bold hover past ook niet op VP2 stappen, want die zijn informatief
- De biome onderscheidt zich via de duidelijke focus-states op inputs en de smooth success-transitie

---

## Mobile

- **parkeren voor aparte mobile-pass sessie**, na alle 6 biome desktop-drafts klaar
- Mobile-strategie: apart dual-tree fork, 100vh per biome, eigen content-keuze
- Voor Pacífico mobile waarschijnlijk:
  - Formulier vol-breed met zelfde vier velden
  - VP2 stappen gestapeld onder formulier in één viewport, niet twee
  - Keyboard-friendly: scroll-to-input on focus
  - Verstuur-knop groter en volle breedte voor thumb-friendly

---

## Open items

- **CONTACT_EMAIL swap:** nu `o.dearmenteras1@gmail.com`, later LimAI business-email. Vervanging via `.env` zonder code-wijziging
- **Resend setup:** account aanmaken, domain verifiëren als `limai.nl` live is (voor goede deliverability en geen spam-markering), API key genereren, toevoegen aan `.env.local` en Vercel-environment
- **Spam protection:** honeypot is er, rate-limiting komt bij eerste spam-golf. Cloudflare Turnstile als alternatief als honeypot niet volstaat
- **Success-state copy:** nu vrij zakelijk. Zou ook warmer kunnen zijn ("Bedankt voor je bericht! Je hoort snel van ons."). Subjectief, later fine-tunen
- **email-subject format:** nu `Nieuw bericht van [Naam], type: [projectType]`. Als volume groot wordt: uitbreiden naar `[LimAI] [type] - [Naam]` of vergelijkbaar voor eenvoudiger sorteren in inbox
- **mobile-pass:** volgt na alle 6 desktop-drafts klaar

---

## Changelog

- 2026-04-24: eerste draft met 4-veld formulier, 3-stappen-reassurance, Resend-backend met environment-gestuurd email-adres
