import Image from "next/image";

interface BiomeSectionProps {
  image: string;
  imageAlt: string;
  title: string;
  tagline: string;
}

export function BiomeSection({
  image,
  imageAlt,
  title,
  tagline,
}: BiomeSectionProps) {
  return (
    <section className="relative w-full aspect-[1024/768] min-h-dvh overflow-hidden">
      <Image
        src={image}
        alt={imageAlt}
        fill
        priority
        sizes="100vw"
        className="object-cover"
      />
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
      <div className="relative z-10 flex h-full items-center px-8 md:px-16 lg:px-24">
        <div className="max-w-2xl">
          <h1 className="font-display text-warm-white text-6xl md:text-8xl lg:text-9xl leading-none tracking-tight">
            {title}
          </h1>
          <p className="mt-6 max-w-xl text-lg md:text-xl text-warm-white/90 leading-relaxed">
            {tagline}
          </p>
        </div>
      </div>
    </section>
  );
}
