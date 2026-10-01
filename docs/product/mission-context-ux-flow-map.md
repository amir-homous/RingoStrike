# Mission Context UX Flow Map

## 1. Purpose

This document defines the product and UX flow map for making mission context clear across the full RingoStrike progression chain:

```txt
Path -> Challenge -> Mission -> Completion -> Reward -> Progress
```

It is documentation only. It does not implement code, redesign the dashboard, introduce a new completion pipeline, or replace the existing MissionCenter, RingoCoach, check-in, XP, streak, achievement, or activity systems.

The goal is to support the next product step:

```txt
Mission Context Wireframe / User Flow
```

The purpose of this document is to make every mission feel understandable, emotionally safe, and connected to a larger progression journey. A user should not see a mission as an isolated task. They should understand where it came from, why Ringo suggested it, what to do, what it affects, and what changed after completion.

Core success feeling:

```txt
“I know exactly what I am doing.”
```

Not:

```txt
“I guess this is what Ringo wants me to do.”
```

## 2. Current UX Problem

During testing, a major UX problem became clear: users often do not fully understand what a mission is asking them to do.

The problem is not only mission wording. The deeper problem is missing mission context.

Users may see:

```txt
Mission
```

instead of understanding:

```txt
Path -> Challenge -> Mission -> Completion -> Reward -> Progress
```

This creates repeated questions:

- What exactly am I supposed to do?
- Why am I doing this?
- Which challenge does this belong to?
- Which path does this belong to?
- What progress will this create?
- What will improve if I complete it?
- Why did Ringo suggest this mission right now?
- What changed after completion?

The confusion becomes worse when the mission is not the primary daily action:

- Tiny missions can feel like unrelated shortcuts.
- Bonus missions can feel like pressure instead of optional momentum.
- Remind-later missions can lose their original context when they return.
- Multiple active challenges can make the selected mission feel arbitrary.
- Reward moments can feel detached if they show XP/streak feedback without the affected path/challenge context.

## 3. Root Cause

The current foundation already has strong progression infrastructure, but mission context is split across multiple surfaces:

- Path context is strongest on `/paths`.
- Challenge context is strongest on challenge/enrollment surfaces.
- Mission action is strongest in MissionCenter.
- Ringo explanation is strongest in RingoCoach / Ringo Brain decisions.
- XP, streak, achievement, and reward feedback live in the existing check-in/reward pipeline.
- Reminder delivery context lives partly in MissionCenter and Telegram automation state.

Because these pieces are not yet presented as one continuous mental model, users can miss the relationship between them.

The current Mission Focus Mode helps attention by reducing dashboard noise, but it is not the full Mission Context UX layer. Focus mode answers:

```txt
“What should I focus on right now?”
```

The planned Mission Context UX layer must also answer:

```txt
“Where does this mission come from, why does it matter, and what changes when I do it?”
```

## 4. Product Principle

RingoStrike is companion-first.

Core rule:

```txt
First Ringo. Then system.
```

Ringo should introduce the mission in human language before the interface exposes system metadata. The system should support Ringo’s explanation rather than compete with it.

Current daily loop to preserve:

```txt
Ringo guidance
-> Today's Mission
-> Mission action
-> Reward / Today Saved
-> Next gentle step
```

The UX must feel:

- warm
- clear
- calm
- emotionally safe
- progression-aware
- premium
- minimal but meaningful

The UX must avoid:

- pressure-based streak anxiety
- casino-style reward noise
- dashboard overload
- disconnected mission cards
- duplicate progression explanations
- making optional work feel required

## 5. User Mental Model We Need To Create

The user should learn this mental model naturally:

```txt
I chose a Path.
That Path contains Challenges.
Each Challenge gives me Missions.
Ringo chooses the best next Mission for my current state.
Completing the right Mission protects today’s progress.
Rewards show what changed.
Then I can rest or choose a gentle next step.
```

A mission should answer five questions at a glance:

1. **Origin** — Where did this mission come from?
2. **Purpose** — Why is this mission being suggested?
3. **Action** — What exactly should I do now?
4. **Progress impact** — What does this move forward?
5. **Reward impact** — What will I receive or protect?

Recommended visible hierarchy:

```txt
Ringo explanation
↓
Path / Challenge context
↓
Mission title
↓
Concrete action instruction
↓
Why this helps
↓
Primary action
↓
Secondary options
```

This hierarchy keeps Ringo emotionally first, while still making the system context visible enough to reduce confusion.

## 6. Current Implemented Foundation

The current project already includes a strong foundation that this UX layer should extend.

### Implemented

