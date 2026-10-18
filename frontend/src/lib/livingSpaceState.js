// Pure Living Space state helpers, kept free of Vue so smoke tests can import them.

const PATH_KEY_ALIASES = {
  body: "fitness",
  focus: "career",
  mind: "sleep",
};

export function normalizePathKey(pathKey) {
  return PATH_KEY_ALIASES[pathKey] || pathKey || "";
}

export function normalizeId(value) {
  const id = String(value ?? "").trim();
  return id && id !== "null" && id !== "undefined" ? id : "";
}

export function normalizedMissionStatus(mission) {
  return String(mission?.status || mission?.today_status || "pending").toLowerCase();
}

export function reminderTimestamp(mission) {
  if (!mission?.reminder_at) return Number.POSITIVE_INFINITY;

  const date = new Date(mission.reminder_at);
  const timestamp = date.getTime();

  return Number.isNaN(timestamp) ? Number.POSITIVE_INFINITY : timestamp;
}

export function isDueReminderMission(mission, now = Date.now()) {
  return normalizedMissionStatus(mission) === "remind_later"
    && reminderTimestamp(mission) <= now
    && !mission?.reminder_sent_at;
}

export function findDueReminderZone(reminder, zones = []) {
  if (!reminder) return null;

  const reminderPathKey = normalizePathKey(reminder.pathKey || "");
  const reminderPathId = normalizeId(reminder.pathId);

  return zones.find((zone) => {
    const zonePathKey = normalizePathKey(zone.path_key || "");
    const zonePathId = normalizeId(zone.pathDetail?.pathId);

    return (reminderPathKey && zonePathKey === reminderPathKey)
      || (reminderPathId && zonePathId === reminderPathId);
  }) || null;
}

export function dueReminderFocusForZone(reminder, reminderZone, zone) {
  if (!reminder || !reminderZone || !zone) return null;
  return reminderZone.zone_key === zone.zone_key ? reminder : null;
}

export function findFirstReward(zone) {
  const rewards = [
    ...(zone?.unlocked_objects || []),
    ...(zone?.locked_preview_objects || []),
  ];

  return rewards.find((reward) => {
    return reward?.unlock_condition_type === "first_path_mission_done";
  }) || null;
}
