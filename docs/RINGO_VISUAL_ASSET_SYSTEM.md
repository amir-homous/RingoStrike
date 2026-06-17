# RingoStrike Visual Asset System

**Version:** 1.0  
**Status:** Draft for production use  
**Owner:** RingoStrike Product / Design  
**Primary Use:** Character consistency, UI asset production, Ringo helper sprites, reward visuals, onboarding graphics, product branding  
**Recommended Location:** `docs/RINGO_VISUAL_ASSET_SYSTEM.md`

---

## 1. Purpose

This document defines the visual asset system for **RingoStrike**, with a primary focus on **Ringo**, the gray British Shorthair cat companion at the center of the product experience.

The goal is to create a stable, reusable, and professional guide that can be used for:

- generating consistent Ringo character sprites;
- designing UI illustrations and empty states;
- improving the emotional quality of the web app;
- supporting onboarding, mission guidance, rewards, reminders, and achievements;
- keeping all visual assets aligned with the product identity;
- preventing random, inconsistent, or visually disconnected character generations.

RingoStrike should feel like a premium progression companion, not a generic habit tracker or noisy gamified dashboard.

---

## 2. Product Context

RingoStrike is a premium self-improvement and progression platform focused on:

- consistency;
- daily missions;
- XP and leveling;
- streaks;
- achievements;
- identity-based progress;
- emotional support;
- social momentum;
- long-term motivation.

The product direction is:

> A premium progression ecosystem.

Ringo is not only a mascot.  
Ringo is the emotional interface of the product.

Core product rule:

```txt
First Ringo. Then system.
```

This means the user should first feel guided, supported, and emotionally seen by Ringo.  
Only after that should the system expose missions, XP, streaks, achievements, profiles, or leaderboards.

---

## 3. Visual Direction

RingoStrike should feel:

- premium;
- cinematic;
- calm;
- emotionally intelligent;
- motivational;
- elegant;
- minimal but rewarding;
- international-quality;
- future-safe.

RingoStrike should not feel:

- noisy;
- chaotic;
- childish;
- casino-like;
- overly gamified;
- generic productivity software;
- emotionally cold;
- visually inconsistent.

The visual language should support the following emotions:

```txt
care
momentum
trust
progress
identity
encouragement
small wins
emotional safety
```

---

## 4. Ringo Character Identity

### 4.1 Character Summary

Ringo is a cute but premium gray British Shorthair cat companion.

He should feel like:

- a friend;
- a gentle coach;
- a caring companion;
- a soft motivator;
- a guide through daily progress.

He should not feel like:

- a strict boss;
- a childish toy;
- a meme character;
- a threatening gamification mascot;
- a random cartoon animal.

### 4.2 Fixed Character Traits

These traits must stay consistent across all Ringo assets.

| Attribute | Rule |
| --- | --- |
| Species | Gray British Shorthair cat |
| Body | Short, round, fluffy, soft |
| Face | Round, friendly, expressive |
| Fur | Silver-gray / soft gray |
| Eyes | Large golden amber eyes |
| Clothing | Premium black / charcoal hoodie |
| Main Symbol | Large shiny gold medal with the letter `R` |
| Mood Baseline | Warm, friendly, caring, emotionally safe |
| Style | Premium cartoon mascot / polished app character |
| Output | Transparent PNG for UI use |

### 4.3 Locked Visual Elements

The following elements must not change between sprites:

```txt
- gray British Shorthair identity
- round face shape
- golden amber eyes
- black charcoal hoodie
- large gold R medal
- short fluffy body proportions
- soft premium cartoon rendering style
- friendly emotional tone
```

### 4.4 Flexible Visual Elements

The following elements may change per mood:

```txt
- facial expression
- mouth shape
- eyebrow position
- paw gesture
- head tilt
- body posture
- small mood-specific props
- subtle particles
- small lighting accents
```

Props must never hide or replace the gold `R` medal.

---

## 5. Core Character Design Rules

### Rule 1 — Same Character, Different Mood

Every Ringo image must look like the same character in a different emotional state.

Bad:

```txt
A new cat design for each mood.
```

Good:

```txt
The same Ringo character with changed expression, gesture, and mood.
```

### Rule 2 — Ringo Must Guide, Not Decorate

Ringo should appear when he has a purpose:

- explaining;
- encouraging;
- warning gently;
- celebrating;
- guiding the next step;
- helping users recover momentum.

Avoid placing Ringo randomly as a decorative element without contextual meaning.

### Rule 3 — Emotion Before System

Ringo should communicate emotional meaning before showing system data.

Preferred pattern:

```txt
Ringo message
→ one clear action
→ progress/reward details
```

### Rule 4 — Premium, Not Noisy

Reward and celebration assets should feel satisfying but restrained.

Avoid:

- excessive confetti;
- loud gaming effects;
- casino-like sparkles;
- aggressive urgency;
- shame-based streak visuals.

Use:

- soft glow;
- subtle golden particles;
- clean motion;
- warm expressions;
- meaningful reward pacing.

### Rule 5 — Clear at Small Sizes

Ringo must remain readable at:

- 256px;
- 128px;
- compact mobile UI;
- dashboard cards;
- modal reward screens.

The face, eyes, hoodie, and medal must remain visually clear.

---

## 6. Ringo Mood Sprite System

### 6.1 Intended Sprite Keys

The core Ringo sprite system should include:

```txt
idle
welcome
talking
explaining
thinking
encouraging
warning
concerned
happy
celebration
achievement
proud
sad
sleeping
focus
victory
```

### 6.2 Sprite Usage Table

| Sprite Key | Emotional Meaning | Primary UI Usage | Visual Direction |
| --- | --- | --- | --- |
| `idle` | calm, available | default dashboard / neutral state | relaxed posture, soft smile |
| `welcome` | warm greeting | onboarding, first visit, join success | open paws, big friendly smile |
| `talking` | active conversation | RingoCoach normal message | one paw raised, speaking expression |
| `explaining` | guidance | empty states, feature explanation | pointing gently, helpful face |
| `thinking` | decision-making | Ringo choosing next action | paw near chin, curious eyes |
| `encouraging` | motivation | before starting mission | small confident gesture |
| `warning` | attention | reminder, streak risk | warning prop, still friendly |
| `concerned` | caring concern | inactivity, missed day | soft worried eyes, no shame |
| `happy` | light joy | positive progress | cheerful but calm |
| `celebration` | reward | reward moment, today saved | raised paws, subtle confetti |
| `achievement` | unlocked success | achievement modal / badge unlock | badge or medal support |
| `proud` | emotional recognition | after mission/check-in | paw on heart, proud smile |
| `sad` | soft disappointment | missed day / recovery UX | gentle sadness, no guilt |
| `sleeping` | rest | today complete / rest mode | sleepy, peaceful |
| `focus` | mission readiness | Today's Mission | determined but friendly |
| `victory` | milestone | level up, major achievement | heroic but restrained pose |

---

## 7. Asset Naming Convention

### 7.1 Recommended Folder

```txt
frontend/src/assets/ringo/
```

### 7.2 Recommended File Names

Use simple sprite-key names to stay aligned with frontend sprite maps:

```txt
idle.png
welcome.png
talking.png
explaining.png
thinking.png
encouraging.png
warning.png
concerned.png
happy.png
celebration.png
achievement.png
proud.png
sad.png
sleeping.png
focus.png
victory.png
```

### 7.3 Optional Optimized Files

For performance, optimized web assets may use:

```txt
idle.webp
welcome.webp
talking.webp
...
```

Recommended structure:

```txt
frontend/src/assets/ringo/
  source/
    idle.png
    welcome.png
  web/
    idle.webp
    welcome.webp
```

For the current frontend, keep the active map simple unless the build process is updated.

---

## 8. Technical Asset Specifications

| Asset Type | Source Format | Production Format | Recommended Size | Background |
| --- | --- | --- | --- | --- |
| Ringo sprite | PNG | PNG or WebP | 1024×1024 source, 512×512 UI | transparent |
| Small UI sprite | WebP | WebP | 256×256 | transparent |
| Reward icon | SVG / PNG | SVG / WebP | scalable / 512px | transparent |
| Badge | SVG / PNG | SVG / WebP | 512px | transparent |
| Social share graphic | PNG | PNG / JPG | 1200×630 | designed background |
| LinkedIn cover | PNG | PNG / JPG | 1584×396 or 16:9 variant | designed background |
| Product hero | PNG | PNG / WebP | 1920×1080 or 1600×900 | designed background |