- Mission focus mode.
- CompactProgressStrip.
- First-run staged reveal.
- Post-first-win completion UX.
- Rest Mode after `Finish for today`.
- Collapsed mission status details.
- MissionCenter as the first dashboard surface.
- RingoCoach for Ringo message, sprite, and action guidance.
- Ringo Brain / Ringo decision layer foundations.
- Backend-backed paths and missions.
- `/paths` planning view with path selection, challenge previews, mission previews, and progress summary.
- Main/tiny mission-family behavior where linked tiny missions act as lower-pressure substitutes.
- Bonus missions as optional extra momentum.
- Remind-later mission state.
- Telegram reminder automation and diagnostics.
- Reward sequence/check-in reward feedback.
- Existing check-in, XP, streak, achievement, activity, and stats pipeline.

### Still Planned

- Full Mission Context UX layer.
- Universal Path -> Challenge -> Mission breadcrumbs.
- Backend mission context model.
- Contextual reward sequence showing affected path/challenge progress.
- Complete tiny/bonus/remind-later context clarity across all surfaces.
- Wireframes and component implementation.

### Boundary

Mission focus mode should not be described as full Mission Context UX. It is an implemented attention/focus layer. Mission Context UX is a planned clarity layer that should sit on top of the current foundation.

## 7. Mission Context Model

Conceptual model:

```txt
Mission Context = origin + purpose + action + progress impact + reward impact
```

### Origin

Where the mission comes from.

Recommended data concepts:

- `path_id`
- `path_title`
- `challenge_id`
- `challenge_name`
- `enrollment_id`
- `mission_id`
- `mission_intensity`
- `parent_mission_id` for tiny missions

User-facing explanation:

```txt
This mission is part of Body Momentum -> Move Your Body.
```

### Purpose

Why this mission exists and why Ringo is suggesting it now.

Recommended data concepts:

- Ringo state.
- Ringo message.
- Challenge goal.
- Mission `ringo_message`.
- Suggested time.
- Current agenda state.
- Today saved / not saved.
- Reminder due / future reminder.
- Returning user or streak-risk state.

User-facing explanation:

```txt
Ringo picked this because it is the smallest useful step for keeping your body path alive today.
```

### Action

What the user should physically or mentally do.

Recommended data concepts:

- Mission title.
- Mission description.
- Estimated minutes.
- Difficulty.
- Mission intensity.
- Concrete completion instruction.

User-facing explanation:

```txt
Move your body for 10 minutes. A walk, stretching, or light mobility all count.
```

### Progress Impact

What changes in the progression system.

Recommended data concepts:

- Whether today becomes safe.
- Whether the main/tiny family is satisfied.
- Challenge daily progress.
- Path progress summary.
- Current streak context from existing stats.
- Optional bonus state.

User-facing explanation:

```txt
Completing this protects today’s progress for Move Your Body and keeps your Body Momentum path moving.
```

### Reward Impact

What reward feedback should appear after completion.

Recommended data concepts:

- XP earned from the existing reward/check-in response.
- Today saved / streak protected.
- Achievement unlocks if any.
- Next gentle step.
- Optional bonus availability.

User-facing explanation:

```txt
You’ll earn today’s progress reward, protect your streak if this is your first required completion today, and see the next gentle option.
```

### How To Show Context Without Overwhelming The UI

Mission context should use progressive disclosure:

1. **Always visible:** Ringo explanation, path/challenge breadcrumb, mission title, concrete action, primary action.
2. **Light secondary visible:** mission intensity, estimated time, “why this helps.”
3. **Collapsed details:** mission status timeline, reminder delivery state, path/challenge progress details.
4. **Reward sequence:** show system changes step-by-step after completion instead of overloading the pre-action mission card.

The mission card should not become a dashboard inside a card. Context should be short, structured, and emotionally readable.

## 8. Mission States To Support

The Mission Context UX must support these states:

- New user with no path.
- Path selected but no challenge joined.
- Main mission pending.
- Main mission completed.
- Tiny mission offered.
- Tiny mission completed.
- Bonus mission offered.
- Bonus mission completed.
- Mission skipped.
- Mission reminded later.
- Reminded mission returns.
- Today already saved.
- Multiple active challenges.
- Reward sequence after completion.
- Telegram reminder context.

The same model should apply across MissionCenter, RingoCoach, reward sequence, reminders, Rest Mode, and later wireframes.

## 9. State-by-State UX Flow Map

### 9.1 New User With No Path

#### User Situation

The user has registered or logged in but has not selected an identity/growth path yet.

#### User Confusion Risk

The user may not understand what RingoStrike wants from them, why they need to choose a path, or how paths relate to daily missions.

#### Required Visible Context

- Path: No path selected yet.
- Challenge: No challenge joined yet.
- Mission: No mission available until the user chooses a direction.
- Mission intensity: Not applicable.
- Progress meaning: Choosing a path creates the first direction for Ringo’s future mission suggestions.

#### Ringo Should Explain

Ringo should explain that paths are not heavy commitments. They are simple directions that help Ringo choose the right first step.

Example:

```txt
Let’s choose your first direction. A path helps me suggest missions that actually fit what you want to grow.
```

