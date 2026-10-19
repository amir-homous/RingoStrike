import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import en from "../src/i18n/locales/en.js";
import fa from "../src/i18n/locales/fa.js";
import {
  localizeSpaceReward,
  localizeSpaceZone,
  spacePathName,
} from "../src/lib/livingSpaceCopy.js";

import {
  getChallengeDisplayCopy,
  getMissionDisplayCopy,
  getPathDisplayCopy,
} from "../src/lib/missionDisplayCopy.js";
import {
  localizeChallenge,
  localizeMission,
  localizePath,
} from "../src/lib/ringoContentLocalization.js";

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function assertUnchanged(actual, expected, label) {
  assert.deepEqual(actual, expected, `${label} should not be mutated`);
}

function runMissionDisplayCopySmoke() {
  const tinyMission = {
    key: "move-10-tiny",
    title: "Move for 2 minutes",
    description: "Walk, stretch, or shake out tension for just two minutes.",
  };

  const persianTiny = getMissionDisplayCopy(tinyMission, "fa");
  assert.equal(persianTiny.found, true);
  assert.equal(persianTiny.title, "دو دقیقه حرکت کن");
  assert.match(persianTiny.description, /دو دقیقه/);

  const englishTiny = getMissionDisplayCopy(tinyMission, "en");
  assert.equal(englishTiny.found, true);
  assert.equal(englishTiny.title, "Move for 2 minutes");
  assert.equal(englishTiny.description, "Walk, stretch, or shake out tension for just two minutes.");

  for (const key of ["move-10-tiny", "move_10_tiny", "move/10/tiny"]) {
    assert.equal(
      getMissionDisplayCopy({ ...tinyMission, key }, "fa").title,
      "دو دقیقه حرکت کن",
      `${key} should resolve to seeded mission copy`,
    );
  }

  const customMission = {
    key: "custom-mission",
    title: "Custom backend title",
    description: "Custom backend description",
  };
  const customMissionBefore = clone(customMission);
  const customCopy = getMissionDisplayCopy(customMission, "fa");
  assert.equal(customCopy.found, false);
  assert.equal(customCopy.title, customMission.title);
  assert.equal(customCopy.description, customMission.description);
  assertUnchanged(customMission, customMissionBefore, "mission display copy fallback");

  assert.deepEqual(
    getMissionDisplayCopy(null, "fa"),
    { title: "", description: "", found: false },
  );
  assert.deepEqual(
    getMissionDisplayCopy({}, "fa"),
    { title: "", description: "", found: false },
  );
}

function runPathChallengeDisplayCopySmoke() {
  const path = {
    key: "fitness",
    title: "Fitness",
    description: "Build energy and body momentum through small movement missions.",
  };
  const pathBefore = clone(path);
  const persianPath = getPathDisplayCopy(path, "fa");
  assert.equal(persianPath.found, true);
  assert.equal(persianPath.title, "بدن و حرکت");
  assert.match(persianPath.description, /مأموریت‌های کوچک/);
  assert.equal(getPathDisplayCopy(path, "en").title, "Fitness");
  assertUnchanged(path, pathBefore, "path display copy");

  const challenge = {
    name: "Move Your Body",
    description: "Create physical momentum with a daily walk, workout, stretch, or movement session.",
    ringo_intro: "Start small. One movement session is enough to protect today's rhythm.",
  };
  const challengeBefore = clone(challenge);
  const persianChallenge = getChallengeDisplayCopy(challenge, "fa");
  assert.equal(persianChallenge.found, true);
  assert.equal(persianChallenge.name, "حرکت روزانه");
  assert.match(persianChallenge.ringo_intro, /کوچک شروع کن/);
  assert.equal(getChallengeDisplayCopy({ slug: "move-your-body" }, "fa").name, "حرکت روزانه");
  assert.equal(getChallengeDisplayCopy(challenge, "en").name, "Move Your Body");
  assertUnchanged(challenge, challengeBefore, "challenge display copy");

  const customPath = {
    key: "custom-path",
    title: "Custom Path",
    description: "Backend path text",
  };
  assert.deepEqual(
    getPathDisplayCopy(customPath, "fa"),
    { title: "Custom Path", description: "Backend path text", found: false },
  );

  const customChallenge = {
    name: "Custom Challenge",
    description: "Backend challenge text",
    ringo_intro: "Backend Ringo text",
  };
  assert.deepEqual(
    getChallengeDisplayCopy(customChallenge, "fa"),
    {
      name: "Custom Challenge",
      description: "Backend challenge text",
      ringo_intro: "Backend Ringo text",
      found: false,
    },
  );
}

