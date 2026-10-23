// B32 (#402, D60 to D64): the five object tiles per zone that replace the "Objects in this corner"
// dropdown. Pure helpers (no Vue), checked by test:living-space.

export const TILE_STATE = Object.freeze({
  PLACED: "placed", // in the room: full art, solid ring
  NEXT: "next", // the next object: ghost art (or its silhouette), dashed
  LATER: "later", // still locked: quiet silhouette by kind, dashed
});

// Simple 2px line silhouettes, 24x24 viewBox, one per reward kind (`object_type`). Each entry is a
// list of [tag, attrs] drawn with stroke currentColor. Unknown kinds fall back to a plain box.
export const KIND_SILHOUETTES = Object.freeze({
  planner: [["rect", { x: 5, y: 3, width: 14, height: 18, rx: 2 }], ["path", { d: "M9 3v18M12 8h4M12 12h4" }]],
  lamp: [["path", { d: "M8 4h8l3 7H5z" }], ["path", { d: "M12 11v8M8 20h8" }]],
  monitor: [["rect", { x: 3, y: 4, width: 18, height: 12, rx: 2 }], ["path", { d: "M8 20h8M12 16v4" }]],
  wall_board: [["rect", { x: 3, y: 3, width: 18, height: 14, rx: 1.5 }], ["path", { d: "M7 8h6M7 12h10M9 21l3-4 3 4" }]],
  trophy: [["path", { d: "M8 4h8v5a4 4 0 0 1-8 0zM8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8 20h8" }]],
  book: [["path", { d: "M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z" }], ["path", { d: "M4 21V5M8 7h7" }]],
  books: [["rect", { x: 4, y: 14, width: 16, height: 4, rx: 1 }], ["rect", { x: 6, y: 9, width: 13, height: 5, rx: 1 }], ["rect", { x: 5, y: 4, width: 12, height: 5, rx: 1 }]],
  easel: [["rect", { x: 6, y: 3, width: 12, height: 10, rx: 1 }], ["path", { d: "M9 13l-3 8M15 13l3 8M12 13v5" }]],
  wall_art: [["rect", { x: 4, y: 4, width: 16, height: 16, rx: 1.5 }], ["path", { d: "M4 16l5-5 4 4 2-2 5 5" }], ["circle", { cx: 15, cy: 9, r: 1.5 }]],
  bottle: [["path", { d: "M10 2h4v3l2 3v12a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2V8l2-3z" }], ["path", { d: "M8 12h8" }]],
  weights: [["path", { d: "M7 12h10" }], ["rect", { x: 3, y: 8, width: 4, height: 8, rx: 1 }], ["rect", { x: 17, y: 8, width: 4, height: 8, rx: 1 }]],
  mat: [["path", { d: "M3 15l4-6h14l-4 6z" }], ["path", { d: "M3 15v2h14l4-6" }]],
  bench: [["path", { d: "M3 10h18M5 10v8M19 10v8M8 14h8" }]],
  shelf: [["path", { d: "M4 3v18M20 3v18M4 9h16M4 15h16M4 21h16" }]],
  pillow: [["path", { d: "M4 8c0-2 2-3 8-3s8 1 8 3v8c0 2-2 3-8 3s-8-1-8-3z" }]],
  blanket: [["path", { d: "M3 6h18v12H3z" }], ["path", { d: "M3 10h18M7 18v3M17 18v3" }]],
});

export function kindSilhouette(kind) {
  return KIND_SILHOUETTES[String(kind || "").trim()] || [["rect", { x: 4, y: 4, width: 16, height: 16, rx: 3 }]];
}

function rewardOrder(a, b) {
  return (Number(a?.stage) || 1) - (Number(b?.stage) || 1) || (Number(a?.id) || 0) - (Number(b?.id) || 0);
}

// The zone's rewards as tiles, in reward order (stage, then id), at most five.
// `inRoom(reward, state)` says whether the room draws that object (placed art or the ghost).
export function objectTiles(zone, { inRoom = () => false, limit = 5 } = {}) {
  const unlocked = (zone?.unlocked_objects || []).filter((reward) => reward?.key);
  const locked = (zone?.locked_preview_objects || []).filter((reward) => reward?.key);
  const nextKey = (zone?.next_reward?.key) || locked.slice().sort(rewardOrder)[0]?.key || "";
  return [...unlocked.map((reward) => ({ reward, unlocked: true })), ...locked.map((reward) => ({ reward, unlocked: false }))]
    .sort((a, b) => rewardOrder(a.reward, b.reward))
    .slice(0, limit)
    .map(({ reward, unlocked }) => {
      const state = unlocked ? TILE_STATE.PLACED : reward.key === nextKey ? TILE_STATE.NEXT : TILE_STATE.LATER;
      return {
        key: reward.key,
        reward,
        state,
        kind: reward.object_type || "",
        // D61: only placed objects and the next ghost are shown in the room, and only when drawn.
        roomEffect: state !== TILE_STATE.LATER && Boolean(inRoom(reward, state)),
        ghost: state === TILE_STATE.NEXT,
      };
    });
}

// D61: every tile gives Ringo's card; only a tile with a room layer also triggers the room effect.
export function tileTapResult(tile) {
  if (!tile) return { card: false, room: false };
  return { card: true, room: Boolean(tile.roomEffect) };
}

// Placed card date: the reward's real unlock timestamp, as a calendar date in the viewer's locale.
// SQLite gives "YYYY-MM-DD HH:MM:SS" (UTC); null when it is missing or unreadable.
export function unlockDate(unlockedAt) {
  const raw = String(unlockedAt || "").trim();
  if (!raw) return null;
  const iso = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?$/.test(raw) ? `${raw.replace(" ", "T")}Z` : raw;
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatUnlockDate(unlockedAt, locale = "en") {
  const date = unlockDate(unlockedAt);
  if (!date) return "";
  try {
    return new Intl.DateTimeFormat(locale || "en", { year: "numeric", month: "long", day: "numeric" }).format(date);
  } catch {
    return date.toISOString().slice(0, 10);
  }
}

// D63: the card text for a tapped tile. Placed: the date (and, for the first-mission reward, the
// path). Next and later: a soft hint from the reward description, never a number or threshold.
// `t(key, params)` resolves the copy; returns { key, params } descriptors when no t is given.
export function objectCardCopy(tile, { pathName = "", locale = "en", t = null } = {}) {
  const reward = tile?.reward || {};
  const say = (key, params = {}) => (t ? t(key, params) : { key, params });
  if (tile?.state === TILE_STATE.PLACED) {
    const date = formatUnlockDate(reward.unlocked_at, locale);
    if (date && reward.unlock_condition_type === "first_path_mission_done" && pathName) {
      return say("space.objectGrid.placedFirst", { date, path: pathName });
    }
    if (date) return say("space.objectGrid.placedOn", { date });
    return say("space.objectGrid.placedNoDate");
  }
  // The first reward's own description is past tense ("Unlocked because ..."), so it gets a soft hint.
  if (reward.unlock_condition_type === "first_path_mission_done" && pathName) {
    return say("space.objectGrid.firstHint", { path: pathName });
  }
  const text = softHint(reward.description);
  return text || say("space.objectGrid.laterHint");
}

// Never show a number or threshold in a hint: a description with a digit falls back to the generic hint.
export function softHint(description) {
  const text = String(description || "").trim();
  if (!text || /[0-9۰-۹٠-٩]/.test(text)) return "";
  return text;
}
