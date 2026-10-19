# Living Space Visual v1 — Spec and Asset Contract (B17)

Status: draft for Amir's approval, 2026-10-19.
Decisions: D7 (visual room in this milestone), **D8 = pixel art** (approved 2026-10-19), D9 (15 v1 art elements, assumed approved unless changed), D10 (RTL never mirrors the room).
Reference: canvas row "Room art style test", pixel version.

> **Addendum (2026-10-19, after B18):** [LIVING_SPACE_VISUAL_V1_ADDENDUM.md](LIVING_SPACE_VISUAL_V1_ADDENDUM.md) overrides parts of this spec: perspective model, sleep-corner nightstand position, PNG lights/dim and vignette, final asset contract and layer order. `frontend/src/assets/room/room_layout.json` is the source of truth for positions. Where they disagree, the addendum wins.

## 1. Format

- One room scene with a **base resolution of 480×270 px** (16:9).
- The scene is displayed **only at integer scales**, using `image-rendering: pixelated`. It is never scaled by a fraction.
- Each layer is a transparent PNG drawn at base resolution, positioned by base-pixel coordinates.
- Palette: one shared night palette of 32–48 colors. Accents use the UI tokens: cyan `#6ee5ff` and gold `#f7d774`.
- UI (panel, labels, buttons) stays smooth HTML. Only the room is pixel art.

## 2. Camera and composition

- Camera: 3/4 view with a soft top-down angle. The back wall is visible at the top (y 0–118). The floor is seen from above, slightly angled (y 118–270). Objects show their front face and their top face.
- Five zones, each with a fixed footprint. Coordinates are in base px and are refined in B18.

| Zone | Area (x, y) | Base prop (Stage 0) | First reward (placed) | Second reward (ghost) | Light personality |
| --- | --- | --- | --- | --- | --- |
| Work Desk (`career`) | 16–150, 52–175 | desk + laptop + chair | Planner | Desk Lamp | cool white |
| Learning Corner (`learning`) | 150–245, 40–165 | low bookshelf + stool | First Book | Study Lamp | cool blue |
| Creative Corner (`creativity`) | 245–350, 48–170 | easel + small table | Sketchbook | Lamp | warm amber |
| Sleep Corner (`sleep`) | 350–476, 70–235 | bed + nightstand | Pillow | Bedside Lamp | moon violet |
| Fitness Corner (`fitness`) | 24–200, 182–262 | floor mat | Water Bottle | Dumbbells | soft green |

- A shared window with a moon sits on the back wall, between Learning and Creative. The moon's light is the room's base light.
- **Central circulation:** a rug at about x 205–345, y 180–250 stays free of zone objects.
- **Three Ringo-safe positions:**
  - A: center rug, about (270, 214), used for overview and rest
  - B: front-right floor, about (372, 246)
  - C: front-left, near Fitness, about (150, 240)
  - Ringo never covers a reward slot.
- **Reserved empty anchors** for later rewards: wall art above the Creative table, a shelf above Work Desk, floor space beside the bed. They stay empty in v1.

## 3. Layer stack (back to front)

1. `room_stage0.png`: walls, floor, window, rug, base lighting (480×270)
2. Zone base props: `prop_{zone_key}.png`
3. Placed reward objects: `{asset_key}.png`, shown when unlocked
4. Ghost previews: the same `{asset_key}.png` file, rendered with the ghost treatment (section 5)
5. Ringo sprite: `ringo_{state}.png`
6. Light overlays: zone pool and selection glow (CSS gradients on top, `mix-blend-mode: screen`)
7. Markers: reminder bell and new-object glint (small pixel icons)
8. HTML layer: zone hit regions (buttons) and labels

## 4. Zone states

