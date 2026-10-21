import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";

import {
  LEGACY_CHALLENGE_ICON_IDS,
  challengeIconCandidates,
  challengeIconKey,
} from "../src/lib/challengeIconKeys.js";
import { localizeChallenge, localizeMission } from "../src/lib/ringoContentLocalization.js";
import {
  ROOM_BASE_HEIGHT,
  ROOM_BASE_WIDTH,
  ZONE_ORDER,
  cameraPan,
  cameraTarget,
  footprintBox,
  footprintClipPath,
  ringoPlacement,
  roomScale,
  roomFit,
  FRACTIONAL_SNAP,
  safeArea,
  safeAreaPanY,
  slotForReward,
  zoneObjects,
  pixelIconScale,
} from "../src/lib/roomScene.js";
import {
  EARLIER_SLOTS,
  buildContext,
  clampDuration,
  localTimeToday,
  performedAtWindow,
  readFocusStart,
  readLastPlace,
  slotEnabled,
  slotPerformedAt,
  writeFocusStart,
} from "../src/lib/missionActionFlow.js";
import { formatClock } from "../src/lib/i18nNumbers.js";
import {
  REMINDER_CHIP,
  pathMarkerColor,
  pathMarkerState,
  reminderChip,
  ringSegments,
  telegramReady,
} from "../src/lib/pathMarker.js";
import {
  BACKFILL_SOURCE,
  MATERIALIZE_TOTAL_MS,
  createMaterializeQueue,
  materializeCandidates,
  materializePhaseAt,
  materializeTimeline,
} from "../src/lib/roomMaterialize.js";
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
  runMaterializeSmoke();
  runMissionActionSmoke();

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

  // Hybrid scale: the integer below the fit, or the fit itself when its fraction is >= 0.85.
  assert.equal(FRACTIONAL_SNAP, 0.85);
  assert.equal(roomScale(0), 1);
  assert.equal(roomScale(479), 1);
  assert.equal(roomScale(840), 1); // fit 1.75
  assert.equal(roomScale(887), 1); // fit 1.848
  assert.equal(roomScale(888), 1.85); // fit 1.85
  assert.equal(roomScale(959), 1.99);
  assert.equal(roomScale(960), 2);
  assert.equal(roomScale(1300), 2); // fit 2.708
  assert.equal(roomScale(1440), 3);
  // Height is a limit too: x3 needs 810px of height; 1920x940 gives fit 2.93 -> fractional.
  assert.equal(roomScale(1446, 766), 2); // fit 2.837
  assert.equal(roomScale(1446, 780), 2.88);
  assert.equal(roomScale(1446, 810), 3);
  assert.equal(roomScale(1446, 200), 1);
  assert.equal(roomScale(966, null), 2);
  assert.equal(roomScale(1446, 791), 2.92); // floor to 1/100: 791 / 270 = 2.9296
  assert.ok(Math.abs(roomFit(1446, 791) - 791 / 270) < 1e-9);
  // A fractional scale never makes the room wider or taller than the space it was fitted to.
  for (const [w, h] of [[1406, 940], [1446, 791], [959, 1000], [1919, 1079]]) {
    const scale = roomScale(w, h);
    assert.ok(ROOM_BASE_WIDTH * scale <= w + 1e-9 && ROOM_BASE_HEIGHT * scale <= h + 1e-9, `${w}x${h}`);
  }

  // B22 safe area: base y 10..252 must stay visible; the fit uses its height (242).
  const safe = safeArea(layout);
  assert.deepEqual(safe, { y0: 10, y1: 252, h: 242 });
  assert.deepEqual(safeArea({}), { y0: 0, y1: ROOM_BASE_HEIGHT, h: ROOM_BASE_HEIGHT });
  assert.equal(roomScale(1460, 791), 2.92); // full height: x2.92 at 1920x940
  assert.equal(roomScale(1460, 791, safe.h), 3); // safe-area height: x3
  assert.equal(roomScale(1460, 701, safe.h), 2.89); // 701 / 242 = 2.896 -> fractional
  assert.equal(roomScale(Number.POSITIVE_INFINITY, 380, safe.h), 1); // phone room height
  for (const [view, s] of [[791, 3], [726, 3], [701, 2.89], [484, 2], [242, 1], [810, 3], [1000, 3]]) {
    const y = safeAreaPanY({ viewportHeight: view, scale: s, safe });
    const top = -y / s;
    assert.ok(y <= 0, `pan y ${y}`);
    if (view < ROOM_BASE_HEIGHT * s) {
      assert.ok(top <= safe.y0 + 1e-9 && top + view / s >= safe.y1 - 1e-9, `safe area visible at ${view}/x${s}: top ${top}`);
      assert.ok(Math.abs(top - Math.round(top)) < 1e-9, "whole base px");
    } else {
      assert.equal(y, 0);
    }
  }

  const fractionalPan = cameraPan({ viewportWidth: 1000, viewportHeight: 791, scale: 2.92, target: cameraTarget(layout, "sleep_corner") });
  assert.ok(fractionalPan.x < 0);
  assert.ok(Math.abs(fractionalPan.x / 2.92 - Math.round(fractionalPan.x / 2.92)) < 1e-9);
  assert.ok(fractionalPan.x >= 1000 - ROOM_BASE_WIDTH * 2.92 - 1e-9);

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
  for (const file of [layout.stage, layout.overlay, layout.markers.glint]) {
    assert.ok(existsSync(new URL(file, roomDir)), file);
  }

  // clip-path is relative to the footprint box and scales with the room.
  const fp = layout.zones.work_desk.footprint;
  assert.deepEqual(footprintBox(fp), { x: 10, y: 60, w: 140, h: 110 });
  assert.equal(footprintClipPath(fp, 2), "polygon(0px 0px, 280px 0px, 280px 220px, 0px 220px)");

  // B30 S1: every zone has a path_marker anchor (new key, not the old bell "marker") and a reserved tray.
  const pathMarkerAnchors = {
    work_desk: [78, 46],
    learning_corner: [160, 47],
    creative_corner: [311, 46],
    sleep_corner: [398, 47],
    fitness_corner: [78, 174],
  };
  for (const key of ZONE_ORDER) {
    assert.deepEqual(layout.zones[key].path_marker, pathMarkerAnchors[key], `${key} path_marker`);
    assert.ok("tray" in layout.zones[key], `${key} tray reserved`);
  }

  testPathMarkerState();

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

  // B21: an unlocked reward still waiting to materialize is the zone's ghost, not placed.
  objects = zoneObjects(creative, { unlocked_objects: [sketchbook], locked_preview_objects: [lamp, easel] }, hasAsset, { pendingKeys: [sketchbook.key] });
  assert.deepEqual(objects.placed, []);
  assert.equal(objects.ghost.key, sketchbook.key);
  objects = zoneObjects(creative, { unlocked_objects: [sketchbook, lamp], locked_preview_objects: [easel] }, hasAsset, { pendingKeys: [lamp.key] });
  assert.deepEqual(objects.placed.map((item) => item.key), [sketchbook.key]);
  assert.equal(objects.ghost.key, lamp.key);
}

