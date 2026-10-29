import assert from "node:assert/strict";
import { buildDayMoment, composeMomentSteps, dayMomentCase, ladderCopy, lastSevenDays, missionsDoneToday, utcTodayIso } from "../src/lib/dayMoment.js";

// B37 (#387, D72 to D74): the Ringo moment's cards and the day moment, without a browser.
const t = (key, params = {}) => `${key}${Object.keys(params).length ? JSON.stringify(params) : ""}`;

// The steps the sequence builder makes today for a done mission (backend sequence merged).
function builtSteps({ level = false } = {}) {
  return [
    { type: "ringo_message", title: "Nice work." },
    { type: "mission_complete", title: "Complete one focus block", missionKey: "deep_work_block" },
    { type: "xp_earned", value: "+15 XP", progressBar: { old: 10, new: 25 }, meta: "40 total XP" },
    { type: "strike_secured", title: "Today is safe" },
    ...(level ? [{ type: "level_up", title: "Level 2 reached" }] : []),
    { type: "challenge_secured", title: "Today counted" },
    { type: "final_choice", title: "Choose your pace.", actions: [{ key: "finish_today" }, { key: "view_choices" }] },
  ];
}
const types = (steps) => steps.map((step) => step.type);
const day = { streak: 11, totalDays: 25, week: lastSevenDays("2026-10-29", [{ date: "2026-10-29", count: 1 }]) };

// Main, first counted of the day: Nice work, the day moment, Choose your pace (3 taps).
const mainFirst = composeMomentSteps(builtSteps(), { intensity: "main", firstOfDay: true, day }, t);
assert.deepEqual(types(mainFirst), ["nice_work", "day_moment", "final_choice"]);
// The ladder line never embeds the mission title; the card shows it as its own label.
assert.equal(mainFirst[0].text, "ringoRewardSequence.moment.ladder.oneLine");
assert.equal(mainFirst[0].missionLabel, "Complete one focus block");
assert.equal(mainFirst[0].value, "+15 XP");
assert.deepEqual(mainFirst[0].progressBar, { old: 10, new: 25 });
assert.equal(mainFirst[0].meta, "40 total XP");
assert.equal(mainFirst[0].celebrate, true);
assert.equal(mainFirst[1].celebrate, true);
assert.equal(mainFirst[2].celebrate, undefined, "Choose your pace keeps its buttons");
assert.equal(mainFirst[2].actions.length, 2);

// Main later the same day: Nice work, Choose your pace (2 taps).
assert.deepEqual(types(composeMomentSteps(builtSteps(), { intensity: "main", firstOfDay: false, day: null }, t)), ["nice_work", "final_choice"]);
// Tiny follows Main.
assert.deepEqual(types(composeMomentSteps(builtSteps(), { intensity: "tiny", firstOfDay: true, day }, t)), ["nice_work", "day_moment", "final_choice"]);
assert.deepEqual(types(composeMomentSteps(builtSteps(), { intensity: "tiny", firstOfDay: false, day: null }, t)), ["nice_work", "final_choice"]);
// Bonus: one card with its XP and the two pace buttons (1 tap).
const bonus = composeMomentSteps(builtSteps(), { intensity: "bonus", firstOfDay: false, day: null }, t);
assert.deepEqual(types(bonus), ["bonus_done"]);
assert.equal(bonus[0].value, "+15 XP");
assert.equal(bonus[0].actions.length, 2);
// A first-of-day flag without data never makes a day moment out of nothing.
assert.deepEqual(types(composeMomentSteps(builtSteps(), { intensity: "main", firstOfDay: true, day: null }, t)), ["nice_work", "final_choice"]);
// A level-up stays as a line on Nice work.
assert.equal(composeMomentSteps(builtSteps({ level: true }), { intensity: "main" }, t)[0].levelLine, "Level 2 reached");
// Nothing built (already done): nothing shown.
assert.deepEqual(composeMomentSteps([], { intensity: "main", firstOfDay: true, day }, t), []);

// The three cases (D74).
assert.equal(dayMomentCase({ streak: 11, totalDays: 25 }), "continue");
assert.equal(dayMomentCase({ streak: 1, totalDays: 1 }), "first");
assert.equal(dayMomentCase({ streak: 1, totalDays: 25 }), "welcome_back");
assert.equal(dayMomentCase({ streak: 1, totalDays: null }), "plain", "no total: no claim about first day or coming back");
assert.equal(dayMomentCase({ streak: null, totalDays: 25 }), "plain");

const cont = buildDayMoment({ streak: 11, totalDays: 25, week: null }, t);
assert.equal(cont.count, 11);
assert.match(cont.countLabel, /inARowLabel/);
assert.match(cont.softLine, /lineContinue/);
assert.match(cont.chip, /daysSoFar\{"count":25\}/);
assert.equal(cont.kicker, "");

const first = buildDayMoment({ streak: 1, totalDays: 1, week: null }, t);
assert.equal(first.count, 1);
assert.match(first.softLine, /lineFirst/);
assert.equal(first.chip, "", "no '1 day so far' chip on the first day");

const back = buildDayMoment({ streak: 1, totalDays: 25, week: null }, t);
assert.match(back.kicker, /welcomeBack/);
assert.equal(back.count, 25, "coming back: the big number is the days so far");
assert.match(back.countLabel, /daysSoFarLabel/);
assert.match(back.chip, /rhythmAgain\{"count":1\}/);
assert.match(back.softLine, /lineBack/);

// A failed /me/stats: no number, no chip; "Today is safe." stays.
const none = buildDayMoment({ streak: null, totalDays: null, week: null }, t);
assert.equal(none.count, null);
assert.equal(none.chip, "");
assert.match(none.line, /moment\.safe/);

