"use client";

import {
  useRef,
  useState,
  type CSSProperties,
  type RefObject,
} from "react";
import {
  motion,
  useInView,
  useMotionValue,
  useMotionValueEvent,
  useReducedMotion,
  useScroll,
  useSpring,
  useTransform,
} from "motion/react";
import type { Biome } from "../data/biomes";
import { useLenis } from "./SmoothScrollProvider";

// Locked spec timeline (apu.md regel 174-186) plus revisies fase B akkoord. Alle
// elementen leunen op deze ease curve voor consistente "soepel ease-out" feel.
const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

// Mono-feel via tabular-nums. Olivier locked: geen extra mono-font, Inter met
// font-feature-settings tnum plus letter-spacing-utility per element.
const MONO_STYLE: CSSProperties = {
  fontFeatureSettings: "'tnum'",
};

// Text-shadow voor copper en warm-white tekst die buiten F6 scrim left-zone valt
// of op licht backdrop-gedeelte landt. Dubbele drop: scherpe korte shadow voor
// letterrand-definitie plus zachte verre shadow voor cinematic depth.
const TEXT_SHADOW_STYLE: CSSProperties = {
  textShadow: "0 1px 2px rgba(26, 22, 18, 0.85), 0 2px 12px rgba(26, 22, 18, 0.5)",
};

const MONO_SHADOW_STYLE: CSSProperties = {
  ...MONO_STYLE,
  ...TEXT_SHADOW_STYLE,
};

// VP1 propositie CTAs naar biome-sections. Anchor href matcht id={biome.id} op
// BiomeSection. Lenis-instance uit useLenis() pickt de jump op via lenis.scrollTo
// in handleCtaClick. Stagger-delays verschuiven 0.15s per CTA, gestart 1.6s na
// page-load om na de body-paragraph (delay 1.2s, dur 0.6s) in te zetten.
const CTAS: ReadonlyArray<{ href: string; label: string; delay: number }> = [
  { href: "#selva", label: "Bekijk ons werk", delay: 0.55 },
  { href: "#yungas", label: "Bekijk prijzen", delay: 0.6 },
  { href: "#pacifico", label: "Plan een gesprek", delay: 0.65 },
];

// Apu plus-punten in VP2: zes brand-pijlers met label en korte beschrijving.
// Hover/focus per punt highlight de actieve, dimt de anderen subtiel. Number
// gebruikt door DOT_DESIGN variant B, icon (via renderDotIcon) door variant C.
const PLUS_POINTS: ReadonlyArray<{
  id: string;
  label: string;
  description: string;
  number: string;
}> = [
  {
    id: "seo",
    label: "SEO",
    description: "Vindbaar in Google vanaf dag één",
    number: "01",
  },
  {
    id: "snel",
    label: "SNEL",
    description: "Live binnen enkele dagen",
    number: "02",
  },
  {
    id: "mobiel",
    label: "MOBIEL",
    description: "Werkt perfect op elk scherm",
    number: "03",
  },
  {
    id: "conversie",
    label: "CONVERSIE",
    description: "Bezoekers worden klanten",
    number: "04",
  },
  {
    id: "ai",
    label: "AI",
    description: "Geïntegreerd waar het waarde toevoegt",
    number: "05",
  },
  {
    id: "amsterdam",
    label: "AMSTERDAM",
    description: "Lokale studio, persoonlijk contact",
    number: "06",
  },
];

type Vp2VariantProps = {
  shouldReduceMotion: boolean | null;
  vp2InView: boolean;
  hoveredPointIndex: number | null;
  setHoveredPointIndex: (i: number | null) => void;
};

