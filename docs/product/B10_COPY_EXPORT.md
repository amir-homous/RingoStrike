# B10 copy export: Living Space flow

Status: **export for review only.** No copy is changed in this PR.

This file lists every user-facing string used by the Living Space flow on `dev` at `5d3fe2e` (after B19–B24 and B21), grouped by where it shows. Each row has the i18n key, the current EN and FA text, and the component that uses it.

- **Source:** `frontend/src/i18n/locales/en.js` and `fa.js`, with keys found by scanning the Living Space components (`components/space/*`, `RingoRewardSequence.vue`, `RingoMoodFigure.vue`, the onboarding steps), `lib/livingSpace*.js`, `lib/roomScene.js`, `lib/roomMaterialize.js`, `utils/rewardSequenceBuilder.js`, and the Living Space parts of `Dashboard.vue` and `Onboarding.vue`.
- **Dynamic keys** (`space.zoneNames.<zone>`, `space.roomObjects.<reward>`, `ringoRewardSequence.types.<type>`, and similar) are expanded to every existing key.
- **Remind-later and skip options** list only what the zone panel actually offers.
- **"State"** after the component is inferred from the key name (for example *button*, *due reminder*, *today safe*), so treat it as a hint. The section intro says which screen the section belongs to.
- **Placeholders** such as `{count}` are kept as written. ` \| ` separates EN plural forms (vue-i18n), and ⏎ marks a line break in the source.
- **Not covered:** seeded challenge and mission content (titles and descriptions of challenges and missions, localized by `ringoContentLocalization.js` / `pathContent.*`) is content rather than room UI. Only the path titles used as zone subtitles are listed.

Total: **349 strings** in 15 sections.

## Contents

