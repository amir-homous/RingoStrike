# Living Space Room Panel v2 — Spec (B9 + B8)

Status: approved by Amir on 2026-10-19 (structure, support-action labels, copy, missions Option A).
Mock-ups: "Living Space Direction Sample" design canvas, rows "Room panel proposal" and "Missions inside a challenge" (Option A chosen).

## Principle

One Ringo message, one primary action. Details only on demand. No action buttons outside the Ringo card.

## Structure (top to bottom)

1. **Header:** path icon, path name (kicker), zone name, Close.
2. **Ringo card** — the only place with action buttons.
   - State label, one-sentence title, body of at most 2 sentences.
   - Mission meta chips when a mission is in focus: intensity, minutes, XP.
   - Primary button: full width, 50px high.
   - Support actions in a 3-column grid. Each button is at least 66px high, with a 22px icon and a visible text label. No tooltip; keep `aria-label`.
3. **Bonus card (B8):** shown only when today's main (or its tiny substitute) is done, a bonus is available, and no reminder is due.
   - Dashed border, label "قدم اضافه · اختیاری", title, meta.
   - Secondary button "انجامش می‌دم" moves the bonus into the Ringo card as the focus mission.
   - Link "پیشنهاد دیگه" switches to the next available bonus or optional mission.
4. **"امروز در این گوشه" strip:** today's main progress (x of y) and the first-object line.
5. **Disclosure rows (accordion, one open at a time):**
   - "مسیر و چالش‌ها"
   - "اشیای این گوشه"
   - "یادآورها" (only when any reminders exist)
   - Opening a row collapses the Ringo card to one line with a "برگرد" button.
6. **"مسیر و چالش‌ها" expanded:** path progress bar, then the challenge list.
   - **Active challenge, expanded (Option A):** a "امروز" list of today's missions.
     - Done missions show a check.
     - A bonus shown before the main is done is dimmed, with the line "بعد از قدم اصلی".
     - Tiny missions appear only after the user taps "کوچیک‌ترش کن".
     - Future missions are shown as a count only ("بعداً در این چالش: N مأموریت دیگه").
     - Rows have no action buttons. Tapping a row makes that mission the Ringo focus; the focused row is marked "پیشنهاد رینگو".
   - Locked or next challenges appear as dashed preview rows.
   - A "دیدن کامل مسیر" link goes to `/paths`.

The five-tab shell nav (Zone/Path/Challenge/Mission/Rest) is removed from the UI. Rest becomes a Ringo card state.

## Ringo card states

| State | Label | Primary | Support |
| --- | --- | --- | --- |
| Mission ready | رینگو | انجامش دادم | کوچیک‌ترش کن · بعداً یادم بنداز · امروز نه |
| Main done / today safe (gold tone) | امروز امنه | برای امروز کافیه (existing finish-for-today flow) | — (bonus card below) |
| Due reminder | badge "یادآور رسیده" | انجامش دادم | کوچیک‌ترش کن · باز هم بعداً · امروز نه |
| Rest | existing rest copy | existing | — |

## Recommendation priority (B8, #338)

1. Due reminder
2. Mission the user explicitly picked
3. Unfinished main
4. Tiny substitute (only if the user chose smaller)
5. Optional bonus offer (only after main or tiny is done)
6. Rest

Bonus is never required and never auto-pushed. A due reminder always outranks a bonus.

## FA copy (approved)

- Mission title: "قدم امروز: {mission}."
- Mission body: "{minutes} دقیقه کافیه. همین یک قدم امروزت رو امن می‌کنه و اتاقت رو جلو می‌بره."
- Done title: "قدم اصلی امروز انجام شد."
- Done body: "برای امروز همین کافیه. اگه هنوز انرژی داری، یک قدم کوچیک اضافه هم هست؛ کاملاً اختیاری."
- Bonus meta suffix: "روی پیشرفت امروزت فشاری نمیاره"
- Reminder title: "وقتشه: {mission}."
- Reminder body: "خودت خواسته بودی الان یادت بندازم. اگه الان هم وقتش نیست، اشکالی نداره."
- Reminder-priority note: "یادآوری که خودت گذاشتی همیشه جلوتر از پیشنهادهای اضافه میاد. قدم اضافه بعد از این دوباره در دسترسه."
- Collapsed Ringo line (today safe): "این گوشه امروز امنه."

EN strings are drafted to match the tone and reviewed by Amir in the PR.

## Constraints

- No backend, schema, XP, check-in, streak, achievement or reward logic changes in B9.
- B8 may need backend Ringo Brain changes. If so, split them into a separate issue and stop for approval.
- Room, colors and the dark/glass style stay unchanged. Desktop side panel and mobile layout keep their current placement.
- EN/FA, RTL, keyboard focus and `prefers-reduced-motion` are required.