### 8.1 Sprite Padding

Each sprite should include enough transparent padding so it does not feel cropped.

Recommended:

```txt
8% to 12% padding around the character
```

Avoid:

- cropped ears;
- cropped tail;
- cropped paws;
- cropped hoodie;
- cropped medal.

### 8.2 Shadow Rules

For UI sprites:

- avoid strong baked shadows;
- use subtle internal shading only;
- let the frontend card/modal decide external shadow;
- keep transparent PNG clean and reusable.

---

## 9. Master Prompt for Ringo Sprite Generation

Use this as the base prompt for all Ringo sprite generation.

Replace `[MOOD DESCRIPTION]` with the specific mood prompt.

```txt
Create a premium transparent PNG mascot illustration for a self-improvement app called RingoStrike.

Character:
A cute gray British Shorthair cat mascot named Ringo, short and fluffy body, round face, soft silver-gray fur, big golden amber eyes, small cute nose, friendly expression, wearing a premium black charcoal hoodie, with a large shiny gold medal necklace on the chest featuring a bold letter "R".

Style:
High-quality polished mascot illustration, soft cinematic lighting, premium mobile app character design, semi-3D cartoon illustration, clean edges, expressive but elegant, warm and emotionally intelligent, not childish, not noisy, not chaotic.

Pose and emotion:
[MOOD DESCRIPTION]

Composition:
Full body character, centered, transparent background, enough padding around the character, suitable for UI usage in a web app, consistent proportions with the same character design, the gold R medal must be clearly visible.

Quality:
Detailed soft fur, clean hoodie folds, subtle highlights on the gold medal, expressive eyes, professional game/app mascot quality, calm premium aesthetic.

Output:
Transparent background PNG, no frame, no text, no extra UI, no watermark.
```

---

## 10. Reference Consistency Prompt

When using existing Ringo images as reference, add this instruction:

```txt
Use the provided reference images as the exact character identity reference.
Keep the same gray British Shorthair cat, same face shape, same golden amber eyes, same black hoodie, same large gold R medal, same soft premium mascot style, and same proportions.
Only change the facial expression, pose, and small mood-related prop.
```

This instruction is critical for avoiding character drift.

---

## 11. Negative Prompt

Use this negative prompt for all generated Ringo assets.

```txt
Do not change the character identity.
Do not make the cat a different breed.
Do not remove the black hoodie.
Do not remove or redesign the gold R medal.
Do not make the character realistic like a photo.
Do not make it horror, angry, aggressive, creepy, or sarcastic.
Do not make it overly childish or baby-like.
Do not add a background scene.
Do not add text.
Do not add a frame.
Do not add random logos.
Do not use chaotic gaming effects.
Do not use casino-style reward visuals.
Do not make the pose too dynamic or distorted.
Do not crop the ears, paws, tail, hoodie, or medal.
Do not cover the R medal with props.
```

---

## 12. Mood Prompt Library

### 12.1 `idle.png`

```txt
Ringo is standing calmly in a relaxed neutral pose, with a soft friendly smile and warm golden eyes. His paws are relaxed, his hoodie and gold R medal are clearly visible. The mood should feel available, calm, and ready to help.
```

### 12.2 `welcome.png`

```txt
Ringo is happily welcoming the user with open paws and a big warm smile. His eyes are bright and friendly. The mood should feel inviting, safe, and emotionally warm, as if he is saying "welcome, I'm here with you."
```

### 12.3 `talking.png`

```txt
Ringo is happily talking to the user, with one paw slightly raised as if explaining something in a friendly way. His mouth is open in a soft speaking smile, eyes warm and attentive. The mood should feel conversational, helpful, and caring.
```

### 12.4 `explaining.png`

```txt
Ringo is gently explaining something, pointing softly to the side with one paw while keeping a friendly and patient expression. The mood should feel clear, helpful, and reassuring.
```

