import assert from "node:assert/strict";
import en from "../src/i18n/locales/en.js";
import fa from "../src/i18n/locales/fa.js";
import { challengeLineKey, shouldShowExplainer } from "../src/lib/roomExplainer.js";

// B37 (D84, Fix B): one rule in both languages. "With others" only at 2 or more active members;
// at 1 member only the plain line. No number is ever shown.
const line = (locale, members) => locale.space.explainer[`${challengeLineKey(members)}Line`];
const expected = {
  en: { 1: "A small daily habit.", 2: "A small daily habit you try with others." },
  fa: { 1: "یک عادت کوچک روزانه.", 2: "یک عادت کوچک روزانه که با بقیه امتحانش می‌کنی." },
};

for (const [name, locale] of [["en", en], ["fa", fa]]) {
  assert.equal(line(locale, 1), expected[name][1], `${name}: 1 member`);
  assert.equal(line(locale, 2), expected[name][2], `${name}: 2 members`);
  assert.equal(line(locale, 7), expected[name][2], `${name}: 7 members`);
  assert.equal(line(locale, 0), expected[name][1], `${name}: no count`);
  // The "with others" line is the plain line plus the "with others" part, in both languages.
  assert.ok(line(locale, 2).startsWith(line(locale, 1).replace(/\.$/, "")), `${name}: plain line plus "with others"`);
  assert.doesNotMatch(line(locale, 2), /[0-9۰-۹]/, `${name}: no number`);
}

assert.equal(shouldShowExplainer({ firstRun: true, seen: false }), true);
assert.equal(shouldShowExplainer({ firstRun: true, seen: true }), false);
assert.equal(shouldShowExplainer({ firstRun: false, seen: false }), false);

console.log("Room explainer copy tests passed.");
