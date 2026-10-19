import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";
import { footprintBox, safeArea } from "../src/lib/roomScene.js";

// Room alignment at integer and fractional scales (hybrid rule): the pixel layers, zone hit
// regions, focus polygons, labels, dim/light layers and camera pan must all use one scale.
// B22: the safe area (base y 10..252) is always visible, and on phones the overview, the x2 zone
// zoom with the bottom sheet, and "Back to room" keep the same alignment, with 44px touch targets.

const FRONTEND_BASE = process.env.FRONTEND_BASE_URL || "http://localhost:5173";
const API_BASE = process.env.VITE_API_BASE || "http://localhost:5005";
const CHROME_BIN = process.env.CHROME_BIN || "/usr/bin/google-chrome";
const DEBUG_PORT = Number(process.env.ROOM_ALIGNMENT_DEBUG_PORT || 9233);
const TOLERANCE = 0.75; // screen px (sub-pixel layout rounding)

// [width, height, expected kind]. The fit uses the safe-area height (242 base px):
// 1920x850 -> ~2.89 (fractional), 1920x940 -> x3 (x2.92 before the safe area), the others integer.
const VIEWPORTS = [
  [1920, 850, "fractional"],
  [1920, 940, "integer", 3],
  [1920, 1080, "integer", 3],
  [1440, 900, "integer", 2],
  [1366, 768, "integer-pan", 2],
];
// Phones (< 600px): [width, height]. Overview x1, a selected zone zooms to x2.
const PHONES = [
  [390, 844],
  [320, 640],
];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForJson(url, timeoutMs = 10000) {
  const started = Date.now();

  while (Date.now() - started < timeoutMs) {
    try {
      const response = await fetch(url);

      if (response.ok) {
        return await response.json();
      }
    } catch {
      // Wait for Chrome to expose the DevTools endpoint.
    }

    await delay(100);
  }

  throw new Error(`Timed out waiting for ${url}`);
}

async function waitForOk(url, timeoutMs = 10000) {
  const started = Date.now();

  while (Date.now() - started < timeoutMs) {
    try {
      const response = await fetch(url);

      if (response.ok) {
        return;
      }
    } catch {
      // Wait for the local server to respond.
    }

    await delay(100);
  }

  throw new Error(`Timed out waiting for ${url}`);
}

function createCdpClient(wsUrl) {
  const socket = new WebSocket(wsUrl);
  let nextId = 1;
  const pending = new Map();
  const handlers = new Map();

  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);

    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);

      if (message.error) {
        reject(new Error(message.error.message || JSON.stringify(message.error)));
      } else {
        resolve(message.result || {});
      }

      return;
    }

    const handler = handlers.get(message.method);
    if (handler) handler(message.params || {});
  });

  return {
    waitForOpen() {
      if (socket.readyState === WebSocket.OPEN) return Promise.resolve();

      return new Promise((resolve, reject) => {
        socket.addEventListener("open", resolve, { once: true });
        socket.addEventListener("error", reject, { once: true });
      });
    },
    send(method, params = {}) {
      const id = nextId++;
      socket.send(JSON.stringify({ id, method, params }));

      return new Promise((resolve, reject) => {
        pending.set(id, { resolve, reject });
      });
    },
    on(method, handler) {
      handlers.set(method, handler);
    },
    close() {
      socket.close();
    },
  };
}


async function createUser() {
  const username = `align${Date.now()}`.slice(0, 18);
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password: "secret123", name: "Align Smoke", email: `${username}@example.com` }),
  });
  assert.equal(response.status, 201);
  const data = await response.json();
  const me = await fetch(`${API_BASE}/me`, { headers: { Authorization: `Bearer ${data.access_token}` } }).then((r) => r.json());
  return { token: data.access_token, id: data.user_id ?? me.user_id };
}

async function evaluate(page, expression) {
  const result = await page.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text);
  return result.result.value;
}

async function waitFor(page, expression, timeoutMs = 20000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await evaluate(page, expression)) return;
    await delay(150);
  }
  throw new Error(`Timed out waiting for ${expression}`);
}