#### Primary User Action

Choose a path.

#### Secondary Actions

- Learn what paths mean.
- Skip for now only if the product still has a safe fallback.
- View example missions for each path.

#### What Happens After Action

The selected path becomes the user’s active direction. The UX should then guide them toward the first relevant challenge or a first mission handoff.

#### UX Notes

Keep this state calm and lightweight. Do not show dense stats, leaderboards, or reward systems before the user understands the basic path concept.

### 9.2 Path Selected But No Challenge Joined

#### User Situation

The user has selected a path but is not yet enrolled in a challenge under that path.

#### User Confusion Risk

The user may think selecting a path already started their daily progress. They may not understand that challenges are the containers that create recurring missions and check-ins.

#### Required Visible Context

- Path: Selected path title and short purpose.
- Challenge: Recommended first challenge under the path.
- Mission: Preview of the first mission if available.
- Mission intensity: Usually main mission preview.
- Progress meaning: Joining a challenge activates the daily loop for that path.

#### Ringo Should Explain

Ringo should bridge path selection into the first challenge without making it feel like a separate system step.

Example:

```txt
Good choice. This path needs one active challenge so I can give you a clear daily mission.
```

#### Primary User Action

Join the recommended first challenge.

#### Secondary Actions

- View path details.
- Choose another challenge in the same path.
- Change path.

#### What Happens After Action

The user joins the challenge through the existing join flow, then sees a soft join success moment and is guided back to Today’s Mission.

#### UX Notes

Do not create a new path-start completion economy. Path start and challenge join should remain separate underneath, but the UI should explain them as one guided start journey.

### 9.3 Main Mission Pending

#### User Situation

The user has an active path/challenge and the primary mission for today is pending.

#### User Confusion Risk

The user may understand the title but not the exact completion criteria, why this mission matters, or what it protects.

#### Required Visible Context

- Path: Active path title.
- Challenge: Challenge name.
- Mission: Main mission title and concrete instruction.
- Mission intensity: Main.
- Progress meaning: Completing this mission protects today’s progress for the connected challenge/path and routes through the existing check-in pipeline.

#### Ringo Should Explain

Ringo should make the mission feel like the one clear daily step.

Example:

```txt
This is today’s main step for Body Momentum. Do this once and today is safe.
```

#### Primary User Action

Complete / mark the main mission done.

#### Secondary Actions

- Make it smaller / choose tiny mission when available.
- Remind me later.
- Skip today with low-shame explanation.
- Show mission status.
- View path/challenge details.

#### What Happens After Action

The mission is marked done through the existing mission completion endpoint, which delegates to the existing check-in/progression pipeline. The reward sequence should show mission completion, XP/check-in reward, today saved/streak protection when applicable, and next gentle step.

#### UX Notes

This state should have the strongest clarity. The main mission card should include a short “What counts?” line to remove ambiguity.

### 9.4 Main Mission Completed

#### User Situation

The user has completed the main mission for today.

#### User Confusion Risk

The user may not know whether they are finished, whether bonus work is required, or what progress was created.

#### Required Visible Context

- Path: Path affected by the completed mission.
- Challenge: Challenge affected by the completed mission.
- Mission: Completed main mission.
- Mission intensity: Main.
- Progress meaning: Today is saved for the required mission family. Any remaining bonus work is optional.

#### Ringo Should Explain

Ringo should confirm success and remove pressure.

Example:

```txt
Today is safe. You completed the main step for this challenge. Anything else is optional.
```

#### Primary User Action

Finish for today.

#### Secondary Actions

- Try optional bonus mission if available.
- View reward details.
- Show dashboard.
- View path progress.

#### What Happens After Action

The user enters Rest Mode or sees optional bonus framing. The full dashboard should only appear if the user explicitly chooses to reveal it.

#### UX Notes

Do not push the bonus mission as if it is required. The product should clearly say the required daily step is complete.

### 9.5 Tiny Mission Offered

#### User Situation

The user is offered a smaller version of the main mission, usually because the main mission may feel too hard, the user chose “make it smaller,” or the agenda has a tiny-flow state.

#### User Confusion Risk

The user may think the tiny mission is unrelated, less valuable, or a separate challenge. They may also wonder whether it still counts for today.

#### Required Visible Context

- Path: Same path as the parent main mission.
- Challenge: Same challenge as the parent main mission.
- Mission: Tiny mission title plus parent main mission reference.
- Mission intensity: Tiny.
- Progress meaning: A linked tiny mission is a lower-pressure substitute for the main mission family and can protect today when completed.

#### Ringo Should Explain

Ringo should make the relationship explicit.

Example:

```txt
This is the smaller version of today’s main mission. It still belongs to Move Your Body, and it is enough to keep today safe.
```

#### Primary User Action

Complete the tiny mission.

#### Secondary Actions