function runMaterializeSmoke() {
  // Sequence (spec §6): light 300, resolve 600, settle 200, glint 500 = 1.6 s, then placed.
  const timeline = materializeTimeline();
  assert.deepEqual(timeline.map((step) => [step.name, step.at, step.ms]), [
    ["light", 0, 300],
    ["resolve", 300, 600],
    ["settle", 900, 200],
    ["glint", 1100, 500],
  ]);
  assert.equal(MATERIALIZE_TOTAL_MS, 1600);
  assert.equal(materializePhaseAt(0, timeline), "light");
  assert.equal(materializePhaseAt(299, timeline), "light");
  assert.equal(materializePhaseAt(300, timeline), "resolve");
  assert.equal(materializePhaseAt(1000, timeline), "settle");
  assert.equal(materializePhaseAt(1599, timeline), "glint");
  assert.equal(materializePhaseAt(1600, timeline), "placed");
  // Reduced motion: no steps, the placed state at once.
  assert.deepEqual(materializeTimeline({ reducedMotion: true }), []);
  assert.equal(materializePhaseAt(0, materializeTimeline({ reducedMotion: true })), "placed");

  // Candidates: unlocked, unseen, not backfilled; oldest unlock first.
  const reward = (key, extra = {}) => ({ id: key.length, key, zone_key: "creative_corner", unlocked: true, is_seen: false, source_type: "mission_reward", unlocked_at: "2026-10-19 10:00:00", ...extra });
  const rewards = [
    reward("late", { unlocked_at: "2026-10-19 12:00:00" }),
    reward("early", { unlocked_at: "2026-10-19 09:00:00" }),
    reward("seen", { is_seen: true }),
    reward("backfilled", { source_type: BACKFILL_SOURCE, is_seen: false }),
    reward("locked", { unlocked: false, unlocked_at: null }),
  ];
  assert.deepEqual(materializeCandidates(rewards).map((item) => item.key), ["early", "late"]);
  assert.deepEqual(materializeCandidates([]), []);

  // Once only: a key that was queued is never queued again (reloads, repeated events).
  const queue = createMaterializeQueue();
  assert.deepEqual(queue.enqueue(materializeCandidates(rewards)), ["early", "late"]);
  assert.deepEqual(queue.enqueue([reward("early"), reward("late")]), []);
  assert.deepEqual(queue.enqueue([reward("backfilled", { source_type: BACKFILL_SOURCE })]), []);
  assert.equal(queue.next().key, "early");
  queue.done("early");
  assert.deepEqual(queue.pendingKeys(), ["late"]);
  assert.deepEqual(queue.enqueue([reward("early")]), [], "played rewards never queue again");
  queue.done("late");
  assert.equal(queue.next(), null);
  assert.equal(queue.size(), 0);

  // Reward card: integer scale to fit the 66px icon box, never below 1.
  assert.equal(pixelIconScale(27, 16, 66), 2);
  assert.equal(pixelIconScale(23, 33, 66), 2);
  assert.equal(pixelIconScale(60, 11, 66), 1);
  assert.equal(pixelIconScale(13, 10, 66), 5);
  assert.equal(pixelIconScale(200, 100, 66), 1);
  assert.equal(pixelIconScale(0, 0, 66), 1);
}

