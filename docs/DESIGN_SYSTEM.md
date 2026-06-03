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
- dark body background from `--bg`
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
- feedback: reward feedback
- profile: hero card, stats grid, settings card/modal, avatar, consistency heatmap
- progress: hero progress, next goal, recent feed, stats grid, XP bar

## Frontend Pages

Current views:

- `Dashboard.vue`
- `Challenges.vue`
- `Enrollment.vue`
- `Leaderboard.vue`
- `Profile.vue`
- `PublicProfile.vue`
- `Login.vue`
- `AuthCallback.vue`
- `ApiDocsView.vue`

## Design Rules For Future Work

- Reuse UI primitives before creating new one-off controls.
- Keep profile and dashboard hierarchy progression-first.
- Prefer meaningful reward feedback after check-ins and achievement unlocks.
- Make public profile views shareable but privacy-safe.
- Avoid adding separate visual languages for each feature.
- Keep empty states hopeful and action-oriented.
- Keep animations subtle and purposeful.

## Implementation Gaps

- Tailwind is listed in dependencies and `assets/main.css` contains Tailwind directives, but that file is not imported by `main.js`.
- `frontend/src/style.css` is Vite starter styling and appears unused.
- API docs view may visually and contractually lag behind the actual backend.
