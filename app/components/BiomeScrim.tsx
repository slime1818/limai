import type { Biome } from "../data/biomes";

export function BiomeScrim({ biome }: { biome: Biome }) {
  if (biome.id === "selva") {
    // TODO Fase 2 substep 13: Selva renders no F6 scrim because TOP-framing canopy plus pikzwart schilder-schaduw bottom-left clashen met left-fade.
    // Scrim-alternatief (text-shadow op content-layer, radial-gradient, of rotated F6) wordt daar geland. Spec in docs/status/2026-04-25-fase-2-start.md substep 13.
    return null;
  }
  return (
    <>
      {/* F6 horizontal scrim, desktop. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 hidden md:block"
        style={{
          background:
            "linear-gradient(90deg, rgba(26,22,18,0.68) 0%, rgba(26,22,18,0.45) 30%, rgba(26,22,18,0.08) 55%, rgba(26,22,18,0.0) 72%)",
        }}
      />
      {/* F6 vertical scrim, mobile. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 md:hidden"
        style={{
          background:
            "linear-gradient(180deg, rgba(26,22,18,0.70) 0%, rgba(26,22,18,0.40) 100%)",
        }}
      />
    </>
  );
}
