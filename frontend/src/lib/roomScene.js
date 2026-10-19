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

// Integer scaling only (spec §7).
export function roomScale(availableWidth) {
  const width = Number(availableWidth) || 0;
  return Math.max(1, Math.floor(width / ROOM_BASE_WIDTH));
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
export function zoneObjects(layoutZone, zone, hasAsset = () => true) {
  const placed = (zone?.unlocked_objects || [])
    .map((reward) => drawable(layoutZone, reward, hasAsset))
    .filter(Boolean);
  const placedSlots = new Set(placed.map((item) => item.slotKey));

  const ghost = (zone?.locked_preview_objects || [])
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