// Runs in the page: every measured rect relative to the (panned) scene, in screen px.
const MEASURE = `(() => {
  const scene = document.querySelector(".roomScene").getBoundingClientRect();
  const base = document.querySelector(".sceneBase");
  const baseScale = new DOMMatrixReadOnly(getComputedStyle(base).transform).a;
  const rel = (el) => { const r = el.getBoundingClientRect(); return { x: r.left - scene.left, y: r.top - scene.top, w: r.width, h: r.height }; };
  const zones = [...document.querySelectorAll(".zoneHitWrap")].map((wrap) => {
    const svg = wrap.querySelector(".zoneOutline");
    const label = wrap.querySelector(".zoneLabel");
    return { key: wrap.dataset.zone, hit: rel(wrap.querySelector(".zoneHit")), outline: rel(svg), viewBoxW: svg.viewBox.baseVal.width, viewBoxH: svg.viewBox.baseVal.height, labelCenter: rel(label).x + rel(label).w / 2 };
  });
  const light = document.querySelector(".lightLayer");
  const dim = document.querySelector(".dimLayer");
  const viewport = document.querySelector(".roomViewport").getBoundingClientRect();
  const sheet = document.querySelector(".zoneSheet");
  return {
    viewportTop: viewport.top - scene.top, viewportBottom: viewport.bottom - scene.top,
    viewportW: viewport.width,
    panY: new DOMMatrixReadOnly(getComputedStyle(document.querySelector(".roomScene")).transform).f,
    hits: [...document.querySelectorAll(".zoneHit")].map((hit) => { const r = hit.getBoundingClientRect(); return [r.width, r.height]; }),
    sheet: sheet ? { top: sheet.getBoundingClientRect().top, bottom: sheet.getBoundingClientRect().bottom, height: innerHeight, focused: sheet.contains(document.activeElement) } : null,
    pageScroll: document.documentElement.scrollWidth - innerWidth,
    sceneW: scene.width, sceneH: scene.height, baseScale,
    pan: new DOMMatrixReadOnly(getComputedStyle(document.querySelector(".roomScene")).transform).e,
    viewportH: viewport.height,
    light: light ? { ...rel(light), nw: light.naturalWidth, nh: light.naturalHeight } : null,
    dim: dim ? rel(dim) : null,
    zones,
    hscroll: document.documentElement.scrollWidth > innerWidth,
  };
})()`;

function near(actual, expected, what) {
  assert.ok(Math.abs(actual - expected) <= TOLERANCE, `${what}: ${actual} vs ${expected}`);
}

function checkSafeArea(m, label, { full = true } = {}) {
  const s = m.baseScale;
  const safe = safeArea(LAYOUT);
  // The visible rows (relative to the scene) must include the safe area, vertically.
  assert.ok(m.viewportTop <= safe.y0 * s + TOLERANCE, `${label} safe area top cropped: ${m.viewportTop} > ${safe.y0 * s}`);
  assert.ok(m.viewportBottom >= safe.y1 * s - TOLERANCE, `${label} safe area bottom cropped: ${m.viewportBottom} < ${safe.y1 * s}`);
  const panBase = m.panY / s;
  assert.ok(Math.abs(panBase - Math.round(panBase)) < 0.01, `${label} pan y ${m.panY} is not whole base px`);
  if (full) assert.ok(m.viewportBottom - m.viewportTop >= safe.h * s - TOLERANCE, `${label} viewport shorter than the safe area`);
}

let LAYOUT = null;

function checkLayout(m, layout, label) {
  const s = m.baseScale;
  near(m.sceneW, 480 * s, `${label} scene width`);
  near(m.sceneH, 270 * s, `${label} scene height`);
  assert.ok(m.viewportH <= 270 * s + TOLERANCE, `${label} viewport taller than the room`);
  assert.equal(m.hscroll, false, `${label} page-level horizontal scroll`);
  assert.ok(m.zones.length >= 5, `${label} zones rendered`);

  for (const zone of m.zones) {
    const box = footprintBox(layout.zones[zone.key].footprint);
    for (const [part, rect] of [["hit", zone.hit], ["outline", zone.outline]]) {
      near(rect.x, box.x * s, `${label} ${zone.key} ${part} x`);
      near(rect.y, box.y * s, `${label} ${zone.key} ${part} y`);
      near(rect.w, box.w * s, `${label} ${zone.key} ${part} w`);
      near(rect.h, box.h * s, `${label} ${zone.key} ${part} h`);
    }
    // The focus polygon's viewBox is the footprint box in base px, so it maps with the same scale.
    near(zone.outline.w / zone.viewBoxW, s, `${label} ${zone.key} polygon scale x`);
    near(zone.outline.h / zone.viewBoxH, s, `${label} ${zone.key} polygon scale y`);
    near(zone.labelCenter, (box.x + box.w / 2) * s, `${label} ${zone.key} label centre`);
  }
}

