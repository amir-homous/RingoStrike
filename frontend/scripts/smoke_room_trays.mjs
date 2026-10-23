// B30 S2: every zone's challenge tray (room_layout.json `tray`) must stay clear of the room's
// props (their real pixels), reward slots (placed or ghost), the Ringo-safe spots, the rug, the
// window and the zone's own path marker, inside the room's safe area. Dependency-free: the prop
// PNGs are decoded with node:zlib. Run: npm run test:room-trays
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { inflateSync } from "node:zlib";

import { MISSION_TRAY_MAX_PAWS, pagePaws, trayRows } from "../src/lib/missionTray.js";
import {
  ROOM_BASE_HEIGHT,
  ROOM_BASE_WIDTH,
  ZONE_ORDER,
  markerSpanPanX,
  placeTray,
  safeArea,
  TRAY_SCREEN,
  trayRect,
  trayScreenFactor,
} from "../src/lib/roomScene.js";

const roomDir = new URL("../src/assets/room/", import.meta.url);
const layout = JSON.parse(readFileSync(new URL("room_layout.json", roomDir), "utf8"));

// Clearance kept around every obstacle (base px).
const MARGIN = 2;
// Scales the tray is checked at: desktop x2 and x3, and the phone zone zoom (x2).
const SCALES = [
  { label: "desktop x2", scale: 2, phone: false },
  { label: "desktop x3", scale: 3, phone: false },
  { label: "phone zoom x2", scale: 2, phone: true },
];

// Alpha channel of an 8-bit RGBA, non-interlaced PNG (the room art export writes only these).
function pngAlpha(url) {
  const buf = readFileSync(url);
  let offset = 8;
  let width = 0;
  let height = 0;
  const idat = [];
  while (offset < buf.length) {
    const length = buf.readUInt32BE(offset);
    const type = buf.toString("ascii", offset + 4, offset + 8);
    const data = buf.subarray(offset + 8, offset + 8 + length);
    if (type === "IHDR") {
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      assert.equal(data[8], 8, `${url.pathname}: bit depth`);
      assert.equal(data[9], 6, `${url.pathname}: RGBA colour type`);
      assert.equal(data[12], 0, `${url.pathname}: interlace`);
    }
    if (type === "IDAT") idat.push(data);
    offset += 12 + length;
  }
  const raw = inflateSync(Buffer.concat(idat));
  const stride = width * 4;
  const pixels = Buffer.alloc(height * stride);
  for (let y = 0; y < height; y++) {
    const filter = raw[y * (stride + 1)];
    const line = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1));
    for (let x = 0; x < stride; x++) {
      const a = x >= 4 ? pixels[y * stride + x - 4] : 0;
      const b = y > 0 ? pixels[(y - 1) * stride + x] : 0;
      const c = x >= 4 && y > 0 ? pixels[(y - 1) * stride + x - 4] : 0;
      let value = line[x];
      if (filter === 1) value += a;
      else if (filter === 2) value += b;
      else if (filter === 3) value += Math.floor((a + b) / 2);
      else if (filter === 4) {
        const p = a + b - c;
        const pa = Math.abs(p - a);
        const pb = Math.abs(p - b);
        const pc = Math.abs(p - c);
        value += pa <= pb && pa <= pc ? a : (pb <= pc ? b : c);
      }
      pixels[y * stride + x] = value & 0xff;
    }
  }
  return { width, height, alpha: (x, y) => pixels[y * stride + x * 4 + 3] };
}

// Opaque prop pixels in base px: "x,y" -> zone key.
const propPixels = new Map();
const propCounts = {};
for (const key of ZONE_ORDER) {
  const prop = layout.zones[key].prop;
  const png = pngAlpha(new URL(prop.file, roomDir));
  for (let y = 0; y < png.height; y++) {
    for (let x = 0; x < png.width; x++) {
      if (png.alpha(x, y) === 0) continue;
      propPixels.set(`${prop.x + x},${prop.y + y}`, `prop:${key}`);
      propCounts[key] = (propCounts[key] || 0) + 1;
    }
  }
}

// Rect obstacles in base px: reward slots, Ringo-safe spots (both sprites), keep-clear art.
const rects = [];
for (const key of ZONE_ORDER) {
  for (const [slotKey, slot] of Object.entries(layout.zones[key].slots || {})) {
    rects.push({ name: `slot:${slotKey}`, x0: slot.x, y0: slot.y, x1: slot.x + slot.w, y1: slot.y + slot.h });
  }
}
for (const [pos, [x, y]] of Object.entries(layout.ringo_positions || {})) {
  for (const sprite of Object.values(layout.ringo_sprites || {})) {
    rects.push({ name: `ringo-safe:${pos}`, x0: x - sprite.w / 2, y0: y - sprite.h, x1: x + sprite.w / 2, y1: y });
  }
}
for (const [name, [x0, y0, x1, y1]] of Object.entries(layout.keep_clear || {})) {
  rects.push({ name, x0, y0, x1, y1 });
}

