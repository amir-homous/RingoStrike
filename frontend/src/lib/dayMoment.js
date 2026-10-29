// B37 Part A (#387, D72 to D77): the Ringo moment after a done mission, and the day moment.
// Pure functions: the step composer and the day moment's case, count, chip and week bar.
// Numbers only ever come from /me/stats (current_streak, total_days) and /me/consistency.

const DAY_MS = 24 * 60 * 60 * 1000;

function safeCount(value) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? Math.floor(number) : null;
}

// "Today" is the UTC date, like the server (stats_service, consistency_service).
export function utcTodayIso(now = Date.now()) {
  return new Date(now).toISOString().slice(0, 10);
}

// The last seven days ending today (not a calendar week). null when the data is missing.
export function lastSevenDays(todayIso, consistencyDays) {
  if (!todayIso || !Array.isArray(consistencyDays)) return null;
  const lit = new Set(consistencyDays.filter((day) => Number(day?.count) > 0).map((day) => String(day.date)));
  const today = Date.parse(`${todayIso}T00:00:00Z`);
  if (!Number.isFinite(today)) return null;
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today - (6 - index) * DAY_MS).toISOString().slice(0, 10);
    return { date, lit: lit.has(date), today: index === 6 };
  });
}

// D74: continuing (2+ in a row), first day (1 in a row, 1 day so far), welcome back (1 in a row
// after earlier days). Without total_days a streak of 1 cannot tell first day from coming back:
// "plain" then says only what the data supports.
export function dayMomentCase({ streak, totalDays }) {
  const s = safeCount(streak);
  const total = safeCount(totalDays);
  if (s === null || s < 1) return "plain";
  if (s >= 2) return "continue";
  if (total === null) return "plain";
  return total > 1 ? "welcome_back" : "first";
}

// The day moment's content: the big count, its label, the kicker, the line and the chip.
export function buildDayMoment({ streak, totalDays, week }, translate) {
  const kind = dayMomentCase({ streak, totalDays });
  const s = safeCount(streak);
  const total = safeCount(totalDays);
  const moment = {
    case: kind,
    count: null,
    countLabel: "",
    kicker: "",
    line: translate("ringoRewardSequence.moment.safe"),
    softLine: "",
    chip: "",
    week: Array.isArray(week) && week.length === 7 ? week : null,
  };

  if (kind === "welcome_back") {
    moment.kicker = translate("ringoRewardSequence.moment.welcomeBack");
    moment.count = total;
    moment.countLabel = translate("ringoRewardSequence.moment.daysSoFarLabel", { count: total });
    moment.chip = translate("ringoRewardSequence.moment.rhythmAgain", { count: 1 });
    moment.softLine = translate("ringoRewardSequence.moment.lineBack");
    return moment;
  }

  if (s !== null && s >= 1) {
    moment.count = s;
    moment.countLabel = translate("ringoRewardSequence.moment.inARowLabel", { count: s });
  }
  if (kind === "continue") moment.softLine = translate("ringoRewardSequence.moment.lineContinue");
  if (kind === "first") moment.softLine = translate("ringoRewardSequence.moment.lineFirst");
  // The chip only when it adds something (not "1 day so far" on the first day).
  if (total !== null && total > 1) moment.chip = translate("ringoRewardSequence.moment.daysSoFar", { count: total });
  return moment;
}

function stepOf(steps, type) {
  return (steps || []).find((step) => step?.type === type) || null;
}

// The reward message ladder: the Main and Tiny missions finished today (distinct missions, not
// check-ins; a Bonus never counts), from the list before this completion plus the one just done.
const LADDER_INTENSITIES = new Set(["main", "tiny"]);

function missionIntensityOf(mission) {
  const value = String(mission?.mission_intensity || mission?.intensity || "main").toLowerCase();
  return ["main", "tiny", "bonus"].includes(value) ? value : "main";
}