function runRingoContentLocalizationSmoke() {
  const mainMission = {
    key: "move-10",
    title: "Move for 10 minutes",
    description: "Walk, stretch, or do a light workout for ten minutes.",
    challenge_name: "Move Your Body",
    path_title: "Fitness",
  };
  const mainMissionBefore = clone(mainMission);
  const localizedMission = localizeMission(mainMission, "fa");
  assert.equal(localizedMission.title, "ده دقیقه حرکت کن");
  assert.equal(localizedMission.challenge_name, "حرکت روزانه");
  assert.equal(localizedMission.path_title, "بدن و حرکت");
  assertUnchanged(mainMission, mainMissionBefore, "localized mission source");

  const challenge = {
    name: "Strength Starter",
    description: "Begin a simple strength rhythm with light bodyweight work.",
    missions: [
      {
        key: "bodyweight-set-tiny",
        title: "Do three honest reps",
        description: "Do three calm reps of any bodyweight movement.",
      },
    ],
  };
  const challengeBefore = clone(challenge);
  const localizedChallenge = localizeChallenge(challenge, "fa");
  assert.equal(localizedChallenge.name, "شروع قدرت");
  assert.equal(localizedChallenge.missions[0].title, "سه تکرار واقعی انجام بده");
  assertUnchanged(challenge, challengeBefore, "localized challenge source");

  const path = {
    key: "sleep",
    title: "Sleep",
    description: "Create calmer nights and better recovery through small reset missions.",
  };
  const pathBefore = clone(path);
  const localizedPath = localizePath(path, "fa");
  assert.equal(localizedPath.title, "استراحت و انرژی");
  assertUnchanged(path, pathBefore, "localized path source");

  const customMission = {
    key: "custom",
    title: "Custom Mission",
    description: "Custom description",
  };
  assert.equal(localizeMission(customMission, "fa"), customMission);
  assert.equal(localizeMission(customMission, "en"), customMission);
}

runMissionDisplayCopySmoke();
runPathChallengeDisplayCopySmoke();
runRingoContentLocalizationSmoke();

function createTranslator(catalog) {
  const lookup = (key) => key.split(".").reduce((node, part) => node?.[part], catalog);

  return {
    t: (key) => lookup(key),
    te: (key) => typeof lookup(key) === "string",
  };
}

