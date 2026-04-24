import Image from "next/image";
import type { RefObject } from "react";
import type { Biome } from "../data/biomes";
import { BiomeScrim } from "./BiomeScrim";

export function BiomeSection({
  biome,
  sectionRef,
}: {
  biome: Biome;
  sectionRef: RefObject<HTMLElement | null>;
  // renderContent prop accepteerd maar genegeerd: pas 4 tijdelijk uit voor
  // diagnostic test. Als scroll-reversal weg is op iPhone, blijft pas 4 uit en
  // wordt alternatieve content-strategy overwogen. Als reversal blijft,
  // restore pas 4 en zoek verder.
  renderContent?: boolean;
}) {
  return (
    <section
      ref={sectionRef}
      className="relative w-full h-[200dvh] pointer-coarse:h-[100vh]"
    >
      {/* Diagnostic 1b: mobile inline fallback image + scrim (desktop gebruikt ImageStack
          fixed-position layers, die zijn verborgen op coarse pointer). Test of
          fixed-position ImageStack de iOS reversal trigger is. */}
      <div className="pointer-fine:hidden absolute inset-0 z-0 overflow-hidden">
        <Image
          src={biome.image}
          alt={biome.imageAlt}
          fill
          sizes="100vw"
          className="object-cover"
          priority={biome.id === "apu"}
        />
        <BiomeScrim biome={biome} />
      </div>
      <div className="absolute inset-0 z-10">
        <div className="h-dvh pointer-coarse:h-1/2 flex items-center px-8 md:px-16 lg:px-24">
          <div className="max-w-2xl">
            <h1 className="font-display text-warm-white text-6xl md:text-8xl lg:text-9xl leading-none tracking-tight">
              {biome.title}
            </h1>
            <p className="mt-6 max-w-xl text-lg md:text-xl text-warm-white/90 leading-relaxed">
              {biome.tagline}
            </p>
          </div>
        </div>
        <div className="h-dvh pointer-coarse:h-1/2 flex items-start px-8 md:px-16 lg:px-24">
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