- [Room corner chip and info popover](#room-corner-chip-and-info-popover)
- [Zone names](#zone-names)
- [Object names and object states](#object-names-and-object-states)
- [Reward card (RewardUnlockMoment)](#reward-card-rewardunlockmoment)
- [Ringo Moment (reward sequence)](#ringo-moment-reward-sequence)
- [Bonus and tiny (smaller step) offers](#bonus-and-tiny-smaller-step-offers)
- [Reminders](#reminders)
- [Skip reasons](#skip-reasons)
- [Today strip and today list](#today-strip-and-today-list)
- [Details accordion (path & challenges, objects)](#details-accordion-path--challenges-objects)
- [Ringo card](#ringo-card)
- [Room overview and rest](#room-overview-and-rest)
- [Room scene, loading and fallback grid](#room-scene-loading-and-fallback-grid)
- [First-run and onboarding texts that touch the room](#first-run-and-onboarding-texts-that-touch-the-room)
- [Room (zone) panel: other states](#room-zone-panel-other-states)
- [Hard-coded strings (not in i18n)](#hard-coded-strings-not-in-i18n)
- [Backend-sourced English](#backend-sourced-english)
- [Where FA currently shows Latin digits](#where-fa-currently-shows-latin-digits)
- [Notes for the review](#notes-for-the-review)

## Room corner chip and info popover

LivingSpace.vue `#corner` slot: object count chip, "New reward" chip, the **i** button and its tooltip.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `space.newReward` | New reward | پاداش تازه | LivingSpace |
| `space.objects` | {count} object \| {count} objects | {count} شیء | LivingSpace |
| `space.roomInfoLabel` | About this room | درباره این اتاق | LivingSpace · label / screen reader |
| `space.rule` | Real mission progress changes the room. Previews only show what can become visible later. | پیشرفت واقعی مأموریت، اتاق را تغییر می‌دهد. پیش‌نمایش‌ها فقط نشان می‌دهند چه چیزی بعداً می‌تواند قابل دیدن شود. | LivingSpace |

## Zone names

Localized zone and path names (`livingSpaceCopy.js`). The backend also sends English zone titles (`ZONE_DEFS`), used only as a fallback.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `pathContent.career.title` | Career | مسیر شغلی | livingSpaceCopy |
| `pathContent.creativity.title` | Creativity | خلاقیت | livingSpaceCopy |
| `pathContent.fitness.title` | Fitness | تناسب و انرژی | livingSpaceCopy |
| `pathContent.learning.title` | Learning | یادگیری | livingSpaceCopy |
| `pathContent.sleep.title` | Sleep | آرامش و خواب | livingSpaceCopy |
| `space.zoneNames.creative_corner` | Creative Corner | گوشه خلاقیت | livingSpaceCopy |
| `space.zoneNames.fitness_corner` | Fitness Corner | گوشه حرکت | livingSpaceCopy |
| `space.zoneNames.learning_corner` | Learning Corner | گوشه یادگیری | livingSpaceCopy |
| `space.zoneNames.sleep_corner` | Sleep Corner | گوشه خواب | livingSpaceCopy |
| `space.zoneNames.work_desk` | Work Desk | میز کار | livingSpaceCopy |

## Object names and object states

Reward object titles/descriptions (`space.roomObjects.<reward key>`), shown in the reward card, the zone panel's object list and aria labels; plus object state labels.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `space.objectHistory.empty` | No room objects are mapped here yet. | هنوز شیئی برای این بخش تعریف نشده. | SpaceZonePanel · empty |
| `space.objectHistory.previewSource` | Future visible change | تغییر قابل دیدن آینده | SpaceZonePanel · preview / not joined |
| `space.objectHistory.previewText` | Preview only. Its unlock rule is not active yet. | فعلاً فقط پیش‌نمایش است و قانون باز شدنش فعال نشده. | SpaceZonePanel · preview / not joined |
| `space.objectHistory.savedSource` | Saved in your room | در اتاق تو ذخیره شده | SpaceZonePanel |
| `space.objectHistory.savedText` | Placed by real mission progress. | با پیشرفت واقعی مأموریت در اتاق قرار گرفته. | SpaceZonePanel |
| `space.objectHistory.summary` | {saved} saved · {preview} previews | {saved} ذخیره‌شده · {preview} پیش‌نمایش | SpaceZonePanel |
| `space.objectHistory.unknown` | Room object | شیء اتاق | SpaceZonePanel |
| `space.objectLockedPreview` | Preview | پیش‌نمایش | SpaceObject, SpaceZonePanel · locked |
| `space.objectUnlocked` | Saved | ذخیره‌شده | SpaceObject, SpaceZonePanel · locked |
| `space.roomObjects.career_desk_lamp.description` | A calm work light for early Career consistency. | یک نور آرام برای ثبات اولیه در مسیر شغلی. | livingSpaceCopy |
| `space.roomObjects.career_desk_lamp.title` | Desk Lamp | چراغ رومیزی | livingSpaceCopy |
| `space.roomObjects.career_monitor.description` | A clearer workspace for Career progress milestones. | یک فضای کار شفاف‌تر برای نقطه‌های پیشرفت مسیر شغلی. | livingSpaceCopy |
| `space.roomObjects.career_monitor.title` | Focus Monitor | مانیتور تمرکز | livingSpaceCopy |
| `space.roomObjects.career_planner.description` | Unlocked because you completed your first Career mission. | با اولین مأموریت شغلی‌ات اینجا جا گرفت. | livingSpaceCopy |
| `space.roomObjects.career_planner.title` | Career Planner | برنامه‌ریز کار | livingSpaceCopy |
| `space.roomObjects.career_project_board.description` | A visible board for Career achievements. | تابلویی که دستاوردهای مسیر شغلی‌ات را نشان می‌دهد. | livingSpaceCopy |
| `space.roomObjects.career_project_board.title` | Project Board | تابلوی پروژه | livingSpaceCopy |
| `space.roomObjects.career_trophy.description` | A major Career milestone marker. | نشانه یک نقطه عطف بزرگ در مسیر شغلی. | livingSpaceCopy |
| `space.roomObjects.career_trophy.title` | Career Trophy | جام مسیر شغلی | livingSpaceCopy |
| `space.roomObjects.creativity_art_wall.description` | A wall that reflects your creative achievements. | دیواری که دستاوردهای خلاقانه‌ات را نشان می‌دهد. | livingSpaceCopy |
| `space.roomObjects.creativity_art_wall.title` | Art Wall | دیوار هنر | livingSpaceCopy |
| `space.roomObjects.creativity_desk_lamp.description` | A warm light for early Creativity consistency. | یک نور گرم برای ثبات اولیه در خلاقیت. | livingSpaceCopy |
| `space.roomObjects.creativity_desk_lamp.title` | Creative Lamp | چراغ خلاقیت | livingSpaceCopy |
| `space.roomObjects.creativity_easel_upgrade.description` | A stronger creative setup for path progress. | یک چیدمان خلاقانه‌تر برای پیشرفت در مسیر. | livingSpaceCopy |
| `space.roomObjects.creativity_easel_upgrade.title` | Easel Upgrade | سه‌پایهٔ تازه | livingSpaceCopy |
| `space.roomObjects.creativity_sketchbook.description` | Unlocked because you completed your first Creativity mission. | با اولین مأموریت خلاقیتت اینجا جا گرفت. | livingSpaceCopy |
| `space.roomObjects.creativity_sketchbook.title` | Sketchbook | دفتر طراحی | livingSpaceCopy |
| `space.roomObjects.creativity_trophy.description` | A major Creativity milestone marker. | نشانه یک نقطه عطف بزرگ در خلاقیت. | livingSpaceCopy |
| `space.roomObjects.creativity_trophy.title` | Creativity Trophy | جام خلاقیت | livingSpaceCopy |
| `space.roomObjects.fitness_better_mat.description` | A more grounded Fitness setup for path progress. | یک چیدمان محکم‌تر برای پیشرفت در تناسب و انرژی. | livingSpaceCopy |
| `space.roomObjects.fitness_better_mat.title` | Better Mat | مت ورزشی بهتر | livingSpaceCopy |
| `space.roomObjects.fitness_dumbbells.description` | A steady Fitness consistency reward. | پاداشی برای ثبات در تناسب و انرژی. | livingSpaceCopy |
| `space.roomObjects.fitness_dumbbells.title` | Dumbbells | دمبل‌ها | livingSpaceCopy |
| `space.roomObjects.fitness_training_bench.description` | A visible marker for Fitness achievements. | نشانه‌ای قابل دیدن برای دستاوردهای تناسب و انرژی. | livingSpaceCopy |
| `space.roomObjects.fitness_training_bench.title` | Training Bench | نیمکت تمرین | livingSpaceCopy |
| `space.roomObjects.fitness_trophy.description` | A major Fitness milestone marker. | نشانه یک نقطه عطف بزرگ در تناسب و انرژی. | livingSpaceCopy |
| `space.roomObjects.fitness_trophy.title` | Fitness Trophy | جام حرکت | livingSpaceCopy |
| `space.roomObjects.fitness_water_bottle.description` | Unlocked because you completed your first Fitness mission. | با اولین مأموریت حرکت و انرژی‌ات اینجا جا گرفت. | livingSpaceCopy |
| `space.roomObjects.fitness_water_bottle.title` | Water Bottle | بطری آب | livingSpaceCopy |
| `space.roomObjects.learning_book_stack.description` | A visible stack for Learning progress. | یک دسته کتاب که پیشرفت یادگیری‌ات را نشان می‌دهد. | livingSpaceCopy |
| `space.roomObjects.learning_book_stack.title` | Book Stack | دسته کتاب | livingSpaceCopy |
| `space.roomObjects.learning_bookshelf.description` | A shelf that reflects Learning achievements. | قفسه‌ای که دستاوردهای یادگیری‌ات را نشان می‌دهد. | livingSpaceCopy |
| `space.roomObjects.learning_bookshelf.title` | Bookshelf | قفسه کتاب | livingSpaceCopy |
| `space.roomObjects.learning_first_book.description` | Unlocked because you completed your first Learning mission. | با اولین مأموریت یادگیری‌ات اینجا جا گرفت. | livingSpaceCopy |
| `space.roomObjects.learning_first_book.title` | First Book | اولین کتاب | livingSpaceCopy |
| `space.roomObjects.learning_study_lamp.description` | A steady Learning consistency reward. | پاداشی برای ثبات در یادگیری. | livingSpaceCopy |
| `space.roomObjects.learning_study_lamp.title` | Study Lamp | چراغ مطالعه | livingSpaceCopy |
| `space.roomObjects.learning_trophy.description` | A major Learning milestone marker. | نشانه یک نقطه عطف بزرگ در یادگیری. | livingSpaceCopy |
| `space.roomObjects.learning_trophy.title` | Learning Trophy | جام یادگیری | livingSpaceCopy |
| `space.roomObjects.sleep_bedside_lamp.description` | A soft Sleep consistency reward. | پاداشی نرم برای ثبات در خواب. | livingSpaceCopy |
| `space.roomObjects.sleep_bedside_lamp.title` | Bedside Lamp | چراغ خواب | livingSpaceCopy |
| `space.roomObjects.sleep_blanket.description` | A cozy marker for Sleep path progress. | نشانه‌ای دنج برای پیشرفت در مسیر خواب. | livingSpaceCopy |
| `space.roomObjects.sleep_blanket.title` | Blanket | پتو | livingSpaceCopy |
| `space.roomObjects.sleep_moon_decoration.description` | A calm decoration for Sleep achievements. | یک تزئین آرام برای دستاوردهای خواب. | livingSpaceCopy |
| `space.roomObjects.sleep_moon_decoration.title` | Moon Decoration | تزئین ماه | livingSpaceCopy |
| `space.roomObjects.sleep_pillow.description` | Unlocked because you completed your first Sleep mission. | با اولین مأموریت آرامشت اینجا جا گرفت. | livingSpaceCopy |
| `space.roomObjects.sleep_pillow.title` | Pillow | بالش | livingSpaceCopy |
| `space.roomObjects.sleep_trophy.description` | A major Sleep milestone marker. | نشانه یک نقطه عطف بزرگ در خواب و ریکاوری. | livingSpaceCopy |
| `space.roomObjects.sleep_trophy.title` | Recovery Trophy | جام ریکاوری | livingSpaceCopy |

## Reward card (RewardUnlockMoment)

Modal after the Ringo Moment when a room object unlocks.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `spaceUnlock.body` | {reward} appeared in your {zone}. | {reward} در {zone} ظاهر شد. | RewardUnlockMoment |
| `spaceUnlock.continue` | View it in the room | دیدنش در اتاق | RewardUnlockMoment · button |
| `spaceUnlock.defaultDescription` | Unlocked by real progress. | با پیشرفت واقعی باز شد. | RewardUnlockMoment |
| `spaceUnlock.eyebrow` | Room reward | پاداش اتاق | RewardUnlockMoment |
| `spaceUnlock.placedIn` | Placed in: {zone} | قرار گرفت در: {zone} | RewardUnlockMoment |
| `spaceUnlock.room` | room | اتاق | RewardUnlockMoment |
| `spaceUnlock.savedNote` | This object is now saved in your Living Space and will stay after refresh. | این شیء حالا در فضای زندگی‌ات ذخیره شده و بعد از رفرش هم می‌ماند. | RewardUnlockMoment |
| `spaceUnlock.title` | Your room changed | اتاقت تغییر کرد | RewardUnlockMoment |

## Ringo Moment (reward sequence)

RingoRewardSequence modal after a mission is done; step copy from `rewardSequenceBuilder.js` (some backend English is mapped to these keys).

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `common.level` | Level {level} | سطح {level} | rewardSequenceBuilder, Dashboard |
| `missions.dailyMomentum.actions.viewChoices` | View choices | دیدن گزینه‌ها | rewardSequenceBuilder |
| `missions.fallbackChallenge` | your challenge | چالش تو | rewardSequenceBuilder, Dashboard · fallback |
| `missions.fallbackPath` | Your path | مسیر تو | rewardSequenceBuilder, Dashboard · fallback |
| `missions.finishForToday` | Finish for today | امروز رو تمام کن | rewardSequenceBuilder |
| `ringoRewardSequence.backend.addedWinText` | You added another small win to today. | یک برد کوچک دیگر به امروزت اضافه کردی. | rewardSequenceBuilder |
| `ringoRewardSequence.backend.bonusText` | Today was already safe. This was optional extra progress. | امروز از قبل امن بود. این یه پیشرفت اضافه و اختیاری بود. | rewardSequenceBuilder |
| `ringoRewardSequence.backend.bonusTitle` | Bonus momentum. | یه قدم اضافه. | rewardSequenceBuilder |
| `ringoRewardSequence.backend.missionDoneText` | This mission is marked done. | این مأموریت انجام‌شده ثبت شد. | rewardSequenceBuilder · done |
| `ringoRewardSequence.backend.niceWorkTitle` | Nice work. | دمت گرم. | rewardSequenceBuilder |
| `ringoRewardSequence.backend.paceText` | You can stop here, or continue only if you have energy. | می‌تونی همین‌جا تمومش کنی، یا اگه انرژی داری ادامه بدی. | rewardSequenceBuilder |
| `ringoRewardSequence.backend.paceTitle` | Choose your pace. | سرعتت رو خودت انتخاب کن. | rewardSequenceBuilder |
| `ringoRewardSequence.backend.smallStepText` | You did the small step. That counts. | همین قدم کوچک انجام شد. حسابه. | rewardSequenceBuilder |
| `ringoRewardSequence.backend.todaySafeText` | You did enough for today. Anything else is optional. | برای امروز کافی بود. هر کار دیگه‌ای اختیاریه. | rewardSequenceBuilder · today safe |
| `ringoRewardSequence.backend.todaySafeTitle` | Today is safe. | امروزت امنه. | rewardSequenceBuilder · today safe |
| `ringoRewardSequence.backend.xpTitle` | XP earned | XP گرفتی | rewardSequenceBuilder |
| `ringoRewardSequence.continue` | Continue | ادامه | RingoRewardSequence · button |
| `ringoRewardSequence.eyebrow` | Ringo Moment | لحظه رینگو | RingoRewardSequence |
| `ringoRewardSequence.fallbackTitle` | Small win secured | یک برد کوچک ثبت شد | RingoRewardSequence · fallback |
| `ringoRewardSequence.finish` | Finish | تمام | RingoRewardSequence · button |
| `ringoRewardSequence.local.missionFallback` | Mission completed | مأموریت کامل شد | rewardSequenceBuilder · fallback |
| `ringoRewardSequence.local.xpValue` | +{count} XP | +{count} XP | rewardSequenceBuilder |
| `ringoRewardSequence.progress` | Reward progress | پیشرفت پاداش | RingoRewardSequence |
| `ringoRewardSequence.skipSummary` | Skip summary | رد کردن خلاصه | RingoRewardSequence |
| `ringoRewardSequence.staged.bonusCompleteTitle` | Bonus complete | بونس کامل شد | rewardSequenceBuilder · done |
| `ringoRewardSequence.staged.challengeSecuredText` | Today's check-in is recorded. | چک‌این امروزت انجام شد. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.challengeSecuredTitle` | Challenge secured | چالش امروز ثبت شد | rewardSequenceBuilder |
| `ringoRewardSequence.staged.challengeText` | {challenge} moved forward today. | {challenge} امروز جلو رفت. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.challengeTitle` | Challenge strengthened | چالش تقویت شد | rewardSequenceBuilder |
| `ringoRewardSequence.staged.completeTitle` | Mission complete | مأموریت کامل شد | rewardSequenceBuilder · done |
| `ringoRewardSequence.staged.finalText` | You can finish here. If you still have energy, you can view choices. | می‌تونی همین‌جا تمام کنی. اگر هنوز انرژی داری، گزینه‌ها را ببین. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.finalTitle` | Choose your pace | ریتمت را انتخاب کن | rewardSequenceBuilder |
| `ringoRewardSequence.staged.levelText` | Your profile crossed into a new level. | پروفایلت وارد سطح تازه‌ای شد. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.levelTitle` | Level {level} reached | به سطح {level} رسیدی | rewardSequenceBuilder |
| `ringoRewardSequence.staged.missionText` | {mission} is marked done. | {mission} انجام‌شده ثبت شد. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.pathText` | {path} moved forward today. | {path} امروز جلو رفت. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.pathTitle` | Path strengthened | مسیر تقویت شد | rewardSequenceBuilder |
| `ringoRewardSequence.staged.progressValue` | {percent}% today | {percent}٪ امروز | rewardSequenceBuilder |
| `ringoRewardSequence.staged.streakValue` | {count} day streak | استریک {count} روزه | rewardSequenceBuilder |
| `ringoRewardSequence.staged.strikeText` | Today became safe. Your rhythm is protected. | امروزت امن شد. ریتمت محافظت شد. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.strikeTitle` | Strike secured | استرایک امن شد | rewardSequenceBuilder |
| `ringoRewardSequence.staged.tinyCompleteTitle` | Small step. Day protected. | قدم کوچک. امروز محافظت شد. | rewardSequenceBuilder · done |
| `ringoRewardSequence.staged.tinyStrikeTitle` | Small step. Day protected. | قدم کوچک. امروز محافظت شد. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.totalXp` | {count} total XP | مجموع {count} XP | rewardSequenceBuilder |
| `ringoRewardSequence.staged.xpText` | Mission XP was added once for this completion. | XP مأموریت فقط یک بار برای این تکمیل اضافه شد. | rewardSequenceBuilder |
| `ringoRewardSequence.staged.xpTitle` | XP earned | XP گرفتی | rewardSequenceBuilder |
| `ringoRewardSequence.types.challenge_secured` | Challenge | چالش | RingoRewardSequence |
| `ringoRewardSequence.types.challenge_strengthened` | Challenge | چالش | RingoRewardSequence |
| `ringoRewardSequence.types.default` | Moment | لحظه | RingoRewardSequence |
| `ringoRewardSequence.types.final_choice` | Next | بعدی | RingoRewardSequence |
| `ringoRewardSequence.types.level_up` | Level | سطح | RingoRewardSequence |
| `ringoRewardSequence.types.mission_complete` | Mission | مأموریت | RingoRewardSequence · done |
| `ringoRewardSequence.types.mission_completed` | Mission | مأموریت | RingoRewardSequence · done |
| `ringoRewardSequence.types.next_choice` | Next | بعدی | RingoRewardSequence |
| `ringoRewardSequence.types.path_strengthened` | Path | مسیر | RingoRewardSequence |
| `ringoRewardSequence.types.progress_impact` | Progress | پیشرفت | RingoRewardSequence |
| `ringoRewardSequence.types.ringo_message` | Ringo | رینگو | RingoRewardSequence |
| `ringoRewardSequence.types.strike_secured` | Strike | استرایک | RingoRewardSequence |
| `ringoRewardSequence.types.today_saved` | Today saved | امروز امن شد | RingoRewardSequence |
| `ringoRewardSequence.types.xp_earned` | XP | XP | RingoRewardSequence |

## Bonus and tiny (smaller step) offers

BonusOfferCard and the smaller-step / intensity labels in the zone panel.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `space.panel.actionSmaller` | Make it smaller | کوچیک‌ترش کن | SpaceZonePanel · button |
| `space.panel.bonusAnother` | Another suggestion | پیشنهاد دیگه | BonusOfferCard |
| `space.panel.bonusDoIt` | I'll do it | انجامش می‌دم | BonusOfferCard |
| `space.panel.bonusFocusTitle` | Extra step: {mission}. | قدم اضافه: {mission}. | SpaceZonePanel |
| `space.panel.bonusLabel` | Extra step · optional | قدم اضافه · اختیاری | BonusOfferCard · label / screen reader |
| `space.panel.bonusMetaSuffix` | no pressure on today's progress | روی پیشرفت امروزت فشاری نمیاره | SpaceZonePanel |
| `space.shell.intensity.bonus` | Bonus | بونوس | ChallengeTodayMissions, SpaceZonePanel |
| `space.shell.intensity.main` | Main mission | مأموریت اصلی | ChallengeTodayMissions, SpaceZonePanel |
| `space.shell.intensity.tiny` | Tiny | کوچک | ChallengeTodayMissions, SpaceZonePanel |
| `space.shell.tinyLivingSpaceGate` | Tiny is not a parallel room action. Ask Ringo to make the main mission smaller when you need the lighter version. | نسخه کوچک اکشن موازی اتاق نیست. وقتی نسخه سبک‌تر می‌خواهی، اول از رینگو بخواه مأموریت اصلی را کوچک کند. | SpaceZonePanel |

## Reminders

Reminder list, badges and markers (zone panel, room markers, aria), remind-later options.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `missions.remindOptions.evening` | Evening | عصر | SpaceZonePanel |
| `missions.remindOptions.fifteenMinutes` | 15 minutes | ۱۵ دقیقه دیگر | SpaceZonePanel |
| `missions.remindOptions.oneHour` | 1 hour | ۱ ساعت دیگر | SpaceZonePanel |
| `missions.remindOptions.prompt` | Okay. When should I remind you? | باشه مشتی. کی صدات کنم؟ | SpaceZonePanel |
| `missions.remindOptions.tonight` | Tonight | امشب | SpaceZonePanel |
| `space.panel.reminderBadge` | Reminder time | یادآور رسیده | ChallengeTodayMissions, SpaceZonePanel |
| `space.panel.reminderBody` | You asked me to remind you now. If now still isn't the time, that's okay. | خودت خواسته بودی الان یادت بندازم. اگه الان هم وقتش نیست، اشکالی نداره. | SpaceZonePanel |
| `space.panel.reminderNoTime` | Scheduled | زمان‌بندی‌شده | SpaceZonePanel · empty |
| `space.panel.reminderPriorityNote` | A reminder you set always comes before extra suggestions. The extra step is still here after this. | یادآوری که خودت گذاشتی همیشه جلوتر از پیشنهادهای اضافه میاد. قدم اضافه بعد از این دوباره در دسترسه. | SpaceZonePanel |
| `space.panel.reminderReady` | Ready now | رسیده | SpaceZonePanel |
| `space.panel.reminderTitle` | It's time: {mission}. | وقتشه: {mission}. | SpaceZonePanel |
| `space.panel.reminderWhere` | {zone} · {path} | {zone} · {path} | SpaceZonePanel |
| `space.panel.rowReminders` | Reminders | یادآورها | SpaceZonePanel |
| `space.panel.scheduledMarker` | Reminder scheduled later today | یادآور برای بعداً امروز تنظیم شده | SpaceZone |
| `space.panel.timeLeftHours` | {hours} h left | {hours} ساعت دیگه | SpaceZonePanel |
| `space.panel.timeLeftHoursMinutes` | {hours} h {minutes} min left | {hours} ساعت و {minutes} دقیقه دیگه | SpaceZonePanel |
| `space.panel.timeLeftMinutes` | {minutes} min left | {minutes} دقیقه دیگه | SpaceZonePanel |
| `space.scene.reminderDue` | reminder due | یادآور رسیده | RoomScene · due reminder |
| `space.scene.reminderScheduled` | reminder scheduled | یادآور تنظیم شده | RoomScene |
| `space.shell.restReminderClear` | No overdue reminders | یادآور عقب‌افتاده نداری | SpaceZonePanel · rest |
| `space.shell.restReminderDue` | {count} overdue reminder | {count} یادآور عقب‌افتاده | SpaceZonePanel · due reminder |
| `space.shell.restReminderFuture` | {count} reminder scheduled for later | {count} یادآور برای بعد تنظیم شده | SpaceZonePanel · rest |
| `space.shell.restReminderReview` | Review reminder | بررسی یادآور | SpaceZonePanel · rest |
| `space.zoneState.reminderDue` | Reminder due | یادآور عقب‌افتاده | SpaceZone · due reminder |

## Skip reasons

"Not today" choice panel in the zone panel.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `missions.skipReasons.dontLike` | Don’t like this mission | این مأموریت رو دوست ندارم | SpaceZonePanel |
| `missions.skipReasons.noTime` | No time | وقت ندارم | SpaceZonePanel · empty |
| `missions.skipReasons.notRelevant` | Not relevant now | الان به کارم نمیاد | SpaceZonePanel |
| `missions.skipReasons.other` | Other | دلیل دیگر | SpaceZonePanel |
| `missions.skipReasons.prompt` | That’s okay. Help me understand why, only if you want to. | اشکالی نداره. اگر خواستی کمکم کن بفهمم چرا. | SpaceZonePanel |
| `missions.skipReasons.tooHard` | Too hard | خیلی سخت بود | SpaceZonePanel |
| `missions.skipReasons.tooTired` | Too tired | خیلی خسته‌ام | SpaceZonePanel |
| `missions.skipReasons.withoutReason` | Skip without reason | بدون دلیل رد کن | SpaceZonePanel |

## Today strip and today list

ZoneTodayStrip and ChallengeTodayMissions in the zone panel.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `space.panel.afterMain` | After the main step | بعد از قدم اصلی | ChallengeTodayMissions |
| `space.panel.futureMissions` | Later in this challenge: {count} more missions | بعداً در این چالش: {count} مأموریت دیگه | ChallengeTodayMissions |
| `space.panel.ringoPick` | Ringo's pick | پیشنهاد رینگو | ChallengeTodayMissions |
| `space.panel.todayList` | Today | امروز | ChallengeTodayMissions |
| `space.panel.todayStrip` | Today in this corner | امروز در این گوشه | ZoneTodayStrip |
| `space.shell.minutes` | {count} min | {count} دقیقه | ChallengeTodayMissions, SpaceZonePanel |
| `space.shell.todayMissions` | Today missions | مأموریت‌های امروز | ZoneTodayStrip |

## Details accordion (path & challenges, objects)

ZoneDetailsRow rows in the zone panel.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `space.panel.fullPath` | See the full path | دیدن کامل مسیر | SpaceZonePanel |
| `space.panel.rowObjects` | Objects in this corner | اشیای این گوشه | SpaceZonePanel |
| `space.panel.rowPath` | Path & challenges | مسیر و چالش‌ها | SpaceZonePanel |
| `space.shell.noPathChallenges` | No challenges are connected to this path yet. | هنوز چالشی به این مسیر وصل نشده. | SpaceZonePanel · empty |
| `space.shell.pathLoading` | Loading this path’s challenge map... | در حال آوردن نقشه چالش‌های این مسیر... | SpaceZonePanel · loading |
| `space.shell.pathProgress` | Path progress | پیشرفت مسیر | SpaceZonePanel |
| `space.shell.pathProgressCount` | {done}/{total} progress units | {done}/{total} واحد پیشرفت | SpaceZonePanel |

## Ringo card

RingoActionCard (zone panel and room overview): Ringo's line, actions and back links.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `missions.backToMissionActions` | Back | برگشت | RingoActionCard |
| `space.panel.back` | Back | برگرد | RingoActionCard |
| `space.ringoGuide.bonusReadyMessage` | The main step is done, so {mission} is extra momentum, not required progress. | قدم اصلی انجام شده، پس {mission} شتاب اضافه است، نه پیشرفت اجباری. | SpaceZonePanel |
| `space.ringoGuide.challengePreviewMessage` | {challenge} belongs to {path}. Start it only when you want this challenge to become the active mission track. | {challenge} به {path} وصل است. فقط وقتی شروعش کن که می‌خواهی مسیر مأموریت فعال این چالش شود. | SpaceZonePanel · preview / not joined |
| `space.ringoGuide.challengePreviewTitle` | This challenge can be your next room step | این چالش می‌تواند قدم بعدی اتاق باشد | SpaceZonePanel · preview / not joined |
| `space.ringoGuide.eyebrow` | Ringo | رینگو | RingoActionCard, RoomOverviewPanel, SpaceZonePanel |
| `space.ringoGuide.fallbackMessage` | Choose what you want to inspect in {path}; I’ll keep the next useful action visible. | هر چیزی را که در {path} می‌خواهی بررسی کن؛ من قدم مفید بعدی را جلوی چشم نگه می‌دارم. | SpaceZonePanel · fallback |
| `space.ringoGuide.fallbackTitle` | Pick a room zone | یک بخش از اتاق را انتخاب کن | SpaceZonePanel · fallback |
| `space.ringoGuide.lockedTitle` | This step has a condition | این قدم شرط دارد | SpaceZonePanel · locked |
| `space.ringoGuide.missionDoneMessage` | {mission} is done. The room should now preserve that progress. | {mission} انجام شده. اتاق باید این پیشرفت را نگه دارد. | SpaceZonePanel · done |
| `space.ringoGuide.missionDoneTitle` | Mission already counted | مأموریت حساب شده | SpaceZonePanel · done |
| `space.ringoGuide.missionFocusMessage` | {mission} is the action that moves the room today. Finish this before bonus steps. | {mission} همان کاری است که امروز اتاق را جلو می‌برد. قبل از بونوس، همین را تمام کن. | SpaceZonePanel |
| `space.ringoGuide.readyMessage` | {path} has a live mission. Do the main step first; tiny only appears when you ask Ringo to make it smaller. | {path} یک مأموریت فعال دارد. اول قدم اصلی را انجام بده؛ نسخه کوچک فقط وقتی باز می‌شود که از رینگو بخواهی مأموریت را کوچک‌تر کند. | SpaceZonePanel |
| `space.ringoGuide.readyTitle` | Best next step is ready | بهترین قدم بعدی آماده است | SpaceZonePanel |
| `space.ringoGuide.restReminderTitle` | One reminder still needs a look | یک یادآور هنوز نیاز به توجه دارد | SpaceZonePanel · rest |
| `space.ringoGuide.restTitle` | Rest inside your room | داخل اتاقت استراحت کن | SpaceZonePanel · rest |
| `space.ringoGuide.startMessage` | {path} does not have an active challenge yet. Pick the first challenge so this room zone can react to real progress. | {path} هنوز چالش فعال ندارد. اولین چالش را انتخاب کن تا این بخش اتاق به پیشرفت واقعی واکنش نشان بدهد. | SpaceZonePanel · start (no active challenge) |
| `space.ringoGuide.startTitle` | Start with one real step | از یک قدم واقعی شروع کن | SpaceZonePanel · start (no active challenge) |
| `space.zoneAction.browseChallenges` | Browse challenges | مرور چالش‌ها | LivingSpace |
| `space.zoneAction.continueMission` | Continue mission | ادامه مأموریت | LivingSpace |
| `space.zoneAction.doneText` | This path already counted today. You can review it or choose another path. | این مسیر امروز حساب شده. می‌توانی جزئیاتش را ببینی یا سراغ مسیر دیگری بروی. | LivingSpace · done |
| `space.zoneAction.doneTitle` | {challenge} is secured today | {challenge} امروز ثبت شده | LivingSpace · done |
| `space.zoneAction.notStartedText` | Start from the path page to connect this room zone to a real daily mission. | از صفحه مسیرها شروع کن تا این بخش اتاق به یک مأموریت روزانه واقعی وصل شود. | LivingSpace · start (no active challenge) |
| `space.zoneAction.notStartedTitle` | No active challenge in this path yet | هنوز چالش فعالی در این مسیر نداری | LivingSpace · start (no active challenge) |
| `space.zoneAction.readyText` | Continue the active challenge for this path and secure today's mission. | چالش فعال این مسیر را ادامه بده و مأموریت امروز را ثبت کن. | LivingSpace |
| `space.zoneAction.readyTitle` | {challenge} is ready today | {challenge} امروز آماده است | LivingSpace |
| `space.zoneAction.reviewChallenge` | Review challenge | دیدن چالش | LivingSpace |
| `space.zoneAction.startPath` | Start this path | شروع این مسیر | LivingSpace · start (no active challenge) |
| `space.zoneAction.viewPath` | View path | دیدن مسیر | LivingSpace |

## Room overview and rest

RoomOverviewPanel (room level after Back to room / Enough for today), overview guidance and room feedback.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `space.eyebrow` | Living Space | فضای زندگی | RoomOverviewPanel, SpaceZonePanel |
| `space.feedback.progressLabel` | Progress saved | پیشرفت ذخیره شد | LivingSpace · label / screen reader |
| `space.feedback.progressText` | {zone} moved forward. No new object unlocked this time, but the room state is up to date. | {zone} جلو رفت. این بار شیء تازه‌ای باز نشد، اما وضعیت اتاق به‌روز است. | LivingSpace |
| `space.feedback.progressTitle` | The room kept this progress | اتاق این پیشرفت را نگه داشت | LivingSpace |
| `space.feedback.rewardLabel` | Object placed | شیء قرار گرفت | LivingSpace · label / screen reader |
| `space.feedback.rewardText` | {reward} is now visible in {zone}. This came from real mission progress. | {reward} حالا در {zone} دیده می‌شود. این از پیشرفت واقعی مأموریت آمد. | LivingSpace |
| `space.feedback.rewardTitle` | {reward} joined the room | {reward} وارد اتاق شد | LivingSpace |
| `space.firstRewardPlaced` | First reward placed: {reward}. Later previews stay locked until their rules are defined. | اولین پاداش قرار گرفت: {reward}. پیش‌نمایش‌های بعدی تا مشخص شدن قانونشان قفل می‌مانند. | SpaceZonePanel |
| `space.overview.progressCta` | Review room | مرور اتاق | LivingSpace · button |
| `space.overview.progressText` | {count} visible objects are saved from real progress. | {count} شیء قابل دیدن از پیشرفت واقعی ذخیره شده. | LivingSpace |
| `space.overview.progressTitle` | Your room is keeping score | اتاقت پیشرفت را نگه می‌دارد | LivingSpace |
| `space.overview.readyCta` | Open mission | باز کردن مأموریت | LivingSpace · button |
| `space.overview.readyText` | One real mission can move this part of the room today. | یک مأموریت واقعی می‌تواند امروز این بخش اتاق را جلو ببرد. | LivingSpace |
| `space.overview.readyTitle` | {path} is ready | {path} آماده است | LivingSpace |
| `space.overview.reminderCta` | Review reminders | مرور یادآورها | LivingSpace · button |
| `space.overview.reminderText` | Overdue reminders: {count}. Review them before the room settles for today. | {count} یادآور از زمانش گذشته. قبل از آرام شدن اتاق، مرورش کن. | LivingSpace |
| `space.overview.reminderTitle` | Reminder waiting in {path} | یادآور در {path} منتظر است | LivingSpace |
| `space.overview.safeCta` | Rest here | همین‌جا استراحت کن | LivingSpace · button |
| `space.overview.safeText` | The room can hold this win. Rest is a valid next step. | اتاق می‌تواند این برد را نگه دارد. استراحت هم قدم بعدی معتبر است. | LivingSpace · today safe |
| `space.overview.safeTitle` | Today is safe | امروز امن است | LivingSpace · today safe |
| `space.overview.startCta` | Preview path | پیش‌نمایش مسیر | LivingSpace · button |
| `space.overview.startText` | Choose one first path so the room can begin reacting to real progress. | یک مسیر اول انتخاب کن تا اتاق با پیشرفت واقعی شروع به واکنش کند. | LivingSpace · start (no active challenge) |
| `space.overview.startTitle` | Start with {path} | از {path} شروع کن | LivingSpace · start (no active challenge) |
| `space.panel.backToRoom` | Back to room | بازگشت به اتاق | SpaceZonePanel |
| `space.room.invite` | Or pick any corner of the room to continue. | یا هر گوشه‌ای از اتاق رو که دوست داری انتخاب کن. | RoomOverviewPanel |
| `space.room.missionsDone` | Missions done today | مأموریت‌های انجام‌شده امروز | RoomOverviewPanel · done |
| `space.room.objectsToday` | Objects placed today | اشیای جدید امروز | RoomOverviewPanel |
| `space.room.openZone` | Go to {zone} | رفتن به {zone} | RoomOverviewPanel |
| `space.room.remindersLabel` | Reminders | یادآورها | RoomOverviewPanel · label / screen reader |
| `space.room.remindersValue` | {due} due · {scheduled} later | {due} رسیده · {scheduled} بعداً | RoomOverviewPanel |
| `space.room.suggestLabel` | Ringo suggests | پیشنهاد رینگو | RoomOverviewPanel, RoomScene, SpaceZone · label / screen reader |
| `space.room.summaryLabel` | Today so far | امروز تا الان | RoomOverviewPanel · label / screen reader |
| `space.shell.restLabel` | Rest day | روز استراحت | SpaceZonePanel · rest |
| `space.shell.restMomentDue` | Today is nearly settled, but {count} reminder is past its time. | امروز تقریباً جمع شده، اما {count} یادآور از زمانش گذشته است. | SpaceZonePanel · due reminder |
| `space.shell.restMomentQuiet` | Pause here for a moment; I’ll keep the room and next step organized. | یک لحظه همین‌جا مکث کن؛ من اتاق و قدم بعدی را مرتب نگه می‌دارم. | SpaceZonePanel · rest |
| `space.shell.restMomentSafe` | Today is safe. You can stop here and let the room hold the win. | امروز امن است. می‌توانی همین‌جا بایستی و برد امروز را به اتاق بسپاری. | SpaceZonePanel · today safe |
| `space.shell.restSummaryOpenValue` | Open | باز | RoomOverviewPanel · rest |
| `space.shell.restSummarySafeLabel` | Today | امروز | RoomOverviewPanel · today safe |
| `space.shell.restSummarySafeValue` | Safe | امن | RoomOverviewPanel · today safe |
| `space.title` | Your progress room | اتاق پیشرفت تو | LivingSpace, RoomOverviewPanel |

## Room scene, loading and fallback grid

RoomScene aria labels, loading/error states, and SpaceZone (fallback grid when the room art cannot load).

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `common.pleaseTryAgain` | Please try again. | لطفا دوباره تلاش کنید. | LivingSpace, Dashboard, Onboarding |
| `space.errorTitle` | Room could not load | اتاق بارگذاری نشد | LivingSpace · error |
| `space.loadingText` | Checking which objects you have earned. | داریم بررسی می‌کنیم چه چیزهایی را به دست آورده‌ای. | LivingSpace · loading |
| `space.loadingTitle` | Loading your room... | در حال بارگذاری اتاق... | LivingSpace · loading |
| `space.roomLabel` | Living Space room zones | بخش‌های اتاق فضای زندگی | LivingSpace, RoomScene · label / screen reader |
| `space.scene.objectsPlaced` | no objects placed \| 1 object placed \| {count} objects placed | هنوز شیئی قرار نگرفته \| 1 شیء قرار گرفته \| {count} شیء قرار گرفته | RoomScene |
| `space.zoneState.clear` | Clear | کامل | SpaceZone |
| `space.zoneState.done` | Done | ثبت شد | SpaceZone · done |
| `space.zoneState.ready` | Ready | آماده | SpaceZone |
| `space.zoneState.start` | Start | شروع | SpaceZone · start (no active challenge) |

## First-run and onboarding texts that touch the room

Onboarding steps (path choice with room preview, challenge suggestion, handoff) and the dashboard first-run card. Only keys whose EN text mentions the room, a corner, an object, a reward, the space or Ringo are listed; the rest are named below the table.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `dashboard.onboardingFallback.title` | Finish your Ringo start first. | اول شروع رینگو رو کامل کن. | Dashboard · fallback |
| `onboarding.handoff.hints.reward.text` | Ringo turns the action into XP, streak, and visible momentum. | رینگو این قدم رو تبدیل می‌کنه به XP، استریک و شتاب قابل دیدن. | Onboarding |
| `onboarding.loadingText` | Ringo is finding a clean way to begin. | رینگو داره ساده‌ترین شروع رو پیدا می‌کنه. | Onboarding · loading |
| `onboarding.path.body` | Choose one direction for today. Preview how that path changes your room before you continue. | برای امروز فقط یک جهت انتخاب کن. قبل از ادامه ببین این مسیر چطور اتاقت رو تغییر می‌ده. | StepPath |
| `onboarding.path.continueWithCount` | Continue | ادامه | StepPath |
| `onboarding.path.defaultPath` | Daily Consistency | ثبات روزانه | ChallengeSuggestion |
| `onboarding.path.eyebrow` | Identity path | مسیر هویت | StepPath |
| `onboarding.path.firstRewardFallback` | first room object | اولین شیء اتاق | StepPath · fallback |
| `onboarding.path.previewHint` | {path} starts by unlocking {reward} after your first mission. | با اولین مأموریت این مسیر، {reward} در اتاقت جا می‌گیرد. | StepPath · preview / not joined |
| `onboarding.path.roomPreviewLabel` | Preview how each path changes your Living Space | پیش‌نمایش تغییرات هر مسیر در فضای زندگی | StepPath · preview / not joined |
| `onboarding.path.roomPreviewTitle` | Room preview | پیش‌نمایش اتاق | StepPath · preview / not joined |
| `onboarding.path.roomZone` | Zone: {zone} | بخش: {zone} | StepPath |
| `onboarding.path.title` | What do you want to build first? | اول می‌خوای چی رو بسازی؟ | StepPath |
| `onboarding.paths.body.label` | Body | بدن و حرکت | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.body.outcome` | Feel a little more alive today. | امروز یکم بیشتر زنده و پرانرژی شو. | StepPath |
| `onboarding.paths.career.firstReward` | Career Planner | برنامه‌ریز کار | StepPath |
| `onboarding.paths.career.label` | Career | کار و مسیر حرفه‌ای | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.career.outcome` | Protect one clean work session. | یک جلسه کار تمیز و محافظت‌شده بساز. | StepPath |
| `onboarding.paths.career.zone` | Work Desk | میز کار | StepPath |
| `onboarding.paths.consistency.label` | Daily Consistency | ثبات روزانه | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.consistency.outcome` | Build the habit of showing up. | عادتِ حاضر شدن رو بساز. | StepPath |
| `onboarding.paths.creativity.firstReward` | Sketchbook | دفتر طراحی | StepPath |
| `onboarding.paths.creativity.label` | Creativity | خلاقیت | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.creativity.outcome` | Keep making with one small spark. | با یک جرقه کوچک، ساختن رو زنده نگه دار. | StepPath |
| `onboarding.paths.creativity.zone` | Creative Corner | گوشه خلاقیت | StepPath |
| `onboarding.paths.fitness.firstReward` | Water Bottle | بطری آب | StepPath |
| `onboarding.paths.fitness.label` | Fitness | بدن و حرکت | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.fitness.outcome` | Feel a little more alive today. | امروز یکم بیشتر زنده و پرانرژی شو. | StepPath |
| `onboarding.paths.fitness.zone` | Fitness Corner | گوشه حرکت | StepPath |
| `onboarding.paths.focus.label` | Focus | تمرکز | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.focus.outcome` | Win one clean work session. | یک جلسه کار تمیز و بی‌حواس‌پرتی ببر. | StepPath |
| `onboarding.paths.learning.firstReward` | First Book | اولین کتاب | StepPath |
| `onboarding.paths.learning.label` | Learning | یادگیری | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.learning.outcome` | Learn one small thing without pressure. | بدون فشار، فقط یک چیز کوچک یاد بگیر. | StepPath |
| `onboarding.paths.learning.zone` | Learning Corner | گوشه یادگیری | StepPath |
| `onboarding.paths.mind.label` | Mind Reset | آرامش ذهن | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.mind.outcome` | Calm the noise a little. | یکم صدای ذهن رو آروم‌تر کن. | StepPath |
| `onboarding.paths.sleep.firstReward` | Pillow | بالش | StepPath |
| `onboarding.paths.sleep.label` | Sleep | خواب و ریکاوری | ChallengeSuggestion, StepPath · label / screen reader |
| `onboarding.paths.sleep.outcome` | Make tonight a little calmer. | امشب رو کمی آرام‌تر کن. | StepPath |
| `onboarding.paths.sleep.zone` | Sleep Corner | گوشه خواب | StepPath |
| `onboarding.suggestion.title` | Ringo picked a starter challenge. | رینگو یک چالش خوب برای شروع انتخاب کرد. | ChallengeSuggestion |
| `onboarding.welcome.cta` | Start with Ringo | شروع با رینگو | StepWelcome · button |
| `onboarding.welcome.eyebrow` | Meet Ringo | آشنایی با رینگو | StepWelcome |
| `onboarding.welcome.title` | Meet Ringo. Start with one small win. | با رینگو شروع کن؛ فقط یک برد کوچیک. | StepWelcome |
| `ringoCoach.eyebrow` | Ringo guidance | راهنمایی رینگو | RingoMoodFigure |

Other first-run keys used by the same components (no room wording, not listed): `dashboard.firstRunFocus.dismiss`, `dashboard.firstRunFocus.done`, `dashboard.firstRunFocus.eyebrow`, `dashboard.firstRunFocus.remind`, `dashboard.firstRunFocus.skip`, `dashboard.firstRunFocus.smaller`, `dashboard.firstRunFocus.text`, `dashboard.firstRunFocus.title`, `dashboard.onboardingFallback.cta`, `dashboard.onboardingFallback.eyebrow`, `dashboard.onboardingFallback.text`, `onboarding.errorTitle`, `onboarding.handoff.body`, `onboarding.handoff.cta`, `onboarding.handoff.eyebrow`, `onboarding.handoff.fallbackMission`, `onboarding.handoff.hints.choice.text`, `onboarding.handoff.hints.choice.title`, `onboarding.handoff.hints.reward.title`, `onboarding.handoff.hints.safe.text`, `onboarding.handoff.hints.safe.title`, `onboarding.handoff.readyPill`, `onboarding.handoff.text`, `onboarding.handoff.title`, `onboarding.loadingTitle`, `onboarding.suggestion.alreadyJoined`, `onboarding.suggestion.alternativesTitle`, `onboarding.suggestion.bestStart`, `onboarding.suggestion.body`, `onboarding.suggestion.browse`, `onboarding.suggestion.chooseText`, `onboarding.suggestion.chooseTitle`, `onboarding.suggestion.eyebrow`, `onboarding.suggestion.fallbackPill`, `onboarding.suggestion.fallbackText`, `onboarding.suggestion.fallbackTitle`, `onboarding.suggestion.laterNotice`, `onboarding.suggestion.noDescription`, `onboarding.suggestion.recommended`, `onboarding.suggestion.skip`, `onboarding.suggestion.startSelected`, `onboarding.welcome.body`.

## Room (zone) panel: other states

SpaceZonePanel: header, Ringo card states (start, preview, mission, done, safe, locked, rest), actions and empty/loading states.

| i18n key | EN | FA | where it appears (component / state) |
|---|---|---|---|
| `common.challenge` | Challenge | چالش | ChallengeSuggestion, LivingSpace, SpaceZonePanel |
| `common.dayChallenge` | {count} day challenge | چالش {count} روزه | ChallengeSuggestion |
| `common.mission` | Mission | مأموریت | LivingSpace, SpaceZonePanel |
| `space.panel.actionDone` | I did it | انجامش دادم | SpaceZonePanel · button |
| `space.panel.actionFinishToday` | Enough for today | برای امروز کافیه | SpaceZonePanel · button |
| `space.panel.actionNotToday` | Not today | امروز نه | SpaceZonePanel · button |
| `space.panel.actionRemind` | Remind me later | بعداً یادم بنداز | SpaceZonePanel · button |
| `space.panel.actionRemindAgain` | Later again | باز هم بعداً | SpaceZonePanel · button |
| `space.panel.collapsedSafe` | This corner is safe today. | این گوشه امروز امنه. | SpaceZonePanel · today safe |
| `space.panel.doneBody` | That's enough for today. If you still have energy, there's a small extra step too, completely optional. | برای امروز همین کافیه. اگه هنوز انرژی داری، یک قدم کوچیک اضافه هم هست؛ کاملاً اختیاری. | SpaceZonePanel · done |
| `space.panel.doneBodyNoBonus` | That's enough for today. Your room moved forward today. | برای امروز همین کافیه. اتاقت امروز یک قدم جلو رفت. | SpaceZonePanel · done |
| `space.panel.doneTitle` | Today's main step is done. | قدم اصلی امروز انجام شد. | SpaceZonePanel · done |
| `space.panel.firstRewardHint` | Finish a main or smaller mission in this path to place {object} in your room. | یک مأموریت اصلی یا کوچیک از این مسیر انجام بده تا {object} در اتاقت جا بگیره. | SpaceZonePanel |
| `space.panel.missionBody` | {minutes} minutes is enough. This one step keeps today safe and moves your room forward. | {minutes} دقیقه کافیه. همین یک قدم امروزت رو امن می‌کنه و اتاقت رو جلو می‌بره. | SpaceZonePanel |
| `space.panel.missionTitle` | Today's step: {mission}. | قدم امروز: {mission}. | SpaceZonePanel |
| `space.panel.stateSafe` | Today is safe | امروز امنه | SpaceZonePanel · today safe |
| `space.shell.bonusLockedGate` | Locked until the main mission is done. Finish the main step first, then this bonus becomes optional extra momentum. | تا وقتی مأموریت اصلی انجام نشود قفل است. اول قدم اصلی را کامل کن، بعد این بونوس به عنوان شتاب اضافه باز می‌شود. | SpaceZonePanel · locked |
| `space.shell.missionLockedGate` | Locked for now. Keep following the current mission to open this step. | فعلاً قفل است. قدم فعلی را ادامه بده تا این مرحله باز شود. | SpaceZonePanel · locked |
| `space.shell.startChallenge` | Start challenge | شروع چالش | SpaceZonePanel · start (no active challenge) |
| `space.shell.statusAvailable` | Available | در دسترس | SpaceZonePanel |
| `space.shell.statusCurrent` | Current step | قدم فعلی | SpaceZonePanel |
| `space.shell.statusDoneToday` | Secured today | امروز ثبت شده | SpaceZonePanel · done |
| `space.shell.statusJoined` | Joined | شروع‌شده | SpaceZonePanel |
| `space.shell.statusRecommended` | Recommended next | پیشنهاد بعدی | SpaceZonePanel |
| `space.shell.unlocksInDays` | Locked today. This opens in {count} days if you keep this challenge active. | امروز قفل است. اگر این چالش را ادامه بدهی {count} روز دیگر باز می‌شود. | SpaceZonePanel |
| `space.shell.unlocksTomorrow` | Locked today. This opens tomorrow if you keep this challenge active. | امروز قفل است. اگر این چالش را ادامه بدهی فردا باز می‌شود. | SpaceZonePanel |
| `space.shell.xp` | +{count} XP | +{count} XP | SpaceZonePanel |

## Hard-coded strings (not in i18n)

These are the user-visible text and separators that are written directly in code. There is no hard-coded English sentence in the Living Space templates; everything else goes through `t()`.

| What | Where | Note |
|---|---|---|
| `i` (info button glyph) | `components/space/LivingSpace.vue:46` | Visible glyph. Its accessible name is i18n (`space.roomInfoLabel`). |
| `": "` and `", "` joining the zone name and its states | `components/space/RoomScene.vue:446` (zone button `aria-label`) | Screen-reader text. In FA it should use `،` and an i18n pattern. |
| `": "` joining the object title and its state | `components/space/SpaceObject.vue:42` (`aria-label`, fallback grid) | Same as above. |
| ` · ` and `{done}/{total}` | `components/space/ZoneTodayStrip.vue:6` | Separator and the count format are not in i18n. |
| ` · ` before the minutes | `components/space/ChallengeTodayMissions.vue:45` | Separator. |
| `{doneCount}/{missionCount}` | `components/space/ChallengeTodayMissions.vue:22` | Count format. |
| ` · ` joining the bonus meta parts | `components/space/SpaceZonePanel.vue:548` | Separator. |
| `{percent}%` path progress meta | `components/space/SpaceZonePanel.vue:57`; `components/space/SpaceZone.vue:69` (fallback grid) | Percent format. |
| `{completed}/{total}` | `components/space/RoomOverviewPanel.vue:21` (inside `<bdi dir="ltr">`) | Count format, forced LTR. |
| `{done}/{total}` | `components/space/SpaceZone.vue:70` (fallback grid) | Count format. |
| `→` between old and new values, and the `→` arrow | `components/ringo/RingoRewardSequence.vue:23` and `:120` | The arrow does not flip in RTL (it reads backwards in FA). |
| `?` / the first letter of the title | `components/space/RewardUnlockMoment.vue:89` | The letter placeholder; only shown when the object has no PNG (B21). |

## Backend-sourced English

These strings come from the API in English, and the frontend localizes them by key or by exact text match:

- **Zone titles:** `ZONE_DEFS` in `backend/services/living_space_service.py` ("Work Desk", "Creative Corner", "Fitness Corner", "Learning Corner", "Sleep Corner"). Replaced by `space.zoneNames.*`; the backend title shows only if a key is missing.
- **Reward titles and descriptions:** from `reward_definitions`. Replaced by `space.roomObjects.<reward key>.title|description` when the key exists (all current rewards have both, listed above). A new reward without keys would show its English DB text in FA.
- **Ringo Moment step copy:** the backend `reward_sequence` sends English sentences. `utils/rewardSequenceBuilder.js` (`BACKEND_STEP_COPY`, 11 entries) maps the exact English text to `ringoRewardSequence.backend.*`. Any backend sentence that changes or is not in the map shows in English in FA.
- **Challenge and mission titles and descriptions** (seeded content): localized by `ringoContentLocalization.js`, outside this export.

## Where FA currently shows Latin digits

vue-i18n does not convert digits, so every number interpolated into a string or rendered directly shows Latin digits (0–9) in FA. The one exception is the reminder time-left label (`space.panel.timeLeft*`): `SpaceZonePanel.vue:940` formats its hours and minutes with `Intl.NumberFormat(locale)`, so FA shows Persian digits there (۱ ساعت و ۵ دقیقه).

**Rendered directly in templates** (Latin digits in FA):
- Room overview "Today so far": `completed/total` missions (forced LTR) and objects placed today (`RoomOverviewPanel.vue:21, 35`).
- Today strip `done/total` (`ZoneTodayStrip.vue:6`) and the per-challenge `done/total` (`ChallengeTodayMissions.vue:22`).
- Path progress percent in the details row (`SpaceZonePanel.vue:57`).
- Fallback grid (`SpaceZone.vue:69–70`): percent and `done/total`.
- Ringo Moment old → new values and the progress bar labels (`RingoRewardSequence.vue:120`).

**Written into the FA text itself:** `space.scene.objectsPlaced` has a literal Latin `1` in its FA singular form ("1 شیء قرار گرفته").

**Interpolated into i18n strings** (Latin digits in FA, except the `timeLeft*` keys):

- `space.objects`: {count} شیء
- `common.level`: سطح {level}
- `ringoRewardSequence.local.xpValue`: +{count} XP
- `ringoRewardSequence.staged.levelTitle`: به سطح {level} رسیدی
- `ringoRewardSequence.staged.progressValue`: {percent}٪ امروز
- `ringoRewardSequence.staged.streakValue`: استریک {count} روزه
- `ringoRewardSequence.staged.totalXp`: مجموع {count} XP
- `space.panel.timeLeftHours`: {hours} ساعت دیگه
- `space.panel.timeLeftHoursMinutes`: {hours} ساعت و {minutes} دقیقه دیگه
- `space.panel.timeLeftMinutes`: {minutes} دقیقه دیگه
- `space.shell.restReminderDue`: {count} یادآور عقب‌افتاده
- `space.shell.restReminderFuture`: {count} یادآور برای بعد تنظیم شده
- `space.panel.futureMissions`: بعداً در این چالش: {count} مأموریت دیگه
- `space.shell.minutes`: {count} دقیقه
- `space.shell.pathProgressCount`: {done}/{total} واحد پیشرفت
- `space.overview.progressText`: {count} شیء قابل دیدن از پیشرفت واقعی ذخیره شده.
- `space.overview.reminderText`: {count} یادآور از زمانش گذشته. قبل از آرام شدن اتاق، مرورش کن.
- `space.room.remindersValue`: {due} رسیده · {scheduled} بعداً
- `space.shell.restMomentDue`: امروز تقریباً جمع شده، اما {count} یادآور از زمانش گذشته است.
- `space.scene.objectsPlaced`: هنوز شیئی قرار نگرفته \| 1 شیء قرار گرفته \| {count} شیء قرار گرفته
- `common.dayChallenge`: چالش {count} روزه
- `space.panel.missionBody`: {minutes} دقیقه کافیه. همین یک قدم امروزت رو امن می‌کنه و اتاقت رو جلو می‌بره.
- `space.shell.unlocksInDays`: امروز قفل است. اگر این چالش را ادامه بدهی {count} روز دیگر باز می‌شود.
- `space.shell.xp`: +{count} XP

Per the digits rule (Persian digits in FA, Latin in EN), B10 will need one number formatter applied to these placeholders and template numbers, plus a decision on the forced-LTR `completed/total`.

## Notes for the review

- **EN strings with `{count}` but no plural forms:** each reads wrong either for 1 or for more than 1. Only `space.objects` and `space.scene.objectsPlaced` have plural forms:
  - `ringoRewardSequence.staged.streakValue`: {count} day streak
  - `space.shell.restReminderDue`: {count} overdue reminder
  - `space.shell.restReminderFuture`: {count} reminder scheduled for later
  - `space.panel.futureMissions`: Later in this challenge: {count} more missions
  - `space.shell.minutes`: {count} min
  - `space.overview.progressText`: {count} visible objects are saved from real progress.
  - `space.overview.reminderText`: Overdue reminders: {count}. Review them before the room settles for today.
  - `space.shell.restMomentDue`: Today is nearly settled, but {count} reminder is past its time.
  - `common.dayChallenge`: {count} day challenge
  - `space.shell.unlocksInDays`: Locked today. This opens in {count} days if you keep this challenge active.
- **FA strings use one form for every count** (Persian does not need plural forms here), so FA needs no plural changes.
- **Duplicate meaning in different keys:** `space.title` and `space.panel.*` / `space.overview.*` titles repeat "Your progress room" / "Today is safe" in several places (for example `space.panel.stateSafe`, `space.shell.restSummarySafeValue`). Worth aligning in the review.