### 12.5 `thinking.png`

```txt
Ringo is thinking carefully, one paw gently touching his chin, head slightly tilted, eyes looking upward with a curious and smart expression. The mood should feel thoughtful, analytical, and kind, as if Ringo is choosing the best next step for the user.
```

### 12.6 `encouraging.png`

```txt
Ringo is encouraging the user with a confident but gentle gesture, such as a small thumbs-up or raised paw. His expression is warm and motivating. The mood should feel supportive, optimistic, and low-pressure.
```

### 12.7 `warning.png`

```txt
Ringo is holding a small yellow warning sign while keeping a caring and friendly expression. He should look protective, not angry or scary. The mood should feel like a gentle attention signal, not a threat.
```

### 12.8 `concerned.png`

```txt
Ringo looks gently concerned, with slightly raised eyebrows and soft caring eyes. One paw is lifted as if saying "hey, I'm here with you." The mood should feel protective and supportive, not scary, not disappointed, and not guilt-inducing.
```

### 12.9 `happy.png`

```txt
Ringo is smiling happily with relaxed paws and bright eyes. The mood should feel positive, simple, and emotionally warm, suitable for showing that the user is making progress.
```

### 12.10 `celebration.png`

```txt
Ringo is celebrating with both paws raised, smiling widely, with a few elegant golden sparkles and small confetti pieces around him. The celebration should feel premium and joyful but restrained, not chaotic or noisy.
```

### 12.11 `achievement.png`

```txt
Ringo is proudly presenting a small achievement badge or medal while smiling warmly. The main gold R medal on his chest must remain visible. The mood should feel like meaningful recognition and progress.
```

### 12.12 `proud.png`

```txt
Ringo looks proud of the user, smiling warmly with his chest slightly forward and one paw over his heart. His expression says "I saw your effort, and it matters." The mood should feel emotionally rewarding, supportive, and sincere.
```

### 12.13 `sad.png`

```txt
Ringo looks softly sad but still caring, with gentle eyes and slightly lowered ears. The mood should communicate empathy, not disappointment or guilt. He should feel like he is ready to help the user restart.
```

### 12.14 `sleeping.png`

```txt
Ringo is peacefully sleeping or resting, with closed eyes and a calm expression. The hoodie and gold R medal remain visible. The mood should feel safe, complete, and restful, as if the user has done enough for today.
```

### 12.15 `focus.png`

```txt
Ringo looks focused and ready for action, standing confidently with a determined but friendly expression. His eyes are sharp but warm, and his posture suggests "let's do one clear mission now." The mood should feel motivating, calm, and focused, not aggressive.
```

### 12.16 `victory.png`

```txt
Ringo stands in a small heroic victory pose, smiling confidently, with one paw raised and subtle golden light around the R medal. The mood should feel like a meaningful milestone achievement, premium and cinematic, not loud or chaotic.
```

---

## 13. UI Integration Map

### 13.1 Dashboard

| User State | Recommended Sprite |
| --- | --- |
| Default dashboard | `idle` |
| Mission ready | `focus` |
| Mission in progress | `encouraging` |
| Mission completed | `proud` |
| Today complete | `sleeping` or `happy` |
| Returning after break | `concerned` |

### 13.2 Onboarding

| Moment | Recommended Sprite |
| --- | --- |
| First welcome | `welcome` |
| Product explanation | `explaining` |
| Path selection | `thinking` |
| First challenge joined | `celebration` |
| Ready for first mission | `focus` |

### 13.3 Mission Center / RingoCoach

| Ringo State | Recommended Sprite |
| --- | --- |
| `new_user_no_path` | `welcome` |
| `path_selected_no_challenge` | `explaining` |
| `today_not_started` | `focus` |
| `today_in_progress` | `encouraging` |
| `today_completed` | `proud` |
| `today_reminded` | `talking` |
| `today_skipped` | `concerned` |
| `streak_at_risk` | `warning` |
| `returning_after_break` | `concerned` |
| `no_mission_today` | `sleeping` |

### 13.4 Reward Moment

