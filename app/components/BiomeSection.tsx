import type { CSSProperties, RefObject } from "react";
import type { Biome } from "../data/biomes";

// Selva-specific text-shadow compensatie voor afwezigheid van F6 scrim. Variant A
// per locked spec (docs/status/2026-04-25-fase-2-start.md substep 13). Twee gelaagde
// shadows: softe brede blur voor atmospheric lift over painterly jungle plus tight
// lager-opacity base voor letterrand-definitie.
const SELVA_TEXT_SHADOW: CSSProperties = {
  textShadow:
    "0 2px 12px rgba(0,0,0,0.6), 0 1px 2px rgba(0,0,0,0.8)",
};

export function BiomeSection({
  biome,
  sectionRef,
}: {
  biome: Biome;
  sectionRef: RefObject<HTMLElement | null>;
}) {
  const textStyle: CSSProperties | undefined =
    biome.id === "selva" ? SELVA_TEXT_SHADOW : undefined;

  return (
    <section ref={sectionRef} className="relative w-full h-[200vh]">
      <div className="absolute inset-0 z-10">
        <div className="h-screen flex items-center px-8 md:px-16 lg:px-24">
          <div className="max-w-2xl">
            <h1
              style={textStyle}
              className="font-display text-warm-white text-6xl md:text-8xl lg:text-9xl leading-none tracking-tight"
            >
              {biome.title}
            </h1>
            <p
              style={textStyle}
              className="mt-6 max-w-xl text-lg md:text-xl text-warm-white/90 leading-relaxed"
            >
              {biome.tagline}
            </p>
          </div>
        </div>
        <div className="h-screen flex items-start px-8 md:px-16 lg:px-24">
          <div className="max-w-xl mt-32">
            {biome.viewport2Teaser !== null ? (
              <p
                style={textStyle}
                className="text-base md:text-lg text-warm-white/90 leading-relaxed"
              >
                {biome.viewport2Teaser}
              </p>
            ) : null}
            {biome.ctaHref !== null && biome.ctaLabel !== null ? (
              <a
                href={biome.ctaHref}
                style={textStyle}
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
