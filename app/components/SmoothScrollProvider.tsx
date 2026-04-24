"use client";

import { useEffect, type ReactNode } from "react";
import Lenis from "lenis";
import { debugCounters } from "../lib/debug-counters";

export function SmoothScrollProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    // Lenis volledig uit op coarse pointer (touch devices). Native iOS en Android
    // momentum-scroll doet z'n ding onveranderd. RAF-loop overhead + gesmoothde
    // scrollY propagatie door 12 useScroll listeners was te duur op iOS Safari.
    // Desktop (fine pointer) blijft Lenis-driven voor smooth wheel scroll.
    const isTouchDevice = window.matchMedia("(pointer: coarse)").matches;
    if (isTouchDevice) return;

    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      // Defensive op desktop-met-touchscreen (Surface, iPads met keyboard): laat
      // eventuele touch-events door naar native ipv door Lenis te smoothen.
      touchMultiplier: 0,
    });

    let rafId: number;
    function raf(time: number) {
      lenis.raf(time);
      debugCounters.lenisRaf++;
      rafId = requestAnimationFrame(raf);
    }
    rafId = requestAnimationFrame(raf);

    return () => {
      cancelAnimationFrame(rafId);
      lenis.destroy();
    };
  }, []);

  return <>{children}</>;
}