| Reward Step | Recommended Sprite |
| --- | --- |
| Ringo message | `proud` |
| Mission completed | `happy` |
| XP earned | `celebration` |
| Achievement unlocked | `achievement` |
| Level up | `victory` |
| Today saved | `sleeping` or `celebration` |

### 13.5 Empty States

| Empty State | Recommended Sprite |
| --- | --- |
| No path selected | `explaining` |
| No activity yet | `idle` |
| No achievements yet | `encouraging` |
| No missions today | `sleeping` |
| Private public profile | `concerned` |
| Telegram not connected | `talking` |
| Challenge list empty | `thinking` |

### 13.6 Telegram / Reminder System

| Notification Type | Recommended Sprite |
| --- | --- |
| Daily reminder | `encouraging` |
| Mission reminder | `talking` |
| Streak risk | `warning` |
| Missed day recovery | `concerned` |
| Weekly summary | `happy` |
| Achievement message | `achievement` |

---

## 14. Visual Asset Categories Beyond Ringo

Ringo is the visual heart of the product, but the full product needs a complete asset system.

### 14.1 Core UI Icon System

Needed icons:

- path;
- challenge;
- mission;
- XP;
- streak;
- achievement;
- profile;
- leaderboard;
- reminder;
- public identity;
- recovery;
- focus;
- rest.

Style:

```txt
minimal premium glyphs
soft rounded geometry
gold / cyan accent compatibility
dark UI readability
no noisy game-style icons
```

### 14.2 Reward Assets

Needed reward assets:

- XP chip;
- streak saved badge;
- today saved badge;
- level-up mark;
- achievement unlock badge;
- soft golden particles;
- subtle progress glow;
- milestone crest.

### 14.3 Empty State Illustrations

Needed empty state assets:

- no path selected;
- no mission available;
- no achievement unlocked;
- no activity timeline;
- no public profile;
- Telegram not connected;
- challenge unavailable.

Empty states should usually use Ringo sprites instead of unrelated illustrations.

### 14.4 Background Atmosphere Assets

Useful background assets:

- soft radial glow;
- dark premium gradient;
- subtle noise texture;
- glass highlight overlay;
- golden spark particles;
- path-line background;
- profile hero glow;
- reward spotlight.

These assets must remain restrained and not compete with content.

### 14.5 Brand / Marketing Assets

Needed brand assets:

- app icon;
- favicon;
- RingoStrike logo lockup;
- R medal mark;
- LinkedIn company cover;
- project cover;
- launch post cover;
- OpenGraph preview;
- profile share card;
- achievement share card;
- Telegram bot avatar;
- PWA icon set.

---

## 15. Asset Production Workflow

### Step 1 — Define Need

Before generating an asset, define:

```txt
What user state does this support?
Where will it appear in the UI?
What action should the user take after seeing it?
What emotion should it create?
```

### Step 2 — Select Asset Type

Choose one:

```txt
Ringo sprite
UI icon
reward badge
empty state
background atmosphere
social/brand asset
```

### Step 3 — Use the Correct Prompt

For Ringo:

```txt
Master prompt
+ reference consistency prompt
+ mood prompt
+ negative prompt
```

For UI icons:

```txt
Use the RingoStrike icon system rules.
Keep shapes minimal, premium, and dark-UI compatible.
```

### Step 4 — Review Consistency

Check:

```txt
Does it match Ringo?
Does it match the product tone?
Does it work in dark UI?
Does it avoid noise?
Does it support one clear action?
```

### Step 5 — Export

Recommended exports:

```txt
source PNG 1024×1024
optimized WebP 512×512
optional small WebP 256×256
```

### Step 6 — Integrate

Add to:

```txt
frontend/src/assets/ringo/
frontend/src/constants/ringoSprites.js
```

Then verify:

```txt
npm run build
```

---

## 16. Quality Checklist

Every Ringo asset must pass this checklist:

```txt
[ ] Same Ringo character identity
[ ] Gray British Shorthair appearance preserved
[ ] Black hoodie preserved
[ ] Gold R medal visible
[ ] Transparent background
[ ] No frame
[ ] No text
[ ] No watermark
[ ] Clear mood
[ ] Emotionally supportive
[ ] Not guilt-based
[ ] Not chaotic
[ ] Not childish
[ ] Works on dark UI
[ ] Readable at small size
[ ] Enough padding
[ ] Suitable for production UI
```

