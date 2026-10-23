// B35 (#407, D69): "Pick a time" for Remind me later. Pure helpers, checked by test:living-space.
// The server refuses a reminder at or after the next day reset (`reminder_after_next_reset`,
// backend services/mission_service.py); the reset is the next UTC midnight (utils/date_utils.py).

export function nextResetAt(now = new Date()) {
  const date = new Date(now.getTime());
  date.setUTCHours(24, 0, 0, 0);
  return date;
}

// The field shows Latin digits in EN and FA; Persian or Arabic-Indic digits typed in are accepted.
export function latinDigits(value) {
  return String(value ?? "")
    .replace(/[۰-۹]/g, (d) => String(d.charCodeAt(0) - 0x06f0))
    .replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660));
}

export function parseTimePart(value, max) {
  const text = latinDigits(value).trim();
  if (!/^\d{1,2}$/.test(text)) return null;
  const number = Number(text);
  return number >= 0 && number <= max ? number : null;
}

export const pad2 = (value) => String(value).padStart(2, "0");

// A local clock time today. A time already past means tomorrow, which is after the reset too.
// -> { ok: true, at: Date } or { ok: false, reason: "invalid" | "after_reset" }
export function customReminderAt({ hour, minute } = {}, { now = new Date(), nextReset = nextResetAt(now) } = {}) {
  const h = parseTimePart(hour, 23);
  const m = parseTimePart(minute, 59);
  if (h === null || m === null) return { ok: false, reason: "invalid" };
  const at = new Date(now.getTime());
  at.setHours(h, m, 0, 0);
  if (at.getTime() <= now.getTime()) at.setDate(at.getDate() + 1);
  if (at.getTime() >= nextReset.getTime()) return { ok: false, reason: "after_reset" };
  return { ok: true, at };
}

// The picker opens one hour ahead (rounded up to 5 minutes), or 15 minutes ahead when an hour would
// cross the reset.
export function defaultPickerTime(now = new Date(), nextReset = nextResetAt(now)) {
  const round = (ms) => {
    const date = new Date(ms);
    const minutes = Math.ceil(date.getMinutes() / 5) * 5;
    date.setMinutes(minutes, 0, 0);
    return date;
  };
  let at = round(now.getTime() + 60 * 60e3);
  if (at.getTime() >= nextReset.getTime()) at = round(now.getTime() + 15 * 60e3);
  return { hour: pad2(at.getHours()), minute: pad2(at.getMinutes()) };
}

// The arrows: hours wrap 0 to 23; minutes move by 5 and wrap 0 to 55.
export function stepTimePart(value, part, delta) {
  const current = parseTimePart(value, part === "hour" ? 23 : 59) ?? 0;
  if (part === "hour") return pad2((current + delta + 24) % 24);
  const snapped = Math.round(current / 5) * 5;
  return pad2((snapped + delta * 5 + 60) % 60);
}
