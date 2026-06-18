# Mission Context Wireframes

## 1. Purpose

This document converts the Mission Context UX Flow Map into low-fidelity text wireframes and user flows.

The previous flow map defined the required mission states, mental model, and context model:

```txt
Mission Context = origin + purpose + action + progress impact + reward impact
```

This document answers:

```txt
What should the user actually see?
Where should each context element appear?
What action hierarchy should each state use?
How does the user move from mission -> action -> reward -> rest/next step?
```

The goal is for users to feel:

```txt
“I know exactly what I am doing, why it matters, and what changes after I do it.”
```

This is product/UX documentation only. It does not implement code, create Codex implementation prompts, change frontend/backend source code, redesign the dashboard, or introduce new progression logic.

## 2. Relationship To UX Flow Map

This document continues:

```txt
docs/product/mission-context-ux-flow-map.md
```

The UX Flow Map defined:

- the mission context problem
- the root cause
- the required user mental model
- the conceptual Mission Context model
- the mission states to support
- the state-by-state UX behavior
- frontend/backend safety boundaries

This wireframe document translates that strategy into visible layouts.

The relationship is:

```txt
UX Flow Map
  -> defines what each state means
  -> defines what context is required
  -> defines what Ringo should explain
  -> defines action/result expectations

Mission Context Wireframes
  -> shows where each context element appears
  -> shows action hierarchy
  -> shows low-fidelity card layouts
  -> shows transition from mission to reward to rest/next step
```

Important boundary:

```txt
Mission focus mode is implemented.
Full Mission Context UX is still planned.
These wireframes describe planned context enhancements, not the current finished UI.
```

## 3. Product Rules

### 3.1 Companion-First Rule

Core rule:

```txt
First Ringo. Then system.
```

Ringo should explain the mission before the UI exposes system detail.

The user should first receive an emotionally clear sentence, then see the path/challenge/mission structure.

### 3.2 Preserve The Daily Loop

Preserve the current daily loop:

```txt
Ringo guidance
-> Today's Mission
-> Mission action
-> Reward / Today Saved
-> Next gentle step
```

### 3.3 One Primary Action

Each state should have one dominant primary action.

Examples:

- Main mission pending: `Complete mission`
- Tiny mission offered: `Complete tiny mission`
- Today already saved: `Finish for today`
- Bonus mission offered: `Finish for today`, not `Start bonus`
- Reminder returned: `Complete mission`

Secondary actions should be visually quieter.

### 3.4 Optional Work Must Feel Optional

Bonus missions must not feel required.

The UI should explicitly say:

```txt
Today is already safe.
This is optional extra momentum.
```

### 3.5 Tiny Missions Must Feel Valid

Tiny missions must not feel like failure.

The UI should explicitly say:

```txt
This is the smaller version of the main mission.
It still counts for today.
```

### 3.6 No Duplicate Progression Logic

These wireframes must not suggest:

- duplicate XP logic
- duplicate streak logic
- duplicate achievement logic
- a new mission completion pipeline
- replacing the existing check-in flow
- replacing MissionCenter
- replacing RingoCoach

Progression remains owned by the existing check-in, stats, streak, achievement, and activity pipeline.

### 3.7 Current-State Boundary

Implemented today:

- Mission focus mode
- CompactProgressStrip
- first-run staged reveal
- post-first-win completion UX
- Rest Mode
- collapsed mission status details
- main/tiny mission-family behavior
- bonus missions as optional extra momentum
- Telegram reminder automation and diagnostics

Still planned:

- full Mission Context UX layer
- universal Path -> Challenge -> Mission breadcrumbs
- backend mission context model
- contextual reward sequence showing affected path/challenge progress
- complete tiny/bonus/remind-later context clarity across all surfaces
- implementation of the wireframes

## 4. Wireframe Language And Conventions

These are low-fidelity text wireframes only.

They are not:

- final UI designs
- screenshots
- Figma files
- implementation code
- component APIs

### 4.1 Visual Symbols

```txt
┌───┐  Card boundary
├───┤  Section divider
│   │  Content area
[ ]    Button/action
(...)  Quiet metadata or optional status
→      Breadcrumb or flow direction
```

### 4.2 Content Blocks

Each wireframe generally follows this order:

```txt
Ringo explanation
Path / Challenge breadcrumb
Mission intensity chip
Mission title
Concrete action instruction
Why this helps
Primary action
Secondary actions
Collapsed mission status
```

### 4.3 Button Hierarchy

```txt
[Primary action]
[Secondary] [Secondary]
Quiet text link / collapsible detail
```

### 4.4 Context Density

The mission card should not become a dashboard.

Always show enough context to reduce confusion, but keep deeper details collapsed.

### 4.5 Copy Tone

Copy should be:

- warm
- short
- clear
- no-shame
- deterministic first
- emotionally safe
- easy to translate into Persian later

Avoid:

- pressure-heavy streak language
- long motivational paragraphs
- “failure” framing
- treating tiny missions as lesser wins
- pushing bonus work as required

## 5. Shared Mission Card Anatomy

Reusable mission context card structure:

```txt
Ringo explanation
Path / Challenge breadcrumb
Mission intensity chip
Mission title
Concrete action instruction
Why this helps
Primary action
Secondary actions
Collapsed mission status
```

### 5.1 Ringo Explanation

#### Purpose

Explains the mission in human language before system detail appears.

#### When It Appears

Always appears at the top of mission-focused states.

#### When It Should Stay Hidden

It should not be hidden in MissionCenter focus states. It may be shortened in compact views or Telegram messages.

#### How It Reduces Confusion

It answers:

```txt
Why is this here?
What does Ringo want me to understand first?
```

### 5.2 Path / Challenge Breadcrumb

#### Purpose

Shows where the mission belongs.

Example:

```txt
Body Momentum -> Move Your Body
```

#### When It Appears

Appears in all mission cards, reward steps, reminder returns, and Telegram reminder context.

