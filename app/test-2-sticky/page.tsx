import Image from "next/image";
import { biomes } from "../data/biomes";

const F6_SCRIM =
  "linear-gradient(90deg, rgba(26,22,18,0.68) 0%, rgba(26,22,18,0.45) 30%, rgba(26,22,18,0.08) 55%, rgba(26,22,18,0.0) 72%)";

// Diagnostic: test-1 plus sticky-top-0 h-dvh image wrapper binnen 200dvh sections.
// Image pinned tijdens eerste viewport van section, content in normal flow
// in tweede viewport. Test sticky-positioning als reversal-trigger.
export default function Test2StickyPage() {
  return (
    <>
      <div className="fixed top-2 right-2 bg-black/80 text-white font-mono text-xs p-2 z-50 rounded-sm pointer-events-none">
        test-2-sticky
      </div>
      {biomes.map((biome, i) => (
        <section key={biome.id} className="relative w-full h-[200dvh]">
          <div className="sticky top-0 h-dvh w-full">
            <div className="relative h-full w-full overflow-hidden">
              <Image
                src={biome.image}
                alt={biome.imageAlt}
                fill
                sizes="100vw"
                className="object-cover"
                priority={i === 0}
              />
              <div
                aria-hidden="true"
                className="absolute inset-0"
                style={{ background: F6_SCRIM }}
              />
            </div>
          </div>
          <div className="h-dvh flex items-center px-8 md:px-16">
            <div className="max-w-2xl">
              <h1 className="font-display text-warm-white text-5xl md:text-7xl leading-none tracking-tight">
                {biome.title}
              </h1>
              <p className="mt-6 max-w-xl text-base md:text-lg text-warm-white/90 leading-relaxed">
                {biome.tagline}
              </p>
            </div>
          </div>
        </section>
      ))}
    </>
  );
}
