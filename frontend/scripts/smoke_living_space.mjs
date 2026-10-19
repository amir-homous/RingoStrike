import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";

import {
  LEGACY_CHALLENGE_ICON_IDS,
  challengeIconCandidates,
  challengeIconKey,
} from "../src/lib/challengeIconKeys.js";
import { localizeChallenge, localizeMission } from "../src/lib/ringoContentLocalization.js";
import {
  bonusOfferCandidates,
  buildTodayMissionRows,
  pickFocusMission,
  reminderTimeLeft,
  ringoCardState,
  shouldOfferBonus,
  todayMainDone,
} from "../src/lib/livingSpacePanel.js";

import {
  dueReminderFocusForZone,
  findDueReminderZone,
  findFirstReward,
  isDueReminderMission,
  normalizeId,
  normalizePathKey,
  normalizedMissionStatus,
  reminderTimestamp,
} from "../src/lib/livingSpaceState.js";

const NOW = Date.parse("2026-10-18T12:00:00Z");

function run() {
  // Zone/path key mapping: legacy zone keys alias to current path keys.
  assert.equal(normalizePathKey("body"), "fitness");
  assert.equal(normalizePathKey("focus"), "career");
  assert.equal(normalizePathKey("mind"), "sleep");
  assert.equal(normalizePathKey("creativity"), "creativity");
  assert.equal(normalizePathKey(undefined), "");
  assert.equal(normalizePathKey(""), "");

  assert.equal(normalizeId(7), "7");
  assert.equal(normalizeId(" 7 "), "7");
  assert.equal(normalizeId(null), "");
  assert.equal(normalizeId("null"), "");
  assert.equal(normalizeId("undefined"), "");

  assert.equal(normalizedMissionStatus({ status: "Remind_Later" }), "remind_later");
  assert.equal(normalizedMissionStatus({ today_status: "done" }), "done");
  assert.equal(normalizedMissionStatus({}), "pending");

  assert.equal(reminderTimestamp({}), Number.POSITIVE_INFINITY);
  assert.equal(reminderTimestamp({ reminder_at: "not-a-date" }), Number.POSITIVE_INFINITY);
  assert.equal(reminderTimestamp({ reminder_at: "2026-10-18T11:00:00Z" }), NOW - 3600000);

  // Due reminders: remind_later, reminder time reached, not yet sent.
  const due = { status: "remind_later", reminder_at: "2026-10-18T11:00:00Z" };
  assert.equal(isDueReminderMission(due, NOW), true);
  assert.equal(isDueReminderMission({ ...due, reminder_at: "2026-10-18T13:00:00Z" }, NOW), false);
  assert.equal(isDueReminderMission({ ...due, reminder_sent_at: "2026-10-18T11:01:00Z" }, NOW), false);
  assert.equal(isDueReminderMission({ ...due, status: "pending" }, NOW), false);
  assert.equal(isDueReminderMission({ status: "remind_later" }, NOW), false);

  // Due-reminder focus selection: match the zone by path key (with aliases) or path id.
  const zones = [
    { zone_key: "body_corner", path_key: "body", pathDetail: { pathId: 1 } },
    { zone_key: "focus_desk", path_key: "focus", pathDetail: { pathId: 2 } },
    { zone_key: "creativity_wall", path_key: "creativity", pathDetail: { pathId: 3 } },
  ];

  assert.equal(findDueReminderZone(null, zones), null);
  assert.equal(findDueReminderZone({ pathKey: "fitness" }, zones).zone_key, "body_corner");
  assert.equal(findDueReminderZone({ pathKey: "career" }, zones).zone_key, "focus_desk");
  assert.equal(findDueReminderZone({ pathKey: "", pathId: "3" }, zones).zone_key, "creativity_wall");
  assert.equal(findDueReminderZone({ pathKey: "unknown", pathId: 2 }, zones).zone_key, "focus_desk");
  assert.equal(findDueReminderZone({ pathKey: "unknown", pathId: null }, zones), null);
  assert.equal(findDueReminderZone({ pathKey: "fitness" }, []), null);

  const reminder = { id: 5, pathKey: "career" };
  const reminderZone = findDueReminderZone(reminder, zones);
  assert.equal(dueReminderFocusForZone(reminder, reminderZone, zones[1]), reminder);
  assert.equal(dueReminderFocusForZone(reminder, reminderZone, zones[0]), null);
  assert.equal(dueReminderFocusForZone(reminder, reminderZone, null), null);
  assert.equal(dueReminderFocusForZone(reminder, null, zones[1]), null);
  assert.equal(dueReminderFocusForZone(null, reminderZone, zones[1]), null);

  // First-reward visibility: the first_path_mission_done object, locked or placed.
  const lockedFirst = {
    key: "desk_plant",
    unlock_condition_type: "first_path_mission_done",
    unlocked: false,
  };
  const laterPreview = {
    key: "lamp",
    unlock_condition_type: "path_missions_done",
    unlocked: false,
  };

  assert.equal(findFirstReward(null), null);
  assert.equal(findFirstReward({}), null);
  assert.equal(findFirstReward({ locked_preview_objects: [laterPreview] }), null);
  assert.equal(
    findFirstReward({ locked_preview_objects: [laterPreview, lockedFirst] }),
    lockedFirst,
  );

  const placedFirst = { ...lockedFirst, unlocked: true };
  const placed = findFirstReward({
    unlocked_objects: [placedFirst],
    locked_preview_objects: [laterPreview],
  });
  assert.equal(placed, placedFirst);
  assert.equal(Boolean(placed.unlocked), true);

  runChallengeIconKeySmoke();
  runPanelV2Smoke();
  runRecommendationPrioritySmoke();
  runReminderTimeLeftSmoke();

  console.log("Living Space smoke test passed.");
}

