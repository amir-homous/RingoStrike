import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import en from "../src/i18n/locales/en.js";
import fa from "../src/i18n/locales/fa.js";
import { getChallengePathKey } from "../src/lib/guidedExperience.js";

// Every seeded challenge (read from the backend seed) resolves to a path key with a label in EN and
// FA, so no raw key like CHALLENGECARD.PATHS.CREATIVITY can show.
const seed = readFileSync(new URL("../../backend/services/path_seed_service.py", import.meta.url), "utf8");
const names = [...seed.matchAll(/^ {16}"name": "([^"]+)",$/gm)].map((m) => m[1]);
assert.equal(names.length, 15, `15 seeded challenges, found ${names.length}`);
// Each path block starts with its 8-space-indented "key" line.
const pathOf = Object.fromEntries(seed.split(/^ {8}"key": "/m).slice(1).map((block) => [block.slice(0, block.indexOf('"')), block]));
for (const name of names) {
  const key = getChallengePathKey({ name });
  assert.ok(key, `${name}: has a path key`);
  const seedPath = Object.entries(pathOf).find(([, block]) => block.includes(`"name": "${name}",`))?.[0];
  assert.equal(key, seedPath, `${name}: the key is its seed path`);
  for (const [locale, messages] of [["en", en], ["fa", fa]]) {
    assert.ok(messages.challengeCard.paths[key], `${locale}: challengeCard.paths.${key} exists (${name})`);
  }
  // Case and spacing in the name do not matter.
  assert.equal(getChallengePathKey({ challenge_name: `  ${name.toUpperCase()} ` }), key);
}
assert.equal(getChallengePathKey({ name: "Daily Strike" }), "consistency", "archived legacy challenge");
assert.equal(getChallengePathKey({ name: "Unknown" }), "", "unknown challenge: no label");

console.log("Challenge card tests passed.");
