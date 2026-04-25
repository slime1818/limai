"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import Lenis from "lenis";

const LenisContext = createContext<Lenis | null>(null);

// useLenis exposeert de actieve Lenis-instance voor consumers (CTA click-handlers
// die anchor-jumps willen smoothen via lenis.scrollTo). Returns null op coarse
// pointer (touch device, geen Lenis init) of voor de eerste render-tick voordat
// de instance via setLenis is gepushed.
export function useLenis(): Lenis | null {
  return useContext(LenisContext);
}

export function SmoothScrollProvider({ children }: { children: ReactNode }) {
  const [lenis, setLenis] = useState<Lenis | null>(null);

  useEffect(() => {
    // Lenis volledig uit op coarse pointer (touch devices). Native iOS en Android
    // momentum-scroll doet z'n ding onveranderd. RAF-loop overhead + gesmoothde
    // scrollY propagatie door 12 useScroll listeners was te duur op iOS Safari.
    // Desktop (fine pointer) blijft Lenis-driven voor smooth wheel scroll.
    const isTouchDevice = window.matchMedia("(pointer: coarse)").matches;
    if (isTouchDevice) return;

    const instance = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      // Defensive op desktop-met-touchscreen (Surface, iPads met keyboard): laat
      // eventuele touch-events door naar native ipv door Lenis te smoothen.
      touchMultiplier: 0,
    });

    // TODO(react-19): refactor naar useSyncExternalStore of derived state patroon.
    // Geparkeerd in substep 2.1 Apu (scope-discipline). Patroon werkt correct in productie.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLenis(instance);

    let rafId: number;
    function raf(time: number) {
      instance.raf(time);
      rafId = requestAnimationFrame(raf);
    }
    rafId = requestAnimationFrame(raf);

    return () => {
      cancelAnimationFrame(rafId);
      instance.destroy();
      setLenis(null);
    };
  }, []);

  return (
    <LenisContext.Provider value={lenis}>{children}</LenisContext.Provider>
  );
}