function backendLivingSpaceKeys() {
  const source = readFileSync(
    new URL("../../backend/services/living_space_service.py", import.meta.url),
    "utf8",
  );
  const rewards = [...source.matchAll(/^\s*\("(\w+)", "(\w+)", "(\w+)", "([^"]+)", "([^"]+)"/gm)]
    .map(([, pathKey, zoneKey, key, title, description]) => ({ pathKey, zoneKey, key, title, description }));
  const zones = [...source.matchAll(/^\s*\("(\w+)", "(\w+)", "([^"]+)"\),$/gm)]
    .map(([, pathKey, zoneKey, title]) => ({ pathKey, zoneKey, title }));

  return { rewards, zones };
}

function runLivingSpaceRoomCopySmoke() {
  const { rewards, zones } = backendLivingSpaceKeys();
  assert.equal(zones.length, 5);
  assert.equal(rewards.length, 25);

  const english = createTranslator(en);
  const persian = createTranslator(fa);
  const latin = /[A-Za-z]/;

  for (const zone of zones) {
    const backendZone = {
      path_key: zone.pathKey,
      zone_key: zone.zoneKey,
      title: zone.title,
      unlocked_objects: [],
      locked_preview_objects: rewards
        .filter((reward) => reward.zoneKey === zone.zoneKey)
        .map((reward) => ({ key: reward.key, title: reward.title, description: reward.description })),
      next_reward: null,
    };
    const before = clone(backendZone);

    const faZone = localizeSpaceZone(backendZone, persian.t, persian.te);
    assert.doesNotMatch(faZone.title, latin, `${zone.zoneKey} zone title in FA`);
    assert.doesNotMatch(faZone.pathName, latin, `${zone.pathKey} path name in FA`);
    for (const reward of faZone.locked_preview_objects) {
      assert.doesNotMatch(reward.title, latin, `${reward.key} title in FA`);
      assert.doesNotMatch(reward.description, latin, `${reward.key} description in FA`);
    }

    const enZone = localizeSpaceZone(backendZone, english.t, english.te);
    assert.equal(enZone.title, zone.title);
    enZone.locked_preview_objects.forEach((reward, index) => {
      assert.equal(reward.title, backendZone.locked_preview_objects[index].title);
      // B10 rewrote some EN descriptions in i18n (first rewards, path renames); EN shows the catalog text.
      assert.equal(reward.description, en.space.roomObjects[reward.key]?.description ?? backendZone.locked_preview_objects[index].description);
    });

    assertUnchanged(backendZone, before, "localized zone source");
  }

  assert.equal(spacePathName("career", persian.t, persian.te), "کار و حرفه");
  assert.equal(spacePathName("unknown_path", persian.t, persian.te), "unknown_path");

  const unknownReward = { key: "future_reward", title: "Future Reward", description: "Later." };
  assert.deepEqual(localizeSpaceReward(unknownReward, persian.t, persian.te), unknownReward);
  assert.equal(localizeSpaceReward(null, persian.t, persian.te), null);
}

runLivingSpaceRoomCopySmoke();

// B10 copy pass (docs/product/B10_COPY_PROPOSAL.md): keys in both locales, Persian digits in FA,
// EN plurals for 1 and 2, backend English never shown in FA, no streak words in FA.
async function runB10CopySmoke() {
  const { createI18n } = await import("vue-i18n");
  const { formatNumber, numberAwareT } = await import("../src/lib/i18nNumbers.js");
  const { BACKEND_STEP_COPY, localizeBackendCopy } = await import("../src/lib/backendStepCopy.js");
  const i18n = createI18n({ legacy: false, locale: "en", fallbackLocale: "en", messages: { en, fa }, missingWarn: false, fallbackWarn: false });
  const g = i18n.global;
  const has = (catalog, key) => typeof key.split(".").reduce((node, part) => node?.[part], catalog) === "string";
  const tFor = (locale) => {
    const t = (key, named, plural) => (plural === undefined ? g.t(key, named, { locale }) : g.t(key, named, { locale, plural }));
    return numberAwareT(t, () => locale);
  };
  const en_ = tFor("en");
  const fa_ = tFor("fa");

  // Every key the proposal changes or adds exists in both locales.
  const proposal = readFileSync(new URL("../../docs/product/B10_COPY_PROPOSAL.md", import.meta.url), "utf8");
  const keys = [...proposal.matchAll(/^\| `([a-zA-Z][\w.]+)` \|/gm)].map(([, key]) => key);
  assert.ok(keys.length > 100, `proposal keys: ${keys.length}`);
  for (const key of keys) {
    assert.ok(has(en, key), `EN missing ${key}`);
    assert.ok(has(fa, key), `FA missing ${key}`);
  }
  for (const key of ["common.countOf", "common.percent", "common.listSeparator", "common.labelSeparator", "common.arrowForward"]) {
    assert.ok(has(en, key) && has(fa, key), key);
  }

  // No streak words left in FA; path names are the new ones.
  assert.doesNotMatch(JSON.stringify(fa), /استریک|استرایک/);
  assert.equal(fa.pathContent.sleep.title, "استراحت و انرژی");
  assert.equal(en.pathContent.sleep.title, "Rest & Energy");
  assert.equal(fa.onboarding.paths.career.label, fa.pathContent.career.title);

  // Digits: Persian in FA, Latin in EN, through the one formatter.
  assert.equal(formatNumber(1234, "fa"), "۱٬۲۳۴");
  assert.equal(formatNumber(20, "en"), "20");
  assert.equal(fa_("common.countOf", { done: 2, total: 5 }), "۲ از ۵");
  assert.equal(en_("common.countOf", { done: 2, total: 5 }), "2/5");
  assert.equal(fa_("common.percent", { value: 40 }), "۴۰٪");
  assert.equal(fa_("ringoRewardSequence.local.xpValue", { count: 20 }), "+۲۰ XP");
  assert.equal(fa_("common.arrowForward"), "←");
  for (const [key, named] of [
    ["space.objects", { count: 3 }],
    ["space.room.remindersValue", { due: 1, scheduled: 2 }],
    ["space.shell.minutes", { count: 15 }],
    ["space.panel.missionBody", { minutes: 10 }],
    ["ringoRewardSequence.staged.streakValue", { count: 4 }],
    ["space.overview.progressText", { count: 2 }],
  ]) {
    assert.doesNotMatch(fa_(key, named), /[0-9]/, `${key} has Latin digits in FA`);
  }

  // EN plurals: singular for 1, plural for 2.
  const plurals = {
    "space.objects": ["1 object", "2 objects"],
    "ringoRewardSequence.staged.streakValue": ["1 day in a row", "2 days in a row"],
    "space.shell.restReminderDue": ["1 reminder waiting", "2 reminders waiting"],
    "space.shell.restReminderFuture": ["1 reminder later today", "2 reminders later today"],
    "space.panel.futureMissions": ["Later in this challenge: 1 more mission", "Later in this challenge: 2 more missions"],
    "space.overview.progressText": ["1 object in your room, all from real progress.", "2 objects in your room, all from real progress."],
    "space.shell.unlocksInDays": ["Opens in 1 day if you keep this challenge going.", "Opens in 2 days if you keep this challenge going."],
  };
  for (const [key, [one, two]] of Object.entries(plurals)) {
    assert.equal(en_(key, { count: 1 }), one, key);
    assert.equal(en_(key, { count: 2 }), two, key);
  }
  assert.equal(en_("space.scene.objectsPlaced", { count: 1 }), "1 object placed");
  assert.equal(en_("space.scene.objectsPlaced", { count: 2 }), "2 objects placed");
  assert.equal(fa_("space.scene.objectsPlaced", { count: 1 }), "۱ شیء جا گرفته");

  // Backend English: every mapped sentence has EN and FA keys; an unmapped one never shows in FA.
  for (const [sentence, key] of Object.entries(BACKEND_STEP_COPY)) {
    assert.ok(has(en, key), `EN missing ${key} (${sentence})`);
    assert.ok(has(fa, key), `FA missing ${key} (${sentence})`);
    assert.notEqual(fa_(key), sentence);
  }
  const faTranslate = Object.assign(fa_, { locale: "fa" });
  const enTranslate = Object.assign(en_, { locale: "en" });
  assert.equal(localizeBackendCopy("Today is safe.", faTranslate), fa.ringoRewardSequence.backend.todaySafeTitle);
  assert.equal(localizeBackendCopy("A brand new backend line.", faTranslate, { role: "title" }), fa.ringoRewardSequence.fallbackTitle);
  assert.equal(localizeBackendCopy("A brand new backend line.", faTranslate), "");
  assert.equal(localizeBackendCopy("A brand new backend line.", enTranslate), "A brand new backend line.");
}

await runB10CopySmoke();
console.log("B10 copy smoke test passed.");
