import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";
import { footprintBox } from "../src/lib/roomScene.js";

// Room alignment at integer and fractional scales (hybrid rule): the pixel layers, zone hit
// regions, focus polygons, labels, dim/light layers and camera pan must all use one scale.

const FRONTEND_BASE = process.env.FRONTEND_BASE_URL || "http://localhost:5173";
const API_BASE = process.env.VITE_API_BASE || "http://localhost:5005";
const CHROME_BIN = process.env.CHROME_BIN || "/usr/bin/google-chrome";
const DEBUG_PORT = Number(process.env.ROOM_ALIGNMENT_DEBUG_PORT || 9233);
const TOLERANCE = 0.75; // screen px (sub-pixel layout rounding)

// [width, height, expected kind]: 1920x940 has fit ~2.93 -> fractional; the others are integer.
const VIEWPORTS = [
  [1920, 940, "fractional"],
  [1920, 1080, "integer"],
  [1440, 900, "integer"],
  [1366, 768, "integer-pan"],
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
  return {
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

function checkLayout(m, layout, label) {
  const s = m.baseScale;
  near(m.sceneW, 480 * s, `${label} scene width`);
  near(m.sceneH, 270 * s, `${label} scene height`);
  near(m.viewportH, 270 * s, `${label} viewport height`);
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
        localStorage.setItem("ringostrike_locale", "en");
        localStorage.setItem(${JSON.stringify(`ringostrike_onboarding_done:user:${user.id}`)}, "1");`,
    });

    for (const [width, height, kind] of VIEWPORTS) {
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
      checkLayout(overview, layout, `${label} overview`);

      // Select each zone: dim covers the scene, light sits at its base position, pan snaps to base px.
      for (const key of Object.keys(layout.zones)) {
        await evaluate(page, `document.querySelector('.zoneHitWrap[data-zone="${key}"] .zoneHit').click()`);
        await waitFor(page, `Boolean(document.querySelector(".lightLayer")?.complete && document.querySelector(".lightLayer").naturalWidth)`);
        await delay(450); // camera pan transition (300 ms)
        const selected = await evaluate(page, MEASURE);
        const zl = layout.zones[key];
        checkLayout(selected, layout, `${label} ${key}`);
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
      console.log(`${label}: x${s} aligned`);
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
