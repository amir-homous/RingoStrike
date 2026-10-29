import assert from "node:assert/strict";
import { createI18n } from "vue-i18n";
import en from "../src/i18n/locales/en.js";
import fa from "../src/i18n/locales/fa.js";
import { numberAwareT } from "../src/lib/i18nNumbers.js";

// EN copy says "1 minute", "1 day", "1 reminder" (never "1 minutes"). The plural comes from the
// existing mechanism: a numeric `count` picks the form, other params pass the number as the plural
// argument. Persian keeps one form.
const i18n = createI18n({ legacy: false, locale: "en", fallbackLocale: "en", messages: { en, fa } });
const g = i18n.global;
const tFor = (locale) => { g.locale.value = locale; return numberAwareT(g.t, () => locale); };

const cases = [
  // [key, params(n), plural argument(n) or null when `count` drives it, singular, plural]
  ["common.days", (n) => ({ count: n }), null, "1 day", "3 days"],
  ["space.panel.missionBody", (n) => ({ minutes: n }), (n) => n, "1 minute is enough.", "25 minutes is enough."],
  ["space.panel.firstStepBody", (n) => ({ minutes: n }), (n) => n, "1 minute is plenty.", "25 minutes is plenty."],
  ["space.scene.pathMarker.doneToday", (n) => ({ done: 0, joined: n }), (n) => n, "0 of 1 challenge done today", "0 of 3 challenges done today"],
  ["space.progressStatus", (n) => ({ count: n }), null, "1 object is now saved", "3 objects are now saved"],
  ["space.historyStatus", (n) => ({ count: n }), null, "1 object is saved", "3 objects are saved"],
  ["space.shell.pathProgressCount", (n) => ({ done: 0, total: n }), (n) => n, "0 of 1 step", "0 of 3 steps"],
  ["space.shell.missionCount", (n) => ({ count: n }), null, "1 mission", "3 missions"],
  ["pathsPage.challengeMissionProgress", (n) => ({ done: 0, total: n }), (n) => n, "0/1 mission today", "0/3 missions today"],
  ["pathsPage.unlocksInDays", (n) => ({ count: n }), null, "Unlocks in 1 day", "Unlocks in 3 days"],
  ["pathsPage.coach.continueToday", (n) => ({ done: 1, total: n }), (n) => n, "1/1 mission today", "1/3 missions today"],
  ["pathsPage.pathCard.continueHint", (n) => ({ done: 0, total: n }), (n) => n, "0/1 mission left", "0/3 missions left"],
  ["missions.planRemindersNotice", (n) => ({ count: n }), null, "planned 1 reminder for", "planned 3 reminders for"],
  ["missions.futureReminderQueue", (n) => ({ count: n }), null, "1 reminder waiting", "3 reminders waiting"],
  ["missions.optionalExplorerList.reminderCount", (n) => ({ count: n }), null, "1 reminder waiting", "3 reminders waiting"],
  ["missions.narrative.optionalPathFutureReminders", (n) => ({ count: n }), null, "1 reminder is saved", "3 reminders are saved"],
  ["missions.narrative.optionalChallengeFutureReminders", (n) => ({ count: n }), null, "1 reminder is waiting", "3 reminders are waiting"],
  ["rewardMoment.mission.othersBefore", (n) => ({ count: n, total: n + 1 }), null, "1 person secured", "3 people secured"],
  ["onboarding.suggestion.cardLine", (n) => ({ days: n, line: "x" }), (n) => n, "1 day · x", "14 days · x"],
  ["guidedFeatures.unlockAfter", (n) => ({ count: n }), null, "Unlocks after 1 check-in", "Unlocks after 3 check-ins"],
  ["dashboard.manyWaiting", (n) => ({ count: n }), null, "1 path is waiting", "3 paths are waiting"],
  ["dashboard.mission.streakValue", (n) => ({ count: n }), null, "1 day", "3 days"],
  ["enrollment.unlocksInDays", (n) => ({ count: n }), null, "Unlocks in 1 day", "Unlocks in 3 days"],
  ["enrollment.checkedDays", (n) => ({ checked: 0, total: n }), (n) => n, "0 / 1 day", "0 / 3 days"],
  ["progress.compactReminders", (n) => ({ count: n }), null, "1 reminder waiting", "3 reminders waiting"],
  ["profileComponents.cellTitle", (n) => ({ date: "d", count: n }), null, "d: 1 check-in", "d: 3 check-ins"],
];

for (const [key, params, plural, singular, pluralText] of cases) {
  const n = /14 days|25 minutes/.test(pluralText) ? Number(/\d+/.exec(pluralText)[0]) : 3;
  for (const [count, expected] of [[1, singular], [n, pluralText]]) {
    const t = tFor("en");
    const out = plural ? t(key, params(count), plural(count)) : t(key, params(count));
    assert.ok(out.includes(expected), `EN ${key} with ${count}: "${out}" should include "${expected}"`);
  }
  // Persian: one form, the number in Persian digits, and never an English plural left over.
  const t = tFor("fa");
  const one = plural ? t(key, params(1), plural(1)) : t(key, params(1));
  assert.ok(/۱/.test(one) || !/\{/.test(one), `FA ${key}: "${one}"`);
  assert.doesNotMatch(one, /\|/, `FA ${key}: no plural separator shown`);
}

// Guard: no EN string puts a number in front of a plural noun without a singular form.
const LABELS = new Set(["space.scene.tray.label", "space.scene.missionTray.label", "paths.relatedTitle",
  // Only used for two or more ("multiple").
  "missions.dailySummary.multipleDoneFact", "missions.dailySummary.multipleDone"]);
const noun = /\{[a-zA-Z]+\} (minutes|days|hours|seconds|weeks|steps|missions|objects|members|people|check-ins|reminders|paths|challenges|times|corners|rewards)\b/;
const missing = [];
(function walk(node, path) {
  for (const [key, value] of Object.entries(node)) {
    const p = path ? `${path}.${key}` : key;
    if (typeof value === "string") {
      if (noun.test(value) && !value.includes("|") && !LABELS.has(p)) missing.push(`${p}: ${value}`);
    } else if (value && typeof value === "object") walk(value, p);
  }
})(en, "");
assert.deepEqual(missing, [], `EN strings without a singular form:\n${missing.join("\n")}`);

console.log(`Plural tests passed (${cases.length} strings, EN and FA).`);
