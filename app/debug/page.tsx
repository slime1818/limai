import { BiomeScroller } from "../components/BiomeScroller";
import { DebugOverlay } from "../components/DebugOverlay";
import { ScrollProgressDots } from "../components/ScrollProgressDots";
import { biomes } from "../data/biomes";

// Throwaway diagnostic route. Rendert identieke home-page content plus DebugOverlay
// met FPS, scrollY, motion-events/s, Lenis RAF/s, memory, viewport readouts.
// Te verwijderen post-diagnosis, zie commit message pas 3+.
export default function DebugPage() {
  return (
    <>
      <BiomeScroller biomes={biomes} />
      <ScrollProgressDots biomes={biomes} />
      <DebugOverlay />
    </>
  );
}
