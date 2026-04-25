"use client";

import { useRef, useState, type CSSProperties, type RefObject } from "react";
import {
  motion,
  useInView,
  useMotionValueEvent,
  useReducedMotion,
  useScroll,
} from "motion/react";
import type { Biome } from "../data/biomes";

// Locked spec timeline (apu.md regel 174-186) plus revisies fase B akkoord. Alle
// elementen leunen op deze ease curve voor consistente "soepel ease-out" feel.
const EASE: [number, number, number, number] = [0.23, 1, 0.32, 1];

// Mono-feel via tabular-nums. Olivier locked: geen extra mono-font, Inter met
// font-feature-settings tnum plus letter-spacing-utility per element.
const MONO_STYLE: CSSProperties = {
  fontFeatureSettings: "'tnum'",
};

// Text-shadow voor copper en warm-white tekst die buiten F6 scrim left-zone valt
// of op licht backdrop-gedeelte landt. Zachte donkere halo voor leesbaarheid
// zonder hard outline.
const TEXT_SHADOW_STYLE: CSSProperties = {
  textShadow: "0 1px 8px rgba(26, 22, 18, 0.6)",
};

const MONO_SHADOW_STYLE: CSSProperties = {
  ...MONO_STYLE,
  ...TEXT_SHADOW_STYLE,
};

// Six-biome route content. Apu-only en niet uit biomes.ts geleend, want het is
// een Apu-specifiek narratief element. PACÍFICO heeft accent op de I.
const ROUTE: ReadonlyArray<{ id: string; label: string }> = [
  { id: "apu", label: "APU" },
  { id: "puna", label: "PUNA" },
  { id: "yungas", label: "YUNGAS" },
  { id: "selva", label: "SELVA" },
  { id: "paracas", label: "PARACAS" },
  { id: "pacifico", label: "PACÍFICO" },
];

const TITLE_LETTERS = "LimAI".split("");

