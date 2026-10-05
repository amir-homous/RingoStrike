# Living Space Visual System Spec

Status: visual source of truth for Living Space v1 and Home Shell evolution.

Last updated: 2026-10-05.

## Visual North Star

Living Space should feel like:

```txt
a premium dark cinematic diorama that slowly becomes personal through consistency
```

The room is emotional infrastructure. It should make progress visible without turning self-growth into a noisy game.

## Direction

Primary:

- Dark Cinematic Diorama

Secondary influence:

- Stylized Night Progress, used with restraint

Use the secondary influence for warmth, softness, and progression magic. Do not let it become neon fantasy, casino reward energy, or cartoon clutter.

## Camera

Use:

```txt
elevated 3/4 soft-perspective
```

Do not use:

- strict isometric
- flat side-on dollhouse
- first-person room view
- full 3D navigation as the v1 default

The camera should make the five zones readable while preserving room atmosphere.

## Spatial Planning

The base room must reserve:

- empty wall areas for future identity/reward expression
- floor anchors for future objects
- tabletop/shelf anchors for smaller rewards
- ceiling or wall lighting anchors
- central circulation so the room does not become a storage grid
- three Ringo-safe positions

Ringo-safe positions should avoid:

- covering primary reward slots
- blocking the active path zone
- overlapping the active work surface
- sitting too close to screen edges on mobile crops

## Zone Label Policy

Path labels must not be permanently visible across the room.

Show zone names primarily on:

- hover
- keyboard focus
- tap/selection
- active state

Permanent labels make the room feel like a map/HUD instead of a living space.

## Stage 0

Stage 0 must be sparse, pleasant, and emotionally safe.

It should include the room's architectural identity, lighting, and subtle zone hints. It should not include future rewards as already-present decorative objects.

Stage 0 quality bar:

- attractive before rewards
- enough empty space for visible progression
- no shameful "empty room" feeling
- no placeholder-looking asset gaps
- clear five-zone layout without text dependency

## Reward Manifestation Behaviors

The canonical v1 matrix remains 25 reward definitions. Visual manifestation does not need 25 independent art objects.

Each reward should be planned with one behavior:

| Behavior | Visual Pattern | Example |
| --- | --- | --- |
| `ADD` | New object appears in reserved space. | Sketchbook appears on Creativity desk. |
| `REPLACE` | Existing object upgrades in place. | Basic lamp becomes warmer studio lamp. |
| `ENVIRONMENT` | Structural/environmental room change. | Wall texture gains subtle creative marks. |
| `ATMOSPHERE` | Light, particles, glow, soundless ambience. | Creativity zone gains warmer pool of light. |
| `IDENTITY` | Personalized expression layer. | A framed mark reflects user's path identity. |

Art anchors can be fewer than 25. Multiple reward definitions may share an anchor through replace, environment, atmosphere, or identity states.

## Locked Preview

Locked preview is built from the final asset.

Treatment:

- ghosted final object
- lower opacity
- desaturated or cooler tint
- lower material contrast
- subtle outline only if needed for readability
- no separate locked-object design language

Preview should answer:

```txt
"Something can become real here."
```

not:

```txt
"This is a store inventory slot."
```

## Reward Reveal

Reward reveal should be calm and premium.

Preferred sequence:

```txt
subtle focus lighting
ghost preview strengthens
material/texture resolves
object settles into room
Ringo acknowledges briefly
room persists in new state
```

Avoid:

- confetti
- loot chests
- large particle explosions
- screen-covering celebration
- repeated modal interruptions
- reward effects that hide the room

## Lighting System

Lighting is a progression layer.

Lighting can express:

- active selected zone
- today's mission focus
- completed/today-safe state
- newly materialized reward
- Rest Mode
- long-term progression maturity

Lighting must remain readable on mobile crops and must not become the only indicator of state.

## Path Personalities

Career:

- precise pools of light
- clean desk/work artifacts
- structured verticals
- quiet competence

Creativity:

- warm localized light
- sketch, paper, lamp, texture
- softer asymmetry
- generative but not messy

Fitness:

- grounded floor presence
- kinetic objects
- slightly stronger contrast
- energy without aggression

Learning:

- shelves, notes, calm accumulation
- layered but organized detail
- cooler focus light
- curiosity and depth

Sleep:

- softest contrast
- moon/rest lighting
- protective quiet
- no productivity pressure

## Creativity Vertical Slice

Reference sequence:

1. Stage 0 base includes a believable creative zone anchor but no reward object.
2. Sketchbook appears as ghost preview after relevant progress context.
3. Unlock materializes the sketchbook calmly in-room.
4. Sketchbook remains placed persistently.
5. Next reward preview appears as a Lamp ghost, sharing the zone's visual language.

This slice is the first QA target for art direction and UI integration.
