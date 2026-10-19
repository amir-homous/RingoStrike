import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";

import {
  LEGACY_CHALLENGE_ICON_IDS,
  challengeIconCandidates,
  challengeIconKey,
} from "../src/lib/challengeIconKeys.js";
import { localizeChallenge, localizeMission } from "../src/lib/ringoContentLocalization.js";
import {
  ROOM_BASE_WIDTH,
  ZONE_ORDER,
  cameraPan,
  cameraTarget,
  footprintBox,
  footprintClipPath,
  ringoPlacement,
  roomScale,
  slotForReward,
  zoneMarker,
  zoneObjects,
} from "../src/lib/roomScene.js";
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
  runRoomSceneSmoke();
  runRoomObjectsSmoke();

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

function roomLayout() {
  return JSON.parse(readFileSync(new URL("../src/assets/room/room_layout.json", import.meta.url), "utf8"));
}

function runRoomSceneSmoke() {
  const layout = roomLayout();
  assert.equal(layout.base.width, ROOM_BASE_WIDTH);

  // Integer scaling only.
  assert.equal(roomScale(0), 1);
  assert.equal(roomScale(479), 1);
  assert.equal(roomScale(959), 1);
  assert.equal(roomScale(960), 2);
  assert.equal(roomScale(1440), 3);
  // Height is a limit too: x3 needs 810px of height, else it falls back to x2.
  assert.equal(roomScale(1446, 766), 2);
  assert.equal(roomScale(1446, 810), 3);
  assert.equal(roomScale(1446, 200), 1);
  assert.equal(roomScale(966, null), 2);

  // Camera pan (x2 room = 960x540 in an 830px-wide viewport).
  const view = { viewportWidth: 830, viewportHeight: 540, scale: 2 };
  // Room fits vertically -> no vertical pan.
  assert.equal(cameraPan({ ...view, target: { x: 240, y: 135 } }).y, 0);
  // Centered on a point, snapped to whole base px (multiples of the scale).
  const centre = cameraPan({ ...view, target: { x: 240, y: 135 } });
  assert.equal(centre.x, -64);
  assert.equal(Math.abs(centre.x % 2), 0);
  // Clamped at the left edge (work desk) and the right edge (sleep corner): never past the room.
  const work = cameraPan({ ...view, target: cameraTarget(layout, "work_desk") });
  assert.equal(work.x, 0);
  const sleep = cameraPan({ ...view, target: cameraTarget(layout, "sleep_corner") });
  assert.equal(sleep.x, 830 - 960);
  // Odd viewport: snapping never reveals space past the room edge.
  const odd = cameraPan({ viewportWidth: 829, viewportHeight: 540, scale: 2, target: { x: 480, y: 0 } });
  assert.ok(odd.x <= 0 && odd.x + 960 >= 829 && Math.abs(odd.x % 2) === 0, `odd viewport ${odd.x}`);
  // Room fits -> no pan.
  assert.deepEqual(cameraPan({ viewportWidth: 1000, viewportHeight: 600, scale: 2, target: { x: 0, y: 0 } }), { x: 0, y: 0 });
  // Targets: zone camera rect, else Ringo A.
  assert.deepEqual(cameraTarget(layout, "creative_corner"), { x: 205, y: 39, w: 195, h: 135 });
  assert.deepEqual(cameraTarget(layout, ""), { x: 270, y: 214, w: 0, h: 0 });
  assert.deepEqual(cameraTarget(layout, "unknown"), { x: 270, y: 214, w: 0, h: 0 });

  // Every layout zone has a footprint, prop, marker and the PNG files the renderer needs.
  const roomDir = new URL("../src/assets/room/", import.meta.url);
  assert.deepEqual([...ZONE_ORDER].sort(), Object.keys(layout.zones).sort());
  for (const key of ZONE_ORDER) {
    const zone = layout.zones[key];
    const box = footprintBox(zone.footprint);
    assert.ok(box.w > 0 && box.h > 0, `${key} footprint`);
    assert.ok(existsSync(new URL(zone.prop.file, roomDir)), `${key} prop`);
    assert.ok(existsSync(new URL(zone.dim, roomDir)), `${key} dim`);
    assert.ok(existsSync(new URL(zone.light.file, roomDir)), `${key} light`);
  }
  for (const file of [layout.stage, layout.overlay, layout.markers.bell, layout.markers.bell_due]) {
    assert.ok(existsSync(new URL(file, roomDir)), file);
  }

  // clip-path is relative to the footprint box and scales with the room.
  const fp = layout.zones.work_desk.footprint;
  assert.deepEqual(footprintBox(fp), { x: 10, y: 60, w: 140, h: 110 });
  assert.equal(footprintClipPath(fp, 2), "polygon(0px 0px, 280px 0px, 280px 220px, 0px 220px)");

  // Markers: due wins over scheduled.
  assert.equal(zoneMarker({ dueReminderCount: 1, scheduledReminderCount: 2 }), "bell_due");
  assert.equal(zoneMarker({ scheduledReminderCount: 1 }), "bell");
  assert.equal(zoneMarker({}), "");

  // Ringo anchors bottom-center at safe position A; sleeping in rest.
  const idle = ringoPlacement(layout);
  assert.deepEqual(idle, { file: "ringo/ringo_idle.png", x: 270 - 17, y: 214 - 33, w: 34, h: 33 });
  assert.equal(ringoPlacement(layout, { rest: true }).file, "ringo/ringo_sleeping.png");
}