| State | Visual |
| --- | --- |
| Idle | normal |
| Hover / keyboard focus | 1px light outline glow around the footprint, plus the zone label (HTML) |
| Selected | the zone's light pool brightens; the other zones dim to about 70% |
| Scheduled reminder (not due) | small calm bell marker at the zone's marker anchor |
| Due reminder | bell marker in cyan and slightly brighter; no blinking |
| Newly placed object | materialize sequence (section 6), then a glint for a few seconds |
| Rest (room level) | room dims a little, the window moon brightens, Ringo switches to the sleeping sprite at safe position A |

## 5. Ghost preview treatment

- A ghost uses the final asset, never a separate drawing.
- CSS: `opacity: .38; filter: grayscale(1) brightness(1.5) sepia(.2) hue-rotate(180deg)`, giving a cool, faint look.
- A static checker dither mask (CSS mask image, 2×2 px) gives the pixel-art "not yet real" feel.

## 6. Materialize sequence (B21)

Total about 1.6 s, played once per newly unlocked reward, after the reward sequence closes:

1. The zone light pool rises (300 ms).
2. The ghost dither mask fades out while opacity rises (600 ms).
3. The object appears at full color with a 1px "settle" drop (200 ms).
4. A glint pixel sparkle shows (500 ms), then the persistent state remains.

With `prefers-reduced-motion`, the final state shows immediately. Backfilled rewards never play this sequence.

## 7. Responsive rules

| Viewport | Overview | Zone selected |
| --- | --- | --- |
| Desktop room area ≥ 960 px | scale ×2 (960×540); ×3 when ≥ 1440 px is available | same scale; zone light; panel beside the room |
| Mobile (≤ 600 px) | scale ×1; the room is 480 px wide, so it is cropped to the viewport with horizontal pan centered on Ringo | camera zooms to ×2 on the zone footprint (crop about 195×135 base px, which is 390×270 on screen); bottom sheet with the v2 panel |

- Scale is always `Math.max(1, Math.floor(availableWidth / 480))`.
- The camera transition between overview and zone uses `transform` and lasts 300 ms. Reduced motion jumps instantly.
- **RTL:** the room is never mirrored. Only HTML UI follows the direction.

## 8. Hit regions and accessibility

- Each zone is a `<button>` positioned over its footprint, with `clip-path: polygon(...)` in base px times the scale.
- Each button has an `aria-label` with the zone name, its state (for example "one object placed, reminder scheduled") and `aria-pressed` when selected.
- Tab order: Work Desk, Learning, Creative, Sleep, Fitness. Focus is always visible.
- The room `<div>` has `role="group"` and an accessible name. The scene image has empty `alt`, because the zone buttons carry the meaning.

## 9. Asset contract

```
frontend/src/assets/room/
  room_stage0.png                 480×270
  props/prop_{zone_key}.png       trimmed, transparent
  objects/{asset_key}.png         trimmed, transparent (asset_key from reward_definitions)
  ringo/ringo_idle.png, ringo_sleeping.png
  markers/bell.png, glint.png
  room_layout.json
```

`room_layout.json` contains, for each zone:
- `footprint` polygon
- `prop` anchor (x, y)
- `slots` keyed by `slot_key`, each with an anchor (x, y)
- `light` color and pool ellipse
- `marker` anchor
- `camera` crop rectangle for mobile zoom

It also contains the three Ringo-safe positions.

- Rendering code reads only `room_layout.json` and the PNGs. Replacing any PNG with a hand-made version needs no code change, as long as it keeps the same size and anchor.
- A reward with no PNG yet is simply not drawn in the room. It still appears in the panel's object list.

## 10. v1 art scope (D9)

- 1 stage-0 room
- 5 base props
- 5 first-reward objects
- 5 second-reward objects (shown as ghosts)
- Ringo idle and sleeping sprites (placeholder)
- bell and glint markers

The final pixel Ringo is a separate future issue (B25). Amir retouches it.

## 11. Out of scope for v1

- art for the other 15 rewards
- Stage system
- day/night by real time
- room customization
- ambient sound (#336)
