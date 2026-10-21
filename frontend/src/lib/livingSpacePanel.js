// Pure helpers for the Living Space room panel v2 (docs/product/LIVING_SPACE_PANEL_V2_SPEC.md).
// Kept free of Vue so test:living-space can import them.

const DONE_STATUSES = ["done", "completed"];
const DECIDED_STATUSES = ["done", "completed", "remind_later", "skipped"];

export function missionIntensity(mission) {
  return String(mission?.intensity || "main").toLowerCase();
}

export function missionStatus(mission) {
  return String(mission?.status || "pending").toLowerCase();
}

export function missionDone(mission) {
  return DONE_STATUSES.includes(missionStatus(mission));
}

export function missionDecided(mission) {
  return DECIDED_STATUSES.includes(missionStatus(mission));
}

function sameId(a, b) {
  const left = String(a ?? "");
  return Boolean(left) && left === String(b ?? "");
}

// Today's main step counts as done when the main mission or its tiny substitute is done.
export function todayMainDone(missions = []) {
  return missions.some((mission) => {
    return ["main", "tiny"].includes(missionIntensity(mission)) && missionDone(mission);
  });
}

// Option A: today's missions only. Tiny appears only after the user asked for it,
// a bonus is dimmed until the main step is done, future missions are a count only.
export function buildTodayMissionRows(missions = [], options = {}) {
  const { focusId = null, requestedTinyId = null, dueReminderId = null } = options;
  const mainDone = todayMainDone(missions);
  const rows = [];
  let futureCount = 0;

  for (const mission of missions) {
    const intensity = missionIntensity(mission);
    const decided = missionDecided(mission);
    const requestedTiny = intensity === "tiny" && sameId(mission?.id, requestedTinyId);

    if (intensity === "tiny" && !requestedTiny && !decided) continue;

    if (!mission?.availableToday && !decided && !requestedTiny) {
      futureCount += 1;
      continue;
    }

    const afterMain = intensity === "bonus" && !mainDone && !missionDone(mission);
    const dueReminder = sameId(mission?.id, dueReminderId);

    rows.push({
      id: mission?.id,
      mission,
      intensity,
      state: missionDone(mission)
        ? "done"
        : dueReminder
          ? "due"
          : missionStatus(mission) === "skipped"
            ? "skipped"
            : missionStatus(mission) === "remind_later"
              ? "reminder"
              : "pending",
      afterMain,
      dueReminder,
      focused: sameId(mission?.id, focusId),
      selectable: !afterMain,
    });
  }

  return { rows, futureCount, mainDone };
}

// Which Ringo card state to show. Inputs are plain booleans so the panel keeps its own predicates.
// explicitPick (B30 S2, D14/D41): the user tapped a challenge, so the card answers for it and a
// due reminder no longer takes the card (it stays as one line). justJoined (D39): the challenge
// was just joined from the room; the card shows the post-join moment until the user moves on.
export function ringoCardState({
  dueReminderFocused = false,
  restMode = false,
  challengeJoined = true,
  hasChallenge = true,
  focusGated = false,
  focusCanComplete = false,
  focusDone = false,
  mainDone = false,
  explicitPick = false,
  justJoined = false,
} = {}) {
  if (dueReminderFocused && focusCanComplete && !explicitPick) return "reminder";
  if (restMode) return "rest";
  if (justJoined && hasChallenge && challengeJoined) return "joined";
  if (hasChallenge && !challengeJoined) return "preview";
  if (focusCanComplete && !focusGated) return "mission";
  if (mainDone && (focusDone || !focusCanComplete)) return "safe";
  if (focusGated) return "locked";
  if (focusDone) return "done";
  return "fallback";
}

// B8 recommendation priority (spec): due reminder > user-picked > unfinished main >
// tiny substitute (only once the user chose smaller) > optional bonus offer > rest.
// A bonus is never auto-focused; it is only offered (see bonusOfferCandidates).
export function pickFocusMission(missions = [], { dueMission = null, pickedId = null } = {}) {
  if (dueMission) return dueMission;

  const picked = pickedId
    ? missions.find((mission) => sameId(mission?.id, pickedId))
    : null;
  if (picked) return picked;

  // Once the main step or its tiny substitute is done, today's step is satisfied:
  // focus the done mission (today-safe state) instead of re-offering the main.
  if (todayMainDone(missions)) {
    return missions.find((mission) => missionIntensity(mission) === "main" && missionDone(mission))
      || missions.find((mission) => missionIntensity(mission) === "tiny" && missionDone(mission));
  }

  const unfinishedMain = missions.find((mission) => {
    return missionIntensity(mission) === "main"
      && mission?.availableToday
      && missionStatus(mission) === "pending";
  });
  if (unfinishedMain) return unfinishedMain;

  const tinySubstitute = missions.find((mission) => {
    return missionIntensity(mission) === "tiny"
      && !missionDone(mission)
      && missionStatus(mission) !== "skipped";
  });
  if (tinySubstitute) return tinySubstitute;

  return missions.find((mission) => missionIntensity(mission) === "main")
    || missions.find((mission) => missionIntensity(mission) === "tiny")
    || missions.find((mission) => missionIntensity(mission) !== "bonus" && mission?.availableToday)
    || null;
}

// Bonus missions that can be offered: available today, not done or skipped, in a joined
// challenge whose main step (or tiny substitute) is done today.
export function bonusOfferCandidates(challenges = []) {
  return challenges.flatMap((challenge) => {
    const missions = challenge?.missions || [];
    if (!challenge?.isJoined || !todayMainDone(missions)) return [];

    return missions
      .filter((mission) => {
        return missionIntensity(mission) === "bonus"
          && mission?.availableToday
          && !missionDone(mission)
          && missionStatus(mission) !== "skipped";
      })
      .map((mission) => ({ challenge, mission }));
  });
}

export function shouldOfferBonus({ mainDone = false, dueReminderCount = 0, candidates = [], focusIsBonus = false } = {}) {
  return Boolean(mainDone && dueReminderCount === 0 && candidates.length && !focusIsBonus);
}

// B24: time left until a reminder, in whole hours and minutes (rounded up to the next minute).
export function reminderTimeLeft(timestamp, now = Date.now()) {
  if (!Number.isFinite(timestamp)) return { state: "unknown", hours: 0, minutes: 0 };

  const diff = timestamp - now;
  if (diff <= 0) return { state: "due", hours: 0, minutes: 0 };

  const totalMinutes = Math.ceil(diff / 60000);
  return {
    state: "scheduled",
    hours: Math.floor(totalMinutes / 60),
    minutes: totalMinutes % 60,
  };
}
