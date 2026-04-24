import Image from "next/image";
import { biomes } from "../data/biomes";

const F6_SCRIM =
  "linear-gradient(90deg, rgba(26,22,18,0.68) 0%, rgba(26,22,18,0.45) 30%, rgba(26,22,18,0.08) 55%, rgba(26,22,18,0.0) 72%)";

// Diagnostic: test-1 met h-[100dvh] ipv h-[200dvh]. Isoleert dvh-unit van
// 2x viewport-height. Test-minimal = h-screen (100vh) = geen reversal.
// Test-1 = h-[200dvh] = reversal. Deze test = h-[100dvh] = splits dvh vs 2x.
export default function Test1aDvhSinglePage() {
  return (
    <>
      <div className="fixed top-2 right-2 bg-black/80 text-white font-mono text-xs p-2 z-50 rounded-sm pointer-events-none">
        test-1a-dvh-single
      </div>
      {biomes.map((biome, i) => (
        <section
          key={biome.id}
          className="relative w-full h-[100dvh] overflow-hidden"
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
            style={{ background: F6_SCRIM }}
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
