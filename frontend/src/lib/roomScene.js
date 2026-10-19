// Pure helpers for the Living Space pixel room (B19/B20).
// Source of truth: frontend/src/assets/room/room_layout.json
// (docs/product/LIVING_SPACE_VISUAL_V1_SPEC.md + LIVING_SPACE_VISUAL_V1_ADDENDUM.md).
// Kept free of Vue and Vite so test:living-space can import it with an explicit layout.

export const ROOM_BASE_WIDTH = 480;
export const ROOM_BASE_HEIGHT = 270;

// Tab order of the zone hit regions (spec §8) and prop draw order (addendum §5).
export const ZONE_ORDER = Object.freeze([
  "work_desk",
  "learning_corner",
  "creative_corner",
  "sleep_corner",
  "fitness_corner",
]);

// Fractional part of the fit at or above which the room uses the fractional fit (pixelated)
// instead of dropping to the integer below it (Amir's hybrid rule, review round 6).
export const FRACTIONAL_SNAP = 0.85;

// Safe area (B22): the base rows that must always be visible (room_layout.json "safe_area",
// base y 10..252). The empty wall strip above it and the floor strip below it may be cropped.
export function safeArea(layout) {
  const area = layout?.safe_area;
  const y0 = Number.isFinite(Number(area?.y0)) ? Number(area.y0) : 0;
  const y1 = Number.isFinite(Number(area?.y1)) ? Number(area.y1) : ROOM_BASE_HEIGHT;
  return { y0, y1, h: Math.max(1, y1 - y0) };
}

// Largest scale that fits both the available width and height (not rounded).
// fitHeight is the base height that has to fit: the full room, or the safe-area height.
export function roomFit(availableWidth, availableHeight = Number.POSITIVE_INFINITY, fitHeight = ROOM_BASE_HEIGHT) {
  const width = Number(availableWidth);
  const height = availableHeight === undefined || availableHeight === null
    ? Number.POSITIVE_INFINITY
    : Number(availableHeight);
  const byWidth = Number.isNaN(width) ? 0 : width / ROOM_BASE_WIDTH;
  const byHeight = Number.isFinite(height) ? height / (Number(fitHeight) || ROOM_BASE_HEIGHT) : Number.POSITIVE_INFINITY;
  return Math.max(0, Math.min(byWidth, byHeight));
}

// Room scale: the integer below the fit, unless the fit is within 0.15 of the next integer;
// then the fit itself (kept to 1/100 and rounded down so it never overflows). Never below 1.
export function roomScale(availableWidth, availableHeight = Number.POSITIVE_INFINITY, fitHeight = ROOM_BASE_HEIGHT) {
  const fit = roomFit(availableWidth, availableHeight, fitHeight);
  const whole = Math.floor(fit);
  const scale = fit - whole >= FRACTIONAL_SNAP ? Math.floor(fit * 100) / 100 : whole;
  return Math.max(1, scale);
}