#### When It Should Stay Hidden

Can be hidden only when there is no path/challenge yet, such as new-user setup.

#### How It Reduces Confusion

It prevents the mission from feeling like a random task.

### 5.3 Mission Intensity Chip

#### Purpose

Shows the user whether the mission is main, tiny, or bonus.

Examples:

```txt
MAIN · 10 min
TINY · 2 min
BONUS · optional
```

#### When It Appears

Appears in every mission card.

#### When It Should Stay Hidden

It can be hidden in very small summary lists if the mission title already includes context, but it should remain visible in the focused daily card.

#### How It Reduces Confusion

It tells users whether the mission is required, a smaller substitute, or optional extra momentum.

### 5.4 Mission Title

#### Purpose

Names the mission.

#### When It Appears

Always appears in mission states.

#### When It Should Stay Hidden

Never hidden in mission focus states.

#### How It Reduces Confusion

It gives the mission a stable identity across MissionCenter, reward sequence, reminders, and status details.

### 5.5 Concrete Action Instruction

#### Purpose

Clarifies what counts as doing the mission.

Example:

```txt
Walk, stretch, or do light mobility. Anything intentional counts.
```

#### When It Appears

Always appears before the primary action.

#### When It Should Stay Hidden

It should not be hidden for main/tiny/reminder states. It may be shortened for bonus missions if the action is already obvious.

#### How It Reduces Confusion

It answers:

```txt
What exactly am I supposed to do?
```

### 5.6 Why This Helps

#### Purpose

Connects the mission to purpose and progress.

Example:

```txt
Keeps today safe for this challenge and keeps your Body Momentum path alive.
```

#### When It Appears

Appears in pending, tiny, bonus, reminder return, and multiple challenge states.

#### When It Should Stay Hidden

Can be collapsed in completion/rest states if the user has already completed the action.

#### How It Reduces Confusion

It answers:

```txt
Why am I doing this?
What progress will this create?
```

### 5.7 Primary Action

#### Purpose

Shows the one most useful next step.

#### When It Appears

Always appears unless the state is a passive reward step.

#### When It Should Stay Hidden

Can be replaced by `Continue` during reward sequence steps.

#### How It Reduces Confusion

It makes the next action obvious.

### 5.8 Secondary Actions

#### Purpose

Offer safe alternatives without competing with the main action.

Examples:

- Make it smaller
- Remind me later
- Return to main
- Skip today
- Start bonus
- Show dashboard

#### When It Appears

Appears when a useful alternative exists.

#### When It Should Stay Hidden

Hide secondary actions when they create decision overload, especially during first-run staged reveal.

#### How It Reduces Confusion

It gives user agency without making every option feel equal.

### 5.9 Collapsed Mission Status

#### Purpose

Provides deeper context for users who want it.

Examples:

- mission status
- reminder time
- other active challenges
- path/challenge details

#### When It Appears

Appears as a collapsed control in focus mode.

#### When It Should Stay Hidden

Stays collapsed by default during mission focus mode.

#### How It Reduces Confusion

It keeps the main card calm while still making context available.

## 6. Shared User Flow

Default daily flow:

```txt
Dashboard opens
  -> Ringo reads current mission state
  -> MissionCenter shows focused mission card
  -> User chooses primary or secondary action
  -> Mission state changes
  -> Reward/confirmation explains what changed
  -> User finishes for today or chooses optional next step
  -> Rest Mode or explicit dashboard reveal
```

### 6.1 Main Mission Success Flow

```txt
Main mission pending
  -> Complete mission
  -> Reward sequence
  -> Today safe
  -> Optional bonus or Finish for today
  -> Rest Mode
```

### 6.2 Tiny Mission Success Flow

```txt
Main mission feels too much
  -> Tiny mission offered
  -> Complete tiny mission
  -> Today safe
  -> No need to force bigger version
  -> Finish for today
  -> Rest Mode
```

### 6.3 Bonus Flow

```txt
Today already safe
  -> Bonus mission offered as optional
  -> User either finishes for today or starts bonus
  -> If bonus completed: extra momentum confirmation
  -> Finish for today
```

### 6.4 Reminder Flow

```txt
Mission pending
  -> Remind me later
  -> Reminder confirmation with mission context
  -> Telegram/app reminder later
  -> Mission returns with “You asked me to remind you” context
  -> Complete / remind again / skip
```

### 6.5 Skip Flow

```txt
Mission skipped
  -> If required: offer smaller/gentler next step
  -> If bonus: confirm today remains safe
  -> User chooses next step or rest
```

## 7. State Wireframes

### 7.1 Main Mission Pending

#### User Situation

The user has an active path/challenge and today’s required main mission is pending.

#### UX Goal

Make the main mission feel like one clear daily step. The user should understand what to do, where it belongs, and why completing it protects today.

