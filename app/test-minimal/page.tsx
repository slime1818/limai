import Image from "next/image";
import { biomes } from "../data/biomes";

// Diagnostic route: vanilla stacked 6 biomes, geen sticky, geen fixed, geen dvh,
// geen motion, geen useScroll, geen Lenis, geen altitude-pan, geen crossfade,
// geen lazy-load, geen client components. Alleen server-rendered stacked divs.
// Doel: isoleren of iPhone scroll-reversal issue uit onze architectuur komt of
// uit iOS Safari platform-level. Te verwijderen post-diagnosis.
export default function TestMinimalPage() {
  return (
    <>
      {biomes.map((biome, i) => (
        <section
          key={biome.id}
          className="relative w-full h-screen overflow-hidden"
        >
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
            style={{
              background:
                "linear-gradient(90deg, rgba(26,22,18,0.68) 0%, rgba(26,22,18,0.45) 30%, rgba(26,22,18,0.08) 55%, rgba(26,22,18,0.0) 72%)",
            }}
          />
          <div className="relative z-10 flex h-full items-center px-8 md:px-16">
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
