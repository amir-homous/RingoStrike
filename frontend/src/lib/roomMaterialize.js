// B21: in-room materialize sequence for newly unlocked rewards (spec §6).
// Pure helpers (no Vue) so test:living-space can check the state machine.

// Spec §6, about 1.6 s in total.
export const MATERIALIZE_PHASES = Object.freeze([
  { name: "light", ms: 300 }, // zone light pool rises
  { name: "resolve", ms: 600 }, // ghost dither fades out while full colour fades in
  { name: "settle", ms: 200 }, // 1px settle drop
  { name: "glint", ms: 500 }, // glint sparkle
]);

export const MATERIALIZE_TOTAL_MS = MATERIALIZE_PHASES.reduce((sum, phase) => sum + phase.ms, 0);

// Steps with start offsets; reduced motion has none (the placed state shows at once).
export function materializeTimeline({ reducedMotion = false } = {}) {
  if (reducedMotion) return [];
  let at = 0;
  return MATERIALIZE_PHASES.map((phase) => {
    const step = { ...phase, at };
    at += phase.ms;
    return step;
  });
}

// Phase at a time since the sequence started; "placed" once it is over.
export function materializePhaseAt(elapsedMs, timeline = materializeTimeline()) {
  const step = timeline.find((item) => elapsedMs >= item.at && elapsedMs < item.at + item.ms);
  return step ? step.name : "placed";
}

// Backfilled unlocks are written as seen ("mission_history"); never animate them.
export const BACKFILL_SOURCE = "mission_history";

function unlockOrder(a, b) {
  const left = String(a?.unlocked_at || "");
  const right = String(b?.unlocked_at || "");
  if (left !== right) return left < right ? -1 : 1;
  return Number(a?.id || 0) - Number(b?.id || 0);
}

// Rewards that should materialize: unlocked, not yet seen, not backfilled. Oldest unlock first.
export function materializeCandidates(rewards = []) {
  return rewards
    .filter((reward) => reward?.key && reward.unlocked && !reward.is_seen && reward.source_type !== BACKFILL_SOURCE)
    .sort(unlockOrder);
}

// Once-only queue by reward key: a key that was ever queued is never queued again.
export function createMaterializeQueue() {
  const known = new Set();
  const pending = [];

  return {
    enqueue(rewards = []) {
      const added = [];
      for (const reward of rewards) {
        const key = reward?.key;
        if (!key || known.has(key) || reward.source_type === BACKFILL_SOURCE) continue;
        known.add(key);
        pending.push({ key, zoneKey: reward.zone_key || "", id: reward.id ?? null });
        added.push(key);
      }
      return added;
    },
    next() {
      return pending[0] || null;
    },
    done(key) {
      const index = pending.findIndex((item) => item.key === key);
      if (index >= 0) pending.splice(index, 1);
    },
    pendingKeys() {
      return pending.map((item) => item.key);
    },
    size() {
      return pending.length;
    },
  };
}
