"use client";

import type { Biome } from "../data/biomes";

export function ScrollProgressDots({ biomes }: { biomes: Biome[] }) {
  return (
    <div
      aria-hidden="true"
      className="hidden md:flex flex-col gap-4 fixed right-8 top-1/2 -translate-y-1/2 z-20"
    >
      {biomes.map((biome) => (
        <div
          key={biome.id}
          className="w-2 h-2 rounded-full bg-mountain-slate ring-1 ring-warm-white/20"
        />
      ))}
    </div>
  );
}
