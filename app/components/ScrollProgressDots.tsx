"use client";

import type { Biome } from "../data/biomes";
import { useActiveBiomeIndex } from "../hooks/useActiveBiomeIndex";

const INACTIVE_CLASS =
  "w-2 h-2 rounded-full bg-mountain-slate ring-1 ring-warm-white/20 transition-all duration-300 ease-out";
// Active-state combineert accent-color plus shape-shift. Een ring bovenop rounded-sm bar-edges
// zou doubled-up tacky ogen. Active blijft ringloos voor crispy edges.
const ACTIVE_CLASS =
  "w-1 h-6 rounded-sm transition-all duration-300 ease-out";

export function ScrollProgressDots({ biomes }: { biomes: Biome[] }) {
  const activeIndex = useActiveBiomeIndex(biomes.length);
  return (
    <div
      aria-hidden="true"
      className="hidden md:flex flex-col gap-4 fixed right-8 top-1/2 -translate-y-1/2 z-20"
    >
      {biomes.map((biome, i) => {
        const isActive = i === activeIndex;
        return (
          <div
            key={biome.id}
            className={isActive ? ACTIVE_CLASS : INACTIVE_CLASS}
            style={
              isActive ? { backgroundColor: biome.accentColor } : undefined
            }
          />
        );
      })}
    </div>
  );
}
