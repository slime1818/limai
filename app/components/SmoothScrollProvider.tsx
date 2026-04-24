"use client";

import { useEffect, type ReactNode } from "react";
import Lenis from "lenis";
import { debugCounters } from "../lib/debug-counters";

export function SmoothScrollProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      // Laat touch-scroll aan native iOS/Android momentum, Lenis alleen voor desktop wheel.
      // Voorkomt Lenis vs native scroll conflict op mobile dat blokkerig scroll-gedrag veroorzaakte.
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
