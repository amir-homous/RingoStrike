# Living Room Friends Beta — Scope Update (2026-10-19)

Status: requested by Amir on 2026-10-19. This file is the source for the new issues B17–B24.

## Decision change

- **D1 is replaced by D7.** Previously, the beta was to ship the current room shell, with art in the next milestone.
- **D7:** This milestone must reach the first presentable **visual** Living Space on desktop and mobile. The room must be a real scene with zones and objects, based on the canvas samples "Desktop — Creative Corner selected, first reward placed" and "Mobile — room crop + bottom sheet", at higher final quality. The friends beta ships with this visual room.
- **D8 (APPROVED 2026-10-19 as PIXEL ART, replacing the SVG proposal below): layered pixel art, 480×270 base, integer scaling only; see docs/product/LIVING_SPACE_VISUAL_V1_SPEC.md.** Original proposal: Visual v1 is a layered **vector (SVG) scene built in code**. This matches the earlier "lightweight vector-style room assets" note. Each zone and object is a separate layer, keyed by the reward `asset_key` and `slot_key`, so hand-made art (raster or vector) can later replace individual layers without code changes.
- **D9 (proposed):** v1 art scope per zone is:
  - one Stage 0 base prop
  - the first-reward object, placed when unlocked
  - the second reward as a ghost preview

  That is 5 zones × 3 = 15 drawn elements. The remaining 15 reward definitions get no art in v1 and appear only in the panel's object list.
- **D10:** RTL never mirrors the room. Only the panel and text are mirrored.

## New issues

### B17 — [Docs/Design] Living Space Visual v1 spec and asset contract

- Scene composition:
  - elevated 3/4 soft-perspective camera
  - 5 zone footprints
  - 3 Ringo-safe positions
  - central circulation
- Layer list, and the anchor coordinates for every zone and object slot.
- Visual states: base, hover/focus, selected (light pool, others subdued), ghost preview, placed, newly placed (materialize), rest/night.
- Desktop layout, mobile layout (overview crop, then zone zoom), RTL rule.
- Asset contract: file naming by `asset_key`, viewBox, and how raster art can replace a layer later.

**Acceptance:** spec merged in `docs/product/`; Amir approves.

### B18 — [Design] High-fidelity Visual v1 mock-ups (approval gate)

Built on the design canvas:
- desktop overview, desktop zone selected
- mobile overview crop, mobile zone zoom + bottom sheet
- first-reward materialize sequence (3 frames)
- room Rest state

All 5 zones and all 15 v1 elements are drawn.

**Acceptance:** Amir approves before B19 starts.

### B19 — [Frontend] Room scene renderer

- Replace the zone card grid with the layered SVG scene from B17/B18.
- Zones are accessible hit regions: real buttons with `aria-label`, keyboard focus and visible focus.
- Labels show on hover, focus and selection only.
- Uses existing `/me/space` data and the existing panel and events. No backend change.
- Ringo appears in the scene at a safe position.
- Keep a simple fallback if the scene fails to render.

**Acceptance:** desktop matches the B18 mock-up in EN and FA. All existing flows still work.

### B20 — [Frontend] v1 object art: base props, placed objects and ghosts

- Draw the 15 v1 elements as layers keyed by `asset_key`.
- Placed objects come from unlocked rewards; the ghost is the next locked reward of that zone.

**Acceptance:** a fresh user sees base props and ghosts; after the first mission in a path, that zone's object is placed and persists after reload.

### B21 — [Frontend] In-room reward materialization

- Calm sequence: focus light, then the ghost strengthens, then the object resolves and settles, then Ringo acknowledges.
- It plays in the room after the reward sequence closes.
- No confetti. `prefers-reduced-motion` shows the final state.

**Acceptance:** plays once per newly unlocked reward; never for backfilled rewards.

### B22 — [Frontend] Mobile room: overview crop, zone zoom, bottom sheet

- Overview shows the cropped room.
- Tapping a zone zooms or pans the camera to that zone, then the bottom sheet opens with the v2 panel.
- Closing returns the camera to the overview.

**Acceptance:** works at 390px in EN and FA, with no horizontal overflow and touch targets of at least 44px.

### B23 — [UX] Room-level overview and Rest state after Close and "Enough for today"

Today, Close and "برای امروز کافیه" put Ringo into rest but keep the selected zone's panel open, so the user stays in that zone.

New behavior:
- Both actions deselect the zone and return to a room-level state:
  - Ringo's room message
  - a day summary (missions done today, today-safe state, scheduled and due reminders, objects placed today)
  - a gentle invitation to pick a zone, for example by highlighting the zone Ringo suggests next
- Rename "بستن" to a room-oriented label, for example "بازگشت به اتاق" / "Back to room". Final wording comes in B10.

**Acceptance:** no zone panel stays open after either action. The room overview or rest state shows in EN and FA, on desktop and mobile.

### B24 — [UX] Reminder visibility: scheduled marker, reminder list, do it now

- A zone with a **scheduled (not yet due)** reminder shows a small, calm marker: a bell icon, distinct from the due state.
- The panel's "یادآورها" section lists each reminder with:
  - the mission title
  - the zone and path
  - the time left ("۲ ساعت و ۱۰ دقیقه دیگه") or "رسیده"
- Tapping a reminder makes that mission the Ringo focus immediately, so the user can do it now through the normal Ringo card actions.
- Reuse the existing reminder data and endpoints. No backend change, unless the investigation shows the scheduled time is not returned.

**Acceptance:** markers, list and tap-to-focus work in EN and FA. Due reminders keep their current priority.

## New phase order

1. **Phase 2b — Room behavior:** B23, B24, then B10 copy and B11 first-run. These run while the visual design (B17, B18) happens on the canvas.
2. **Phase 2c — Visual v1:** B17 → B18 (approval gate) → B19 → B20 → B21 → B22.
3. **Phase 3 — Release:** B12 QA, B13 merge to main, B14 deploy. Unchanged, but now QA covers the visual room.
4. **Phase 4 — Friends beta week:** B15, B16. Unchanged.

### B25 — [Art] Final pixel Ringo sprite (future, Amir retouch)

- v1 ships a placeholder pixel Ringo (idle + sleeping) drawn for the style test.
- Amir later draws or retouches the final pixel Ringo sprites (idle, sleeping, happy), keeping the same size and anchors so no code change is needed.
- Milestone: next (Living Room Visual polish). Not a beta blocker.