export function ApuSection({
  sectionRef,
}: {
  biome: Biome;
  sectionRef: RefObject<HTMLElement | null>;
}) {
  const shouldReduceMotion = useReducedMotion();
  const vp2Ref = useRef<HTMLElement | null>(null);
  // Trigger entrance wanneer 25% van VP2 in viewport komt. once true zorgt dat
  // animatie niet opnieuw speelt bij heen-en-weer scrollen door de hero.
  const vp2InView = useInView(vp2Ref, { margin: "0% 0% -25% 0%", once: true });

  // Pulse-loop op scroll-indicator stopt zodra bezoeker begint te scrollen.
  // Threshold 40px om iOS Safari rubber-banding en accidental micro-scrolls te
  // negeren. One-way flag, blijft true ook bij scroll-back.
  const { scrollY } = useScroll();
  const [hasScrolled, setHasScrolled] = useState(false);
  useMotionValueEvent(scrollY, "change", (v) => {
    if (v > 40 && !hasScrolled) setHasScrolled(true);
  });

  // Hover-swap state voor CTAs: index van de hovered/focused CTA wordt primary,
  // anderen worden secondary. Bij geen hover: index 0 (Bekijk ons werk) primary
  // als default. Pointer plus keyboard-focus beide getriggerd voor a11y-pariteit.
  const [activeCtaIndex, setActiveCtaIndex] = useState<number | null>(null);
  const primaryIndex = activeCtaIndex !== null ? activeCtaIndex : 0;

  // VP2 plus-punten hover-state. Hovered/focused punt highlight, anderen dimmen
  // subtiel. null = default state, alle punten op rust-niveau.
  const [hoveredPointIndex, setHoveredPointIndex] = useState<number | null>(
    null,
  );

  // Lenis-instance uit context. null op coarse pointer (touch device, geen Lenis
  // init) of op eerste render-tick voor setLenis is gepushed. Fallback naar
  // scrollIntoView als instance niet beschikbaar is.
  const lenis = useLenis();
  const handleCtaClick = (
    e: React.MouseEvent<HTMLAnchorElement>,
    target: string,
  ) => {
    e.preventDefault();
    const element = document.querySelector(target);
    if (!(element instanceof HTMLElement)) return;
    if (shouldReduceMotion) {
      element.scrollIntoView({ behavior: "auto" });
      return;
    }
    if (lenis) {
      lenis.scrollTo(element, {
        duration: 1.5,
        easing: (t: number) => 1 - Math.pow(1 - t, 3),
      });
    } else {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <section
      ref={sectionRef}
      id="apu"
      aria-labelledby="apu-heading"
      className="relative w-full h-[200vh]"
    >
      {/* Warmte-overlays altijd actief. Drie lagen tussen ImageStack (z-0) en
          content (z-10) tillen Apu uit het koele schaduw-spectrum naar warmer
          painterly: warm scrim shift, soft-light blend, warm radial gloed. */}
      <div
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none z-[3]"
        style={{
          background:
            "linear-gradient(90deg, rgba(74, 45, 30, 0.15) 0%, rgba(74, 45, 30, 0.08) 30%, transparent 55%)",
        }}
      />
      <div
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none z-[4]"
        style={{
          background: "rgba(255, 220, 180, 0.08)",
          mixBlendMode: "soft-light",
        }}
      />
      <div
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none z-[5]"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 70% 35%, rgba(212, 154, 106, 0.18) 0%, rgba(212, 154, 106, 0.08) 40%, transparent 75%)",
        }}
      />

      <div className="absolute inset-0 z-10">
        <h2 id="apu-heading" className="sr-only">
          LimAI, studio uit Amsterdam
        </h2>

        {/* VIEWPORT 1: hero */}
        <article
          aria-labelledby="hero-heading"
          className="relative h-screen grid grid-rows-[auto_1fr_auto] px-8 md:px-16 lg:px-24 py-8 md:py-12"
        >
          {/* Eyebrow met copper-streep prefix, top-left */}
          <motion.p
            className="copper-glow self-start flex items-center gap-3 text-[var(--color-andes-copper-bright)] text-[13px] tracking-[0.08em]"
            style={MONO_STYLE}
            initial={
              shouldReduceMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: -8 }
            }
            animate={{ opacity: 1, x: 0 }}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 0.05, duration: 0.4, ease: EASE }
            }
          >
            <span
              aria-hidden="true"
              className="block w-4 h-px bg-[var(--color-andes-copper-bright)]"
            />
            Studio uit Amsterdam
          </motion.p>

          {/* Midblock: commerciële propositie. H1 als hero-statement, klein
              LIMAI brand-mark, body-paragraph plus drie CTAs. self-end met
              pb-6/8 ankert CTAs strak op de onderkant van VP1 (24-32px tot
              scroll-indicator), bovenste 70% blijft open mountain-zicht met
              alleen eyebrow top-left. max-w-5xl voor H1-breedte (body blijft
              max-w-2xl voor leesbaarheid van langere paragrafen). */}
          <div className="self-end max-w-5xl pb-6 md:pb-8">
            <motion.h1
              id="hero-heading"
              className="font-display italic text-warm-white -ml-2 md:-ml-4 text-[64px] md:text-[88px] lg:text-[104px] leading-[1.05] tracking-tight max-w-5xl"
              style={TEXT_SHADOW_STYLE}
              initial={
                shouldReduceMotion
                  ? { opacity: 1, y: 0 }
                  : { opacity: 0, y: 16 }
              }
              animate={{ opacity: 1, y: 0 }}
              transition={
                shouldReduceMotion
                  ? { duration: 0 }
                  : { delay: 0.15, duration: 0.4, ease: EASE }
              }
            >
              Website laten maken
            </motion.h1>

            <motion.p
              aria-hidden="true"
              className="copper-glow mt-6 mb-6 text-[13px] tracking-[0.15em] uppercase text-[var(--color-andes-copper-bright)]"
              style={MONO_SHADOW_STYLE}
              initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={
                shouldReduceMotion
                  ? { duration: 0 }
                  : { delay: 0.3, duration: 0.4, ease: EASE }
              }
            >
              LIMAI
            </motion.p>

            <motion.p
              className="copper-glow font-sans text-warm-white text-[17px] md:text-[19px] leading-[1.6] max-w-2xl"
              initial={
                shouldReduceMotion
                  ? { opacity: 1, y: 0 }
                  : { opacity: 0, y: 8 }
              }
              animate={{ opacity: 1, y: 0 }}
              transition={
                shouldReduceMotion
                  ? { duration: 0 }
                  : { delay: 0.4, duration: 0.4, ease: EASE }
              }
            >
              Wil je een professionele website die snel online staat en direct
              resultaat oplevert? Bij LimAI in Amsterdam bouwen we sites voor
              ZZP&apos;ers, MKB en groeibedrijven. Vanaf €400 voor een one-pager
              tot maatwerk vanaf €1000. Altijd snel, SEO-geoptimaliseerd, en
              gebouwd met de nieuwste tech.
            </motion.p>

            {/* Drie CTAs onder de body. Smooth-scroll naar biome-section via
                Lenis, hover-swap primary plus secondary mechaniek met identieke
                dimensies om layout-shift te voorkomen. */}
            <div className="flex flex-row gap-6 md:gap-10 mt-12">
              {CTAS.map((cta, i) => {
                const isPrimary = i === primaryIndex;
                const baseClass =
                  "group inline-flex items-center gap-2 px-7 py-3 rounded-sm text-[15px] md:text-[16px] tracking-[0.1em] uppercase font-medium transition-colors duration-300";
                const stateClass = isPrimary
                  ? "bg-[var(--color-andes-copper-bright)] text-noche-andina"
                  : "bg-transparent text-[var(--color-andes-copper-bright)]";
                return (
                  <motion.a
                    key={cta.href}
                    href={cta.href}
                    onClick={(e) => handleCtaClick(e, cta.href)}
                    onMouseEnter={() => setActiveCtaIndex(i)}
                    onMouseLeave={() => setActiveCtaIndex(null)}
                    onFocus={() => setActiveCtaIndex(i)}
                    onBlur={() => setActiveCtaIndex(null)}
                    className={
                      isPrimary
                        ? `${baseClass} ${stateClass}`
                        : `copper-glow-soft ${baseClass} ${stateClass}`
                    }
                    style={isPrimary ? MONO_STYLE : MONO_SHADOW_STYLE}
                    initial={
                      shouldReduceMotion
                        ? { opacity: 1, y: 0 }
                        : { opacity: 0, y: 8 }
                    }
                    animate={{ opacity: 1, y: 0 }}
                    transition={
                      shouldReduceMotion
                        ? { duration: 0 }
                        : { delay: cta.delay, duration: 0.4, ease: EASE }
                    }
                  >
                    {cta.label}
                    <span
                      aria-hidden="true"
                      className="inline-block transition-transform duration-300 motion-safe:group-hover:translate-x-1"
                    >
                      →
                    </span>
                  </motion.a>
                );
              })}
            </div>
          </div>

          {/* Scroll-indicator gecentreerd onderaan VP1, met intro fade plus
              pulse-loop tot eerste scroll. */}
          <motion.div
            aria-hidden="true"
            className="copper-glow self-end justify-self-center text-[var(--color-andes-copper-bright)] text-[15px] tracking-[0.12em] text-center"
            style={MONO_SHADOW_STYLE}
            initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 0.5, duration: 0.4, ease: EASE }
            }
          >
            <motion.span
              className="inline-flex items-center gap-2"
              animate={
                shouldReduceMotion || hasScrolled
                  ? { y: 0 }
                  : { y: [0, 6, 0] }
              }
              transition={
                shouldReduceMotion || hasScrolled
                  ? { duration: 0.3, ease: EASE }
                  : { repeat: Infinity, duration: 1.6, ease: "easeInOut" }
              }
            >
              <span>↓</span>
              <span>scroll</span>
            </motion.span>
          </motion.div>

          {/* Coordinates rechtsonder, los van grid-flow via absolute positioning. */}
          <motion.p
            aria-hidden="true"
            className="copper-glow-soft absolute bottom-8 right-8 md:bottom-12 md:right-16 text-[var(--color-andes-copper-bright)] text-[12px] tracking-[0.05em]"
            style={MONO_SHADOW_STYLE}
            initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 0.5, duration: 0.4, ease: EASE }
            }
          >
            52°22&apos;N · 12°03&apos;S
          </motion.p>

          {/* VP1 rechterzijde anker: status-pill rechtsboven plus coordinates
              rechtsonder. Twee verticale zones gescheiden, geen overlap. */}
          <RightSideVariantA shouldReduceMotion={shouldReduceMotion} />
        </article>

        {/* VIEWPORT 2: zes plus-punten als brand-pijlers. Centraal eyebrow plus
            hoofdtekst Fraunces italic, daaronder horizontaal gerangschikte
            plus-punten met hover/focus highlighting (active warm-white, anderen
            gedimd). */}
        <article
          ref={vp2Ref}
          aria-labelledby="vp2-heading"
          className="relative h-screen flex flex-col items-center justify-center px-8 md:px-16 lg:px-24"
        >
          <h3 id="vp2-heading" className="sr-only">
            Wat wij anders doen
          </h3>

          <motion.p
            className="copper-glow-soft text-[14px] md:text-[15px] tracking-[0.15em] uppercase font-semibold text-[var(--color-andes-copper-bright)] text-center"
            style={MONO_SHADOW_STYLE}
            initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
            animate={vp2InView ? { opacity: 1 } : {}}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 0.1, duration: 0.4, ease: EASE }
            }
          >
            Wat wij anders doen
          </motion.p>

          <motion.p
            className="font-display italic text-warm-white text-[28px] md:text-[36px] lg:text-[44px] leading-[1.2] text-center max-w-3xl mx-auto mt-4"
            style={TEXT_SHADOW_STYLE}
            initial={
              shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }
            }
            animate={vp2InView ? { opacity: 1, y: 0 } : {}}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 0.2, duration: 0.4, ease: EASE }
            }
          >
            Snelle, SEO geoptimaliseerde sites die binnen enkele dagen live
            staan en direct resultaat opleveren.
          </motion.p>

          {/* Zes plus-punten als 3-koloms grid van cards met 3D hover-tilt. */}
          <Vp2Cards
            shouldReduceMotion={shouldReduceMotion}
            vp2InView={vp2InView}
            hoveredPointIndex={hoveredPointIndex}
            setHoveredPointIndex={setHoveredPointIndex}
          />
        </article>
      </div>
    </section>
  );
}