function runMissionActionSmoke() {
  // Only the chosen fields are sent; {} is a valid save.
  assert.deepEqual(buildContext({}), {});
  assert.deepEqual(buildContext({ mode: "now", durationSeconds: 125.4 }), { mode: "now", duration_seconds: 125 });
  assert.deepEqual(buildContext({ mode: "now", durationSeconds: 0 }), { mode: "now", duration_seconds: 1 });
  assert.deepEqual(buildContext({ mode: "now", durationSeconds: 999999 }), { mode: "now", duration_seconds: 86400 });
  assert.deepEqual(buildContext({ mode: "earlier", durationSeconds: 60 }), { mode: "earlier" });
  assert.deepEqual(
    buildContext({ mode: "earlier", performedAt: "2026-10-20T08:00:00Z", place: "other", placeLabel: "  " + "x".repeat(50), feeling: "hard_but_done", note: "  hi  " }),
    { mode: "earlier", performed_at: "2026-10-20T08:00:00Z", place_key: "other", place_label: "x".repeat(40), feeling_key: "hard_but_done", note: "hi" },
  );
  assert.deepEqual(buildContext({ mode: "now", durationSeconds: 5, place: "home", placeLabel: "ignored", feeling: "happy" }), { mode: "now", duration_seconds: 5, place_key: "home" });
  assert.equal(clampDuration(-3), 1);

  // The time window comes from the server's ringo day; chips outside it are disabled.
  const ringoDay = { next_reset_at: "2026-10-21T00:00:00Z", server_now: "2026-10-20T15:00:00Z" };
  const window = performedAtWindow(ringoDay, { fetchedAt: 1000, clientNow: 1000 });
  assert.equal(window.start, Date.parse("2026-10-20T00:00:00Z"));
  assert.equal(window.end, Date.parse("2026-10-20T15:00:00Z"));
  assert.equal(performedAtWindow(ringoDay, { fetchedAt: 1000, clientNow: 61000 }).end, Date.parse("2026-10-20T15:01:00Z"));
  assert.equal(performedAtWindow(null), null);
  const base = new Date(Date.parse("2026-10-20T15:00:00Z"));
  const inside = (hhmm) => { const t = localTimeToday(hhmm, base); return t >= window.start && t <= window.end; };
  for (const slot of Object.keys(EARLIER_SLOTS)) {
    assert.equal(slotEnabled(slot, { window, base }), inside(EARLIER_SLOTS[slot]), slot);
    const value = slotPerformedAt(slot, { window, base });
    assert.equal(Boolean(value), inside(EARLIER_SLOTS[slot]), slot);
    if (value) assert.match(value, /^\d{4}-\d\d-\d\dT\d\d:\d\d:00Z$/);
  }
  assert.equal(slotEnabled("exact", { window }), true);
  assert.equal(slotEnabled("exact", { window: null }), false);
  assert.equal(slotPerformedAt("exact", { exactTime: "25:00", window, base }), null);
  assert.equal(localTimeToday("9:5"), null);

  // Storage is guarded: no window/storage in Node, so reads are null and writes do not throw.
  assert.equal(readFocusStart("user:1", 7), null);
  writeFocusStart("user:1", 7, Date.now());
  assert.equal(readLastPlace("user:1", "creativity"), null);

  // Count-up clock in the locale's digits.
  assert.equal(formatClock(65, "en"), "01:05");
  assert.equal(formatClock(3725, "en"), "1:02:05");
  assert.equal(formatClock(65, "fa"), "۰۱:۰۵");
}