export function missionsDoneToday(missionsBefore = [], finished = null) {
  const done = new Set();
  for (const mission of Array.isArray(missionsBefore) ? missionsBefore : []) {
    const id = mission?.mission_id ?? mission?.id;
    if (id === null || id === undefined) continue;
    if (String(mission?.status || "").toLowerCase() !== "done") continue;
    if (LADDER_INTENSITIES.has(missionIntensityOf(mission))) done.add(String(id));
  }
  const finishedId = finished?.mission_id ?? finished?.id;
  if (finishedId !== null && finishedId !== undefined && LADDER_INTENSITIES.has(missionIntensityOf(finished))) {
    done.add(String(finishedId));
  }
  return done.size;
}

// The first card's title and line for the count: 1, 2, 3, then 4 and above. The mission title is
// not part of the sentence (titles are imperatives); the card shows it as its own label.
export function ladderCopy(count, missionTitle, translate) {
  const n = Math.max(1, Math.floor(Number(count) || 1));
  if (n === 1) {
    return {
      title: translate("ringoRewardSequence.moment.niceWork"),
      text: translate("ringoRewardSequence.moment.ladder.oneLine"),
    };
  }
  if (n === 2) {
    return { title: translate("ringoRewardSequence.moment.ladder.twoTitle"), text: translate("ringoRewardSequence.moment.ladder.twoLine") };
  }
  if (n === 3) {
    return { title: translate("ringoRewardSequence.moment.ladder.threeTitle"), text: translate("ringoRewardSequence.moment.ladder.threeLine") };
  }
  return {
    title: translate("ringoRewardSequence.moment.ladder.manyTitle"),
    text: translate("ringoRewardSequence.moment.ladder.manyLine", { count: n }),
  };
}

// D72: compose the new cards from the steps the sequence builder already made (so XP, the bar
// and the total stay exactly as computed today, D77).
// - Bonus: one card ("Extra step done." with its XP and the two pace buttons).
// - First counted Main or Tiny of the day: Nice work, the day moment, Choose your pace.
// - Later missions the same day: Nice work, Choose your pace.
export function composeMomentSteps(steps, { intensity = "main", firstOfDay = false, day = null, doneToday = 1 } = {}, translate) {
  if (!Array.isArray(steps) || !steps.length) return [];
  const mission = stepOf(steps, "mission_complete");
  const xp = stepOf(steps, "xp_earned");
  const level = stepOf(steps, "level_up");
  const final = stepOf(steps, "final_choice");
  const missionTitle = mission?.title || translate("ringoRewardSequence.local.missionFallback");
  const xpDetails = {
    value: xp?.value || "",
    progressBar: xp?.progressBar || null,
    meta: xp?.meta || "",
    levelLine: level?.title || "",
  };

  if (intensity === "bonus") {
    return [{
      type: "bonus_done",
      label: translate("ringoRewardSequence.types.mission_complete"),
      title: translate("ringoRewardSequence.moment.bonusTitle"),
      text: missionTitle,
      missionKey: mission?.missionKey || "",
      ...xpDetails,
      sprite: "happy",
      actions: final?.actions || [],
    }];
  }

  const ladder = ladderCopy(doneToday, missionTitle, translate);
  const composed = [{
    type: "nice_work",
    celebrate: true,
    label: translate("ringoRewardSequence.types.mission_complete"),
    title: ladder.title,
    text: ladder.text,
    missionLabel: missionTitle,
    doneToday: Math.max(1, Math.floor(Number(doneToday) || 1)),
    missionKey: mission?.missionKey || "",
    ...xpDetails,
    sprite: "celebration",
  }];

  if (firstOfDay && day) {
    composed.push({
      type: "day_moment",
      celebrate: true,
      label: translate("ringoRewardSequence.types.strike_secured"),
      sprite: "proud",
      moment: buildDayMoment(day, translate),
    });
  }

  if (final) composed.push(final);
  return composed;
}
