import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";

// B21 materialize, end to end: complete the Creative main step in the room -> Ringo Moment ->
// reward card open (the object is still a ghost, the card shows its pixel PNG) -> close ->
// light, resolve, settle, glint -> placed. A reload never plays it again.

const FRONTEND_BASE = process.env.FRONTEND_BASE_URL || "http://localhost:5173";
const API_BASE = process.env.VITE_API_BASE || "http://localhost:5005";
const CHROME_BIN = process.env.CHROME_BIN || "/usr/bin/google-chrome";
const DEBUG_PORT = Number(process.env.ROOM_MATERIALIZE_DEBUG_PORT || 9234);
const REWARD = "creativity_sketchbook";
const VIEWPORTS = [
  [1440, 900, "en"],
  [390, 844, "fa"],
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



async function api(path, token, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  return { status: response.status, data: await response.json().catch(() => null) };
}

// A user in the Creative path with its first challenge joined (no mission done yet).
async function createUser(tag) {
  const username = `${tag}${Date.now()}`.slice(0, 18);
  const register = await api("/auth/register", null, { username, password: "secret123", name: "Materialize Smoke", email: `${username}@example.com` });
  assert.equal(register.status, 201);
  const token = register.data.access_token;
  const me = await api("/me", token);
  const paths = await api("/paths", token);
  const creative = (paths.data.items || paths.data).find((path) => path.key === "creativity");
  assert.ok(creative, "creativity path");
  assert.equal((await api(`/paths/${creative.path_id}/start`, token, {})).status, 200);
  const challenges = await api(`/paths/${creative.path_id}/challenges`, token);
  const challenge = challenges.data.items[0];
  assert.equal((await api(`/challenges/${challenge.challenge_id}/join`, token, {})).status, 200);
  return { token, id: register.data.user_id ?? me.data.user_id };
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


// Room state for the reward: ghost (with its phase class), colour layer, glint, placed.
const ROOM = `(() => {
  const ghost = document.querySelector('.ghostLayer[data-reward="${REWARD}"]');
  return {
    ghost: Boolean(ghost),
    phase: document.querySelector('[data-reward="${REWARD}"][class*="mat-"]')?.className.match(/mat-(\\w+)/)?.[1] || "",
    lightRise: Boolean(document.querySelector(".lightLayer.lightRise")),
    glint: Boolean(document.querySelector(".glintLayer")),
    placed: [...document.querySelectorAll(".sceneBase img.layer:not(.ghostLayer):not(.matColor)")].some((img) => img.src.includes("${REWARD}")),
    card: Boolean(document.querySelector(".unlockPanel")),
  };
})()`;

// Clicks the Ringo Moment's primary button (Continue / Finish), whatever the language.
const NEXT_STEP = `(() => {
  const skip = document.querySelector(".skipButton");
  let box = skip?.parentElement;
  while (box && box.querySelectorAll("button").length < 2) box = box.parentElement;
  const button = box ? [...box.querySelectorAll("button")].find((item) => item !== skip && item.offsetParent) : null;
  button?.click();
  return Boolean(button);
})()`;

// B10: FA copy shows Persian digits only (no 0-9) in these surfaces.
const TEXT_OF = (selector) => `(() => { const el = ${selector}; return el ? el.innerText : null; })()`;
const MOMENT = `(() => { const skip = document.querySelector(".skipButton"); let box = skip?.parentElement; while (box && !box.querySelector("h2, h3, strong, p")) box = box.parentElement; return box?.parentElement || null; })()`;
async function assertNoLatinDigits(page, label, what, selector) {
  const text = await evaluate(page, TEXT_OF(selector));
  assert.ok(text, `${label} ${what} not found`);
  assert.doesNotMatch(text, /[0-9]/, `${label} ${what} shows Latin digits in FA: ${JSON.stringify(text.match(/.{0,20}[0-9].{0,20}/)?.[0])}`);
}

async function runViewport(page, [width, height, locale]) {
  const label = `${width}x${height} ${locale}`;
  const user = await createUser("mat");
  await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
  await page.send("Page.navigate", { url: `${FRONTEND_BASE}/dashboard?smoke=${Date.now()}` });
  await delay(200);
  await evaluate(page, `localStorage.setItem("ringo_token", ${JSON.stringify(user.token)});
    localStorage.setItem("ringostrike_locale", "${locale}");
    localStorage.setItem(${JSON.stringify(`ringostrike_onboarding_done:user:${user.id}`)}, "1"); true`);
  await page.send("Page.navigate", { url: `${FRONTEND_BASE}/dashboard` });
  await waitFor(page, `Boolean(document.querySelector('.ghostLayer[data-reward="${REWARD}"]'))`);
  await delay(800);

  if (locale === "fa") await assertNoLatinDigits(page, label, "room overview", `document.querySelector(".roomPanel")`);

  // Open Creative and complete today's main step from the room.
  await evaluate(page, `document.querySelector('.zoneHitWrap[data-zone="creative_corner"] .zoneHit').click()`);
  await waitFor(page, `Boolean([...document.querySelectorAll(".roomSafeZone button.primaryAction")].find((b) => b.offsetParent))`);
  if (locale === "fa") await assertNoLatinDigits(page, label, "zone panel", `document.querySelector(".roomSafeZone .zonePanel")`);
  await evaluate(page, `[...document.querySelectorAll(".roomSafeZone button.primaryAction")].find((b) => b.offsetParent).click()`);

  // Ringo Moment, then the reward card. The object stays a ghost behind both.
  let steps = 0;
  for (let i = 0; i < 40 && !(await evaluate(page, ROOM)).card; i += 1) {
    const room = await evaluate(page, ROOM);
    assert.ok(room.ghost && !room.placed && !room.phase, `${label} the object changed behind the Ringo Moment: ${JSON.stringify(room)}`);
    if (locale === "fa" && await evaluate(page, `Boolean(document.querySelector(".skipButton"))`)) await assertNoLatinDigits(page, label, "Ringo Moment", MOMENT);
    if (await evaluate(page, NEXT_STEP)) steps += 1;
    await delay(400);
  }
  assert.ok((await evaluate(page, ROOM)).card, `${label} reward card did not open (${steps} Ringo Moment steps)`);
  await delay(1200);
  const behindCard = await evaluate(page, ROOM);
  assert.deepEqual(
    { ghost: behindCard.ghost, placed: behindCard.placed, phase: behindCard.phase },
    { ghost: true, placed: false, phase: "" },
    `${label} object must stay a ghost while the card is open`,
  );

  if (locale === "fa") await assertNoLatinDigits(page, label, "reward card", `document.querySelector(".unlockPanel")`);

  // The card shows the object's pixel PNG at an integer scale (not the letter placeholder).
  const icon = await evaluate(page, `(() => { const img = document.querySelector(".objectPixel img"); return img && img.complete ? { src: img.src, w: img.getBoundingClientRect().width, h: img.getBoundingClientRect().height, nw: img.naturalWidth, nh: img.naturalHeight, rendering: getComputedStyle(img).imageRendering } : null; })()`);
  assert.ok(icon && icon.src.includes(REWARD), `${label} card pixel PNG`);
  assert.ok(Number.isInteger(icon.w / icon.nw) && icon.w / icon.nw === icon.h / icon.nh && icon.w / icon.nw >= 1, `${label} integer icon scale ${icon.w}/${icon.nw}`);
  assert.equal(icon.rendering, "pixelated");

  // Close: the sequence plays in order, then the object is placed.
  await evaluate(page, `document.querySelector(".unlockPanel .continueButton").click()`);
  const phases = [];
  const started = Date.now();
  let glint = false;
  let lightRise = false;
  while (Date.now() - started < 5000) {
    const room = await evaluate(page, ROOM);
    if (room.phase && phases[phases.length - 1] !== room.phase) phases.push(room.phase);
    glint ||= room.glint;
    lightRise ||= room.lightRise;
    if (room.placed && !room.ghost && !room.phase) break;
    await delay(25);
  }
  assert.deepEqual(phases, ["camera", "light", "resolve", "settle", "glint"], `${label} phase order`);
  assert.ok(glint && lightRise, `${label} glint and light rise shown`);
  const placed = await evaluate(page, ROOM);
  assert.ok(placed.placed && !placed.ghost && !placed.phase, `${label} placed after the sequence: ${JSON.stringify(placed)}`);
  assert.equal((await api("/me/space", user.token)).data.has_unseen_rewards, false, `${label} reward marked seen`);

  // Reload: never again.
  await page.send("Page.navigate", { url: `${FRONTEND_BASE}/dashboard` });
  await waitFor(page, `Boolean(document.querySelector(".roomScene .zoneHitWrap"))`);
  const reloadStart = Date.now();
  while (Date.now() - reloadStart < 2500) {
    const room = await evaluate(page, ROOM);
    assert.ok(!room.phase && !room.glint, `${label} replayed after reload`);
    await delay(50);
  }
  const after = await evaluate(page, ROOM);
  assert.ok(after.placed && !after.ghost, `${label} still placed after reload`);
  console.log(`${label}: ghost behind card, ${phases.join(" > ")}, placed, no replay after reload`);
}

async function run() {
  await waitForJson(`${API_BASE}/health`);
  await waitForOk(`${FRONTEND_BASE}/`);

  const userDataDir = await mkdtemp(join(tmpdir(), "ringo-room-materialize-"));
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

    for (const viewport of VIEWPORTS) await runViewport(page, viewport);
    page.close();
  } finally {
    chrome.kill();
    await delay(300);
    await rm(userDataDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
  }
}

run().then(
  () => console.log("Room materialize smoke test passed."),
  (error) => { console.error(error); process.exitCode = 1; },
);