// The zone's own path marker at its widest (reminder chip and check badge both shown), as
// RoomScene draws it (pathMarkerSizes / pathMarkerExtents): screen px converted to base px.
function markerRect([ax, ay], { scale, phone }) {
  const grow = phone ? 0 : Math.min(2, Math.max(0, scale - 1));
  const ring = Math.round(34 + grow * 11);
  const radius = ring / 2;
  const chip = ring * 0.3 + 18;
  const badge = ring * 0.22 + 16;
  return {
    name: "own path marker",
    x0: ax - radius / scale,
    y0: ay - Math.max(radius, chip) / scale,
    x1: ax + Math.max(radius, chip, badge) / scale,
    y1: ay + Math.max(radius, badge) / scale,
  };
}

function overlaps(a, b) {
  return a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
}

// Everything a tray rect (base px) touches, with MARGIN clearance.
export function trayConflicts(zoneKey, rect, options) {
  const box = { x0: rect.x - MARGIN, y0: rect.y - MARGIN, x1: rect.x + rect.w + MARGIN, y1: rect.y + rect.h + MARGIN };
  const hits = new Set();
  const safe = safeArea(layout);
  if (rect.x < 0 || rect.x + rect.w > ROOM_BASE_WIDTH || rect.y < safe.y0 || rect.y + rect.h > safe.y1) {
    hits.add("outside the room's safe area");
  }
  for (const r of rects) if (overlaps(box, r)) hits.add(r.name);
  if (overlaps(box, markerRect(layout.zones[zoneKey].path_marker, options))) hits.add("own path marker");
  for (let y = Math.floor(box.y0); y < Math.ceil(box.y1); y++) {
    for (let x = Math.floor(box.x0); x < Math.ceil(box.x1); x++) {
      const prop = propPixels.get(`${x},${y}`);
      if (prop) hits.add(prop);
    }
  }
  return [...hits];
}