- Return to main mission.
- Remind me later.
- Skip today.
- Show why this still counts.
- View path/challenge context.

#### What Happens After Action

The tiny mission is marked done. The linked main/tiny family is treated as satisfied for today, but the parent main mission does not need to be visually marked as separately completed unless the system has explicit support for that representation.

#### UX Notes

The tiny mission card must show a parent relationship label such as:

```txt
Smaller version of: Move for 10 minutes
```

This prevents the tiny mission from feeling like a random substitute.

### 9.6 Tiny Mission Completed

#### User Situation

The user completed the linked tiny mission instead of the main mission.

#### User Confusion Risk

The user may wonder whether today really counts, why the parent main mission is not marked done, and whether they still need to do the main version.

#### Required Visible Context

- Path: Path affected by the tiny completion.
- Challenge: Challenge affected by the tiny completion.
- Mission: Completed tiny mission and parent main mission reference.
- Mission intensity: Tiny.
- Progress meaning: Today is safe because the tiny mission satisfied the required mission family.

#### Ringo Should Explain

Ringo should validate the smaller win without shame.

Example:

```txt
You chose the smaller step and it counts. Today is safe — no need to force the bigger version now.
```

#### Primary User Action

Finish for today.

#### Secondary Actions

- View what changed.
- Show dashboard.
- Optional bonus only if the UX can keep it clearly non-required.

#### What Happens After Action

The reward sequence should show tiny completion, today saved/streak protected when applicable, and a calm next choice. It should not push the parent main mission as another required task.

#### UX Notes

This is an important emotional UX moment. The copy should reinforce self-efficacy and consistency, not make the user feel they did a weaker or incomplete version.

### 9.7 Bonus Mission Offered

#### User Situation

The required daily mission family is already safe, and a bonus mission is available as optional extra momentum.

#### User Confusion Risk

The user may think the bonus mission is required to finish the day or protect the streak.

#### Required Visible Context

- Path: Path connected to the bonus mission.
- Challenge: Challenge connected to the bonus mission.
- Mission: Bonus mission title and concrete action.
- Mission intensity: Bonus.
- Progress meaning: Optional extra momentum. Not required for today to be safe.

#### Ringo Should Explain

Ringo should present bonus work as an invitation, not a demand.

Example:

```txt
You already saved today. This bonus is only extra momentum if you still have energy.
```

#### Primary User Action

Finish for today.

#### Secondary Actions

- Start bonus mission.
- Remind me later for bonus.
- Skip optional bonus.
- View path/challenge details.

#### What Happens After Action

If the user finishes for today, they enter Rest Mode. If they start the bonus, the card should remain explicit that the action is optional.

#### UX Notes

The primary action should usually remain `Finish for today`. The bonus action should not visually overpower the safe-day action.

### 9.8 Bonus Mission Completed

#### User Situation

The user completed an optional bonus mission after the required day was already safe.

#### User Confusion Risk

The user may expect another full check-in reward, or may not understand how optional completion affects progress.

#### Required Visible Context

- Path: Path receiving extra momentum.
- Challenge: Challenge receiving extra momentum.
- Mission: Completed bonus mission.
- Mission intensity: Bonus.
- Progress meaning: Extra recognition/momentum, not the required daily protection step.

#### Ringo Should Explain

Ringo should celebrate without exaggerating system impact.

Example:

```txt
Extra momentum added. You were already safe today — this is a bonus win.
```

#### Primary User Action

Finish for today.

#### Secondary Actions

- View reward details.
- Show dashboard.
- View path progress.

#### What Happens After Action

The reward sequence should show bonus completion as optional extra progress. It should not repeat `Today is safe` as if the day was just saved again if the required step was already completed earlier.

#### UX Notes

Avoid duplicate reward language. Bonus completion should feel good, but not confusing.

### 9.9 Mission Skipped

#### User Situation

The user skips a mission for today.

#### User Confusion Risk

The user may not know whether skipping ends the day, damages streak/progress, or triggers alternative options.

#### Required Visible Context

- Path: Path connected to the skipped mission.
- Challenge: Challenge connected to the skipped mission.
- Mission: Skipped mission title.
- Mission intensity: Main, tiny, or bonus.
- Progress meaning: Depends on intensity. Skipping a required main/tiny mission does not save today. Skipping a bonus mission does not harm today if the required family is already safe.

#### Ringo Should Explain

Ringo should stay no-shame and clarify impact.

Example for required mission:

```txt
No shame. This mission is skipped for today, but today is not saved yet. We can try a smaller step if you want.
```

Example for bonus mission:

```txt
Bonus skipped. That’s okay — today was already safe.
```

#### Primary User Action

Choose the next gentle step based on mission intensity.

#### Secondary Actions

- Try tiny version if a required main mission was skipped.
- Remind me later.
- Finish for today only if today is already safe.
- Show dashboard.

#### What Happens After Action