#### Wireframe

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “This is your main step today. Do this once  │
│ and today is safe.”                          │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ MAIN · 10 min                                │
│                                              │
│ Move for 10 minutes                          │
│ Walk, stretch, or do light mobility.         │
│ Anything intentional counts.                 │
│                                              │
│ Why this helps                               │
│ Keeps today safe for this challenge and      │
│ keeps your Body Momentum path moving.        │
│                                              │
│ [Complete mission]                           │
│ [Make it smaller] [Remind me later]          │
│                                              │
│ Show mission status                          │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│ CompactProgressStrip                         │
│ Level 2 · 40% to next · Streak 3             │
└──────────────────────────────────────────────┘
```

#### Primary Action

`Complete mission`

#### Secondary Actions

- `Make it smaller`
- `Remind me later`
- `Show mission status`
- Optional: `Skip today` if current UX supports it without pressure

#### Context Shown

- Ringo explanation
- Path -> Challenge breadcrumb
- MAIN chip
- Estimated time
- Mission title
- What counts instruction
- Why this helps
- Primary/secondary actions
- Compact progress strip

#### Context Hidden

- Full dashboard sections
- Full path planning details
- Full leaderboard/activity/achievement surfaces
- Other active challenges unless user expands status

#### Copy Direction

Warm, direct, enough-for-today framing.

Avoid:

```txt
Don’t lose your streak.
You must complete this.
```

Prefer:

```txt
Do this once and today is safe.
```

#### Transition To Next State

- Complete mission -> `Reward Sequence After Completion`
- Make it smaller -> `Tiny Mission Offered`
- Remind me later -> `Mission Reminded Later`
- Show mission status -> expanded mission status details inside focus mode

#### Notes

This is the most important baseline state. If this wireframe is unclear, every other mission context state will feel unstable.

### 7.2 Main Mission Completed

#### User Situation

The user completed the main mission for today.

#### UX Goal

Confirm that today is safe and make stopping feel successful. If a bonus exists, present it as optional only.

#### Wireframe

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “Nice. Today is safe. You completed the main │
│ step for this challenge.”                    │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ COMPLETED · MAIN                             │
│                                              │
│ Move for 10 minutes                          │
│ Completed today                              │
│                                              │
│ What changed                                 │
│ Today is protected for this challenge.       │
│ Your progress can continue from here.        │
│                                              │
│ [Finish for today]                           │
│ [Try optional bonus] [View reward details]   │
│                                              │
│ Show dashboard                               │
└──────────────────────────────────────────────┘
```

#### Primary Action

`Finish for today`

#### Secondary Actions

- `Try optional bonus` if bonus exists
- `View reward details`
- `Show dashboard`

#### Context Shown

- Completed mission
- Affected path/challenge
- Today safe confirmation
- Optional bonus framing if available

#### Context Hidden

- Full dashboard by default
- Bonus details unless user chooses bonus
- Dense mission status history unless expanded

#### Copy Direction

Completion copy should remove pressure.

Prefer:

```txt
Today is safe. Anything else is optional.
```

#### Transition To Next State

- Finish for today -> `Today Already Saved / Rest Mode`
- Try optional bonus -> `Bonus Mission Offered`
- View reward details -> reward detail/sequence view
- Show dashboard -> full dashboard reveal

#### Notes

The primary action should be rest/finish, not more work.

### 7.3 Tiny Mission Offered

#### User Situation

The user chooses a smaller version of the main mission or Ringo offers a lower-pressure substitute.

#### UX Goal

Make the tiny mission feel connected, valid, and enough for today if applicable.

#### Wireframe

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “Let’s make it smaller. This still belongs   │
│ to today’s mission and it still counts.”     │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ TINY · 2 min                                 │
│ Smaller version of: Move for 10 minutes      │
│                                              │
│ Move for 2 minutes                           │
│ Stand up, stretch, or walk around the room.  │
│                                              │
│ Why this helps                               │
│ This keeps the same challenge alive without  │
│ forcing the bigger version today.            │
│                                              │
│ [Complete tiny mission]                      │
│ [Return to main] [Remind me later]           │
│                                              │
│ Show mission status                          │
└──────────────────────────────────────────────┘
```

#### Primary Action

`Complete tiny mission`

#### Secondary Actions

- `Return to main`
- `Remind me later`
- `Show mission status`
- Optional: `Skip today`

#### Context Shown

- Path/challenge breadcrumb
- TINY chip
- Parent main mission relationship
- Clear “still counts” explanation
- Concrete tiny action

#### Context Hidden

- Full parent mission details
- Full dashboard
- Bonus missions unless today becomes safe

#### Copy Direction

No shame. No “easy mode” language.

Prefer:

```txt
This is the smaller version. It still counts.
```

Avoid:

```txt
If you can’t do the real one...
```

#### Transition To Next State

- Complete tiny mission -> `Tiny Mission Completed`
- Return to main -> `Main Mission Pending`
- Remind me later -> `Mission Reminded Later`

#### Notes

The parent relationship must be visually explicit. Without it, tiny missions feel random.

### 7.4 Tiny Mission Completed

#### User Situation

The user completed the tiny substitute mission.

#### UX Goal

Confirm that the smaller win counts and the user does not need to force the bigger version.

#### Wireframe

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “Good. The smaller step counts. Today is     │
│ safe — no need to force the bigger version.” │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ COMPLETED · TINY                             │
│ Smaller version of: Move for 10 minutes      │
│                                              │
│ Move for 2 minutes                           │
│ Completed today                              │
│                                              │
│ What changed                                 │
│ The main mission family is satisfied for     │
│ today. You protected today with a smaller    │
│ step.                                        │
│                                              │
│ [Finish for today]                           │
│ [View reward details] [Show dashboard]       │
└──────────────────────────────────────────────┘
```

#### Primary Action

`Finish for today`

#### Secondary Actions

- `View reward details`
- `Show dashboard`
- Optional bonus only if it remains clearly non-required

#### Context Shown

- Tiny completion
- Parent main mission relation
- Today safe explanation
- No need to force bigger version

#### Context Hidden

- Parent main as a pending required task
- Bonus pressure
- Full dashboard by default

#### Copy Direction

Validate the smaller action as a real win.

Prefer:

```txt
You protected today with a smaller step.
```

#### Transition To Next State

- Finish for today -> `Today Already Saved / Rest Mode`
- View reward details -> `Reward Sequence After Completion`
- Show dashboard -> full dashboard reveal

#### Notes

This state is key for emotional safety. It should strengthen self-efficacy.

### 7.5 Bonus Mission Offered

#### User Situation

The required mission family is already completed, and a bonus mission is available.

#### UX Goal

Frame the bonus as optional extra momentum, not required work.