export function ApuSection({
  biome,
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

  return (
    <section
      ref={sectionRef}
      id="apu"
      aria-labelledby="apu-heading"
      className="relative w-full h-[200vh]"
    >
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
            className="self-start flex items-center gap-3 text-andes-copper text-[12px] tracking-[0.08em]"
            style={MONO_STYLE}
            initial={
              shouldReduceMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: -8 }
            }
            animate={{ opacity: 1, x: 0 }}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 0.2, duration: 0.4, ease: EASE }
            }
          >
            <span aria-hidden="true" className="block w-4 h-px bg-andes-copper" />
            01 · Studio uit Amsterdam
          </motion.p>

          {/* Midblock: h1 LimAI, tagline, divider, metrics. Verticaal centraal,
              links uitgelijnd, max-w-2xl voor regel-controle. */}
          <div className="self-center max-w-2xl">
            <motion.h1
              id="hero-heading"
              aria-label="LimAI"
              className="font-display italic text-warm-white text-[64px] md:text-[84px] lg:text-[96px] leading-none tracking-tight"
            >
              {TITLE_LETTERS.map((letter, i) => (
                <motion.span
                  key={i}
                  aria-hidden="true"
                  className="inline-block"
                  initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={
                    shouldReduceMotion
                      ? { duration: 0 }
                      : { delay: 0.5 + i * 0.06, duration: 0.4, ease: EASE }
                  }
                >
                  {letter}
                </motion.span>
              ))}
            </motion.h1>

            <motion.p
              className="mt-6 font-sans text-[var(--color-secondary-warm)] text-base md:text-lg"
              initial={
                shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 6 }
              }
              animate={{ opacity: 1, y: 0 }}
              transition={
                shouldReduceMotion
                  ? { duration: 0 }
                  : { delay: 1.0, duration: 0.5, ease: EASE }
              }
            >
              {biome.tagline}
            </motion.p>

            <motion.hr
              aria-hidden="true"
              className="mt-6 w-60 h-px border-0 bg-andes-copper/40 origin-left"
              initial={shouldReduceMotion ? { scaleX: 1 } : { scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={
                shouldReduceMotion
                  ? { duration: 0 }
                  : { delay: 1.2, duration: 0.4, ease: EASE }
              }
            />

            <motion.p
              className="mt-4 uppercase text-andes-copper text-[12px] tracking-[0.1em]"
              style={MONO_SHADOW_STYLE}
              initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={
                shouldReduceMotion
                  ? { duration: 0 }
                  : { delay: 1.3, duration: 0.5, ease: EASE }
              }
            >
              6 BIOMES · 2 MAKERS · AMSTERDAM
            </motion.p>
          </div>

          {/* Scroll-indicator gecentreerd onderaan VP1, met intro fade plus
              pulse-loop tot eerste scroll. */}
          <motion.div
            aria-hidden="true"
            className="self-end justify-self-center text-andes-copper text-[14px] tracking-[0.12em] text-center"
            style={MONO_SHADOW_STYLE}
            initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 1.5, duration: 0.5, ease: EASE }
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
            className="absolute bottom-8 right-8 md:bottom-12 md:right-16 text-andes-copper text-[11px] tracking-[0.05em]"
            style={MONO_SHADOW_STYLE}
            initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 1.5, duration: 0.5, ease: EASE }
            }
          >
            52°22&apos;N · 12°03&apos;S
          </motion.p>
        </article>

        {/* VIEWPORT 2: zes-biome route preview */}
        <article
          ref={vp2Ref}
          aria-labelledby="route-heading"
          className="relative h-screen flex flex-col justify-center items-center px-8 md:px-16 lg:px-24"
        >
          <h3 id="route-heading" className="sr-only">
            De reis door zes biomes
          </h3>

          <div className="relative w-full max-w-3xl lg:max-w-4xl">
            {/* Connector lijn achter de dots. left/right 8.333% lijnt op de
                kolom-centers van grid-cols-6 (1/12 en 11/12 van totale breedte).
                z-0 plus z-10 op ol garandeert dat dots over de lijn renderen. */}
            <motion.div
              aria-hidden="true"
              className="absolute h-px bg-andes-copper/35 pointer-events-none origin-left z-0"
              style={{ left: "8.333%", right: "8.333%", top: "12px" }}
              initial={shouldReduceMotion ? { scaleX: 1 } : { scaleX: 0 }}
              animate={vp2InView ? { scaleX: 1 } : { scaleX: 0 }}
              transition={
                shouldReduceMotion
                  ? { duration: 0 }
                  : { duration: 0.6, ease: EASE }
              }
            />

            <ol
              className="relative z-10 grid grid-cols-6 gap-0"
              aria-label="Zes biomes op de homepage"
            >
              {ROUTE.map((b, i) => {
                const isActive = i === 0;
                const dotDelay = 0.6 + i * 0.08;
                const labelDelay = 1.2 + i * 0.06;
                return (
                  <li key={b.id} className="flex flex-col items-center gap-3">
                    <div className="flex items-center justify-center h-6">
                      <motion.span
                        aria-hidden="true"
                        className={
                          isActive
                            ? "block w-6 h-6 rounded-full bg-andes-copper"
                            : "block w-3 h-3 rounded-full bg-andes-copper/30"
                        }
                        initial={
                          shouldReduceMotion
                            ? { scale: 1, opacity: 1 }
                            : isActive
                              ? { scale: 1, opacity: 0 }
                              : { scale: 0.6, opacity: 0 }
                        }
                        animate={
                          vp2InView
                            ? isActive
                              ? { scale: [1, 1.3, 1], opacity: 1 }
                              : { scale: 1, opacity: 1 }
                            : {}
                        }
                        transition={
                          shouldReduceMotion
                            ? { duration: 0 }
                            : { delay: dotDelay, duration: 0.3, ease: EASE }
                        }
                      />
                    </div>
                    <motion.span
                      className={
                        isActive
                          ? "text-[11px] tracking-[0.1em] uppercase text-andes-copper"
                          : "text-[11px] tracking-[0.1em] uppercase text-andes-copper/45"
                      }
                      style={MONO_SHADOW_STYLE}
                      initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
                      animate={vp2InView ? { opacity: 1 } : {}}
                      transition={
                        shouldReduceMotion
                          ? { duration: 0 }
                          : { delay: labelDelay, duration: 0.3, ease: EASE }
                      }
                    >
                      {b.label}
                    </motion.span>
                  </li>
                );
              })}
            </ol>
          </div>

          <motion.p
            className="mt-12 font-display italic text-warm-white text-4xl md:text-5xl text-center"
            style={TEXT_SHADOW_STYLE}
            initial={
              shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }
            }
            animate={vp2InView ? { opacity: 1, y: 0 } : {}}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 1.7, duration: 0.5, ease: EASE }
            }
          >
            Zes taferelen.
          </motion.p>
          <motion.p
            className="mt-3 font-sans text-[var(--color-secondary-warm)] text-base md:text-lg text-center"
            style={TEXT_SHADOW_STYLE}
            initial={
              shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }
            }
            animate={vp2InView ? { opacity: 1, y: 0 } : {}}
            transition={
              shouldReduceMotion
                ? { duration: 0 }
                : { delay: 1.9, duration: 0.5, ease: EASE }
            }
          >
            Scroll om ze te ontmoeten.
          </motion.p>
        </article>
      </div>
    </section>
  );
}