The mission log status becomes skipped. No check-in should be created by skip. Ringo should either offer a smaller route or settle the user into Rest Mode if today is already safe.

#### UX Notes

Skipping must not become a punishment state. It should be a signal for Ringo to adapt.

### 9.10 Mission Reminded Later

#### User Situation

The user chooses to be reminded later about a mission.

#### User Confusion Risk

The user may not know whether the mission is paused, whether today is safe, when the reminder will happen, or whether Telegram must be connected.

#### Required Visible Context

- Path: Path connected to the reminded mission.
- Challenge: Challenge connected to the reminded mission.
- Mission: Mission title being reminded later.
- Mission intensity: Main, tiny, or bonus.
- Progress meaning: The mission is not completed yet. If it is required and today was not already safe, progress is still pending.

#### Ringo Should Explain

Ringo should frame remind-later as a remembered agreement.

Example:

```txt
Got it. I’ll bring this mission back later. It still belongs to Move Your Body, and today is not saved until you complete it or a smaller version.
```

#### Primary User Action

Confirm reminder / return later.

#### Secondary Actions

- Change reminder time.
- Connect Telegram if needed.
- Enable reminders if disabled.
- Finish for today only if today is already safe.
- Show mission status.

#### What Happens After Action

The mission log status becomes `remind_later` with `reminder_at`. MissionCenter can show scheduled/due/sent frontend-only delivery context based on existing metadata and authenticated Telegram settings.

#### UX Notes

The reminder confirmation should include both time and context:

```txt
Reminder set for Move for 10 minutes · Body Momentum -> Move Your Body
```

### 9.11 Reminded Mission Returns

#### User Situation

A mission that the user postponed returns in MissionCenter or through a Telegram reminder.

#### User Confusion Risk

The user may not remember why this mission appeared, what they asked Ringo to remind them about, or whether it is still required.

#### Required Visible Context

- Path: Path connected to the returned reminder.
- Challenge: Challenge connected to the returned reminder.
- Mission: Mission title and original reminder context.
- Mission intensity: Main, tiny, or bonus.
- Progress meaning: If the mission is required and today is not safe, completing it can still protect today before reset. If today is already safe, it is optional context.

#### Ringo Should Explain

Ringo should explicitly say the user asked for this reminder.

Example:

```txt
You asked me to remind you about this. It’s still today’s step for Move Your Body.
```

If today is already safe:

```txt
This reminder is back, but today is already safe. You can do it only if you still want the extra momentum.
```

#### Primary User Action

Start or complete the returned mission.

#### Secondary Actions

- Remind me again if still before reset.
- Make it smaller if available.
- Skip today.
- Finish for today if already safe.
- View why this returned.

#### What Happens After Action

If completed, the normal mission completion/reward sequence runs. If reminded again, the reminder state is updated. If skipped, the skipped state rules apply.

#### UX Notes

Returned reminders need stronger context than normal pending missions. They should include a small “You asked for this” label or Ringo copy.

### 9.12 Today Already Saved

#### User Situation

The required mission family is already complete for the day.

#### User Confusion Risk

The user may think they still need to complete more tasks because the dashboard shows more missions, reminders, or optional work.

#### Required Visible Context

- Path: Most recently affected path or active path summary.
- Challenge: Challenge already secured today.
- Mission: Completed mission that saved today.
- Mission intensity: Main or tiny that satisfied the required family.
- Progress meaning: Today is safe. Remaining missions are optional, reminder-based, or informational.

#### Ringo Should Explain

Ringo should make stopping feel like success.

Example:

```txt
Today is safe. You did enough. You can rest now, or continue only if it feels good.
```

#### Primary User Action

Finish for today.

#### Secondary Actions

- Optional bonus mission.
- Show dashboard.
- View today’s reward.
- View path progress.

#### What Happens After Action

The user enters Rest Mode. Dashboard sections remain hidden until the user intentionally chooses `Show dashboard`.

#### UX Notes

This state protects emotional UX. It prevents the product from feeling like endless tasks.

### 9.13 Multiple Active Challenges

#### User Situation

The user is enrolled in multiple active challenges, possibly across one or more paths.

#### User Confusion Risk

The user may not understand why Ringo picked one mission over another or how the selected mission relates to their broader progress.

#### Required Visible Context

- Path: Path for the selected mission, plus optional small note if other paths/challenges exist.
- Challenge: Challenge selected by Ringo.
- Mission: Selected mission title.
- Mission intensity: Main, tiny, or bonus.
- Progress meaning: Ringo selected the most useful next action based on the current agenda state. Other active challenges can remain visible in collapsed status.

#### Ringo Should Explain

Ringo should briefly explain the priority decision without exposing complex algorithms.

Example:

```txt
You have a few active challenges. I picked this one because it is the clearest step that still needs attention today.
```

#### Primary User Action

Complete the selected mission.

#### Secondary Actions

