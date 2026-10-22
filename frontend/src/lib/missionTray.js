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

// Paging (D50, reachability): the row has `slots` places, one of them the challenge icon. When the
// paws do not all fit (at most MISSION_TRAY_MAX_PAWS per page), the last place becomes a pager
// control in the same row: "next" ("+N", N = paws after this page) or, on the last page, "back"
// to the first page. Every mission is on exactly one page, so each one stays reachable.
export function pagePaws(missions = [], { slots = 1 + MISSION_TRAY_MAX_PAWS, page = 0 } = {}) {
  const pawSlots = Math.max(1, Math.floor(slots) - 1);
  if (missions.length <= Math.min(pawSlots, MISSION_TRAY_MAX_PAWS)) {
    return { visible: missions, control: null, page: 0, pages: 1 };
  }
  const size = Math.max(1, Math.min(MISSION_TRAY_MAX_PAWS, pawSlots - 1));
  const pages = Math.ceil(missions.length / size);
  const current = Math.min(Math.max(0, Math.floor(page) || 0), pages - 1);
  const visible = missions.slice(current * size, current * size + size);
  const after = missions.length - (current + 1) * size;
  const control = after > 0
    ? { kind: "next", count: after, page: current + 1 }
    : { kind: "back", count: 0, page: 0 };
  return { visible, control, page: current, pages };
}

// Row sizing (D50): items = challenge icon + paws (+ a pager control). Try the 48px pitch, then the
// 44px minimum, then a second row when one exists. rows: available lengths (screen px) of each row
// after the flag tab and padding. slots: how many items fit (never more than wanted).
export function trayRows({ pawCount, rows = [], pitches = [48, 44] }) {
  const wanted = 1 + Math.min(pawCount, MISSION_TRAY_MAX_PAWS) + (pawCount > MISSION_TRAY_MAX_PAWS ? 1 : 0);
  const fit = (length, pitch) => Math.max(0, Math.floor((Number(length) || 0) / pitch));
  for (const pitch of pitches) {
    if (fit(rows[0], pitch) >= wanted) return { pitch, perRow: [wanted], slots: wanted };
  }
  const pitch = pitches[pitches.length - 1];
  const first = fit(rows[0], pitch);
  const second = rows.length > 1 ? fit(rows[1], pitch) : 0;
  if (first + second >= wanted) return { pitch, perRow: [first, wanted - first], slots: wanted };
  // Not enough room for everything: the paws page inside the room there is (pagePaws).
  return { pitch, perRow: second ? [first, second] : [first], slots: first + second };
}