function run() {
  assert.ok(Object.keys(layout.keep_clear || {}).length >= 2, "keep_clear lists the window and the rug");

  // Decoded prop pixels per zone (opaque), so a decoder fault cannot pass silently.
  for (const key of ZONE_ORDER) assert.ok(propCounts[key] > 1000, `${key}: prop pixels decoded`);

  // The check itself must catch a tray on the window and one off the room's edge.
  assert.ok(trayConflicts("creative_corner", trayRect({ flag: [214, 40], dir: "right" }, 2), SCALES[0]).includes("window"));
  assert.ok(trayConflicts("work_desk", trayRect({ flag: [20, 46], dir: "left" }, 2), SCALES[0]).includes("outside the room's safe area"));
  // ...and one on a prop (the learning shelf) and on its own marker.
  assert.ok(trayConflicts("learning_corner", trayRect({ flag: [170, 80], dir: "right" }, 2), SCALES[0]).includes("prop:learning_corner"));
  assert.ok(trayConflicts("creative_corner", trayRect({ flag: [300, 46], dir: "right" }, 2), SCALES[0]).includes("own path marker"));

  for (const key of ZONE_ORDER) {
    const zone = layout.zones[key];
    assert.ok(zone.tray, `${key}: tray placement present`);
    assert.ok(["left", "right"].includes(zone.tray.dir), `${key}: tray dir`);
    for (const options of SCALES) {
      const rect = trayRect(zone.tray, options.scale, options);
      const conflicts = trayConflicts(key, rect, options);
      assert.deepEqual(conflicts, [], `${key} tray at ${options.label} overlaps: ${conflicts.join(", ")}`);
    }
  }

  // B30 S3 (D50): the mission tray uses the same anchor; its row may run as far as `run` (base
  // px from the flag edge, along dir). That whole run must be clear; the optional second row
  // (wrap) may cover furniture props only when over_props is set (D45 fallback).
  for (const key of ZONE_ORDER) {
    const zone = layout.zones[key];
    assert.ok(Number(zone.tray.run) >= 88, `${key}: mission tray run covers at least the challenge tray`);
    for (const options of SCALES.filter((option) => !option.phone)) {
      const k = trayScreenFactor(options.scale, options);
      const half = (TRAY_SCREEN.flag * k) / 2 / options.scale;
      const halfH = (TRAY_SCREEN.height * k) / 2 / options.scale;
      // The row ends where the x2 row ends (flag edge at x2 + run), whatever the scale.
      const rowRect = (dy, run) => {
        const [fx, fy] = zone.tray.flag;
        const w = run - 7 + half;
        const x = zone.tray.dir === "left" ? fx + 7 - run : fx - half;
        return { x, y: fy + dy - halfH, w, h: halfH * 2 };
      };
      const first = trayConflicts(key, rowRect(0, zone.tray.run), options);
      assert.deepEqual(first, [], `${key} mission row at ${options.label} overlaps: ${first.join(", ")}`);
      if (zone.tray.wrap) {
        const second = trayConflicts(key, rowRect(zone.tray.wrap.dy, zone.tray.wrap.run), options)
          .filter((name) => !(zone.tray.wrap.over_props && name.startsWith("prop:")));
        assert.deepEqual(second, [], `${key} second mission row at ${options.label} overlaps: ${second.join(", ")}`);
      }
    }
  }

  // Reachability (B30 S3): with the same sizing as RoomScene, every mission of a challenge (1 to 6
  // paws) is on a page of the zone's mission tray, each page fits the row's slots, the pager walks
  // through all pages in Tab/DOM order (challenge, paws, pager) and back returns to the first.
  const views = [
    { label: "desktop x2", scale: 2, phone: false },
    { label: "desktop x3", scale: 3, phone: false },
    { label: "phone 390", scale: 2, phone: true, frame: 328 },
    { label: "phone 360", scale: 2, phone: true, frame: 298 },
    { label: "phone 440", scale: 2, phone: true, frame: 378 },
  ];
  for (const key of ZONE_ORDER) {
    const zone = layout.zones[key];
    for (const view of views) {
      const k = trayScreenFactor(view.scale, view);
      const pad = TRAY_SCREEN.pad * k;
      const fixed = (TRAY_SCREEN.flag * k) / 2 + pad * 2;
      const rows = view.phone
        ? [view.frame - 8 - fixed, view.frame - 8 - fixed]
        : [(zone.tray.run - 7) * view.scale - pad * 2, ...(zone.tray.wrap ? [(zone.tray.wrap.run - 7) * view.scale - pad * 2] : [])];
      for (let count = 1; count <= 6; count++) {
        const missions = Array.from({ length: count }, (_, index) => ({ id: index + 1 }));
        const sizing = trayRows({ pawCount: count, rows, pitches: [48 * k, 44 * k] });
        assert.ok(sizing.slots >= Math.min(3, 1 + count), `${key} ${view.label} ${count} missions: room for the challenge, a paw and the pager (${sizing.slots})`);
        const reached = [];
        let page = pagePaws(missions, { slots: sizing.slots });
        for (let step = 0; step <= count; step++) {
          const items = 1 + page.visible.length + (page.control ? 1 : 0);
          assert.ok(items <= sizing.slots, `${key} ${view.label} ${count} missions: page ${page.page} has ${items} items for ${sizing.slots} slots`);
          assert.ok(page.visible.length <= MISSION_TRAY_MAX_PAWS);
          reached.push(...page.visible.map((mission) => mission.id));
          if (!page.control || page.control.kind === "back") break;
          page = pagePaws(missions, { slots: sizing.slots, page: page.control.page });
        }
        assert.deepEqual(reached, missions.map((mission) => mission.id), `${key} ${view.label} ${count} missions: every mission reachable once`);
        if (page.control) assert.equal(pagePaws(missions, { slots: sizing.slots, page: page.control.page }).page, 0, "back goes to the first page");
      }
    }
  }

  // Footprint math: the compact tray at x2 is 176x50 screen px (flag included), 88x25 base px.
  const fitness = trayRect(layout.zones.fitness_corner.tray, 2);
  assert.deepEqual([fitness.w, fitness.h], [88, 25]);
  assert.ok(ROOM_BASE_HEIGHT === 270);

  // D46: the phone overview centres the marker anchors (x 78..398, centre 238) in the frame.
  assert.equal(markerSpanPanX(layout, 328, 1), -74);
  assert.equal(markerSpanPanX(layout, 298, 1), -89);
  assert.equal(markerSpanPanX(layout, 378, 1), -49);
  assert.equal(markerSpanPanX(layout, 960, 2), 0);

  // D45 phone: the tray stays inside the frame and off its (possibly clamped) marker.
  const frame = { x0: 0, y0: 0, x1: 328, y1: 242 };
  const marker = { cx: 300, cy: 24, ax: 300, ay: 24, left: 22, right: 31, up: 31, down: 22 };
  const overlaps = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  const keepOut = { x: 300 - 22, y: 24 - 31, w: 53, h: 53 };
  for (const dir of ["right", "left"]) {
    const placed = placeTray({ rect: { x: dir === "right" ? 314 : 112, y: -1, w: 176, h: 50 }, dir, marker, frame });
    assert.ok(placed.x >= 4 && placed.x + placed.w <= 324 && placed.y >= 4 && placed.y + placed.h <= 238, `${dir}: in frame`);
    assert.ok(!overlaps(placed, keepOut), `${dir}: off the marker`);
  }
  // Desktop (no frame): the tray stays at its anchor.
  assert.deepEqual(placeTray({ rect: { x: 10, y: 20, w: 176, h: 50 }, dir: "right", marker, frame: null }), { x: 10, y: 20, w: 176, h: 50, dir: "right" });

  // B34 (D68): the reminder clock next to Ringo's spot A never covers a reward slot, a Ringo-safe
  // spot, a prop, the window, a path marker, or any zone's challenge tray or mission rows, at every
  // scale. It stands on the rug next to Ringo (boards 22 to 24), so the rug is allowed.
  const clock = layout.reminder_clock;
  assert.ok(clock && clock.w === 16 && clock.h === 18 && clock.set && clock.ring, "reminder_clock anchor (16x18, both sprites)");
  for (const file of [clock.set, clock.ring]) {
    const png = pngAlpha(new URL(file, roomDir));
    assert.deepEqual([png.width, png.height], [clock.w, clock.h], `${file}: 16x18`);
  }
  const boxesHit = (a, b) => a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
  const clockConflicts = (box) => {
    const hits = new Set();
    const safe = safeArea(layout);
    if (box.x0 < 0 || box.x1 > ROOM_BASE_WIDTH || box.y0 < safe.y0 || box.y1 > safe.y1) hits.add("outside the room's safe area");
    for (const r of rects) if (r.name !== "rug" && boxesHit(box, r)) hits.add(r.name);
    for (let y = Math.floor(box.y0); y < Math.ceil(box.y1); y++) {
      for (let x = Math.floor(box.x0); x < Math.ceil(box.x1); x++) {
        const prop = propPixels.get(`${x},${y}`);
        if (prop) hits.add(prop);
      }
    }
    for (const key of ZONE_ORDER) {
      const zone = layout.zones[key];
      for (const options of SCALES) {
        const t = trayRect(zone.tray, options.scale, options);
        if (boxesHit(box, { x0: t.x, y0: t.y, x1: t.x + t.w, y1: t.y + t.h })) hits.add(`${key} tray at ${options.label}`);
        if (boxesHit(box, markerRect(zone.path_marker, options))) hits.add(`${key} path marker at ${options.label}`);
        const k = trayScreenFactor(options.scale, options);
        const half = (TRAY_SCREEN.flag * k) / 2 / options.scale;
        const halfH = (TRAY_SCREEN.height * k) / 2 / options.scale;
        for (const [dy, run] of [[0, zone.tray.run], ...(zone.tray.wrap ? [[zone.tray.wrap.dy, zone.tray.wrap.run]] : [])]) {
          const [fx, fy] = zone.tray.flag;
          const x = zone.tray.dir === "left" ? fx + 7 - run : fx - half;
          const row = { x0: x, y0: fy + dy - halfH, x1: x + run - 7 + half, y1: fy + dy + halfH };
          if (boxesHit(box, row)) hits.add(`${key} mission row at ${options.label}`);
        }
      }
    }
    return [...hits];
  };
  const clockBox = { x0: clock.x - MARGIN, y0: clock.y - MARGIN, x1: clock.x + clock.w + MARGIN, y1: clock.y + clock.h + MARGIN };
  assert.deepEqual(clockConflicts(clockBox), [], `reminder clock overlaps: ${clockConflicts(clockBox).join(", ")}`);
  // The check itself catches a clock on Ringo (spot A), on a reward slot and on the window.
  assert.ok(clockConflicts({ x0: 262, y0: 190, x1: 278, y1: 208 }).includes("ringo-safe:A"));
  const lamp = layout.zones.work_desk.slots.work_desk_consistency;
  assert.ok(clockConflicts({ x0: lamp.x, y0: lamp.y, x1: lamp.x + 16, y1: lamp.y + 18 }).includes("slot:work_desk_consistency"));
  assert.ok(clockConflicts({ x0: 230, y0: 30, x1: 246, y1: 48 }).includes("window"));

  console.log(`Prop pixels: ${ZONE_ORDER.map((key) => `${key} ${propCounts[key]}`).join(", ")}`);
  console.log("Room tray placement check passed (challenge trays and mission rows in clear space; Fitness second mission row over furniture only; reminder clock clear of slots, trays, markers, props and Ringo).");
}

run();