function runChallengeIconKeySmoke() {
  assert.equal(challengeIconKey("Deep Work Sprint"), "deep-work-sprint");
  assert.equal(challengeIconKey("  Sleep Wind-Down! "), "sleep-wind-down");
  assert.equal(challengeIconKey(""), "");

  // Stable key first, legacy id alias last.
  assert.deepEqual(challengeIconCandidates({ id: 7, name: "Deep Work Sprint" }), ["deep-work-sprint"]);
  assert.deepEqual(challengeIconCandidates({ id: 30, name: "Deep Work Sprint" }), ["deep-work-sprint"]);
  assert.deepEqual(challengeIconCandidates({ id: 31 }), ["move-your-body"]);
  assert.deepEqual(challengeIconCandidates({ challenge_id: 7 }), []);
  assert.deepEqual(challengeIconCandidates("44"), ["morning-recovery"]);
  assert.deepEqual(challengeIconCandidates(7), []);
  assert.deepEqual(challengeIconCandidates(null), []);
  assert.deepEqual(
    challengeIconCandidates({ iconKey: "deep-work-sprint", name: "اسپرینت کار عمیق", id: 7 }),
    ["deep-work-sprint"],
  );

  // Persian localization keeps the English-derived key.
  const faChallenge = localizeChallenge({ challenge_id: 7, name: "Deep Work Sprint" }, "fa");
  assert.notEqual(faChallenge.name, "Deep Work Sprint");
  assert.equal(faChallenge.icon_key, "deep-work-sprint");
  assert.deepEqual(challengeIconCandidates(faChallenge), ["deep-work-sprint"]);

  const faMission = localizeMission(
    { key: "move-10", title: "Move for 10 minutes", challenge_name: "Move Your Body", challenge_id: 1 },
    "fa",
  );
  assert.notEqual(faMission.challenge_name, "Move Your Body");
  assert.equal(faMission.challenge_icon_key, "move-your-body");

  // Every seeded challenge and every legacy alias has an icon file.
  const iconDir = new URL("../src/assets/challenge-icons/", import.meta.url);
  const seed = readFileSync(
    new URL("../../backend/services/path_seed_service.py", import.meta.url),
    "utf8",
  );
  const seededNames = [...seed.matchAll(/^\s*"name": "([^"]+)",$/gm)].map(([, name]) => name);
  assert.equal(seededNames.length, 15);

  for (const name of seededNames) {
    assert.ok(existsSync(new URL(`${challengeIconKey(name)}.png`, iconDir)), `icon for ${name}`);
  }
  for (const key of Object.values(LEGACY_CHALLENGE_ICON_IDS)) {
    assert.ok(existsSync(new URL(`${key}.png`, iconDir)), `legacy icon ${key}`);
  }
  assert.ok(existsSync(new URL("default_challenge_icon.png", iconDir)));
}

function runPanelV2Smoke() {
  const main = { id: 1, intensity: "main", status: "pending", availableToday: true };
  const tiny = { id: 2, intensity: "tiny", status: "pending", availableToday: true, parentMissionId: 1 };
  const bonus = { id: 3, intensity: "bonus", status: "pending", availableToday: true };
  const future = { id: 4, intensity: "main", status: "locked", availableToday: false, unlocksInDays: 2 };

  // Option A: today only, tiny hidden until asked, bonus dimmed before main, future as a count.
  let today = buildTodayMissionRows([main, tiny, bonus, future], { focusId: 1 });
  assert.deepEqual(today.rows.map((row) => row.id), [1, 3]);
  assert.equal(today.futureCount, 1);
  assert.equal(today.mainDone, false);
  assert.equal(today.rows[0].focused, true);
  assert.equal(today.rows[1].afterMain, true);
  assert.equal(today.rows[1].selectable, false);

  today = buildTodayMissionRows([main, tiny, bonus], { requestedTinyId: 2 });
  assert.deepEqual(today.rows.map((row) => row.id), [1, 2, 3]);

  // Tiny substitute done counts as today's main step; bonus becomes selectable.
  const tinyDone = { ...tiny, status: "done" };
  assert.equal(todayMainDone([main, tinyDone]), true);
  today = buildTodayMissionRows([main, tinyDone, bonus]);
  assert.deepEqual(today.rows.map((row) => [row.id, row.state]), [[1, "pending"], [2, "done"], [3, "pending"]]);
  assert.equal(today.rows[2].afterMain, false);

  today = buildTodayMissionRows([{ ...main, status: "remind_later" }], { dueReminderId: 1 });
  assert.equal(today.rows[0].state, "due");
  assert.equal(today.rows[0].dueReminder, true);

  assert.deepEqual(buildTodayMissionRows([]), { rows: [], futureCount: 0, mainDone: false });

  // Ringo card state priority.
  assert.equal(ringoCardState({ dueReminderFocused: true, focusCanComplete: true, restMode: true }), "reminder");
  assert.equal(ringoCardState({ restMode: true, focusCanComplete: true }), "rest");
  assert.equal(ringoCardState({ hasChallenge: true, challengeJoined: false }), "preview");
  assert.equal(ringoCardState({ focusCanComplete: true }), "mission");
  assert.equal(ringoCardState({ mainDone: true, focusDone: true }), "safe");
  assert.equal(ringoCardState({ mainDone: true, focusCanComplete: true }), "mission");
  assert.equal(ringoCardState({ focusGated: true }), "locked");
  assert.equal(ringoCardState({ focusDone: true }), "done");
  assert.equal(ringoCardState({}), "fallback");
}

