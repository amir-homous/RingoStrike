// B36 (#408, D70): Bonus stars. One gold star per Bonus finished today: on a challenge icon (top
// left of its ring) and in a row under a path icon. Daily like the rest (D44): built from today's
// missions (GET /me/today-missions), so the stars go with the day. Pure helpers, no Vue.

export const MAX_CHALLENGE_STARS = 3;
export const MAX_PATH_STARS = 5;

export function isBonusDoneToday(mission) {
  const intensity = String(mission?.mission_intensity || mission?.intensity || "").toLowerCase();
  const status = String(mission?.status || mission?.today_status || "").toLowerCase();
  return intensity === "bonus" && (status === "done" || status === "completed");
}

export function bonusDoneByChallenge(missions) {
  const counts = new Map();
  for (const mission of Array.isArray(missions) ? missions : []) {
    if (!isBonusDoneToday(mission)) continue;
    const id = String(mission?.challenge_id ?? mission?.challengeId ?? "");
    if (!id) continue;
    counts.set(id, (counts.get(id) || 0) + 1);
  }
  return counts;
}

// pathKeyOf(mission) -> the mission's path key (LivingSpace knows how to map path ids).
export function bonusDoneByPath(missions, pathKeyOf = (mission) => mission?.path_key || "") {
  const counts = {};
  for (const mission of Array.isArray(missions) ? missions : []) {
    if (!isBonusDoneToday(mission)) continue;
    const key = pathKeyOf(mission);
    if (!key) continue;
    counts[key] = (counts[key] || 0) + 1;
  }
  return counts;
}

// Star centres on a challenge ring of size `ring` px (top left arc, clockwise from the top-left
// diagonal): never near the reminder chip (top right) or the state badge (bottom right).
export const CHALLENGE_STAR_ANGLES = Object.freeze([-135, -160, -110]);

export function challengeStarPoints(count, ring = 44) {
  const n = Math.max(0, Math.min(MAX_CHALLENGE_STARS, Math.floor(Number(count) || 0)));
  const r = ring / 2;
  return CHALLENGE_STAR_ANGLES.slice(0, n).map((deg) => {
    const a = (deg * Math.PI) / 180;
    return { x: Math.round((r + r * Math.cos(a)) * 10) / 10, y: Math.round((r + r * Math.sin(a)) * 10) / 10 };
  });
}

export function pathStarCount(count) {
  return Math.max(0, Math.min(MAX_PATH_STARS, Math.floor(Number(count) || 0)));
}