#### Wireframe

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “Today is already safe. This bonus is only   │
│ extra momentum if you still have energy.”    │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ BONUS · optional · 5 min                     │
│                                              │
│ Add one extra movement minute                │
│ Do a small extra stretch, walk, or mobility  │
│ move. Stop anytime.                          │
│                                              │
│ Why this helps                               │
│ Adds extra momentum, but it is not needed    │
│ to protect today.                            │
│                                              │
│ [Finish for today]                           │
│ [Start bonus] [Remind me later]              │
│                                              │
│ Show mission status                          │
└──────────────────────────────────────────────┘
```

#### Primary Action

`Finish for today`

#### Secondary Actions

- `Start bonus`
- `Remind me later`
- `Show mission status`
- `Skip bonus`

#### Context Shown

- Today already safe
- BONUS chip
- Optional framing
- Bonus title/action
- Why this helps without pressure

#### Context Hidden

- Any implication that bonus protects streak
- Full reward details until completion
- Full dashboard by default

#### Copy Direction

Optional, no-pressure, energy-aware.

Prefer:

```txt
Only if you still have energy.
```

#### Transition To Next State

- Finish for today -> `Today Already Saved / Rest Mode`
- Start bonus -> active bonus mission state or `Bonus Mission Completed` after completion
- Remind me later -> `Mission Reminded Later`
- Skip bonus -> `Mission Skipped` optional-bonus version

#### Notes

The primary action should remain `Finish for today` because the day is already safe.

### 7.6 Bonus Mission Completed

#### User Situation

The user completed an optional bonus mission.

#### UX Goal

Celebrate extra momentum without confusing it with required daily progress.

#### Wireframe

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “Extra momentum added. You were already safe │
│ today — this is a bonus win.”                │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ COMPLETED · BONUS                            │
│                                              │
│ Add one extra movement minute                │
│ Completed today                              │
│                                              │
│ What changed                                 │
│ Extra effort recorded for this mission.      │
│ Today was already protected before this.     │
│                                              │
│ [Finish for today]                           │
│ [View reward details] [Show dashboard]       │
└──────────────────────────────────────────────┘
```

#### Primary Action

`Finish for today`

#### Secondary Actions

- `View reward details`
- `Show dashboard`

#### Context Shown

- Bonus completed
- Affected path/challenge
- Extra momentum language
- Reminder that today was already safe

#### Context Hidden

- Duplicate today-safe celebration if it already happened
- Required-task framing
- Full dashboard by default

#### Copy Direction

Celebrate, but do not exaggerate system impact.

Prefer:

```txt
This is a bonus win.
```

#### Transition To Next State

- Finish for today -> `Today Already Saved / Rest Mode`
- View reward details -> reward detail/sequence view
- Show dashboard -> full dashboard reveal

#### Notes

This state should not create the feeling that one day needs endless completion.

### 7.7 Mission Skipped

#### User Situation

The user skipped a mission. The UX must distinguish required mission skip from optional bonus skip.

#### UX Goal

Keep the user emotionally safe and clarify what skipping means for today.

#### Wireframe

Required main/tiny skipped:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “No shame. This mission is skipped for now,  │
│ but today is not safe yet.”                  │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ SKIPPED · MAIN                               │
│                                              │
│ Move for 10 minutes                          │
│ Skipped today                                │
│                                              │
│ What this means                              │
│ This required step did not protect today.    │
│ We can still try something smaller.          │
│                                              │
│ [Try a smaller step]                         │
│ [Remind me later] [Show dashboard]           │
│                                              │
│ Show mission status                          │
└──────────────────────────────────────────────┘
```

Optional bonus skipped:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “Bonus skipped. That’s okay — today was      │
│ already safe.”                               │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ SKIPPED · BONUS                              │
│                                              │
│ Add one extra movement minute                │
│ Skipped today                                │
│                                              │
│ What this means                              │
│ No progress is at risk. This was optional.   │
│                                              │
│ [Finish for today]                           │
│ [Show dashboard]                             │
└──────────────────────────────────────────────┘
```

#### Primary Action

Required skip: `Try a smaller step`

Bonus skip: `Finish for today`

#### Secondary Actions

Required skip:

- `Remind me later`
- `Show dashboard`
- `Show mission status`

Bonus skip:

- `Show dashboard`
- Optional: `View today’s completed mission`

#### Context Shown

- Mission skipped
- Intensity of skipped mission
- Whether today is safe
- Gentler next step for required skips

#### Context Hidden

- Punishment language
- Streak panic
- Dense failure state

#### Copy Direction

No shame. Adaptive. Clear.

Required skip should say:

```txt
Today is not safe yet.
We can still try something smaller.
```

Bonus skip should say:

```txt
Today was already safe.
This was optional.
```

#### Transition To Next State

- Required skip + smaller step -> `Tiny Mission Offered`
- Required skip + remind later -> `Mission Reminded Later`
- Bonus skip + finish -> `Today Already Saved / Rest Mode`

#### Notes

Skipping is a signal for adaptation, not a failure state.

### 7.8 Mission Reminded Later

#### User Situation

The user scheduled a mission reminder.

#### UX Goal

Confirm the reminder while preserving path/challenge/mission context and clarifying whether today is safe.

#### Wireframe

Required mission reminder while today is not safe:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “Got it. I’ll bring this back later. It      │
│ still belongs to today’s main step.”         │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ REMINDER SET · MAIN                          │
│                                              │
│ Move for 10 minutes                          │
│ Reminder: Today at 18:30                     │
│                                              │
│ What this means                              │
│ The mission is paused, not completed.        │
│ Today is not safe until you finish this or   │
│ a smaller version before reset.              │
│                                              │
│ Telegram                                     │
│ Connected · reminders enabled                │
│                                              │
│ [Done for now]                               │
│ [Change time] [Make it smaller now]          │
│                                              │
│ Show mission status                          │
└──────────────────────────────────────────────┘
```

Reminder after today is already safe:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “Reminder saved. Today is already safe, so   │
│ this will come back as optional context.”    │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ REMINDER SET · BONUS                         │
│                                              │
│ Add one extra movement minute                │
│ Reminder: Today at 19:00                     │
│                                              │
│ Telegram                                     │
│ Not connected · open settings to connect     │
│                                              │
│ [Finish for today]                           │
│ [Connect Telegram] [Change time]             │
└──────────────────────────────────────────────┘
```

