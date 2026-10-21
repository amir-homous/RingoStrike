// B27 (#384): split mission action, "Do it now" / "Already did it".
// Pure helpers (no Vue) for the two flows, so test:living-space can check them.
// The server rules live in backend services/checkin_context.py (B26).

export const PLACE_KEYS = Object.freeze(["home", "work_school", "gym", "outside", "cafe", "on_the_way", "other"]);
export const FEELING_KEYS = Object.freeze(["light", "good", "okay", "hard_but_done", "tired"]);
export const PLACE_LABEL_MAX = 40;
export const NOTE_MAX = 280;
export const DURATION_MAX_SECONDS = 24 * 60 * 60;

// "Already did it" time chips: local clock times today. "exact" uses an <input type="time">.
export const EARLIER_SLOTS = Object.freeze({
  morning: "09:00",
  noon: "12:30",
  afternoon: "16:00",
  evening: "20:00",
});

export function clampDuration(seconds) {
  const value = Math.round(Number(seconds) || 0);
  return Math.min(DURATION_MAX_SECONDS, Math.max(1, value));
}

// The window performed_at must fall in: today's day start to now, both from the server's ringo
// day (GET /me/ringo/today -> ringo_day). The day boundary is the server's (UTC today, #388);
// change it here only. clientNow / fetchedAt let "now" move on after the metadata was fetched.
export function performedAtWindow(ringoDay, { fetchedAt = Date.now(), clientNow = Date.now() } = {}) {
  const nextReset = Date.parse(ringoDay?.next_reset_at || "");
  const serverNow = Date.parse(ringoDay?.server_now || "");
  if (!Number.isFinite(nextReset) || !Number.isFinite(serverNow)) return null;
  return {
    start: nextReset - 24 * 60 * 60 * 1000,
    end: serverNow + Math.max(0, clientNow - fetchedAt),
  };
}

// Local time "HH:MM" today (the device's clock) -> epoch ms.
export function localTimeToday(hhmm, base = new Date()) {
  const match = /^(\d{1,2}):(\d{2})$/.exec(String(hhmm || ""));
  if (!match) return null;
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  if (hours > 23 || minutes > 59) return null;
  const day = new Date(base.getTime());
  day.setHours(hours, minutes, 0, 0);
  return day.getTime();
}

export function inWindow(time, window) {
  return Boolean(window) && Number.isFinite(time) && time >= window.start && time <= window.end;
}

// performed_at for a chip (or the exact time): an ISO UTC string inside the window, else null.
export function slotPerformedAt(slot, { exactTime = "", window = null, base = new Date() } = {}) {
  const hhmm = slot === "exact" ? exactTime : EARLIER_SLOTS[slot];
  const time = localTimeToday(hhmm, base);
  if (!inWindow(time, window)) return null;
  return new Date(time).toISOString().replace(/\.\d{3}Z$/, "Z");
}

export function slotEnabled(slot, { window = null, base = new Date() } = {}) {
  if (slot === "exact") return Boolean(window);
  return inWindow(localTimeToday(EARLIER_SLOTS[slot], base), window);
}

// The request body: only what the user chose. Everything is optional; {} is a valid save.
export function buildContext({ mode, durationSeconds, performedAt, place, placeLabel, feeling, note } = {}) {
  const body = {};
  if (mode === "now" || mode === "earlier") body.mode = mode;
  if (mode === "now" && durationSeconds != null) body.duration_seconds = clampDuration(durationSeconds);
  if (mode === "earlier" && performedAt) body.performed_at = performedAt;
  if (PLACE_KEYS.includes(place)) {
    body.place_key = place;
    const label = String(placeLabel || "").trim().slice(0, PLACE_LABEL_MAX);
    if (place === "other" && label) body.place_label = label;
  }
  if (FEELING_KEYS.includes(feeling)) body.feeling_key = feeling;
  const text = String(note || "").trim().slice(0, NOTE_MAX);
  if (text) body.note = text;
  return body;
}

// Storage is a convenience only: every access is guarded (private mode, blocked storage).
function store(kind) {
  try {
    return typeof window !== "undefined" ? window[kind] : null;
  } catch {
    return null;
  }
}

function read(kind, key) {
  try {
    return store(kind)?.getItem(key) ?? null;
  } catch {
    return null;
  }
}

function write(kind, key, value) {
  try {
    if (value == null) store(kind)?.removeItem(key);
    else store(kind)?.setItem(key, value);
  } catch {
    // ignore
  }
}

export const focusStartKey = (userKey, missionId) => `ringostrike_focus_start:${userKey || "anon"}:${missionId}`;
export const lastPlaceKey = (userKey, pathKey) => `ringostrike_last_place:${userKey || "anon"}:${pathKey || "path"}`;

export function readFocusStart(userKey, missionId) {
  const value = Number(read("sessionStorage", focusStartKey(userKey, missionId)));
  return Number.isFinite(value) && value > 0 ? value : null;
}

export function writeFocusStart(userKey, missionId, startedAt) {
  write("sessionStorage", focusStartKey(userKey, missionId), startedAt == null ? null : String(startedAt));
}

export function readLastPlace(userKey, pathKey) {
  try {
    const value = JSON.parse(read("localStorage", lastPlaceKey(userKey, pathKey)) || "null");
    return value && PLACE_KEYS.includes(value.key) ? { key: value.key, label: String(value.label || "") } : null;
  } catch {
    return null;
  }
}

export function writeLastPlace(userKey, pathKey, place, label = "") {
  if (!PLACE_KEYS.includes(place)) return;
  write("localStorage", lastPlaceKey(userKey, pathKey), JSON.stringify({ key: place, label: place === "other" ? label : "" }));
}