function runRoomObjectsSmoke() {
  const layout = roomLayout();
  const roomDir = new URL("../src/assets/room/", import.meta.url);
  const hasAsset = (path) => existsSync(new URL(path, roomDir));
  const creative = layout.zones.creative_corner;
  const reward = (key, slotKey, assetKey) => ({ key, slot_key: slotKey, asset_key: assetKey });
  const sketchbook = reward("creativity_sketchbook", "creative_corner_first_reward", "creativity_sketchbook");
  const lamp = reward("creativity_desk_lamp", "creative_corner_consistency", "creativity_desk_lamp");
  const easel = reward("creativity_easel_upgrade", "creative_corner_progress", "creativity_easel_upgrade");

  // The 10 v1 objects: first + consistency reward per zone, each with a PNG at its slot.
  for (const key of ZONE_ORDER) {
    for (const [slotKey, slot] of Object.entries(layout.zones[key].slots)) {
      assert.ok(hasAsset(`objects/${slot.asset_key}.png`), `${slotKey} PNG`);
    }
  }

  // Slot -> asset placement uses the layout slot position.
  assert.deepEqual(slotForReward(creative, sketchbook), { key: "creative_corner_first_reward", ...creative.slots.creative_corner_first_reward });
  // Fallback by asset_key when the reward's slot_key is not in the layout.
  assert.equal(slotForReward(creative, { asset_key: "creativity_desk_lamp", slot_key: "unknown" }).key, "creative_corner_consistency");
  assert.equal(slotForReward(creative, easel), null);

  // Fresh user: nothing placed, ghost = first locked reward with a PNG.
  let objects = zoneObjects(creative, { unlocked_objects: [], locked_preview_objects: [sketchbook, lamp, easel] }, hasAsset);
  assert.deepEqual(objects.placed, []);
  assert.equal(objects.ghost.assetKey, "creativity_sketchbook");
  assert.equal(objects.ghost.path, "objects/creativity_sketchbook.png");
  assert.equal(objects.ghost.x, creative.slots.creative_corner_first_reward.x);

  // First reward placed: it is drawn at its slot, and the ghost moves to the next reward with a PNG.
  objects = zoneObjects(creative, { unlocked_objects: [sketchbook], locked_preview_objects: [lamp, easel] }, hasAsset);
  assert.deepEqual(objects.placed.map((item) => [item.assetKey, item.x, item.y]), [["creativity_sketchbook", 308, 84]]);
  assert.equal(objects.ghost.assetKey, "creativity_desk_lamp");

  // Both v1 objects placed: no PNG left for later rewards, so no ghost.
  objects = zoneObjects(creative, { unlocked_objects: [sketchbook, lamp], locked_preview_objects: [easel] }, hasAsset);
  assert.equal(objects.placed.length, 2);
  assert.equal(objects.ghost, null);

  // Missing PNG -> not drawn (placed or ghost), even when the slot exists.
  const noLampPng = (path) => path !== "objects/creativity_desk_lamp.png" && hasAsset(path);
  objects = zoneObjects(creative, { unlocked_objects: [lamp], locked_preview_objects: [sketchbook] }, noLampPng);
  assert.deepEqual(objects.placed, []);
  assert.equal(objects.ghost.assetKey, "creativity_sketchbook");
  objects = zoneObjects(creative, { unlocked_objects: [sketchbook], locked_preview_objects: [lamp, easel] }, noLampPng);
  assert.equal(objects.ghost, null);

  // A ghost never sits on a slot that is already placed.
  objects = zoneObjects(creative, { unlocked_objects: [sketchbook], locked_preview_objects: [sketchbook] }, hasAsset);
  assert.equal(objects.ghost, null);
  assert.deepEqual(zoneObjects(creative, null, hasAsset), { placed: [], ghost: null });
}

run();