#### Primary Action

- If today is not safe: `Done for now`
- If today is safe: `Finish for today`

#### Secondary Actions

- `Change time`
- `Make it smaller now` if main/tiny family is not safe
- `Connect Telegram` if not connected
- `Enable reminders` if connected but disabled
- `Show mission status`

#### Context Shown

- Reminder set state
- Reminder time
- Mission context
- Today-safe meaning
- Telegram status if relevant

#### Context Hidden

- Protected admin diagnostics
- Raw Telegram chat IDs
- Reminder automation tokens
- Full dashboard by default

#### Copy Direction

Make the reminder feel like a remembered agreement.

Prefer:

```txt
I’ll bring this back later.
```

#### Transition To Next State

- Reminder time arrives -> `Reminded Mission Returns`
- Finish for today if safe -> `Today Already Saved / Rest Mode`
- Make it smaller now -> `Tiny Mission Offered`

#### Notes

The reminder confirmation must include the mission context, not only the time.

### 7.9 Reminded Mission Returns

#### User Situation

A mission that the user postponed becomes due and returns in the app.

#### UX Goal

Restore context clearly so the user remembers why the mission is back.

#### Wireframe

Due reminder while today is not safe:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “You asked me to remind you. This is still   │
│ today’s step for Move Your Body.”            │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ DUE REMINDER · MAIN · 10 min                 │
│                                              │
│ Move for 10 minutes                          │
│ Walk, stretch, or do light mobility.         │
│                                              │
│ Why this returned                            │
│ You saved this reminder earlier today.       │
│ Completing it can still protect today.       │
│                                              │
│ [Complete mission]                           │
│ [Remind me again] [Make it smaller]          │
│                                              │
│ Skip today · Show mission status             │
└──────────────────────────────────────────────┘
```

Due reminder after today is already safe:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “This reminder is back, but today is already │
│ safe. Only continue if you want extra energy.”│
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ DUE REMINDER · BONUS                         │
│                                              │
│ Add one extra movement minute                │
│ Optional reminder                            │
│                                              │
│ [Finish for today]                           │
│ [Start optional mission] [Remind again]      │
└──────────────────────────────────────────────┘
```

#### Primary Action

- If today is not safe: `Complete mission`
- If today is safe: `Finish for today`

#### Secondary Actions

- `Remind me again`
- `Make it smaller`
- `Skip today`
- `Start optional mission`
- `Show mission status`

#### Context Shown

- “You asked me to remind you” copy
- Due reminder state
- Path/challenge breadcrumb
- Mission title/action
- Today-safe status

#### Context Hidden

- Full dashboard
- Raw reminder delivery diagnostics
- Other active missions unless expanded

#### Copy Direction

Reminder return should feel personal and remembered.

Prefer:

```txt
You asked me to remind you.
```

#### Transition To Next State

- Complete mission -> `Reward Sequence After Completion`
- Remind again -> `Mission Reminded Later`
- Make it smaller -> `Tiny Mission Offered`
- Finish for today -> `Today Already Saved / Rest Mode`

#### Notes

Returned reminders need stronger context than normal missions because the user may have forgotten the original decision.

### 7.10 Today Already Saved / Rest Mode

#### User Situation

The required daily mission family is complete, and the user chooses to finish.

#### UX Goal

Make rest feel like a successful ending, not abandonment.

#### Wireframe

```txt
┌──────────────────────────────────────────────┐
│ Ringo sleeping / calm                        │
│ “Today is safe. You did enough.”             │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ TODAY SAVED                                  │
│                                              │
│ Completed today                              │
│ Move for 10 minutes                          │
│                                              │
│ Optional reminder                            │
│ Bonus reminder set for 19:00                 │
│                                              │
│ Rest state                                   │
│ You can close the app now. I’ll be here      │
│ when you come back.                          │
│                                              │
│ [Rest / close for today]                     │
│ [Show dashboard]                             │
└──────────────────────────────────────────────┘
```

No future reminder variant:

```txt
┌──────────────────────────────────────────────┐
│ Ringo sleeping / calm                        │
│ “Today is safe. You did enough.”             │
├──────────────────────────────────────────────┤
│ TODAY SAVED                                  │
│ No more required action today.               │
│                                              │
│ [Rest / close for today]                     │
│ [Show dashboard]                             │
└──────────────────────────────────────────────┘
```

#### Primary Action

`Rest / close for today`

#### Secondary Actions

- `Show dashboard`
- Optional: `View today’s reward`

#### Context Shown

- Ringo calm/sleeping state
- Today safe confirmation
- Completed mission summary
- Optional future reminder timing if available
- Explicit dashboard escape hatch

#### Context Hidden

- Full dashboard by default
- Bonus missions unless user chose to continue
- Dense progress systems

#### Copy Direction

Rest should feel earned.

Prefer:

```txt
You did enough.
```

#### Transition To Next State

- Rest / close -> end of daily loop
- Show dashboard -> full dashboard reveal
- Future reminder due -> `Reminded Mission Returns`

#### Notes

Rest Mode is a successful ending, not an empty state.

### 7.11 Multiple Active Challenges

#### User Situation

The user has multiple active challenges. Ringo selects one mission as the clearest next step.

#### UX Goal

Show one selected mission without hiding that other challenges exist.

