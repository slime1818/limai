// Diagnostic counters. Throwaway post-diagnosis. Increments zijn zero-cost mutaties
// op één gedeelde object, geen React state churn. DebugOverlay leest periodiek.
export const debugCounters = {
  motionEvents: 0,
  lenisRaf: 0,
};
