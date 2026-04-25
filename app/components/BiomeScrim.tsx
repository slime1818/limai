import type { Biome } from "../data/biomes";

export function BiomeScrim({ biome }: { biome: Biome }) {
  if (biome.id === "selva" || biome.id === "apu") {
    // Selva: TOP-framing canopy plus pikzwart schilder-schaduw bottom-left
    // clashen met left-fade. Text-shadow alternatief landt op content-layer
    // in BiomeSection (Variant A per commit 1dea0f4 + substep 13).
    // Apu: site-breed F6 conflicteert met de bovenste helft van VP1 (eyebrow
    // links, LIMA-pill rechtsboven). ApuSection rendert eigen lokale content-
    // scrim (z-6 radial onder content-zone) plus warmte-overlays als alternatief
    // (substep 2.1 commercial revision).
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