- View other active challenges.
- Switch mission only if supported later.
- Remind selected mission later.
- Show mission status.

#### What Happens After Action

The selected mission follows the normal completion flow. Other active challenges remain available in supporting surfaces but should not steal focus.

#### UX Notes

Do not show all challenge details upfront. Use a compact context label like:

```txt
Selected from 3 active challenges
```

Then allow `Show mission status` or `View all` for deeper details.

### 9.14 Reward Sequence After Completion

#### User Situation

The user completed a mission and enters the reward/result moment.

#### User Confusion Risk

The user may see XP or streak changes without understanding which path/challenge/mission caused them. They may also miss whether today is safe or what the next gentle step is.

#### Required Visible Context

- Path: Affected path.
- Challenge: Affected challenge.
- Mission: Completed mission.
- Mission intensity: Main, tiny, or bonus.
- Progress meaning: Show whether the completion saved today, added optional momentum, or simply completed a reminder/bonus.

#### Ringo Should Explain

Ringo should narrate the reward sequence in small steps.

Example:

```txt
Nice. This completed your Move Your Body mission inside Body Momentum.
```

Then:

```txt
Today is safe. Your streak is protected.
```

Then:

```txt
You can stop here or choose one gentle extra step.
```

#### Primary User Action

Continue through reward sequence, then Finish for today.

#### Secondary Actions

- View details.
- Continue with optional bonus.
- Show dashboard.

#### What Happens After Action

Reward sequence should show, step by step:

1. Completed mission.
2. Affected challenge.
3. Affected path.
4. XP/check-in reward from existing reward data.
5. Today saved / streak protected when applicable.
6. Achievements if any.
7. Next gentle step.

#### UX Notes

Current reward sequence exists, but full contextual reward sequence showing affected path/challenge progress remains planned. Do not claim the full context layer is implemented until it exists across the UI.

### 9.15 Telegram Reminder Context

#### User Situation

The user receives or configures a Telegram mission reminder.

#### User Confusion Risk

The Telegram message may feel disconnected from the app if it only shows the mission title. The user may not remember the path/challenge, why the reminder was scheduled, or what action to take.

#### Required Visible Context

- Path: Path title connected to the reminded mission.
- Challenge: Challenge name connected to the reminded mission.
- Mission: Mission title and short action instruction.
- Mission intensity: Main, tiny, or bonus.
- Progress meaning: Clarify whether the mission can still save today or is optional because today is already safe.

#### Ringo Should Explain

Ringo should remind the user like a companion, not like an alarm.

Example:

```txt
You asked me to remind you: Move for 10 minutes.
Path: Body Momentum
Challenge: Move Your Body
One small step can still save today.
```

If today is already safe:

```txt
You asked me to remind you about this bonus step. Today is already safe, so only do it if you have energy.
```

#### Primary User Action

Open RingoStrike / open dashboard to complete the mission.

#### Secondary Actions

- Snooze/remind again later if a future bot action supports it.
- Ignore safely if optional and today is already safe.

#### What Happens After Action

The app should open with the reminded mission context preserved in MissionCenter, not just the generic dashboard.

#### UX Notes

Current Telegram reminder automation and diagnostics are implemented. Full deep-linked contextual reminder return behavior remains planned unless implemented later. For now, keep Telegram copy context-rich and route users back to the dashboard.

## 10. Recommended Mission Card Hierarchy

Recommended mission card hierarchy:

```txt
Ringo explanation
Path / Challenge context
Mission intensity label
Mission title
Concrete action instruction
Why this helps
Primary action
Secondary actions
Collapsed status/context details
```

### Always Visible

- Ringo’s short explanation.
- Path -> Challenge breadcrumb.
- Mission title.
- Mission intensity label: Main, Tiny, or Bonus.
- Estimated time if available.
- One concrete “what counts” instruction.
- Primary action.

### Visible But Lightweight

- Why this helps.
- Today-safe meaning.
- Tiny parent relation.
- Bonus optional label.
- Reminder timing.

### Collapsed By Default

- Mission status list.
- Other active challenges.
- Detailed path progress.
- Reminder delivery diagnostics-like UI.
- Full reward history.

### Example Layout

```txt
[Ringo]
This is your main step for Body Momentum today.

Body Momentum -> Move Your Body
MAIN · 10 min

Move for 10 minutes
Walk, stretch, or do light mobility. Anything intentional counts.

Why this helps
This keeps your body path active and protects today’s progress.

[Complete mission]
[Make it smaller] [Remind me later]

Show mission status
```

## 11. Recommended Ringo Explanation Layer

Ringo’s explanation should always answer:

```txt
Why this mission, why now, and what is enough?
```

### Explanation Rules

- Use deterministic copy first.
- Keep copy short and warm.
- Avoid long motivational paragraphs.
- Avoid shame or pressure.
- Explain the relation between mission type and progress impact.
- Mention optional status clearly when relevant.
- Mention user agency: rest, smaller step, remind later.