#### Wireframe

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “You have a few active challenges. I picked  │
│ the clearest one that needs attention now.”  │
├──────────────────────────────────────────────┤
│ Selected from 3 active challenges            │
│                                              │
│ Body Momentum → Move Your Body               │
│ MAIN · 10 min                                │
│                                              │
│ Move for 10 minutes                          │
│ Walk, stretch, or do light mobility.         │
│                                              │
│ Why this one                                 │
│ This is the best required step to protect    │
│ today right now.                             │
│                                              │
│ [Complete mission]                           │
│ [Make it smaller] [Remind me later]          │
│                                              │
│ Show other active challenges                 │
│ Show mission status                          │
└──────────────────────────────────────────────┘
```

Expanded other challenges:

```txt
┌──────────────────────────────────────────────┐
│ Other active challenges                      │
│                                              │
│ Creative Spark                               │
│ Pending bonus · optional                     │
│                                              │
│ Read Five Pages                              │
│ Reminder set for 20:00                       │
│                                              │
│ [View all paths]                             │
└──────────────────────────────────────────────┘
```

#### Primary Action

`Complete mission`

#### Secondary Actions

- `Make it smaller`
- `Remind me later`
- `Show other active challenges`
- `Show mission status`
- `View all paths`

#### Context Shown

- Ringo priority explanation
- Selected mission
- Selected from X active challenges note
- Collapsed access to other challenges

#### Context Hidden

- Full challenge list by default
- Full path planning details
- Dense ranking/recommendation logic

#### Copy Direction

Explain enough to create trust, but do not expose algorithmic complexity.

Prefer:

```txt
I picked the clearest one that needs attention now.
```

#### Transition To Next State

- Complete mission -> `Reward Sequence After Completion`
- Show other active challenges -> expanded secondary context
- View all paths -> `/paths` planning surface

#### Notes

This state prevents Ringo’s suggestion from feeling arbitrary.

### 7.12 Reward Sequence After Completion

#### User Situation

The user has completed a mission and enters the reward/result moment.

#### UX Goal

Explain what changed step by step, with Ringo emotional feedback first and system context after.

#### Wireframe

Step 1 — Ringo reaction:

```txt
┌──────────────────────────────────────────────┐
│ Ringo proud / celebration                    │
│ “Nice work. You did the step.”               │
│                                              │
│ [Continue]                                   │
└──────────────────────────────────────────────┘
```

Step 2 — Mission completed:

```txt
┌──────────────────────────────────────────────┐
│ Mission completed                            │
├──────────────────────────────────────────────┤
│ Move for 10 minutes                          │
│ MAIN · completed today                       │
│                                              │
│ [Continue]                                   │
└──────────────────────────────────────────────┘
```

Step 3 — Challenge affected:

```txt
┌──────────────────────────────────────────────┐
│ Challenge progress                           │
├──────────────────────────────────────────────┤
│ Move Your Body                               │
│ Today’s required step is complete.           │
│                                              │
│ [Continue]                                   │
└──────────────────────────────────────────────┘
```

Step 4 — Path affected:

```txt
┌──────────────────────────────────────────────┐
│ Path progress                                │
├──────────────────────────────────────────────┤
│ Body Momentum                                │
│ This keeps your path moving today.           │
│                                              │
│ [Continue]                                   │
└──────────────────────────────────────────────┘
```

Step 5 — XP / check-in reward:

```txt
┌──────────────────────────────────────────────┐
│ Reward                                       │
├──────────────────────────────────────────────┤
│ +10 XP                                       │
│ Progress updated through today’s check-in.   │
│                                              │
│ [Continue]                                   │
└──────────────────────────────────────────────┘
```

Step 6 — Today saved / streak protected:

```txt
┌──────────────────────────────────────────────┐
│ Today saved                                  │
├──────────────────────────────────────────────┤
│ Today is safe.                               │
│ Your consistency is protected for today.     │
│                                              │
│ [Continue]                                   │
└──────────────────────────────────────────────┘
```

Step 7 — Achievement unlocked if any:

```txt
┌──────────────────────────────────────────────┐
│ Achievement unlocked                         │
├──────────────────────────────────────────────┤
│ First Strike                                 │
│ You completed your first daily action.       │
│                                              │
│ [Continue]                                   │
└──────────────────────────────────────────────┘
```

Step 8 — Next gentle step:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “You can stop here. Anything else is         │
│ optional.”                                   │
├──────────────────────────────────────────────┤
│ [Finish for today]                           │
│ [Try optional bonus] [Show dashboard]        │
└──────────────────────────────────────────────┘
```

#### Primary Action

During sequence: `Continue`

Final step: `Finish for today`

#### Secondary Actions

- `Try optional bonus` if available
- `Show dashboard`
- Optional: `View details`

#### Context Shown

- Ringo reaction
- Mission completed
- Challenge affected
- Path affected
- XP/check-in reward
- Today saved/streak protected
- Achievements if any
- Next gentle step

#### Context Hidden

- Raw reward payloads
- Duplicate progression calculations
- Detailed stats unless user opens dashboard

#### Copy Direction

Reward sequence should explain before it celebrates too much.

Prefer:

```txt
This keeps your path moving today.
```

Avoid:

```txt
Massive win! Don’t stop now!
```

#### Transition To Next State

- Final finish -> `Today Already Saved / Rest Mode`
- Optional bonus -> `Bonus Mission Offered`
- Show dashboard -> full dashboard reveal

#### Notes

Already implemented:

- reward/check-in feedback
- MissionCenter completion flow
- post-first-win copy
- Rest Mode
- existing XP/streak/achievement data through current pipeline

Planned context enhancements:

- affected challenge step
- affected path step
- consistent mission-context reward framing across main/tiny/bonus/reminder states
- universal contextual reward sequence UI

### 7.13 Telegram Reminder Opens The App

#### User Situation

The user receives a Telegram reminder and opens RingoStrike from it.

#### UX Goal

Restore the reminded mission inside MissionCenter with full context, so the user does not land on a confusing generic dashboard.

#### Wireframe

Telegram message:

```txt
┌──────────────────────────────────────────────┐
│ Telegram                                     │
├──────────────────────────────────────────────┤
│ Ringo reminder                               │
│ You asked me to remind you:                  │
│ Move for 10 minutes                          │
│                                              │
│ Body Momentum → Move Your Body               │
│ One small step can still save today.         │
│                                              │
│ [Open RingoStrike]                           │
└──────────────────────────────────────────────┘
```

App opens to MissionCenter:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “You opened the reminder. This is the step   │
│ you asked me to bring back.”                 │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ DUE REMINDER · MAIN · 10 min                 │
│                                              │
│ Move for 10 minutes                          │
│ Walk, stretch, or do light mobility.         │
│                                              │
│ Reminder context                             │
│ Reminder set earlier today.                  │
│ Completing it can still protect today.       │
│                                              │
│ [Complete mission]                           │
│ [Remind again] [Make it smaller]             │
│                                              │
│ Skip today · Show mission status             │
└──────────────────────────────────────────────┘
```

If today already safe:

```txt
┌──────────────────────────────────────────────┐
│ Ringo                                        │
│ “This reminder came back, but today is       │
│ already safe. You can rest.”                 │
├──────────────────────────────────────────────┤
│ Body Momentum → Move Your Body               │
│ OPTIONAL REMINDER                            │
│                                              │
│ [Finish for today]                           │
│ [Start optional mission] [Remind again]      │
└──────────────────────────────────────────────┘
```

#### Primary Action

- If today is not safe: `Complete mission`
- If today is safe: `Finish for today`

#### Secondary Actions

- `Remind again`
- `Make it smaller`
- `Skip today`
- `Start optional mission`
- `Show mission status`

#### Context Shown

- Telegram message context
- Path/challenge breadcrumb
- Mission title/action
- “You asked me to remind you” copy
- Today-safe status

#### Context Hidden

- Admin reminder diagnostics
- Raw reminder IDs
- Telegram chat IDs
- Automation tokens

#### Copy Direction

The transition from Telegram to app should feel continuous.

Prefer:

```txt
This is the step you asked me to bring back.
```

#### Transition To Next State

- Complete mission -> `Reward Sequence After Completion`
- Remind again -> `Mission Reminded Later`
- Make it smaller -> `Tiny Mission Offered`
- Finish for today -> `Today Already Saved / Rest Mode`

#### Notes

Current Telegram reminder automation exists. Mission-specific deep-link restoration may require future additive backend/frontend support and should remain planned until implemented.

## 8. Action Hierarchy Rules

### 8.1 Main Mission Pending

```txt
Primary: Complete mission
Secondary: Make it smaller, Remind me later
Quiet: Show mission status
```

### 8.2 Main Mission Completed

```txt
Primary: Finish for today
Secondary: Try optional bonus, View reward details
Quiet: Show dashboard
```

### 8.3 Tiny Mission Offered

```txt
Primary: Complete tiny mission
Secondary: Return to main, Remind me later
Quiet: Show mission status
```

### 8.4 Tiny Mission Completed

```txt
Primary: Finish for today
Secondary: View reward details
Quiet: Show dashboard
```

### 8.5 Bonus Mission Offered

```txt
Primary: Finish for today
Secondary: Start bonus, Remind me later
Quiet: Skip bonus, Show mission status
```

### 8.6 Bonus Mission Completed

```txt
Primary: Finish for today
Secondary: View reward details
Quiet: Show dashboard
```

### 8.7 Required Mission Skipped

```txt
Primary: Try a smaller step
Secondary: Remind me later
Quiet: Show dashboard, Show mission status
```

### 8.8 Optional Bonus Skipped

```txt
Primary: Finish for today
Secondary: Show dashboard
Quiet: View today’s completed mission
```

### 8.9 Reminder Set

```txt
Primary: Done for now or Finish for today
Secondary: Change time, Make it smaller now, Connect/enable Telegram
Quiet: Show mission status
```

### 8.10 Due Reminder

```txt
Primary: Complete mission or Finish for today
Secondary: Remind again, Make it smaller, Start optional mission
Quiet: Skip today, Show mission status
```

### 8.11 Reward Sequence

```txt
Primary: Continue through steps
Final primary: Finish for today
Secondary: Optional bonus, Show dashboard
```

## 9. Copy Placement Rules

### 9.1 Ringo Copy Comes First

The first meaningful text should be Ringo’s explanation.

Ringo copy should answer:

```txt
Why this mission?
Why now?
What is enough?
```

### 9.2 Breadcrumb Comes Before Mission Title

The breadcrumb should appear before the mission title.

Reason:

```txt
Users need origin before action.
```

### 9.3 Intensity Chip Must Be Near The Breadcrumb

The user should immediately know if the mission is:

- Main
- Tiny
- Bonus
- Reminder
- Completed
- Skipped

### 9.4 Concrete Instruction Goes Above The Primary Button

The user should not need to open details to understand what counts.

### 9.5 Why This Helps Goes Before Actions

The purpose should appear before the user decides.

### 9.6 Today-Safe Copy Must Be Explicit

Use direct language:

```txt
Today is safe.
You did enough.
Anything else is optional.
```

### 9.7 Reminder Copy Must Preserve User Agency

Use:

```txt
You asked me to remind you.
```

This makes the reminder feel intentional, not random.

### 9.8 Bonus Copy Must Avoid Pressure

Use:

```txt
Only if you still have energy.
```

Avoid:

```txt
Keep going.
Don’t stop now.
```

### 9.9 Tiny Copy Must Avoid Failure Framing

Use:

```txt
The smaller step counts.
```

Avoid:

```txt
If you failed the main one...
```

## 10. Responsive Notes

### 10.1 Mobile

On mobile, the card should stack vertically:

```txt
Ringo
Message
Breadcrumb
Chip
Title
Instruction
Why this helps
Primary action
Secondary actions
Collapsed details
Compact progress
```

Mobile rules:

- one full-width primary button
- secondary actions may wrap into two rows
- collapsed status should remain below actions
- avoid horizontal overflow in breadcrumb
- truncate long path/challenge names carefully
- keep tap targets large

### 10.2 Desktop

On desktop, the card can remain centered and narrow during focus mode.

Rules:

- do not reveal full dashboard just because space exists
- keep MissionCenter as the focus
- CompactProgressStrip can sit under MissionCenter
- optional status/details can appear below the main card, not beside it

### 10.3 Small Screens

For very small screens:

- shorten breadcrumb labels
- keep intensity chip visible
- preserve primary action visibility
- collapse “Why this helps” to one or two lines if necessary
- never hide the concrete action instruction

### 10.4 Reduced Motion

Reward sequence and first-run reveal should respect reduced-motion preferences.

If reduced motion is active:

- show content immediately
- avoid opacity/transform sequencing
- keep step-by-step reward progression as simple content changes

## 11. Accessibility Notes

### 11.1 Semantic Hierarchy

The mission title should be the main heading inside the mission card.

Ringo copy should be readable as supportive text, not only decorative speech.

### 11.2 Button Labels

Buttons should describe the action clearly:

- `Complete mission`
- `Complete tiny mission`
- `Finish for today`
- `Remind me later`
- `Show mission status`

Avoid vague labels like:

- `Go`
- `Okay`
- `Do it`

### 11.3 Color Independence

Do not rely only on color to distinguish:

- MAIN
- TINY
- BONUS
- REMINDER
- COMPLETED
- SKIPPED

Use text labels.

### 11.4 Screen Reader Context

Path/challenge breadcrumb should be readable as text:

```txt
Path: Body Momentum. Challenge: Move Your Body.
```

### 11.5 Focus Order

Recommended focus order:

```txt
Ringo explanation
Mission context
Mission title
Instruction
Primary action
Secondary actions
Show mission status
```

### 11.6 No Shame Accessibility

Copy should not create emotional penalty for users who skip, use tiny missions, or rest.

This is part of accessibility for users with low energy, ADHD, anxiety, burnout, or inconsistent capacity.

## 12. Frontend Impact Notes

This document does not implement frontend changes. It only identifies likely future impact areas.

Likely future frontend areas:

- `MissionCenter.vue`
- `RingoCoach.vue`
- `RewardMoment.vue`
- `CompactProgressStrip.vue`
- Rest Mode section inside MissionCenter
- mission action panels
- mission status collapsed details
- i18n locale files
- possible reusable mission context components

Possible future reusable UI pieces:

- `MissionContextBreadcrumb`
- `MissionIntensityChip`
- `MissionWhyBlock`
- `MissionParentRelation`
- `ReminderContextNotice`
- `TodaySafeSummary`
- `RewardContextStep`

These are names for analysis only, not implementation instructions.

Frontend rules:

- extend MissionCenter instead of replacing it
- extend RingoCoach instead of replacing it
- keep CompactProgressStrip as display-only context
- preserve focus-mode dashboard gating
- preserve Rest Mode as successful ending
- keep secondary details collapsed by default
- keep English/Persian display labels in frontend i18n
- do not duplicate progression calculations in frontend

## 13. Backend Impact Notes

This document does not propose backend writes or new progression logic.

Current fields may support much of the planned UX:

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

Future additive read-model fields may be useful only if the frontend cannot reliably produce clear context from existing data.

Potential additive read-model needs:

- clearer `why_now` reason text/key
- contextual reward sequence labels
- path/challenge progress labels
- mission-specific deep-link restoration metadata
- parent mission title for tiny mission context if not already available in the selected mission list
- today-safe/family-satisfied explanation fields

Backend safety rules:

- mission completion must continue through the existing mission/check-in pipeline
- XP remains owned by existing stats/check-in/achievement services
- streak remains owned by existing stats/check-in services
- achievements remain owned by the existing achievement pipeline
- reminder automation remains protected and server-owned
- frontend must not receive admin reminder tokens or raw Telegram chat IDs

Do not add:

- duplicate XP writes
- duplicate streak writes
- duplicate achievement writes
- a new mission completion pipeline
- path progress as a second economy without a separate product decision

## 14. Non-Goals

This document does not:

- implement code
- create Codex implementation prompts
- create Figma files
- create screenshots or images
- redesign the full dashboard
- replace MissionCenter
- replace RingoCoach
- replace RewardMoment
- replace CompactProgressStrip
- replace the check-in flow
- duplicate XP/streak/achievement logic
- introduce new backend writes
- introduce a new progression economy
- claim full Mission Context UX is already implemented
- define final component APIs
- define final visual design

## 15. Open Questions

- Should the breadcrumb always be visible, or can it collapse after the user has repeated the same mission several times?
- Should the tiny card show the parent mission title every time, or only on first exposure?
- Should bonus missions appear in the same card style or a softer “optional card” style?
- What should the exact Persian copy be for “Today is safe”?
- Should skipped required missions always lead to a tiny option if one exists?
- Should a skipped required mission ever route directly to Rest Mode, or only after a user explicitly accepts that today is not saved?
- Should reward sequence steps be tap-by-tap, auto-advance, or mixed?
- How much path/challenge progress can be shown before a formal path progress model exists?
- Should Telegram reminder links eventually deep-link into a specific mission focus state?
- How should the UI behave if a reminded mission returns after the daily reset?
- Should multiple active challenges allow manual mission switching in v1, or only show other challenges as collapsed context?
- What is the minimum data needed for a contextual reward sequence without backend schema changes?

## 16. Next Step

Next recommended step: Component Impact Analysis

After these wireframes, the next document should map:

- which existing components need extension
- which small reusable components may be introduced
- which API fields are already enough
- which context fields may require future additive read-model support
- how to preserve current MissionCenter, RingoCoach, reward, focus-mode, Rest Mode, and progression ownership boundaries

The next step should still avoid code implementation and should not create Codex prompts unless a later issue explicitly asks for implementation planning.
