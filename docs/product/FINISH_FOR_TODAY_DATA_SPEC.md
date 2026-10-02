# Finish for Today Data Spec

## Purpose

`Finish for today` should feel like a successful daily close, not just a navigation action.

The user should be able to press `Finish for today` and immediately understand:

- whether today is protected
- what meaningful work was completed
- what was safely postponed
- whether any optional/bonus work remains
- how to return to the dashboard

This is a Daily Loop polish item. It supports Living Space indirectly by making the daily progress moment clearer before/after room rewards, but it is not required for Living Space v1.

## Current State

Current MissionCenter behavior already has the needed foundations:

- `finishForToday()` enters frontend-only Rest Mode.
- `ringoGuidance.progress.today_saved` tells whether today is safe.
- `dailySummary` / `dailySummaryNarrative` already summarize done, reminded, skipped, tiny, main, and bonus mission groups.
- `nearestFutureReminder` / `nearestFutureReminderLabel` already expose the next reminder timing.
- Daily Momentum Bar already has action icons for `finish-today`, `protect-today`, `view-choices`, and related actions.
- `Show dashboard` is the intended escape hatch from focus/rest mode.

## Product Rule

Real daily progress should become a visible, understandable closeout state.

This is the daily equivalent of the Living Space rule:

```txt
Real progress -> visible change
```

For Finish for Today:

```txt
Real daily actions -> visible daily summary
```

## V1 Scope

V1 should extend Rest Mode with a concise daily summary using existing data.

Included:

- Today status: safe / at risk / finished with reminders.
- Completed mission count.
- Tiny substitute count, when relevant.
- Bonus completed count, when relevant.
- Reminded/deferred count and nearest reminder time.
- Skipped count, framed gently.
- One primary CTA: `Back to dashboard` / `Show dashboard`.
- One optional CTA only when useful: view remaining optional missions or explore paths.
- EN/FA copy.
- QA checklist entry.

Excluded:

- New backend endpoint.
- New database tables.
- New progression economy.
- Shop/inventory/editor behavior.
- Any new illustration, icon family, or sleeping Ringo art decision without explicit visual approval.
- Full activity timeline inside the finish card.

## Data Contract

V1 can be implemented from existing frontend state.

Source data:

| Need | Existing Source |
| --- | --- |
| Today is safe | `ringoGuidance.progress.today_saved` or `dailyMomentumTodaySafe` |
| Current streak | `dailyMomentumStreakCount` |
| Done missions | `dailySummary.done` |
| Main done | `dailySummary.mainDone` |
| Tiny done | `dailySummary.tinyDone` |
| Bonus done | `dailySummary.bonusDone` |
| Bonus available | `dailySummary.bonusAvailable` |
| Reminded/deferred | `dailySummary.reminded`, `nearestFutureReminderLabel` |
| Skipped | `dailySummary.skipped` |
| Path groups | `dailyMomentumPathGroups` |

Suggested internal projection:

```js
{
  todaySafe: true,
  completedCount: 1,
  tinyCount: 0,
  bonusCompletedCount: 1,
  bonusAvailableCount: 0,
  remindedCount: 1,
  skippedCount: 0,
  nextReminderLabel: "in 45 minutes",
  streakCount: 4,
  pathSummaries: [
    {
      key: "career",
      title: "Career",
      done: 1,
      total: 1,
      percent: 100
    }
  ]
}
```

This projection should be computed inside MissionCenter or a small local helper. It should not become a backend contract until a later analytics/reporting need exists.

## Recommended UX Behavior

When the user presses `Finish for today`:

1. Keep the existing Rest Mode route.
2. Replace or enrich the current rest card body with a compact summary.
3. Keep the mood calm and final.
4. Do not reopen dense dashboard content automatically.
5. Let the user explicitly choose `Show dashboard`.

Suggested content hierarchy:

- Title: today is safe / today is closed.
- One-line reassurance from Ringo.
- Summary row/list:
  - protected today
  - completed missions
  - optional/bonus progress
  - reminders set
  - skipped or deferred items
- CTA: show dashboard.

## Visual Decision Gate

The issue mentions a minimal sleeping Ringo/cat feeling.

That is a visual direction decision and needs explicit approval before implementation.

Before any visual implementation, confirm:

- Use current `sleeping` Ringo sprite only, or create/choose a new visual?
- Should the closeout be a card, a modal-like panel, or part of the existing MissionCenter surface?
- Should icons use the existing action icon set only?
- Should the summary use compact chips, rows, or a small progress strip?

Until approved, implementation should use existing components, existing icons, and existing Ringo sprites only.

## Acceptance Criteria

- Pressing `Finish for today` shows a daily summary, not only generic rest copy.
- Summary is derived from current mission state without extra backend writes.
- The user sees whether today is safe.
- Done, reminded, skipped, tiny, and bonus states are represented when present.
- The existing Rest Mode behavior remains.
- The full dashboard remains hidden until the user explicitly chooses to reveal it.
- The component works in English and Persian.
- Reduced-motion users do not receive new required animation.
- No new visual asset is added without approval.

## QA Notes

Test these cases:

- Main mission done, no bonus.
- Tiny mission done instead of main.
- Main done plus bonus available.
- Main done plus bonus completed.
- Reminder set for later.
- Skipped optional mission.
- All available missions completed.
- Persian locale.
- Mobile width.