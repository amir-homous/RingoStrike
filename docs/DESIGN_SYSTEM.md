# RingoStrike - Design System

## Current Implementation

The active global design system is implemented through:

- `frontend/src/styles/tokens.css`
- `frontend/src/styles/base.css`
- Vue component-scoped styles across `frontend/src/components/` and `frontend/src/views/`
- UI primitives in `frontend/src/components/ui/`

`frontend/src/main.js` imports only `tokens.css` and `base.css`. `frontend/src/style.css` and `frontend/src/assets/main.css` exist but are not currently imported by the app entry point.

## Product Design Direction

RingoStrike should continue to feel:

- premium
- cinematic
- progression-oriented
- calm and motivational
- identity-driven
- restrained, not noisy

Avoid:

- casino-style reward spam
- chaotic animations
- overloaded social comparison
- generic productivity-dashboard visuals

## Guided Progression UX Principles

RingoStrike should guide users through a clear daily progression path instead of presenting every feature at once.

Primary UX rule:

The next action should always be obvious.

Preferred pattern:

```txt
Path -> Today's Mission -> Check-in -> Reward -> Next Step
```

Design principles:

- Reduce first-time cognitive load.
- Show one primary action per screen where possible.
- Keep reward moments premium, calm, and emotionally meaningful.
- Avoid noisy animations, casino-like effects, or pressure-based streak messaging.
- Reveal advanced systems gradually: leaderboard, achievements, public profile, and Telegram reminders should support the core loop, not compete with it.
- Use RingoCoach as the primary guidance surface when the backend returns a Ringo decision. It should feel like contextual coaching, not a separate notification feed.

## Active CSS Tokens

Defined in `tokens.css`:

- Layout: `--container`, `--px`
- Spacing: `--s-4`, `--s-8`, `--s-12`, `--s-16`, `--s-20`, `--s-24`, `--s-32`
- Radius: `--r-10`, `--r-12`
- Color/surface: `--bg`, `--card`, `--card2`, `--border`, `--muted`, `--muted2`, `--focus`
- Shadow: `--shadow`
- Type sizing: `--h1`, `--h2`, `--body`, `--cap`
- Line heights: `--lh-tight`, `--lh`

Current palette is dark graphite with translucent card surfaces and muted white text.

## Active Base Styles

`base.css` applies:

- local Vazirmatn `@font-face` for Persian mode
- global `box-sizing`
- dark root, body, app, and shell background from `--bg`
- white text color
- system font stack for English/default UI
- Vazirmatn font stack only when `html[lang="fa"]`
- inherited fonts for native buttons and form controls
- basic link styling
- utility classes: `.h1`, `.h2`, `.caption`, `.stack-*`, `.hr`

Typography behavior:

- English (`lang="en"`) uses the existing system font stack.
- Persian (`lang="fa"`) uses `frontend/src/assets/fonts/Vazirmatn.woff2`.
- Font switching is tied to document `lang`; do not add component-local font overrides for ordinary UI text.
- `html`, `body`, `#app`, and the app shell should keep full-height dark background coverage. This prevents exposed browser/root background in both LTR and RTL layouts.

## Growth-Map Surfaces

MissionCenter's optional explorer uses a restrained growth-map visual language after the required daily loop is safe.

Use this pattern for similar progression surfaces:

- Progress-surface cards should keep progress fills clipped inside the card, with the card as the `position: relative` / `overflow: hidden` boundary.
- Progress fills should respect text direction without creating horizontal overflow: LTR fills start from the left, RTL fills start from the right.
- Circular icon progress rings can show path/challenge completion while keeping the main row calm.
- Reward-ready/building slots are visual status affordances only; they should feel premium but not imply backend reward-claim logic.
- XP summaries should be compact: earned/total while in progress, earned/completed language when complete.
- Mission rows can use mission-key icons and status-aware color accents, but status should win over intensity/bonus styling.
- Completed paths/challenges may remain visible to reinforce completion and give users a sense of closed progress.