Every non-character UI asset must pass this checklist:

```txt
[ ] Premium dark UI compatible
[ ] Consistent with RingoStrike palette
[ ] Minimal and readable
[ ] Not visually noisy
[ ] Supports progression identity
[ ] Reusable across components
[ ] Exported in appropriate format
```

---

## 17. Governance Rules

### 17.1 Do Not Add Random Assets

Every asset must belong to one of the defined categories:

```txt
Ringo sprite
UI icon
reward badge
empty state
background atmosphere
brand/social asset
```

### 17.2 Do Not Create a New Visual Language Per Feature

Paths, missions, rewards, profiles, reminders, and achievements should all feel like part of the same product.

### 17.3 Do Not Replace Ringo's Core Identity

Ringo can evolve, but his core identity should not drift.

Do not change:

- species;
- fur color;
- hoodie;
- R medal;
- personality;
- visual style.

### 17.4 Keep Assets Future-Safe

Assets should work for:

- web app;
- mobile/PWA;
- Telegram bot;
- social share cards;
- public profiles;
- future app store visuals;
- portfolio presentation.

---

## 18. Recommended Production Priorities

### Batch 1 — MVP Critical Ringo Sprites

```txt
talking.png
thinking.png
focus.png
proud.png
celebration.png
concerned.png
victory.png
```

Purpose:

- complete RingoCoach;
- improve MissionCenter;
- support reward moments;
- fix missing or weak frontend sprite states;
- prepare launch-quality guided UX.

### Batch 2 — Full Emotional Range

```txt
explaining.png
encouraging.png
happy.png
achievement.png
sad.png
sleeping.png
```

Purpose:

- empty states;
- onboarding;
- recovery UX;
- achievement UX;
- rest/today-complete states.

### Batch 3 — Product Expansion Assets

```txt
low_energy.png
rest_mode.png
telegram_reminder.png
path_start.png
level_up.png
weekly_summary.png
profile_share.png
```

Purpose:

- future Ringo Brain states;
- Telegram reminders;
- social sharing;
- public identity;
- advanced progression feedback.

### Batch 4 — UI System Assets

```txt
path icons
mission icons
achievement badges
XP chips
streak badges
profile share card
OpenGraph card
LinkedIn cover
Telegram bot avatar
PWA icons
```

---

## 19. Frontend Integration Notes

### 19.1 Sprite Map

Ringo sprites should be resolved through a central sprite map.

Example:

```js
export const ringoSprites = {
  idle: idleSprite,
  welcome: welcomeSprite,
  talking: talkingSprite,
  explaining: explainingSprite,
  thinking: thinkingSprite,
  encouraging: encouragingSprite,
  warning: warningSprite,
  concerned: concernedSprite,
  happy: happySprite,
  celebration: celebrationSprite,
  achievement: achievementSprite,
  proud: proudSprite,
  sad: sadSprite,
  sleeping: sleepingSprite,
  focus: focusSprite,
  victory: victorySprite,
};
```

### 19.2 Fallback Rule

If a sprite key is missing, the UI should fall back to:

```txt
idle
```

or, for reward states:

```txt
proud
```

### 19.3 Accessibility

Each sprite should have meaningful alt text when used as an image.

Examples:

```txt
Ringo smiling and welcoming you
Ringo focused on today's mission
Ringo proudly celebrating your progress
Ringo gently reminding you
```

Avoid meaningless alt text such as:

```txt
cat image
mascot
png
```

---

## 20. Final Creative Direction

Ringo should always feel like:

```txt
a caring little companion
who noticed your effort
and gently helps you take the next small step
```

The visual system should make users feel:

```txt
seen
safe
motivated
proud
guided
ready to continue
```

The final goal is not only to make RingoStrike beautiful.

The goal is to make progress feel emotionally alive.

---

## 21. Working Motto

```txt
Small step.
Soft reward.
Visible progress.
Ringo by your side.
```
