import assert from "node:assert/strict";

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
  assert.equal(persianPath.title, "تناسب و انرژی");
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
  assert.equal(localizedMission.path_title, "تناسب و انرژی");
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
  assert.equal(localizedPath.title, "آرامش و خواب");
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
