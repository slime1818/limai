"use client";

import Image from "next/image";
import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
} from "motion/react";
import { useRef } from "react";
import type { Biome } from "../data/biomes";

export function BiomeSection({
  biome,
  priority = false,
}: {
  biome: Biome;
  priority?: boolean;
}) {
  const sectionRef = useRef<HTMLElement>(null);
  const shouldReduceMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"],
  });
  const y = useTransform(
    scrollYProgress,
    [0, 1],
    shouldReduceMotion ? ["0%", "0%"] : ["-8%", "8%"],
  );

  return (
    <section ref={sectionRef} className="relative w-full h-[200dvh]">
      <div className="sticky top-0 h-dvh w-full">
        <div className="relative h-full w-full overflow-hidden">
          <motion.div
            className="absolute inset-x-0 top-[-10%] bottom-[-10%] will-change-transform"
            style={{ y }}
          >
            <Image
              src={biome.image}
              alt={biome.imageAlt}
              fill
              priority={priority}
              sizes="100vw"
              className="object-cover"
            />
          </motion.div>
          {/* F6 horizontal scrim. Selva needs variant, TOP-framing canopy clashes with left-fade. Must-do gate before T3 integration, see Fase 2 substep 13. */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 z-0 hidden md:block"
            style={{
              background:
                "linear-gradient(90deg, rgba(26,22,18,0.68) 0%, rgba(26,22,18,0.45) 30%, rgba(26,22,18,0.08) 55%, rgba(26,22,18,0.0) 72%)",
            }}
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 z-0 md:hidden"
            style={{
              background:
                "linear-gradient(180deg, rgba(26,22,18,0.70) 0%, rgba(26,22,18,0.40) 100%)",
            }}
          />
        </div>
      </div>
      <div className="absolute inset-0 z-10">
        <div className="h-dvh flex items-center px-8 md:px-16 lg:px-24">
          <div className="max-w-2xl">
            <h1 className="font-display text-warm-white text-6xl md:text-8xl lg:text-9xl leading-none tracking-tight">
              {biome.title}
            </h1>
            <p className="mt-6 max-w-xl text-lg md:text-xl text-warm-white/90 leading-relaxed">
              {biome.tagline}
            </p>
          </div>
        </div>
        <div className="h-dvh flex items-start px-8 md:px-16 lg:px-24">
          <div className="max-w-xl mt-32">
            {biome.viewport2Teaser !== null ? (
              <p className="text-base md:text-lg text-warm-white/90 leading-relaxed">
                {biome.viewport2Teaser}
              </p>
            ) : null}
            {biome.ctaHref !== null && biome.ctaLabel !== null ? (
              <a
                href={biome.ctaHref}
                className="mt-8 inline-block text-warm-white hover:text-andes-copper underline underline-offset-4 decoration-1 transition-colors"
              >
                {biome.ctaLabel}
              </a>
            ) : null}
            {/* TODO Apu scroll-chevron: when ctaHref is null and viewport2Teaser is null, render a subtle scroll-down indicator in viewport 2. Deferred to a follow-up substep. */}
          </div>
        </div>
      </div>
    </section>
  );
}