// The last seven days end today (not a calendar week); quiet days stay quiet; missing data: no bar.
const week = lastSevenDays("2026-10-29", [{ date: "2026-10-23", count: 2 }, { date: "2026-10-27", count: 1 }, { date: "2026-10-29", count: 1 }, { date: "2026-10-20", count: 1 }]);
assert.deepEqual(week.map((d) => d.date), ["2026-10-23", "2026-10-24", "2026-10-25", "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]);
assert.deepEqual(week.map((d) => d.lit), [true, false, false, false, true, false, true]);
assert.equal(week[6].today, true);
assert.deepEqual(lastSevenDays("2026-03-01", []).map((d) => d.date)[0], "2026-02-23", "month boundary");
assert.equal(lastSevenDays("2026-10-29", null), null);
assert.equal(utcTodayIso(Date.parse("2026-10-29T23:30:00-05:00")), "2026-10-30", "UTC day, like the server");
assert.equal(buildDayMoment({ streak: 3, totalDays: 9, week: [{}, {}] }, t).week, null, "a broken week is dropped");

// The reward message ladder on the first card: Main and Tiny missions done today (distinct
// missions, not check-ins); a Bonus never counts.
const mission = (id, intensity, status = "done") => ({ mission_id: id, mission_intensity: intensity, status });
assert.equal(missionsDoneToday([], { mission_id: 1, mission_intensity: "main" }), 1, "first Main");
assert.equal(missionsDoneToday([mission(1, "main")], { mission_id: 2, mission_intensity: "main" }), 2);
assert.equal(missionsDoneToday([mission(1, "main"), mission(2, "tiny")], { mission_id: 3, mission_intensity: "main" }), 3, "a Tiny counts");
assert.equal(missionsDoneToday([mission(1, "main"), mission(2, "main"), mission(3, "tiny")], { mission_id: 4, mission_intensity: "tiny" }), 4, "a Tiny just finished counts");
const seven = [1, 2, 3, 4, 5, 6].map((id) => mission(id, id % 2 ? "main" : "tiny"));
assert.equal(missionsDoneToday(seven, { mission_id: 7, mission_intensity: "main" }), 7);
assert.equal(missionsDoneToday([mission(1, "main"), mission(9, "bonus")], { mission_id: 2, mission_intensity: "main" }), 2, "a done Bonus never counts");
assert.equal(missionsDoneToday([mission(1, "main")], { mission_id: 9, mission_intensity: "bonus" }), 1, "finishing a Bonus adds nothing");
assert.equal(missionsDoneToday([mission(1, "main"), mission(2, "main", "pending"), mission(3, "main", "skipped")], { mission_id: 4, mission_intensity: "main" }), 2, "only done missions count");
assert.equal(missionsDoneToday([mission(1, "main")], { mission_id: 1, mission_intensity: "main" }), 1, "the same mission counts once");

const ladderTitle = (n) => ladderCopy(n, "Complete one focus block", t);
assert.deepEqual(ladderTitle(1), { title: "ringoRewardSequence.moment.niceWork", text: "ringoRewardSequence.moment.ladder.oneLine" });
assert.equal(ladderTitle(2).title, "ringoRewardSequence.moment.ladder.twoTitle");
assert.equal(ladderTitle(2).text, "ringoRewardSequence.moment.ladder.twoLine");
assert.equal(ladderTitle(3).title, "ringoRewardSequence.moment.ladder.threeTitle");
assert.equal(ladderTitle(4).title, "ringoRewardSequence.moment.ladder.manyTitle");
assert.equal(ladderTitle(4).text, 'ringoRewardSequence.moment.ladder.manyLine{"count":4}');
assert.equal(ladderTitle(7).text, 'ringoRewardSequence.moment.ladder.manyLine{"count":7}', "the number goes to the plural helper");
assert.equal(ladderTitle(0).title, "ringoRewardSequence.moment.niceWork", "an unknown count reads as the first");

// Through the composer: the Nice work card carries the ladder; a Tiny uses it; a Bonus keeps its card.
for (const [n, title] of [[1, "moment.niceWork"], [2, "moment.ladder.twoTitle"], [3, "moment.ladder.threeTitle"], [4, "moment.ladder.manyTitle"], [7, "moment.ladder.manyTitle"]]) {
  const card = composeMomentSteps(builtSteps(), { intensity: "main", doneToday: n }, t)[0];
  assert.equal(card.type, "nice_work");
  assert.equal(card.title, `ringoRewardSequence.${title}`, `count ${n}`);
  assert.equal(card.doneToday, n);
  assert.equal(card.value, "+15 XP", "XP unchanged");
  assert.equal(card.missionLabel, "Complete one focus block", `count ${n}: the mission title as its own label`);
  assert.ok(!card.text.includes("Complete one focus block"), `count ${n}: the line does not embed the title`);
}
const tinyCard = composeMomentSteps(builtSteps(), { intensity: "tiny", firstOfDay: false, doneToday: 2 }, t)[0];
assert.equal(tinyCard.title, "ringoRewardSequence.moment.ladder.twoTitle", "a Tiny gets the ladder");
const bonusCard = composeMomentSteps(builtSteps(), { intensity: "bonus", doneToday: 5 }, t);
assert.deepEqual(bonusCard.map((c) => c.type), ["bonus_done"], "a Bonus keeps its one card");
assert.equal(bonusCard[0].title, "ringoRewardSequence.moment.bonusTitle");

console.log("Day moment tests passed.");