type VariantProps = { shouldReduceMotion: boolean | null };

// Variant A: status-pill rechtsboven, "LIMA · AMSTERDAM". Tegenhanger eyebrow,
// zonder horizontale streep prefix.
function RightSideVariantA({ shouldReduceMotion }: VariantProps) {
  return (
    <motion.p
      aria-hidden="true"
      className="copper-glow absolute top-8 right-8 md:top-12 md:right-16 text-[var(--color-andes-copper-bright)] text-[13px] tracking-[0.08em]"
      style={MONO_SHADOW_STYLE}
      initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={
        shouldReduceMotion
          ? { duration: 0 }
          : { delay: 0.1, duration: 0.4, ease: EASE }
      }
    >
      LIMA · AMSTERDAM
    </motion.p>
  );
}

// Variant A: zes cards in 2 rijen x 3 kolommen. Donkere semi-transparante bg
// met copper border. Hover: scale 1.03, border vol, bg donkerder, glow shadow.
function Vp2Cards({
  shouldReduceMotion,
  vp2InView,
  hoveredPointIndex,
  setHoveredPointIndex,
}: Vp2VariantProps) {
  return (
    <div className="grid grid-cols-3 gap-6 md:gap-8 max-w-6xl mx-auto mt-16 w-full [perspective:1000px]">
      {PLUS_POINTS.map((point, i) => (
        <Vp2Card
          key={point.id}
          point={point}
          index={i}
          isThis={i === hoveredPointIndex}
          shouldReduceMotion={shouldReduceMotion}
          vp2InView={vp2InView}
          onHover={() => setHoveredPointIndex(i)}
          onLeave={() => setHoveredPointIndex(null)}
        />
      ))}
    </div>
  );
}