function runRecommendationPrioritySmoke() {
  const main = { id: 1, intensity: "main", status: "pending", availableToday: true };
  const tiny = { id: 2, intensity: "tiny", status: "remind_later", availableToday: true, parentMissionId: 1 };
  const bonus = { id: 3, intensity: "bonus", status: "pending", availableToday: true };
  const due = { ...main, status: "remind_later" };

  // 1. Due reminder beats everything, including an explicit pick.
  assert.equal(pickFocusMission([main, bonus], { dueMission: due, pickedId: 3 }), due);
  // 2. User pick beats the default order.
  assert.equal(pickFocusMission([main, bonus], { pickedId: 3 }), bonus);
  // 3. Unfinished main beats a tiny with an earlier decision.
  assert.equal(pickFocusMission([main, tiny, bonus]), main);
  // 4. Tiny substitute when the main is not pending.
  assert.equal(pickFocusMission([{ ...main, status: "skipped" }, tiny, bonus]).id, 2);
  // 5. Bonus is never auto-focused.
  assert.notEqual(pickFocusMission([{ ...main, status: "skipped" }, bonus])?.id, 3);
  assert.equal(pickFocusMission([bonus]), null);
  // Main or tiny done: focus the done mission (today-safe), not the bonus or a still-pending main.
  assert.equal(pickFocusMission([{ ...main, status: "done" }, bonus]).id, 1);
  assert.equal(pickFocusMission([main, { ...tiny, status: "done" }, bonus]).id, 2);
  assert.equal(pickFocusMission([]), null);

  // Bonus offer: only for joined challenges whose main (or tiny) is done today.
  const open = { id: 10, isJoined: true, missions: [main, bonus] };
  const safe = { id: 11, isJoined: true, missions: [{ ...main, status: "done" }, bonus] };
  const tinySafe = { id: 12, isJoined: true, missions: [main, { ...tiny, status: "done" }, { ...bonus, id: 4 }] };
  const preview = { id: 13, isJoined: false, missions: [{ ...main, status: "done" }, bonus] };
  const usedBonus = { id: 14, isJoined: true, missions: [{ ...main, status: "done" }, { ...bonus, status: "done" }] };
  const candidates = bonusOfferCandidates([open, safe, tinySafe, preview, usedBonus]);
  assert.deepEqual(candidates.map((item) => [item.challenge.id, item.mission.id]), [[11, 3], [12, 4]]);

  assert.equal(shouldOfferBonus({ mainDone: true, candidates }), true);
  assert.equal(shouldOfferBonus({ mainDone: false, candidates }), false);
  assert.equal(shouldOfferBonus({ mainDone: true, dueReminderCount: 1, candidates }), false);
  assert.equal(shouldOfferBonus({ mainDone: true, candidates, focusIsBonus: true }), false);
  assert.equal(shouldOfferBonus({ mainDone: true, candidates: [] }), false);
}

function runReminderTimeLeftSmoke() {
  const base = Date.parse("2026-10-19T10:00:00Z");
  assert.deepEqual(reminderTimeLeft(base + (2 * 60 + 10) * 60000, base), { state: "scheduled", hours: 2, minutes: 10 });
  assert.deepEqual(reminderTimeLeft(base + 45 * 60000, base), { state: "scheduled", hours: 0, minutes: 45 });
  assert.deepEqual(reminderTimeLeft(base + 30000, base), { state: "scheduled", hours: 0, minutes: 1 });
  assert.deepEqual(reminderTimeLeft(base + 3 * 3600000, base), { state: "scheduled", hours: 3, minutes: 0 });
  assert.equal(reminderTimeLeft(base, base).state, "due");
  assert.equal(reminderTimeLeft(base - 60000, base).state, "due");
  assert.equal(reminderTimeLeft(Number.POSITIVE_INFINITY, base).state, "unknown");
}

run();
