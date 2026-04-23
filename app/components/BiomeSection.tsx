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
    <section className="relative h-dvh w-full overflow-hidden">
      <Image
        src={image}
        alt={imageAlt}
        fill
        priority
        sizes="100vw"
        className="object-cover"
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