async function run() {
  await waitForJson(`${API_BASE}/health`);
  await waitForOk(`${FRONTEND_BASE}/`);

  const layout = JSON.parse(await readFile(new URL("../src/assets/room/room_layout.json", import.meta.url), "utf8"));
  LAYOUT = layout;
  const user = await createUser();
  const userDataDir = await mkdtemp(join(tmpdir(), "ringo-room-alignment-"));
  const chrome = spawn(CHROME_BIN, [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    `--remote-debugging-port=${DEBUG_PORT}`,
    `--user-data-dir=${userDataDir}`,
    "about:blank",
  ]);

  try {
    chrome.stderr.on("data", () => {});
    chrome.stdout.on("data", () => {});

    await waitForJson(`http://127.0.0.1:${DEBUG_PORT}/json/version`);
    const target = await fetch(`http://127.0.0.1:${DEBUG_PORT}/json/new?about:blank`, { method: "PUT" }).then((r) => r.json());
    const page = createCdpClient(target.webSocketDebuggerUrl);
    await page.waitForOpen();
    await page.send("Runtime.enable");
    await page.send("Page.enable");
    await page.send("Page.addScriptToEvaluateOnNewDocument", {
      source: `localStorage.setItem("ringo_token", ${JSON.stringify(user.token)});
        if (!localStorage.getItem("ringostrike_locale")) localStorage.setItem("ringostrike_locale", "en");
        localStorage.setItem(${JSON.stringify(`ringostrike_onboarding_done:user:${user.id}`)}, "1");`,
    });

    for (const [width, height, kind, expectedScale] of VIEWPORTS) {
      const label = `${width}x${height}`;
      await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: false });
      await page.send("Page.navigate", { url: `${FRONTEND_BASE}/dashboard` });
      await waitFor(page, `Boolean(document.querySelector(".roomScene .zoneHitWrap"))`);
      await evaluate(page, `document.querySelector(".zonePanel .closeButton")?.click()`);
      await delay(900);

      const overview = await evaluate(page, MEASURE);
      const s = overview.baseScale;
      if (kind === "fractional") {
        assert.ok(!Number.isInteger(s) && s - Math.floor(s) >= 0.85, `${label} expected a fractional scale, got ${s}`);
      } else {
        assert.ok(Number.isInteger(s) && s >= 2, `${label} expected an integer scale >= 2, got ${s}`);
      }
      if (expectedScale) assert.equal(s, expectedScale, `${label} scale`);
      checkLayout(overview, layout, `${label} overview`);
      checkSafeArea(overview, `${label} overview`);

      // Select each zone: dim covers the scene, light sits at its base position, pan snaps to base px.
      for (const key of Object.keys(layout.zones)) {
        await evaluate(page, `document.querySelector('.zoneHitWrap[data-zone="${key}"] .zoneHit').click()`);
        await waitFor(page, `Boolean(document.querySelector(".lightLayer")?.complete && document.querySelector(".lightLayer").naturalWidth)`);
        await delay(450); // camera pan transition (300 ms)
        const selected = await evaluate(page, MEASURE);
        const zl = layout.zones[key];
        checkLayout(selected, layout, `${label} ${key}`);
        checkSafeArea(selected, `${label} ${key}`);
        near(selected.dim.x, 0, `${label} ${key} dim x`);
        near(selected.dim.y, 0, `${label} ${key} dim y`);
        near(selected.dim.w, 480 * s, `${label} ${key} dim w`);
        near(selected.dim.h, 270 * s, `${label} ${key} dim h`);
        near(selected.light.x, zl.light.x * s, `${label} ${key} light x`);
        near(selected.light.y, zl.light.y * s, `${label} ${key} light y`);
        near(selected.light.w, selected.light.nw * s, `${label} ${key} light w`);
        near(selected.light.h, selected.light.nh * s, `${label} ${key} light h`);
        const panBase = selected.pan / s;
        assert.ok(Math.abs(panBase - Math.round(panBase)) < 0.01, `${label} ${key} pan ${selected.pan} is not whole base px at x${s}`);
        if (kind !== "integer-pan") assert.equal(selected.pan, 0, `${label} ${key} unexpected pan`);
      }
      console.log(`${label}: x${s} aligned, safe area visible`);
    }

    for (const [width, height] of PHONES) {
      for (const locale of ["en", "fa"]) {
        const label = `${width}x${height} ${locale}`;
        await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: true });
        await page.send("Runtime.evaluate", { expression: `localStorage.setItem("ringostrike_locale", "${locale}")` });
        await page.send("Page.navigate", { url: `${FRONTEND_BASE}/dashboard` });
        await waitFor(page, `Boolean(document.querySelector(".roomScene .zoneHitWrap"))`);
        await delay(900);

        assert.equal(await evaluate(page, "document.documentElement.dir || 'ltr'"), locale === "fa" ? "rtl" : "ltr", `${label} page direction`);

        // Overview: x1 fitted to the phone room height, safe area visible, no sheet, no page scroll.
        const overview = await evaluate(page, MEASURE);
        assert.equal(overview.baseScale, 1, `${label} overview scale`);
        assert.equal(overview.sheet, null, `${label} no sheet on the overview`);
        assert.ok(overview.pageScroll <= 0, `${label} page-level horizontal scroll ${overview.pageScroll}`);
        checkLayout(overview, layout, `${label} overview`);
        checkSafeArea(overview, `${label} overview`);
        for (const [w, h] of overview.hits) assert.ok(w >= 44 && h >= 44, `${label} zone touch target ${w}x${h}`);
        // The 26px info button has a 44px touch area.
        const infoHit = await evaluate(page, `(() => { const r = document.querySelector(".roomInfoButton").getBoundingClientRect(); const cx = r.left + r.width / 2, cy = r.top + r.height / 2; return [[cx - 21, cy], [cx + 21, cy], [cx, cy - 21], [cx, cy + 21]].every(([x, y]) => document.elementFromPoint(x, y)?.closest(".roomInfoButton")); })()`);
        assert.ok(infoHit, `${label} info button touch area < 44px`);

        for (const key of Object.keys(layout.zones)) {
          // Tap: the camera zooms to x2 on the zone and the sheet opens below the room.
          await evaluate(page, `document.querySelector('.zoneHitWrap[data-zone="${key}"] .zoneHit').click()`);
          await waitFor(page, `Boolean(document.querySelector(".zoneSheet") && document.querySelector(".lightLayer")?.naturalWidth)`);
          await delay(500); // 300 ms camera transition
          const zoomed = await evaluate(page, MEASURE);
          assert.equal(zoomed.baseScale, 2, `${label} ${key} zoom scale`);
          checkLayout(zoomed, layout, `${label} ${key} zoomed`);
          const zl = layout.zones[key];
          near(zoomed.light.x, zl.light.x * 2, `${label} ${key} light x`);
          near(zoomed.dim.w, 480 * 2, `${label} ${key} dim w`);
          // The camera centres the zone's camera rect (clamped to the room edges).
          const [cx, , cw] = zl.camera;
          const centre = -zoomed.pan + zoomed.viewportW / 2;
          const wanted = Math.min(Math.max((cx + cw / 2) * 2, zoomed.viewportW / 2), 960 - zoomed.viewportW / 2);
          assert.ok(Math.abs(centre - wanted) <= 2, `${label} ${key} camera centre ${centre} vs ${wanted}`);
          assert.ok(zoomed.sheet.focused, `${label} ${key} focus moves into the sheet`);
          const smallTargets = await evaluate(page, `[...document.querySelectorAll(".zoneSheet button, .zoneSheet a")].filter((e) => e.offsetParent).map((e) => { const r = e.getBoundingClientRect(); return [e.textContent.trim().slice(0, 20), Math.round(r.width), Math.round(r.height)]; }).filter(([, w, h]) => w < 44 || h < 44)`);
          assert.deepEqual(smallTargets, [], `${label} ${key} sheet touch targets < 44px`);
          assert.ok(zoomed.sheet.bottom <= zoomed.sheet.height + 1, `${label} ${key} sheet off screen`);
          assert.ok(zoomed.pageScroll <= 0, `${label} ${key} page-level horizontal scroll`);

          // Back to room: the camera returns to the overview.
          await evaluate(page, `document.querySelector(".zoneSheet .closeButton").click()`);
          await waitFor(page, `!document.querySelector(".zoneSheet")`);
          await delay(500);
          const back = await evaluate(page, MEASURE);
          assert.equal(back.baseScale, 1, `${label} ${key} back scale`);
          assert.equal(back.pan, overview.pan, `${label} ${key} back pan x`);
          assert.equal(back.panY, overview.panY, `${label} ${key} back pan y`);
          checkLayout(back, layout, `${label} ${key} back`);
        }
        console.log(`${label}: overview x1, zoom x2 + sheet, back to room aligned`);
      }
    }

    page.close();
  } finally {
    chrome.kill();
    await delay(300);
    await rm(userDataDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
  }
}

run().then(
  () => console.log("Room alignment smoke test passed."),
  (error) => { console.error(error); process.exitCode = 1; },
);
