// B30: read-only path marker per room zone (ring, colour, lit, check badge, reminder chip).
// Pure state: built from data the room already loads (GET /paths/:id/challenges, the missions
// prop, the Telegram settings MissionCenter loads). No Vue or Vite, so test:living-space imports it.

export const REMINDER_CHIP = Object.freeze({
  DUE: "due",
  TELEGRAM_OFF: "telegram_off",
  SET: "set",
});

// Path icon names (frontend/src/assets/path-icons) when /paths has not loaded the path's own icon;
// the same map SpaceZone and SpaceZonePanel use.
export const PATH_ICON_FALLBACK = Object.freeze({
  career: "briefcase",
  fitness: "activity",
  learning: "book",
  creativity: "sparkles",
  sleep: "moon",
});

const HEX_COLOR = /^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i;

// The path's own colour from paths.color; anything that is not a hex colour is ignored.
export function pathMarkerColor(color) {
  const value = String(color || "").trim();
  return HEX_COLOR.test(value) ? value : "";
}

function isJoined(challenge) {
  return Boolean(challenge?.isJoined ?? challenge?.is_joined ?? challenge?.enrollmentId ?? challenge?.enrollment_id);
}

function todayChecked(challenge) {
  return Boolean(challenge?.todayChecked ?? challenge?.today_checked);
}

// Telegram can deliver a reminder only when connected with reminders on. null = not known yet
// (settings not loaded or the request failed): then the chip never claims Telegram is off.
export function telegramReady(settings) {
  if (!settings || typeof settings !== "object") return null;
  return Boolean(settings.connected && settings.reminders_enabled);
}

// One chip per zone: due > Telegram not connected (a pending reminder it cannot deliver) > set.
export function reminderChip({ dueCount = 0, scheduledCount = 0, telegram = null } = {}) {
  const due = Number(dueCount) || 0;
  const scheduled = Number(scheduledCount) || 0;
  if (due > 0) return REMINDER_CHIP.DUE;
  if (scheduled > 0 && telegram === false) return REMINDER_CHIP.TELEGRAM_OFF;
  if (scheduled > 0) return REMINDER_CHIP.SET;
  return "";
}

// challenges: the path's challenge items (camelCase from LivingSpace or the raw API shape).
// Daily state (D44): it resets at the day boundary. One ring segment per joined challenge, filled
// when that challenge has a counted check-in today (today_checked), done ones first so the filled
// arc is contiguous. The glyph takes the path colour and glows when at least one is done today;
// the check badge shows only when every joined challenge is done today. total_checkins (Day N)
// is not read here.
export function pathMarkerState({ challenges = [], color = "", dueCount = 0, scheduledCount = 0, telegram = null } = {}) {
  const list = Array.isArray(challenges) ? challenges : [];
  const joined = list.filter(isJoined);
  const segments = joined
    .map((challenge) => ({ done: todayChecked(challenge) }))
    .sort((a, b) => Number(b.done) - Number(a.done));
  const doneToday = segments.filter((segment) => segment.done).length;
  const pathColor = pathMarkerColor(color);
  const coloured = doneToday > 0 && Boolean(pathColor);

  return {
    segments,
    joined: joined.length,
    doneToday,
    empty: joined.length === 0,
    coloured,
    color: coloured ? pathColor : "",
    lit: doneToday > 0,
    allDoneToday: joined.length > 0 && doneToday === joined.length,
    reminder: reminderChip({ dueCount, scheduledCount, telegram }),
  };
}

// SVG ring geometry: one arc per segment with a small gap, starting at the top, clockwise.
// Returns stroke-dasharray / dashoffset pairs for a circle of radius r (the room never mirrors).
export function ringSegments(count, r, gapDegrees = 10) {
  const n = Math.max(0, Math.floor(Number(count) || 0));
  if (!n) return [];
  const circumference = 2 * Math.PI * r;
  const gap = n > 1 ? (circumference * gapDegrees) / 360 : 0;
  const arc = circumference / n - gap;

  return Array.from({ length: n }, (_, index) => {
    const start = (circumference / n) * index + gap / 2;
    return {
      dasharray: `${round(arc)} ${round(circumference - arc)}`,
      dashoffset: round(circumference / 4 - start),
    };
  });
}

function round(value) {
  return Math.round(value * 100) / 100;
}