// Vp2Card: per-card hooks (useMotionValue plus useSpring) voor tilt op basis
// van muis-positie. Hooks moeten per card geïsoleerd zijn dus aparte component
// ipv inline in de map. Tilt komt bovenop bestaande hover-effects (scale,
// border, bg, glow), max 3 graden, smooth spring damping 30 stiffness 200.
function Vp2Card({
  point,
  index,
  isThis,
  shouldReduceMotion,
  vp2InView,
  onHover,
  onLeave,
}: {
  point: (typeof PLUS_POINTS)[number];
  index: number;
  isThis: boolean;
  shouldReduceMotion: boolean | null;
  vp2InView: boolean;
  onHover: () => void;
  onLeave: () => void;
}) {
  // Uniforme tilt-amplitude voor alle 6 cards. 6 graden voelt sterk reactief
  // ongeacht kolom-positie. Spring-easing damping 30 stiffness 200 voor smooth
  // niet-snappy gedrag.
  const TILT_AMPLITUDE = 6;
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springConfig = { damping: 30, stiffness: 200, mass: 0.5 };
  const rotateX = useSpring(
    useTransform(y, [-0.5, 0.5], [TILT_AMPLITUDE, -TILT_AMPLITUDE]),
    springConfig,
  );
  const rotateY = useSpring(
    useTransform(x, [-0.5, 0.5], [-TILT_AMPLITUDE, TILT_AMPLITUDE]),
    springConfig,
  );

  const handleMouseMove = shouldReduceMotion
    ? undefined
    : (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        x.set((e.clientX - rect.left) / rect.width - 0.5);
        y.set((e.clientY - rect.top) / rect.height - 0.5);
      };

  const handleMouseLeave = () => {
    if (!shouldReduceMotion) {
      x.set(0);
      y.set(0);
    }
    onLeave();
  };

  const cardDelay = 0.3 + index * 0.05;

  return (
    <motion.div
      role="button"
      tabIndex={0}
      aria-label={`${point.label}: ${point.description}`}
      onMouseEnter={onHover}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onFocus={onHover}
      onBlur={onLeave}
      className={
        isThis
          ? "relative p-6 md:p-8 rounded-lg backdrop-blur-sm border bg-noche-andina/60 border-[var(--color-andes-copper-bright)] outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-andes-copper-bright)]"
          : "relative p-6 md:p-8 rounded-lg backdrop-blur-sm border bg-noche-andina/40 border-[var(--color-andes-copper-bright)]/40 outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-andes-copper-bright)]"
      }
      style={
        shouldReduceMotion
          ? undefined
          : { rotateX, rotateY, transformStyle: "preserve-3d" }
      }
      initial={
        shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }
      }
      animate={
        vp2InView
          ? {
              opacity: 1,
              y: 0,
              scale: shouldReduceMotion ? 1 : isThis ? 1.03 : 1,
              boxShadow: isThis
                ? "0 0 32px rgba(212, 154, 106, 0.3)"
                : "0 0 0 rgba(212, 154, 106, 0)",
            }
          : {}
      }
      transition={
        shouldReduceMotion
          ? { duration: 0 }
          : {
              opacity: { delay: cardDelay, duration: 0.3, ease: EASE },
              y: { delay: cardDelay, duration: 0.3, ease: EASE },
              scale: { duration: 0.3, ease: EASE },
              boxShadow: { duration: 0.3, ease: EASE },
            }
      }
    >
      <p
        className="copper-glow-soft text-[12px] tracking-[0.15em] text-[var(--color-andes-copper-bright)]/70 mb-3 font-semibold"
        style={MONO_SHADOW_STYLE}
      >
        {point.number}
      </p>
      <h4
        className="copper-glow-soft text-[20px] md:text-[22px] font-semibold uppercase tracking-[0.1em] text-warm-white mb-2"
        style={TEXT_SHADOW_STYLE}
      >
        {point.label}
      </h4>
      <p
        className="text-[14px] md:text-[15px] leading-relaxed text-warm-white/80"
        style={TEXT_SHADOW_STYLE}
      >
        {point.description}
      </p>
    </motion.div>
  );
}