// B30: path marker state, daily (D44): ring segments, grey/coloured rule, lit, badge, reminder chip.
function testPathMarkerState() {
  const color = "#4ade80";
  // A joined challenge; totalCheckins (Day N) must not affect the daily marker.
  const joined = (todayChecked = false, totalCheckins = 0) => ({ isJoined: true, totalCheckins, todayChecked });
  const open = { isJoined: false, totalCheckins: 0, todayChecked: false };

  // 0 joined: grey dashed ring, no segments, neutral, no badge.
  const none = pathMarkerState({ challenges: [open, open], color });
  assert.deepEqual(none.segments, []);
  assert.equal(none.empty, true);
  assert.equal(none.coloured, false);
  assert.equal(none.color, "");
  assert.equal(none.allDoneToday, false);
  assert.equal(none.lit, false);

  // 1 joined, nothing done today: one empty segment, grey, no glow.
  const one = pathMarkerState({ challenges: [joined(), open], color });
  assert.deepEqual(one.segments, [{ done: false }]);
  assert.equal(one.coloured, false);
  assert.equal(one.lit, false);
  assert.equal(one.allDoneToday, false);

  // Done on earlier days only (total_checkins > 0, not today): still grey, no badge. The day reset.
  const yesterdayOnly = pathMarkerState({ challenges: [joined(false, 5), joined(false, 1)], color });
  assert.deepEqual(yesterdayOnly.segments, [{ done: false }, { done: false }]);
  assert.equal(yesterdayOnly.coloured, false);
  assert.equal(yesterdayOnly.color, "");
  assert.equal(yesterdayOnly.lit, false);
  assert.equal(yesterdayOnly.allDoneToday, false);

  // 3 joined, 2 done today: done segments first, path colour, glow, no badge.
  const twoOfThree = pathMarkerState({ challenges: [joined(false, 9), joined(true, 3), joined(true, 1)], color });
  assert.deepEqual(twoOfThree.segments, [{ done: true }, { done: true }, { done: false }]);
  assert.equal(twoOfThree.joined, 3);
  assert.equal(twoOfThree.doneToday, 2);
  assert.equal(twoOfThree.coloured, true);
  assert.equal(twoOfThree.color, color);
  assert.equal(twoOfThree.lit, true);
  assert.equal(twoOfThree.allDoneToday, false);

  // 3 of 3 done today: check badge.
  const all = pathMarkerState({ challenges: [joined(true, 1), joined(true, 2), joined(true, 5)], color });
  assert.equal(all.allDoneToday, true);
  assert.equal(all.doneToday, 3);

  // Joining one more adds an empty segment; today's filled segments stay.
  const grown = pathMarkerState({ challenges: [joined(true), joined(true), joined(true), joined()], color });
  assert.equal(grown.segments.filter((segment) => segment.done).length, 3);
  assert.equal(grown.segments.length, 4);
  assert.equal(grown.allDoneToday, false);

  // A not-joined challenge never fills a segment. Raw API shape works too.
  assert.equal(pathMarkerState({ challenges: [{ isJoined: false, todayChecked: true }], color }).lit, false);
  const raw = pathMarkerState({ challenges: [{ is_joined: 1, total_checkins: 2, today_checked: true }], color });
  assert.equal(raw.doneToday, 1);
  assert.equal(raw.lit, true);
  assert.equal(raw.coloured, true);
  assert.equal(raw.allDoneToday, true);

  // Colour only from a valid hex paths.color; otherwise neutral even when done today.
  assert.equal(pathMarkerColor("#6EE5FF"), "#6EE5FF");
  assert.equal(pathMarkerColor("#abc"), "#abc");
  assert.equal(pathMarkerColor("red; background:url(x)"), "");
  assert.equal(pathMarkerState({ challenges: [joined(true)], color: "" }).coloured, false);

  // Telegram readiness: connected and reminders on; unknown settings stay null.
  assert.equal(telegramReady({ connected: true, reminders_enabled: true }), true);
  assert.equal(telegramReady({ connected: true, reminders_enabled: false }), false);
  assert.equal(telegramReady({ connected: false, reminders_enabled: true }), false);
  assert.equal(telegramReady(null), null);

  // Reminder chip precedence: due > Telegram not connected > set; one chip per zone.
  assert.equal(reminderChip({ dueCount: 1, scheduledCount: 2, telegram: false }), REMINDER_CHIP.DUE);
  assert.equal(reminderChip({ dueCount: 1, telegram: true }), REMINDER_CHIP.DUE);
  assert.equal(reminderChip({ scheduledCount: 1, telegram: false }), REMINDER_CHIP.TELEGRAM_OFF);
  assert.equal(reminderChip({ scheduledCount: 1, telegram: true }), REMINDER_CHIP.SET);
  assert.equal(reminderChip({ scheduledCount: 1, telegram: null }), REMINDER_CHIP.SET);
  assert.equal(reminderChip({ telegram: false }), "");
  assert.equal(reminderChip({}), "");
  assert.equal(pathMarkerState({ challenges: [], scheduledCount: 1, telegram: false }).reminder, REMINDER_CHIP.TELEGRAM_OFF);

  // Ring geometry: one arc per segment starting at the top; a single segment is a closed ring.
  assert.deepEqual(ringSegments(0, 10), []);
  const circumference = 2 * Math.PI * 10;
  const [single] = ringSegments(1, 10);
  assert.equal(single.dasharray, `${Math.round(circumference * 100) / 100} 0`);
  assert.equal(single.dashoffset, Math.round((circumference / 4) * 100) / 100);
  const three = ringSegments(3, 10);
  assert.equal(three.length, 3);
  assert.ok(three.every((segment) => Number(segment.dasharray.split(" ")[0]) > 0));
}

run();