### Main Mission Copy Pattern

```txt
This is today’s main step for [Path]. Complete it once and today is safe.
```

### Tiny Mission Copy Pattern

```txt
This is the smaller version of [Parent Mission]. It still counts for today.
```

### Bonus Mission Copy Pattern

```txt
Today is already safe. This is optional extra momentum if you have energy.
```

### Remind-Later Copy Pattern

```txt
You asked me to bring this back later. It still belongs to [Challenge] in [Path].
```

### Multiple Challenges Copy Pattern

```txt
You have a few active challenges. I picked the clearest one that still needs attention.
```

## 12. Recommended Reward Sequence Context

The reward sequence should make the result understandable before it makes it exciting.

Recommended flow:

```txt
1. Ringo reaction
2. Mission completed
3. Challenge affected
4. Path affected
5. XP/check-in reward
6. Today saved / streak protected
7. Achievements if unlocked
8. Next gentle step
```

### Current Implemented Boundary

Implemented today:

- Reward/check-in feedback exists.
- Mission completion delegates to the existing check-in pipeline.
- Reward sequence/check-in response can show XP, streak, achievements, and next-step style feedback.
- Post-first-win copy and Rest Mode exist.

Still planned:

- Full contextual reward sequence across all mission types.
- Universal affected path/challenge framing in reward steps.
- Contextual tiny/bonus/reminder reward copy across every surface.
- Wireframed component-level reward sequence layout.

### Main Mission Completion

Should show:

```txt
Mission completed -> Challenge moved -> Path moved -> XP earned -> Today safe -> Next gentle step
```

### Tiny Mission Completion

Should show:

```txt
Tiny mission completed -> Smaller version of main mission -> Today safe -> No need to force more -> Next gentle step
```

### Bonus Mission Completion

Should show:

```txt
Bonus completed -> Extra momentum -> Today was already safe -> Finish/rest
```

### Reminder Completion

Should show:

```txt
Reminder returned -> Mission completed -> Context restored -> Today safe or optional momentum -> Next gentle step
```

## 13. Visual Hierarchy Recommendations

Mission Context UX should preserve the premium dark/glass visual language.

### Recommended Patterns

- Use a compact breadcrumb pill for `Path -> Challenge`.
- Use a clear mission-intensity chip: `MAIN`, `TINY`, `BONUS`.
- Use one calm primary button.
- Keep secondary actions visually quieter.
- Use Ringo sprite mood to reinforce context: focus, thinking, encouraging, proud, sleeping, victory.
- Use soft motion only for staged reveal or reward transition.
- Keep `Show mission status` collapsed by default during focus mode.
- Use Rest Mode as the calm endpoint.

### Avoid

- Large nested progress dashboards inside MissionCenter.
- Too many buttons with equal visual weight.
- Flashy reward effects.
- Over-explaining system logic.
- Turning bonus missions into pressure.
- Treating tiny missions as failure states.

### Information Density Rule

A mission card should answer:

```txt
What is this?
Why now?
What do I do?
What happens if I do it?
```

It should not try to show the entire product architecture.

## 14. Information Architecture Notes

Mission Context UX should unify existing surfaces rather than creating disconnected new ones.

### Dashboard / MissionCenter

Primary surface for daily action and contextual explanation.

Should show:

- Ringo explanation.
- Selected mission context.
- Path/challenge breadcrumb.
- Primary action.
- Secondary options.
- Today-safe/rest state.

### `/paths`

Planning and overview surface.

Should show:

- Path meaning.
- Challenge stages.
- Mission previews.
- Daily path summary.
- Progress context.

It should not compete with MissionCenter as the daily action surface.

### Enrollment Detail

Challenge detail/progress surface.

Should show:

- Challenge history.
- Daily reset rhythm.
- Leaderboard preview.
- Recent logs.

It can support mission context, but should not replace Ringo-led action.

### RewardMoment / Reward Sequence

Result interpretation surface.

Should show:

- What was completed.
- What was affected.
- What reward was earned.
- Whether today is safe.
- What to do next.

### Telegram

Out-of-app reminder surface.

Should show:

- Reminder reason.
- Mission title.
- Path/challenge context.
- Safe action link back to app.

## 15. Frontend Impact Notes

This issue should remain product/UX documentation only, but the future implementation should be frontend-first where possible.

Recommended future frontend direction:

- Extend MissionCenter context presentation instead of replacing MissionCenter.
- Extend RingoCoach copy/context display instead of replacing RingoCoach.
- Keep CompactProgressStrip as minimal progress context, not a duplicate stats engine.
- Add reusable context UI only if needed, such as:
  - mission context breadcrumb
  - mission intensity chip
  - parent mission relation line
  - why-this-helps block
  - reward context step
  - reminder context notice
