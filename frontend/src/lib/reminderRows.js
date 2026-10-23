// B33 (#405, D65 to D67): reminder rows and the challenge reminder chip. Pure helpers (no Vue),
// checked by test:living-space. Items come from LivingSpace's reminderItems (due and later today).

import { REMINDER_CHIP } from "./pathMarker.js";
import { normalizePathKey } from "./livingSpaceState.js";

// D65: a zone lists only its own reminders: due first, then by time.
export function zoneReminders(items, zone) {
  const key = normalizePathKey(zone?.path_key || zone?.pathKey || "");
  if (!key) return [];
  return (Array.isArray(items) ? items : [])
    .filter((item) => normalizePathKey(item?.pathKey || "") === key)
    .sort((a, b) => Number(Boolean(b.due)) - Number(Boolean(a.due)) || (a.timestamp || 0) - (b.timestamp || 0));
}

export function reminderSummary(items) {
  const list = Array.isArray(items) ? items : [];
  const due = list.filter((item) => item?.due).length;
  return { due, later: list.length - due };
}

// D66: the trailing chip. Due -> "Now"; set -> its time; set but Telegram cannot deliver -> time
// plus "Telegram off". telegram null (not known) never claims Telegram is off.
export function reminderRowState(item, { telegram = null } = {}) {
  if (item?.due) return REMINDER_CHIP.DUE;
  return telegram === false ? REMINDER_CHIP.TELEGRAM_OFF : REMINDER_CHIP.SET;
}

// "20:30" in the viewer's locale digits (24 hours); "" for a missing time.
export function reminderClockTime(timestamp, locale = "en") {
  const value = Number(timestamp);
  if (!Number.isFinite(value)) return "";
  try {
    return new Intl.DateTimeFormat(locale || "en", { hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(value));
  } catch {
    return new Date(value).toISOString().slice(11, 16);
  }
}

// D67: a challenge icon carries its missions' chip: due, then Telegram off, then set.
const CHIP_ORDER = [REMINDER_CHIP.DUE, REMINDER_CHIP.TELEGRAM_OFF, REMINDER_CHIP.SET];

export function challengeReminderChip(missions) {
  const chips = new Set((Array.isArray(missions) ? missions : []).map((mission) => mission?.reminder).filter(Boolean));
  return CHIP_ORDER.find((chip) => chips.has(chip)) || "";
}