// Vertical crop that keeps the safe area visible: the translate (screen px, <= 0) for a room of
// scale s in a viewport shorter than the room. Centred on the safe area, snapped to whole base px.
export function safeAreaPanY({ viewportHeight, scale = 1, safe = { y0: 0, y1: ROOM_BASE_HEIGHT } } = {}) {
  const s = Math.max(1, Number(scale) || 1);
  const view = Number(viewportHeight);
  const room = ROOM_BASE_HEIGHT * s;
  if (!Number.isFinite(view) || room <= view) return 0;

  // Scroll offset (in base px) range that keeps [y0, y1] inside the viewport and the room edges out.
  const viewBase = view / s;
  const low = Math.max(0, safe.y1 - viewBase);
  const high = Math.min(safe.y0, ROOM_BASE_HEIGHT - viewBase);
  const offset = high >= low
    ? clamp(Math.round((low + high) / 2), Math.ceil(low), Math.floor(high))
    : Math.round((safe.y0 + safe.y1 - viewBase) / 2);
  return -clamp(offset, 0, Math.floor(ROOM_BASE_HEIGHT - viewBase)) * s || 0;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

// Camera pan for a room larger than its viewport (desktop mid widths now, B22 mobile zoom later).
// target is in base px: a point { x, y } or a rect { x, y, w, h } (its center is used).
// Returns the translate in screen px for the scaled room: centered on the target, clamped so the
// room's edges are never passed, and snapped to whole base pixels so the pixel art stays crisp.
// scale may be fractional (hybrid rule); the snap is then to multiples of that scale.
// An axis where the room fits the viewport gets 0 (the caller centers or aligns it).
export function cameraPan({ viewportWidth, viewportHeight, scale = 1, target } = {}) {
  const s = Math.max(1, Number(scale) || 1);
  const roomWidth = ROOM_BASE_WIDTH * s;
  const roomHeight = ROOM_BASE_HEIGHT * s;
  const cx = (Number(target?.x) || 0) + (Number(target?.w) || 0) / 2;
  const cy = (Number(target?.y) || 0) + (Number(target?.h) || 0) / 2;

  const axis = (viewport, room, center) => {
    const view = Number(viewport);
    if (!Number.isFinite(view) || room <= view) return 0;
    const raw = clamp(view / 2 - center * s, view - room, 0);
    const snapped = Math.round(raw / s) * s;
    return clamp(snapped, Math.ceil((view - room) / s) * s, 0) || 0;
  };

  return {
    x: axis(viewportWidth, roomWidth, cx),
    y: axis(viewportHeight, roomHeight, cy),
  };
}

// The pan target for the room: the selected zone's camera rect, else Ringo-safe position A.
export function cameraTarget(layout, zoneKey = "") {
  const camera = zoneKey ? layout?.zones?.[zoneKey]?.camera : null;
  if (Array.isArray(camera) && camera.length === 4) {
    const [x, y, w, h] = camera;
    return { x, y, w, h };
  }

  const [x, y] = layout?.ringo_positions?.A || [ROOM_BASE_WIDTH / 2, ROOM_BASE_HEIGHT / 2];
  return { x, y, w: 0, h: 0 };
}

export function footprintBox(footprint = []) {
  if (!footprint.length) return { x: 0, y: 0, w: 0, h: 0 };

  const xs = footprint.map(([x]) => x);
  const ys = footprint.map(([, y]) => y);
  const x = Math.min(...xs);
  const y = Math.min(...ys);

  return { x, y, w: Math.max(...xs) - x, h: Math.max(...ys) - y };
}

// clip-path polygon relative to the footprint's bounding box, in screen px.
export function footprintClipPath(footprint = [], scale = 1) {
  const box = footprintBox(footprint);
  const points = footprint.map(([x, y]) => `${(x - box.x) * scale}px ${(y - box.y) * scale}px`);
  return `polygon(${points.join(", ")})`;
}

// SVG points string relative to the footprint box (base px), for the focus/hover outline.
export function footprintPoints(footprint = []) {
  const box = footprintBox(footprint);
  return footprint.map(([x, y]) => `${x - box.x},${y - box.y}`).join(" ");
}

export function objectAssetPath(assetKey) {
  return assetKey ? `objects/${assetKey}.png` : "";
}

// B21 reward card: largest integer scale at which a w x h pixel PNG fits a square box (never below 1).
export function pixelIconScale(width, height, box) {
  const w = Number(width) || 0;
  const h = Number(height) || 0;
  if (!w || !h) return 1;
  return Math.max(1, Math.floor(Math.min(Number(box) / w, Number(box) / h)));
}

// Find the layout slot for a reward: by slot_key first, then by asset_key.
export function slotForReward(layoutZone, reward) {
  const slots = layoutZone?.slots || {};
  if (reward?.slot_key && slots[reward.slot_key]) {
    return { key: reward.slot_key, ...slots[reward.slot_key] };
  }

  const match = Object.entries(slots).find(([, slot]) => slot.asset_key && slot.asset_key === reward?.asset_key);
  return match ? { key: match[0], ...match[1] } : null;
}

function drawable(layoutZone, reward, hasAsset) {
  const slot = slotForReward(layoutZone, reward);
  const assetKey = reward?.asset_key || slot?.asset_key || "";
  const path = objectAssetPath(assetKey);
  if (!slot || !path || !hasAsset(path)) return null;

  return {
    key: reward?.key || assetKey,
    assetKey,
    path,
    slotKey: slot.key,
    x: slot.x,
    y: slot.y,
    w: slot.w,
    h: slot.h,
  };
}

// B20: placed objects = unlocked rewards with a PNG; ghost = the zone's next locked reward with a PNG.
// B21: rewards still waiting to materialize (pendingKeys) are not placed yet; the first of them in
// the zone is the zone's ghost instead (the same PNG, so the sequence starts from what was shown).
export function zoneObjects(layoutZone, zone, hasAsset = () => true, { pendingKeys = [] } = {}) {
  const pending = new Set(pendingKeys);
  const unlocked = (zone?.unlocked_objects || [])
    .map((reward) => ({ reward, item: drawable(layoutZone, reward, hasAsset) }))
    .filter(({ item }) => item);
  const placed = unlocked.filter(({ reward }) => !pending.has(reward?.key)).map(({ item }) => item);
  const placedSlots = new Set(placed.map((item) => item.slotKey));

  const waiting = unlocked.find(({ reward }) => pending.has(reward?.key) && !placedSlots.has(slotForReward(layoutZone, reward)?.key));
  const ghost = waiting?.item || (zone?.locked_preview_objects || [])
    .map((reward) => drawable(layoutZone, reward, hasAsset))
    .find((item) => item && !placedSlots.has(item.slotKey)) || null;

  return { placed, ghost };
}

// Reminder marker for a zone: a due reminder wins over a scheduled one.
export function zoneMarker(zone) {
  if (Number(zone?.dueReminderCount || 0) > 0) return "bell_due";
  if (Number(zone?.scheduledReminderCount || 0) > 0) return "bell";
  return "";
}

// Ringo sprite placement: anchor bottom-center at a Ringo-safe position (addendum §4).
export function ringoPlacement(layout, { rest = false } = {}) {
  const key = rest ? "sleeping" : "idle";
  const sprite = layout?.ringo_sprites?.[key];
  const positionKey = rest ? (layout?.rest?.ringo_pos || "A") : "A";
  const [px, py] = layout?.ringo_positions?.[positionKey] || [0, 0];
  if (!sprite) return null;

  return {
    file: sprite.file,
    x: Math.round(px - sprite.w / 2),
    y: py - sprite.h,
    w: sprite.w,
    h: sprite.h,
  };
}