- Use existing API fields first:
  - `path_id`
  - `path_title`
  - `challenge_id`
  - `challenge_name`
  - `enrollment_id`
  - `mission_intensity`
  - `estimated_minutes`
  - `parent_mission_id`
  - `ringo_message`
  - `status`
  - `reminder_at`
  - `reminder_sent_at`
  - `done_at`
  - `skipped_at`
- Preserve current dashboard focus gating.
- Preserve Rest Mode as the calm finish path.
- Preserve reduced-motion behavior.
- Preserve English/Persian i18n architecture by keeping backend values raw and translating display labels in frontend.

Do not:

- Replace MissionCenter.
- Replace RingoCoach.
- Redesign the full dashboard.
- Duplicate XP/streak/achievement calculations in frontend.
- Treat MissionCenter focus reasons as backend-stable enum values.

## 16. Backend Impact Notes

Future backend work should be additive only if the frontend cannot reliably construct mission context from existing fields.

Recommended backend direction:

- Keep mission completion routed through existing mission/check-in pipeline.
- Keep XP, streak, achievement, activity, and stats ownership centralized in existing services.
- Keep Ringo Brain / Ringo decision logic deterministic.
- Add mission context fields only when required and clearly documented.
- Consider a future `mission_context` object only as a read-model convenience, not a new progression model.

Possible future read-model shape:

```json
{
  "mission_context": {
    "origin": {
      "path_id": 1,
      "path_title": "Body Momentum",
      "challenge_id": 1,
      "challenge_name": "Move Your Body",
      "enrollment_id": 10
    },
    "purpose": {
      "reason_key": "today_not_started",
      "ringo_message": "Today's main step is ready.",
      "why_now": "This is the clearest required step for today."
    },
    "action": {
      "mission_id": 1,
      "title": "Move for 10 minutes",
      "instruction": "Walk, stretch, or do light mobility.",
      "estimated_minutes": 10,
      "mission_intensity": "main",
      "parent_mission_id": null
    },
    "progress_impact": {
      "today_saved_after_completion": true,
      "family_satisfied_after_completion": true,
      "challenge_progress_label": "Protects today's challenge progress",
      "path_progress_label": "Keeps Body Momentum active"
    },
    "reward_impact": {
      "uses_existing_checkin_pipeline": true,
      "shows_xp": true,
      "shows_streak_protection": true,
      "shows_achievements_if_any": true
    }
  }
}
```

This object should be a projection/read model only. It must not own progression writes.

Do not:

- Add duplicate XP logic.
- Add duplicate streak logic.
- Add duplicate achievement logic.
- Add a new mission completion pipeline.
- Replace check-in flow.
- Make path progress a second economy before the product model is clarified.
- Move frontend display decisions into backend prematurely.

## 17. Non-Goals

This document does not recommend:

- Implementing code.
- Creating Codex implementation prompts.
- Replacing MissionCenter.
- Replacing RingoCoach.
- Redesigning the full dashboard.
- Replacing the existing check-in flow.
- Duplicating XP, streak, achievement, activity, or stats logic.
- Creating a new progression economy.
- Adding a heavy skill tree.
- Adding a full AI-generated mission explanation system now.
- Making bonus missions required.
- Treating tiny missions as failure states.
- Building native mobile, widgets, or push notification systems as part of this issue.

## 18. Open Questions

- Should the future UI always show `Path -> Challenge` breadcrumbs, or only when users are likely to be confused?
- What is the shortest possible “what counts?” instruction pattern for each mission category?
- Should tiny mission completion visually mark the parent main mission as “satisfied” without marking it as “done”?
- How should the UI explain bonus mission rewards if the existing check-in for today already exists?
- Should users be allowed to switch between multiple pending missions manually, or should Ringo always choose one?
- How much path progress can be shown before a formal path-progress model exists?
- Should Telegram reminders deep-link to a mission-specific focused state later?
- How should reminder copy behave near the daily reset boundary?
- What is the right Persian wording for “Today is safe” so it feels warm and natural, not mechanical?
- Should “skip” and “rest” remain separate concepts, or should skipping sometimes route into a softer rest-state explanation?
- Should Ringo explain why a specific challenge was prioritized when multiple active challenges exist?
- How much of the reward sequence should be tap-by-tap versus visible as one calm summary?

## 19. Next Step

Next recommended step:

```txt
Mission Context Wireframe / User Flow
```

That next document should convert this flow map into concrete wireframes for:

- Main mission pending.
- Tiny mission offered.
- Bonus mission offered.
- Remind-later confirmation.
- Reminded mission return.
- Reward sequence after completion.
- Today already saved / Rest Mode.
- Multiple active challenges.
- Telegram reminder return.

The wireframe step should still preserve the same safety boundaries:

- no duplicate progression logic
- no full dashboard redesign
- no replacement of MissionCenter or RingoCoach
- frontend-first UX improvements where possible
- additive backend context only if required later
