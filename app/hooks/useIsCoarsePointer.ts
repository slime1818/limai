"use client";

import { useEffect, useState } from "react";

// Detecteert of het primary input-device coarse (touch) is. Gebruikt voor
// conditional-disable van GPU-zware animaties op mobile. Listener blijft actief
// zodat viewport-resizing met pointer-mode switch (bijv. detachable keyboard
// tablet) juist respondeert.
export function useIsCoarsePointer(): boolean {
  const [isCoarse, setIsCoarse] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(pointer: coarse)");
    setIsCoarse(mq.matches);
    const handler = (e: MediaQueryListEvent) => setIsCoarse(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  return isCoarse;
}
