# Living Space Visual v1 — Addendum after B18 (2026-10-19)

Status: approved by Amir on 2026-10-19 after review on the design canvas, B18 row. This addendum updates `docs/product/LIVING_SPACE_VISUAL_V1_SPEC.md`. Where the two disagree, this addendum wins.

## 1. Perspective model (new, binding for all room art)

- The floor uses one vanishing point at **VP = (240, -60)**, in base px. The wall/floor seam is at **y = 118**.
- Projection from world to screen:
  - `k = (yf + 60) / 178`
  - `x = 240 + (xb - 240) * k`
  - `y = yf - h * k`
  - `xb` is the x position along the back wall, `yf` is the floor depth row, and `h` is the height above the floor.
- Furniture is drawn as projected boxes:
  - Objects left of x 240 show their **right** side face.
  - Objects right of x 240 show their **left** side face.
  - Front faces stay horizontal.
- The side walls meet the back wall at x 22 and x 458.
- The window shape is cast onto the floor as moonlight.
- Any future hand-made or replacement art must use this same projection, so it sits in the room correctly.

## 2. Composition changes against the original spec

- **Sleep corner:**
  - The bed is a projected box (head against the wall, foot toward the viewer).
  - The **nightstand moved to the right of the bed**. On the left, the bed would leave the frame.
  - The Bedside Lamp slot sits on the nightstand.
- **Fitness corner:** the mat follows the floor perspective and has a rolled end at the back.
- **Zone footprints, pools, markers and cameras:** updated. The source of truth is `room_layout.json`, not the table in the spec.

## 3. Lights and dimming are PNG layers, not CSS gradients

- `lights/light_{zone}.png` is the stepped pixel light pool for the selected state.
  - It is opaque RGB on black.
  - Draw it with `mix-blend-mode: screen` at its `x`, `y`.
- `lights/dim_{zone}.png` is a full-size black layer with stepped alpha.
  - Draw it over the scene, under the light, when that zone is selected.
  - It keeps the selected zone bright and dims the rest of the room.
- `vignette.png` is a full-size black alpha overlay. It is always on top of the scene layers and under the HTML layer.
- Rest state: dim the whole scene with a black overlay at opacity 0.26, show `ringo_sleeping` at position A, and show no zone light.
- `room_stage0.png` already includes the static ambient light (moon cast, window halo, faint zone pockets).

## 4. Asset contract (final for v1)

```
frontend/src/assets/room/
  room_stage0.png            480×270
  vignette.png               480×270
  room_layout.json
  props/prop_{zone_key}.png  trimmed, placed at layout zones[z].prop.{x,y}
  objects/{asset_key}.png    trimmed, placed at layout zones[z].slots[slot_key].{x,y}
  lights/light_{zone_key}.png, lights/dim_{zone_key}.png
  ringo/ringo_idle.png, ringo_sleeping.png   anchor: bottom-center at the ringo_positions point
  markers/bell.png, bell_due.png, glint.png  anchor: center at zones[z].marker
```

- Slot keys match the `reward_definitions.slot_key` values in the backend seed.
- Asset keys match `reward_definitions.asset_key`.
- The 10 v1 objects are the first reward and the consistency reward of each zone.
- A reward with no PNG is not drawn in the room. It still appears in the panel.

## 5. Layer order (back to front)

1. stage
2. props (zone order: work_desk, learning_corner, creative_corner, sleep_corner, fitness_corner)
3. placed objects
4. ghost objects (same PNG, ghost CSS from the layout)
5. Ringo
6. dim (selected zone) or rest overlay
7. light (selected zone, screen blend)
8. markers and glint
9. vignette
10. HTML hit regions and labels

## 6. Verified

The room was re-assembled from these files and `room_layout.json` alone, and it matches the B18 mock-ups.

## 7. Room scale: hybrid rule (decided in B19 review round 6)

- `fit = min(availableWidth / 480, availableHeight / safeAreaHeight)` (242 base px since B22, see §8; 270 before).
- If `fit - floor(fit) >= 0.85`, the room uses `fit`, kept to 1/100 and rounded down, with `image-rendering: pixelated`. Otherwise it uses `floor(fit)`. The scale is never below 1.
- From 600 px wide the minimum stays ×2: a room wider than its column is cropped with the camera pan. Phones keep ×1, scrolling inside the room frame.
- Every layer uses the same effective scale: the pixel layers (one `scale()` on the base layer), the hit regions, the labels, the focus polygon, the dim and light layers, and the camera pan (snapped to whole base pixels of that scale). `npm run test:room-alignment` checks this at 1920×940 (fractional), 1920×1080, 1440×900 and 1366×768.

## 8. Safe area and the phone camera (B22)

**Safe area.** `room_layout.json` has `"safe_area": {"y0": 10, "y1": 252}`. Base rows 10–252 must always be visible.
- The scale fit uses the safe-area height (242), so the empty wall strip above the window and the floor below the mat may be cropped.
- The visible height is the whole room when it fits. Otherwise it is cropped down to the available height, but never below the safe area, with the crop centred on the safe area and snapped to whole base pixels.
- At 1920×940 this gives ×3 instead of ×2.92.

**Phones (< 600 px).**
- **Overview:** the largest (hybrid) scale whose safe-area height fits the phone room frame. The frame is 45% of the screen height, so the scale is ×1 on current phones. The camera centres on Ringo.
- **Moving around:** a horizontal drag looks around inside the frame (vertical swipes still scroll the page). Keyboard focus brings the focused zone into view.
- **Zoom:** tapping a zone zooms the camera to ×2 on that zone's `camera` rect (`cameraPan`), with a 300 ms transform (instant with reduced motion). The v2 zone panel opens as a bottom sheet below the room, and focus moves into it.
- **Return:** "Back to room", "Enough for today" or Esc closes the sheet and returns the camera to the overview.
- **Overview content:** below the room is the room-level overview panel. There is no sheet until a zone is tapped.

Touch targets are at least 44 px (zones, the info button and the sheet buttons), in EN and FA. There is no page-level horizontal overflow from 320 to 599 px. `npm run test:room-alignment` covers this at 390×844 and 320×640.

