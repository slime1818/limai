"use client";

import { useEffect, useState } from "react";
import { debugCounters } from "../lib/debug-counters";

type PerformanceWithMemory = Performance & {
  memory?: { usedJSHeapSize: number };
};

export function DebugOverlay() {
  const [fps, setFps] = useState(0);
  const [scrollY, setScrollY] = useState(0);
  const [rafPerSec, setRafPerSec] = useState(0);
  const [motionPerSec, setMotionPerSec] = useState(0);
  const [memoryMB, setMemoryMB] = useState("n/a");
  const [viewport, setViewport] = useState("0x0");

  useEffect(() => {
    let lastTime = performance.now();
    let frames = 0;
    let lastRafCount = debugCounters.lenisRaf;
    let lastMotionCount = debugCounters.motionEvents;
    let rafId: number;

    function tick() {
      frames++;
      const now = performance.now();
      const elapsed = now - lastTime;

      if (elapsed >= 250) {
        setFps(Math.round((frames * 1000) / elapsed));
        const currentRaf = debugCounters.lenisRaf;
        const currentMotion = debugCounters.motionEvents;
        setRafPerSec(
          Math.round(((currentRaf - lastRafCount) * 1000) / elapsed),
        );
        setMotionPerSec(
          Math.round(((currentMotion - lastMotionCount) * 1000) / elapsed),
        );
        lastRafCount = currentRaf;
        lastMotionCount = currentMotion;

        setScrollY(Math.round(window.scrollY));
        setViewport(`${window.innerWidth}x${window.innerHeight}`);

        const mem = (performance as PerformanceWithMemory).memory;
        if (mem) {
          setMemoryMB(`${Math.round(mem.usedJSHeapSize / 1024 / 1024)}`);
        }

        frames = 0;
        lastTime = now;
      }

      rafId = requestAnimationFrame(tick);
    }

    rafId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafId);
  }, []);

  return (
    <div
      className="fixed top-2 left-2 bg-black/85 text-white font-mono text-xs p-3 z-50 leading-tight rounded-md select-none"
      style={{ minWidth: 160 }}
    >
      <div className="font-bold mb-1">Debug</div>
      <div>FPS: {fps}</div>
      <div>scrollY: {scrollY}</div>
      <div>RAF/s: {rafPerSec}</div>
      <div>motion/s: {motionPerSec}</div>
      <div>memory: {memoryMB}MB</div>
      <div>viewport: {viewport}</div>
    </div>
  );
}