Keep this style restrained: the optional explorer should feel like a calm progression map, not a noisy game board.

## Component System

UI primitives:

- `AppContainer.vue`
- `AppFooter.vue`
- `AppHeader.vue`
- `BaseButton.vue`
- `BaseCard.vue`
- `BaseInput.vue`
- `SkeletonBlock.vue`
- `Spinner.vue`
- `UiState.vue`

Feature components:

- achievements: cards, grids, previews, toasts
- activity: timeline, timeline items, day grouping, empty state
- challenges: challenge card
- missions: MissionCenter, PathSelection, focus-mode mission surfaces, collapsed mission status details, and Rest Mode
- feedback: RewardMoment for check-ins and JoinSuccessMoment for softer challenge-start transitions
- guided: reusable first-path empty state
- onboarding: welcome, identity path selection, and suggested challenge steps
- profile: hero card, stats grid, settings card/modal, avatar, consistency heatmap
- progress: hero progress, compact focus strip, next goal, recent feed, stats grid, XP bar

## Frontend Pages

Current views:

- `Dashboard.vue`
- `Paths.vue`
- `Challenges.vue`
- `Enrollment.vue`
- `Leaderboard.vue`
- `Profile.vue`
- `PublicProfile.vue`
- `Onboarding.vue`
- `Login.vue`
- `AuthCallback.vue`
- `ApiDocsView.vue`

## Ringo Helper Assets

Ringo helper sprites live in `frontend/src/assets/ringo/` and are resolved through `frontend/src/constants/ringoSprites.js`.

Intended sprite keys:

```txt
idle, welcome, talking, explaining, thinking, encouraging, warning, concerned,
happy, celebration, achievement, proud, sad, sleeping, focus, victory
```

`RingoCoach.vue` displays a sprite, message, and one or two actions from backend Ringo decisions. `RewardMoment.vue` no longer carries its own Ringo image; it is a focused reward dialog with XP, streak, achievements, and feature unlock hints.

Current asset consistency note: the sprite map resolves assets from `frontend/src/assets/ringo/` with fallback aliases. When adding or renaming moods, keep `RINGO_SPRITE_KEYS`, sprite filenames, and backend `sprite_key` values aligned.

## Design Rules For Future Work

- Reuse UI primitives before creating new one-off controls.
- Keep profile and dashboard hierarchy progression-first.
- Prefer meaningful reward feedback after check-ins and achievement unlocks.
- Use JoinSuccessMoment after starting a challenge when a softer transition prevents new users from being dropped directly into dense enrollment details.
- Use MissionCenter as the first dashboard surface. Keep legacy TodayMission available as a fallback only when the mission API errors or returns no actionable mission.
- During mission focus mode, keep the visible surface limited to Ringo guidance, the current mission/reminder/completion state, compact progress, and an explicit `Show mission status` detail reveal.
- Treat `Finish for today` as a successful ending. It should land on the calm Rest Mode screen rather than dumping the user into dense dashboard sections.
- Reveal the full dashboard only after focus mode is resolved or the user explicitly chooses `Show dashboard`; use subtle stagger/fade motion and honor reduced-motion preferences.
- Keep `/paths` as the richer path planning surface: path picker, active path status, challenge stage panels, mission previews, and daily path summary.
- Keep progressive disclosure subtle: reveal deeper sections after existing check-in stats make them meaningful, without blocking direct routes.
- Make public profile views shareable but privacy-safe.
- Avoid adding separate visual languages for each feature.
- Keep empty states hopeful and action-oriented.
- Keep animations subtle and purposeful.

## Implementation Gaps

- Tailwind is listed in dependencies and `assets/main.css` contains Tailwind directives, but that file is not imported by `main.js`.
- `frontend/src/style.css` is not currently imported by `main.js`, but it is kept as a safe dark root-shell stylesheet if it is imported later.
- API docs view may visually and contractually lag behind the actual backend.
- Full Mission Context UX is not complete yet. Current focus-mode polish improves attention and family-aware display, but future work is still needed for consistent path/challenge/mission context framing everywhere.
