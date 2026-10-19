# B10: Living Space copy proposal

Status: **approved by Amir, 2026-10-19** (decisions in section 0). Amir will do a full Persian copy pass later (B29).
Source: `docs/product/B10_COPY_EXPORT.md` (#380), which covers 349 strings on dev `5d3fe2e`.
Rule: only the keys listed below change. Every other key stays exactly as it is.

---

## 0. Decisions (Amir, 2026-10-19)

1. **Path names** are identical everywhere: path titles, onboarding labels and chips.
   - Career: «کار و حرفه»
   - Fitness: «بدن و حرکت»
   - The sleep path is renamed **EN "Rest & Energy" / FA «استراحت و انرژی»**. It covers sleep, starting the day and getting energy back.
   - The room corner name stays "Sleep Corner" / «گوشه خواب», because it shows a bed.
2. **Streak** becomes «{n} روز پشت‌سرهم» / "{n} days in a row". The words «استریک» and «استرایک» are removed everywhere.
3. **Room title** becomes "Your room" / «اتاقت».
4. **Ringo's FA register is colloquial.**
   - This applies to every Ringo line and action button in the Living Space flow, including keys not listed in section 2.
   - Claude Code converts any remaining formal Ringo-voice FA string (است / می‌کنید / می‌باشد) to the colloquial register, using the glossary, and lists those extra changes in the PR for review.
   - Labels and headings stay neutral.
5. **Later (B29):** Amir reviews and rewrites all Persian copy himself after the product decisions settle. This pass makes the copy consistent; it is not final wording.

## 1. Principles

**Voice**

- **Ringo's lines and action buttons** are warm, short and lightly colloquial in FA, for example «امروزت امنه»، «برای امروز کافیه». No formal «است / می‌باشد» in Ringo's mouth.
- **Labels and headings** (section names, chips) are short and neutral.
- **No system language** in the UI. Words like «قانون», «فعال نشده», «وضعیت به‌روز است», «چک‌این», «ذخیره بعد از رفرش» and «قفل» describe the system, not the user's life. Replace them with what the user experiences.
- **Honest, no pressure.** Never promise an object whose rule doesn't exist yet. Say «بعداً میاد», not «با ادامه باز می‌شه», unless that really is the rule.
- **No shame.** Overdue becomes «منتظره», never «عقب‌افتاده».

**Glossary (one word per concept)**

| Concept | EN | FA | Replaces |
|---|---|---|---|
| Day is protected | Today is safe | امروزت امنه | امروز امن است، استرایک امن شد |
| Consecutive days | {n} days in a row | {n} روز پشت‌سرهم | استریک، استرایک |
| Bonus mission | Extra step | قدم اضافه | بونوس، بونس |
| Tiny mission | Smaller step | قدم کوچیک‌تر | کوچک، نسخه کوچک |
| Ghost object | Coming later | بعداً میاد | پیش‌نمایش، قفل |
| Placed object | In your room | توی اتاقت | ذخیره‌شده |
| Reminder due | Reminder now / waiting | یادآور رسیده / منتظره | عقب‌افتاده |
| Back (one word) | Back | برگشت | برگرد |
| Room | Your room | اتاقت | اتاق پیشرفت تو |

**Numbers (digits rule)**

- FA shows **Persian digits everywhere**. EN shows Latin digits.
- One shared formatter (`Intl.NumberFormat(locale)`) is used for every number placeholder and every number rendered in a template.
- Counts use `common.countOf`: EN `{done}/{total}`, FA `{done} از {total}`. Remove the forced-LTR `<bdi>`.
- Percent uses `common.percent`: EN `{value}%`, FA `{value}٪`.
- `XP` stays in Latin letters in FA, with the number in Persian digits (`+۲۰ XP`).

**Punctuation**

- New keys:
  - `common.listSeparator`: EN `, ` / FA `، `
  - `common.labelSeparator`: EN `: ` / FA `: `
  - `common.arrowForward`: EN `→` / FA `←`
- The arrow and the separators currently hard-coded in `RoomScene.vue`, `SpaceObject.vue` and `RingoRewardSequence.vue` move to these keys.

**Plurals (EN)**

Every EN string with `{count}` gets `singular | plural` forms. FA keeps one form.

---

## 2. Changes by key

### Room corner and zone names

| key | EN (new) | FA (new) |
|---|---|---|
| `space.rule` | Your real progress changes this room. Faded objects are things that can come later. | پیشرفت واقعیت این اتاق رو تغییر می‌ده. اشیای کم‌رنگ چیزهایی‌ان که بعداً می‌تونن بیان. |
| `space.title` | Your room | اتاقت |
| `pathContent.career.title` | Career | کار و حرفه |
| `pathContent.fitness.title` | Fitness | بدن و حرکت |
| `pathContent.sleep.title` | Rest & Energy | استراحت و انرژی |
| `onboarding.paths.career.label` | Career | کار و حرفه |
| `onboarding.paths.sleep.label` | Rest & Energy | استراحت و انرژی |
| `onboarding.path.roomZone` | Corner: {zone} | گوشه: {zone} |
| `space.roomLabel` | Room corners | گوشه‌های اتاق |

### Objects

| key | EN (new) | FA (new) |
|---|---|---|
| `space.objectLockedPreview` | Coming later | بعداً میاد |
| `space.objectUnlocked` | In your room | توی اتاقت |
| `space.objectHistory.previewSource` | Coming later | بعداً میاد |
| `space.objectHistory.previewText` | Not in your room yet. More objects come to this corner later. | هنوز توی اتاقت نیست. اشیای بیشتری بعداً به این گوشه میان. |
| `space.objectHistory.savedSource` | In your room | توی اتاقت |
| `space.objectHistory.savedText` | Earned with a real mission. | با یه مأموریت واقعی به دستش آوردی. |
| `space.objectHistory.summary` | {saved} in your room · {preview} coming later | {saved} توی اتاق · {preview} بعداً |
| `space.objectHistory.empty` | Nothing here yet. | هنوز چیزی اینجا نیست. |
| `space.roomObjects.*_first_* .description` (5 first rewards) | Earned with your first {Path} mission. | (unchanged FA) |
| `space.firstRewardPlaced` | First object placed: {reward}. More objects come to this corner later. | اولین شیء جا گرفت: {reward}. اشیای بیشتری بعداً به این گوشه میان. |
| `space.scene.objectsPlaced` | no objects yet \| {count} object placed \| {count} objects placed | هنوز شیئی جا نگرفته \| {count} شیء جا گرفته \| {count} شیء جا گرفته |

### Reward card

| key | EN (new) | FA (new) |
|---|---|---|
| `spaceUnlock.eyebrow` | New in your room | تازه توی اتاقت |
| `spaceUnlock.body` | {reward} found its place in your {zone}. | {reward} توی {zone} جا گرفت. |
| `spaceUnlock.placedIn` | In {zone} | توی {zone} |
| `spaceUnlock.savedNote` | It's yours now. It stays in your room. | حالا مال توئه و توی اتاقت می‌مونه. |
| `spaceUnlock.continue` | See it in the room | دیدنش توی اتاق |
| `spaceUnlock.defaultDescription` | Earned with real progress. | با پیشرفت واقعی به دستش آوردی. |

### Ringo Moment

| key | EN (new) | FA (new) |
|---|---|---|
| `missions.finishForToday` | Enough for today | برای امروز کافیه |
| `ringoRewardSequence.finish` | Done | تمام |
| `ringoRewardSequence.skipSummary` | Skip | رد کن |
| `ringoRewardSequence.backend.missionDoneText` | This mission is done. | این مأموریت انجام شد. |
| `ringoRewardSequence.backend.todaySafeTitle` | Today is safe. | امروزت امنه. |
| `ringoRewardSequence.staged.challengeSecuredTitle` | Today counted | امروز حساب شد |
| `ringoRewardSequence.staged.challengeSecuredText` | Today's step is counted. | قدم امروزت ثبت شد. |
| `ringoRewardSequence.staged.challengeTitle` | Challenge moved forward | چالشت جلو رفت |
| `ringoRewardSequence.staged.pathTitle` | Path moved forward | مسیرت جلو رفت |
| `ringoRewardSequence.staged.strikeTitle` | Today is safe | امروزت امنه |
| `ringoRewardSequence.staged.strikeText` | Today is safe now. Your rhythm is protected. | امروزت امن شد. ریتمت حفظ شد. |
| `ringoRewardSequence.staged.streakValue` | {count} day in a row \| {count} days in a row | {count} روز پشت‌سرهم |
| `ringoRewardSequence.staged.tinyCompleteTitle` | Small step. Today is safe. | قدم کوچیک. امروزت امن شد. |
| `ringoRewardSequence.staged.tinyStrikeTitle` | Small step. Today is safe. | قدم کوچیک. امروزت امن شد. |
| `ringoRewardSequence.staged.bonusCompleteTitle` | Extra step done | قدم اضافه انجام شد |
| `ringoRewardSequence.staged.xpText` | XP added for this mission. | XP این مأموریت اضافه شد. |
| `ringoRewardSequence.staged.levelText` | You reached a new level. | به سطح تازه‌ای رسیدی. |
| `ringoRewardSequence.staged.finalTitle` | Choose your pace | ریتمت رو خودت انتخاب کن |
| `ringoRewardSequence.staged.finalText` | You can stop here. If you still have energy, see your choices. | می‌تونی همین‌جا تمومش کنی. اگه هنوز انرژی داری، گزینه‌ها رو ببین. |
| `ringoRewardSequence.types.strike_secured` | Today | امروز |

### Extra and smaller steps

| key | EN (new) | FA (new) |
|---|---|---|
| `space.shell.intensity.bonus` | Extra | اضافه |
| `space.shell.intensity.tiny` | Smaller | کوچیک‌تر |
| `space.shell.tinyLivingSpaceGate` | Need a lighter version? Ask Ringo to make today's step smaller. | نسخهٔ سبک‌تر می‌خوای؟ از رینگو بخواه قدم امروز رو کوچیک‌تر کنه. |
| `space.shell.bonusLockedGate` | Opens after today's main step, as an optional extra. | بعد از قدم اصلی امروز باز می‌شه؛ به‌عنوان یه قدم اضافهٔ اختیاری. |
| `space.shell.missionLockedGate` | Not yet. Keep going with your current step and this one opens. | هنوز نه. قدم فعلی رو ادامه بده تا این یکی باز بشه. |
| `space.shell.unlocksTomorrow` | Opens tomorrow if you keep this challenge going. | اگه این چالش رو ادامه بدی، فردا باز می‌شه. |
| `space.shell.unlocksInDays` | Opens in {count} day if you keep this challenge going. \| Opens in {count} days if you keep this challenge going. | اگه این چالش رو ادامه بدی، {count} روز دیگه باز می‌شه. |

### Reminders

| key | EN (new) | FA (new) |
|---|---|---|
| `missions.remindOptions.prompt` | Okay. When should I remind you? | باشه. کی یادت بندازم؟ |
| `missions.remindOptions.fifteenMinutes` | In 15 minutes | ۱۵ دقیقه دیگه |
| `missions.remindOptions.oneHour` | In 1 hour | ۱ ساعت دیگه |
| `space.panel.reminderBadge` | Reminder now | یادآور رسیده |
| `space.zoneState.reminderDue` | Reminder now | یادآور رسیده |
| `space.shell.restReminderClear` | No reminders waiting | یادآوری منتظر نیست |
| `space.shell.restReminderDue` | {count} reminder waiting \| {count} reminders waiting | {count} یادآور منتظره |
| `space.shell.restReminderFuture` | {count} reminder later today \| {count} reminders later today | {count} یادآور برای بعد |
| `space.shell.restMomentDue` | Today is almost settled. {count} reminder is still waiting. \| Today is almost settled. {count} reminders are still waiting. | امروز تقریباً تمومه؛ فقط {count} یادآور هنوز منتظره. |
| `space.overview.reminderText` | {count} reminder is waiting. Take a look before you rest. \| {count} reminders are waiting. Take a look before you rest. | {count} یادآور منتظره. قبل از استراحت یه نگاه بنداز. |
| `space.overview.reminderTitle` | A reminder is waiting in {path} | یه یادآور توی {path} منتظره |
| `space.ringoGuide.restReminderTitle` | One reminder is still waiting | یه یادآور هنوز منتظره |

### Ringo card (zone panel)

| key | EN (new) | FA (new) |
|---|---|---|
| `space.panel.back` | Back | برگشت |
| `space.ringoGuide.readyTitle` | Your next step is ready | قدم بعدیت آماده‌ست |
| `space.ringoGuide.readyMessage` | {path} has a step for today. If it feels like too much, ask me to make it smaller. | {path} امروز یه قدم داره. اگه زیاده، بگو کوچیک‌ترش کنم. |
| `space.ringoGuide.missionFocusMessage` | {mission} is today's step. Extra steps can wait. | {mission} قدم امروزته. قدم‌های اضافه می‌تونن صبر کنن. |
| `space.ringoGuide.bonusReadyMessage` | The main step is done. {mission} is an extra, only if you feel like it. | قدم اصلی انجام شده. {mission} فقط یه قدم اضافه‌ست، اگه حسش هست. |
| `space.ringoGuide.missionDoneTitle` | Already counted today | امروز حساب شده |
| `space.ringoGuide.missionDoneMessage` | {mission} is done. Your room keeps it. | {mission} انجام شده و اتاقت نگهش می‌داره. |
| `space.ringoGuide.lockedTitle` | Not yet | هنوز نه |
| `space.ringoGuide.fallbackTitle` | Pick a corner | یه گوشه رو انتخاب کن |
| `space.ringoGuide.fallbackMessage` | Look around {path}. I'll keep the next step in sight. | توی {path} یه نگاهی بنداز؛ قدم بعدی رو جلوی چشمت نگه می‌دارم. |
| `space.ringoGuide.challengePreviewTitle` | This could be your next step | این می‌تونه قدم بعدیت باشه |
| `space.ringoGuide.challengePreviewMessage` | {challenge} is part of {path}. Start it when you want it as your daily step. | {challenge} بخشی از {path} ـه. هر وقت خواستی قدم روزانه‌ت باشه، شروعش کن. |
| `space.ringoGuide.startTitle` | Start with one real step | با یه قدم واقعی شروع کن |
| `space.ringoGuide.startMessage` | {path} has no challenge yet. Pick one, and this corner starts changing with you. | {path} هنوز چالشی نداره. یکی انتخاب کن تا این گوشه همراهت تغییر کنه. |
| `space.ringoGuide.restTitle` | Rest in your room | توی اتاقت استراحت کن |
| `space.panel.firstRewardHint` | Finish today's step in this path to place {object} in your room. | قدم امروز این مسیر رو انجام بده تا {object} توی اتاقت جا بگیره. |

### Room overview and rest

| key | EN (new) | FA (new) |
|---|---|---|
| `space.overview.safeTitle` | Today is safe | امروزت امنه |
| `space.overview.safeText` | Today is safe. Resting is a good next step too. | امروزت امنه. استراحت هم قدم خوبیه. |
| `space.overview.readyTitle` | {path} is ready | {path} آماده‌ست |
| `space.overview.readyText` | One real mission can move this corner today. | یه مأموریت واقعی می‌تونه امروز این گوشه رو جلو ببره. |
| `space.overview.progressTitle` | Your room keeps your progress | اتاقت پیشرفتت رو نگه می‌داره |
| `space.overview.progressText` | {count} object in your room, all from real progress. \| {count} objects in your room, all from real progress. | {count} شیء توی اتاقته؛ همه از پیشرفت واقعی. |
| `space.overview.startText` | Choose a first path, and your room starts changing with your progress. | یه مسیر اول انتخاب کن تا اتاقت با پیشرفتت شروع به تغییر کنه. |
| `space.feedback.progressTitle` | Your room kept this progress | اتاق این پیشرفت رو نگه داشت |
| `space.feedback.progressText` | {zone} moved forward. No new object this time, and that's fine. | {zone} جلو رفت. این بار شیء تازه‌ای نیومد؛ اشکالی نداره. |
| `space.feedback.rewardTitle` | {reward} joined your room | {reward} اومد توی اتاقت |
| `space.feedback.rewardText` | {reward} is now in {zone}. You earned it with a real mission. | {reward} حالا توی {zone} ـه. با یه مأموریت واقعی به دستش آوردی. |
| `space.shell.restLabel` | Rest | استراحت |
| `space.shell.restMomentQuiet` | Take a breath here. I'll keep the room and your next step in order. | یه لحظه همین‌جا نفس بگیر؛ اتاق و قدم بعدیت رو مرتب نگه می‌دارم. |
| `space.shell.restMomentSafe` | Today is safe. You can stop here; your room keeps today's win. | امروزت امنه. می‌تونی همین‌جا تمومش کنی؛ اتاقت برد امروز رو نگه می‌داره. |
| `space.shell.restSummaryOpenValue` | Not yet | هنوز نه |
| `space.room.objectsToday` | New objects today | اشیای تازهٔ امروز |
| `space.panel.stateSafe` | Today is safe | امروزت امنه |

### Today strip, details, loading

| key | EN (new) | FA (new) |
|---|---|---|
| `space.panel.futureMissions` | Later in this challenge: {count} more mission \| Later in this challenge: {count} more missions | بعداً در این چالش: {count} مأموریت دیگه |
| `space.shell.pathProgressCount` | {done} of {total} steps | {done} از {total} قدم |
| `space.shell.pathLoading` | Getting this path's challenges… | دارم چالش‌های این مسیر رو میارم… |
| `space.loadingTitle` | Opening your room… | اتاقت داره باز می‌شه… |
| `space.loadingText` | Checking what you've earned. | دارم نگاه می‌کنم چی به دست آوردی. |
| `space.zoneAction.readyTitle` | {challenge} is ready today | {challenge} امروز آماده‌ست |
| `space.zoneAction.doneText` | This path is counted today. You can look at it, or pick another path. | این مسیر امروز حساب شده. می‌تونی جزئیاتش رو ببینی یا بری سراغ یه مسیر دیگه. |
| `space.zoneAction.notStartedTitle` | No challenge in this path yet | این مسیر هنوز چالشی نداره |
| `space.zoneAction.notStartedText` | Start from the paths page to connect this corner to a real daily step. | از صفحهٔ مسیرها شروع کن تا این گوشه به یه قدم روزانهٔ واقعی وصل بشه. |
| `space.zoneAction.readyText` | Continue this path's challenge and take today's step. | چالش این مسیر رو ادامه بده و قدم امروز رو بردار. |
| `common.dayChallenge` | {count}-day challenge | چالش {count} روزه |

### New shared keys

| key | EN | FA |
|---|---|---|
| `common.countOf` | {done}/{total} | {done} از {total} |
| `common.percent` | {value}% | {value}٪ |
| `common.listSeparator` | `, ` | `، ` |
| `common.labelSeparator` | `: ` | `: ` |
| `common.arrowForward` | → | ← |

---

## 3. Implementation notes for Claude Code

1. Change only the keys above, in `en.js` and `fa.js`. Keep every other key byte-identical.
2. **Digits:** add one `formatNumber(value, locale)` helper, or use vue-i18n number formats, and pass formatted numbers into every placeholder and template number listed in the export's "Latin digits" section.
   - Remove the forced-LTR `<bdi>` around `completed/total` and use `common.countOf`.
   - Keep `timeLeft*` working as today.
3. **Hard-coded strings:**
   - Replace the separators, percent, `x/y` counts and the `→` with the new shared keys.
   - The `i` glyph stays.
   - The reward card letter fallback stays.
4. **Backend English:**
   - In `rewardSequenceBuilder.js`, an unmapped backend sentence must fall back to a localized generic line (for example `ringoRewardSequence.fallbackTitle` plus no body). It must never show English in FA.
   - Add a unit test that every `BACKEND_STEP_COPY` entry has EN and FA keys.
5. **Tests:**
   - Extend the localization test so these keys exist in both locales.
   - FA renders no Latin digits in the room panel, the overview and the Ringo Moment.
   - EN plurals render correctly for 1 and 2.
   - Update any test that asserts old copy.
6. **Screenshots:** EN and FA, desktop and 390, for:
   - zone panel: ready, done, extra step
   - room overview
   - rest
   - Ringo Moment
   - reward card
   - reminders

## 4. Open questions for Amir (answered, see section 0)

1. **FA path names:** «کار و حرفه» / «بدن و حرکت» / «خواب و آرامش», used everywhere, including onboarding. OK?
2. **Streak:** «{n} روز پشت‌سرهم» instead of «استریک», and no «استرایک» anywhere. OK?
3. **Room title:** EN "Your room", FA «اتاقت», instead of "Your progress room / اتاق پیشرفت تو". OK?
4. **Ringo's register:** lightly colloquial FA (می‌تونی، آماده‌ست، کافیه) for Ringo and buttons, neutral for labels. OK?
