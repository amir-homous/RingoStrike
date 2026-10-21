// B30 S3: the mission tray of a picked challenge (D50, D51, D19, D20, D32, D44).
// Pure state and sizing: the challenge's missions from GET /paths/:id/challenges, joined by
// mission id with GET /me/today-missions for the reminder fields. No Vue or Vite, so the
// dependency-free tests import it.

import { isDueReminderMission, normalizedMissionStatus, reminderTimestamp } from "./livingSpaceState.js";
import { reminderChip } from "./pathMarker.js";

// At most this many paws; more become one "+N" chip that Ringo explains (D50).
export const MISSION_TRAY_MAX_PAWS = 4;

export const PAW_STATE = Object.freeze({ OPEN: "open", LOCKED: "locked", DONE: "done" });

function intensity(mission) {
  return mission?.intensity || mission?.mission_intensity || "main";
}

function status(mission) {
  return String(mission?.status || mission?.today_status || "pending").toLowerCase();
}

function isDone(mission) {
  return status(mission) === "done";
}

// Paw state for the room (S0 canvas): done today, locked (not open yet, or a Bonus before the
// main step, D20), otherwise open. bonus drives the dashed ring and the gold done paw.
export function missionPawState(mission, { mainDone = false } = {}) {
  const bonus = intensity(mission) === "bonus";
  if (isDone(mission)) return { state: PAW_STATE.DONE, bonus };
  const available = Boolean(mission?.availableToday ?? mission?.available_today);
  const locked = !available || status(mission) === "locked" || (bonus && !mainDone);
  return { state: locked ? PAW_STATE.LOCKED : PAW_STATE.OPEN, bonus };
}

// Reminder chip for one mission: due > Telegram not connected > set, from the today-missions row
// (status, reminder_at, reminder_sent_at). Missions that are not in today's list have none.
export function missionReminderChip(todayMission, { now = Date.now(), telegram = null } = {}) {
  if (!todayMission) return "";
  const due = isDueReminderMission(todayMission, now) ? 1 : 0;
  const scheduled = normalizedMissionStatus(todayMission) === "remind_later" && reminderTimestamp(todayMission) > now ? 1 : 0;
  return reminderChip({ dueCount: due, scheduledCount: scheduled, telegram });
}

// Which missions get a paw: main and Bonus always, a tiny substitute only once it is in play
// (the user chose "smaller", or it has a decision today), as in the panel's list.
export function trayMissions(missions = [], { activeTinyIds = [] } = {}) {
  const active = new Set(activeTinyIds.map(String));
  return missions.filter((mission) => {
    if (intensity(mission) !== "tiny") return true;
    return active.has(String(mission?.id)) || status(mission) !== "pending";
  });
}

// Split into visible paws and the "+N" overflow. capacity is how many paws fit next to the
// challenge icon (the room's free space can allow fewer than MISSION_TRAY_MAX_PAWS).
export function splitPaws(missions = [], capacity = MISSION_TRAY_MAX_PAWS) {
  const max = Math.max(0, Math.min(MISSION_TRAY_MAX_PAWS, Math.floor(capacity)));
  if (missions.length <= max) return { visible: missions, hidden: [] };
  // One slot goes to the "+N" chip.
  const shown = Math.max(0, max - 1);
  return { visible: missions.slice(0, shown), hidden: missions.slice(shown) };
}

// Row sizing (D50): items = challenge icon + paws (+ chip). Try the 48px pitch, then the 44px
// minimum, then a second row when one exists. rows: available lengths (screen px) of each row
// after the flag tab and padding. Returns the pitch, items per row and how many paws fit.
export function trayRows({ pawCount, rows = [], pitches = [48, 44] }) {
  const wanted = 1 + Math.min(pawCount, MISSION_TRAY_MAX_PAWS) + (pawCount > MISSION_TRAY_MAX_PAWS ? 1 : 0);
  const fit = (length, pitch) => Math.max(0, Math.floor((Number(length) || 0) / pitch));
  for (const pitch of pitches) {
    if (fit(rows[0], pitch) >= wanted) return { pitch, perRow: [wanted], pawCapacity: MISSION_TRAY_MAX_PAWS };
  }
  const pitch = pitches[pitches.length - 1];
  const first = fit(rows[0], pitch);
  const second = rows.length > 1 ? fit(rows[1], pitch) : 0;
  if (first + second >= wanted) return { pitch, perRow: [first, wanted - first], pawCapacity: MISSION_TRAY_MAX_PAWS };
  // Not enough room: fewer paws, the rest go to the chip (one slot for the challenge icon).
  const slots = first + second;
  return { pitch, perRow: second ? [first, slots - first] : [slots], pawCapacity: Math.max(0, slots - 1) };
}
