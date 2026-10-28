import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";

// B11: a new user reaches the first room object unaided, through the real UI:
// register -> onboarding (welcome, corner, challenge) -> the room with the first mission -> Ringo
// Moment -> reward card -> object placed. Desktop EN at 1366x768 and phone FA at 390x844.
// B37 (D78 to D82): three short choices, a corner picked on the real room, no handoff screen.

const FRONTEND_BASE = process.env.FRONTEND_BASE_URL || "http://localhost:5173";
const API_BASE = process.env.VITE_API_BASE || "http://localhost:5005";
const CHROME_BIN = process.env.CHROME_BIN || "/usr/bin/google-chrome";
const DEBUG_PORT = Number(process.env.FIRST_RUN_DEBUG_PORT || 9235);
const RUNS = [
  [1366, 768, "en"],
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



// Clicks the visible button whose text matches, inside the topmost overlay when one is open.
const CLICK = (pattern) => `(() => {
  const z = (e) => Number(getComputedStyle(e).zIndex) || 0;
  const overlays = [...document.querySelectorAll(".unlockOverlay, .rewardOverlay")].filter((e) => e.querySelector("button"));
  const scope = overlays.sort((a, b) => z(b) - z(a))[0] || document;
  const re = new RegExp(${JSON.stringify("PATTERN")});
  const button = [...scope.querySelectorAll("button")].find((b) => b.offsetParent && !b.disabled && re.test(b.innerText.trim()));
  button?.click();
  return button ? button.innerText.trim().replace(/\\s+/g, " ").slice(0, 40) : null;
})()`.replace("PATTERN", pattern.replace(/\\/g, "\\\\").replace(/"/g, '\\"'));

async function step(page, pattern, label, ctx) {
  let clicked = null;
  const started = Date.now();
  while (!clicked && Date.now() - started < 15000) {
    clicked = await evaluate(page, CLICK(pattern));
    if (!clicked) await delay(200);
  }
  assert.ok(clicked, `${ctx.label} could not find "${label}" (${pattern})`);
  ctx.clicks += 1;
  await delay(700);
  return clicked;
}

async function runFirstRun(page, [width, height, locale]) {
  const ctx = { label: `${width}x${height} ${locale}`, clicks: 0 };
  const fa = locale === "fa";
  await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
  await page.send("Page.navigate", { url: `${FRONTEND_BASE}/login` });
  await delay(400);
  await evaluate(page, `localStorage.clear(); localStorage.setItem("ringostrike_locale", "${locale}"); true`);
  await page.send("Page.navigate", { url: `${FRONTEND_BASE}/login` });
  await waitFor(page, `Boolean(document.querySelector("form input"))`);
  const started = Date.now();

  // Register through the form.
  await step(page, fa ? "^(ثبت نام|ثبت‌نام)$" : "^Register$", "switch to register", ctx);
  const username = `fr${Date.now() % 1e9}`;
  await evaluate(page, `(() => {
    const set = (input, value) => { input.value = value; input.dispatchEvent(new Event("input", { bubbles: true })); };
    const inputs = [...document.querySelectorAll("form input")];
    set(inputs[0], "${username}"); set(inputs[1], "secret123");
    return inputs.length;
  })()`);
  await evaluate(page, `document.querySelector("form button[type=submit]").click()`);
  ctx.clicks += 1;
  await waitFor(page, `location.pathname === "/onboarding"`);

  // Welcome, then the corner step: the real room with five markers and five chips; Continue waits
  // for a corner.
  await step(page, fa ? "^شروع با رینگو$" : "^Start with Ringo$", "start", ctx);
  await waitFor(page, `document.querySelectorAll(".roomPicture .cornerMarker").length === 5`);
  const corner = await evaluate(page, `(() => {
    const cont = [...document.querySelectorAll(".cornerStep .actions button")][0];
    return { chips: document.querySelectorAll(".cornerChip").length, disabled: cont?.disabled, backendSleep: /\bSleep\b(?! Corner)/.test(document.querySelector(".cornerStep").innerText) };
  })()`);
  assert.equal(corner.chips, 5, `${ctx.label} five corner chips`);
  assert.equal(corner.disabled, true, `${ctx.label} Continue before a corner is picked`);
  if (!fa) assert.equal(corner.backendSleep, false, `${ctx.label} backend "Sleep" shown`);
  // Pick Creativity on the room itself, then see it "After a few steps".
  await evaluate(page, `document.querySelector('.cornerMarker[data-zone="creative_corner"]').click(); true`);
  ctx.clicks += 1;
  await waitFor(page, `document.querySelector('.cornerChip[data-path="creativity"]')?.getAttribute("aria-pressed") === "true"`);
  await evaluate(page, `document.querySelector('.switchButton[data-switch="after"]').click(); true`);
  ctx.clicks += 1;
  await waitFor(page, `[...document.querySelectorAll(".roomPicture img")].some((img) => img.src.includes("creativity_"))`, 5000);
  const cont = await evaluate(page, `(() => { const b = document.querySelector(".cornerStep .actions button"); const r = b.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, h: innerHeight, disabled: b.disabled }; })()`);
  assert.ok(!cont.disabled && cont.top >= 0 && cont.bottom <= cont.h + 1, `${ctx.label} Continue not in view: ${JSON.stringify(cont)}`);
  await step(page, fa ? "^ادامه" : "^Continue", "continue", ctx);

  // First challenge: up to three cards; "Start this challenge" in view without scrolling.
  await waitFor(page, `document.querySelectorAll(".challengeOption").length > 0`);
  const start = await evaluate(page, `(() => { const b = document.querySelector(".suggestionStep .actions button"); const r = b.getBoundingClientRect(); return { cards: document.querySelectorAll(".challengeOption").length, bottom: r.bottom, h: innerHeight }; })()`);
  assert.ok(start.cards >= 1 && start.cards <= 3, `${ctx.label} challenge cards: ${start.cards}`);
  assert.ok(start.bottom <= start.h + 1, `${ctx.label} Start this challenge not in view: ${JSON.stringify(start)}`);
  await step(page, fa ? "^شروع این چالش$" : "^Start this challenge$", "start challenge", ctx);
  // Straight into the room (no handoff screen, D78).
  await waitFor(page, `location.pathname === "/dashboard" && Boolean(document.querySelector(".roomScene .zoneHitWrap"))`);
  assert.doesNotMatch(await evaluate(page, `document.body.innerText`), /Go to my first mission|رفتن به اولین مأموریت من/, `${ctx.label} handoff still shown`);

  // The first mission is on screen right away: desktop panel, phone sheet (F1).
  await waitFor(page, `Boolean([...document.querySelectorAll(".roomSafeZone .splitAction button")].find((b) => b.offsetParent))`);
  if (width < 600) assert.ok(await evaluate(page, `Boolean(document.querySelector(".zoneSheet"))`), `${ctx.label} phone did not open the mission sheet`);
  // Today counts agree between the zone strip and the room overview (F5): 0 of 2.
  // The room lands right after the join now (no handoff screen), so wait for today's missions.
  await waitFor(page, `/[0-9۰-۹]+\\s*(\\/|از)\\s*[0-9۰-۹]+/.test(document.querySelector(".todayStrip strong")?.innerText || "")`, 10000).catch(() => {});
  const strip = await evaluate(page, `document.querySelector(".zoneTodayStrip, .todayStrip")?.innerText || document.querySelector(".roomSafeZone").innerText`);
  assert.match(strip, fa ? /۰ از ۲/ : /0\/2/, `${ctx.label} zone strip count`);

  // B27: the main mission's action is the split bar; "Already did it" then Save (no answers).
  await step(page, fa ? "^قبلاً انجام دادم$" : "^Already did it$", "already did it", ctx);
  await step(page, fa ? "^ثبت$" : "^Save$", "save", ctx);
  for (let i = 0; i < 12 && !(await evaluate(page, `Boolean(document.querySelector(".unlockPanel"))`)); i += 1) {
    await step(page, fa ? "^(ادامه|برای امروز کافیه)$" : "^(Continue|Enough for today)$", "Ringo Moment", ctx);
  }
  assert.ok(await evaluate(page, `Boolean(document.querySelector(".unlockPanel"))`), `${ctx.label} reward card`);
  await step(page, fa ? "^دیدنش توی اتاق$" : "^See it in the room$", "see it in the room", ctx);
  await waitFor(page, `[...document.querySelectorAll(".sceneBase img.layer:not(.ghostLayer):not(.matColor)")].some((img) => img.src.includes("creativity_sketchbook"))`, 8000);
  const seconds = Math.round((Date.now() - started) / 1000);
  if (width >= 600) {
    await evaluate(page, `document.querySelector(".zonePanel .closeButton")?.click(); true`);
    await delay(900);
    const overview = await evaluate(page, `document.querySelector(".roomPanel .summaryGrid strong")?.innerText || ""`);
    assert.equal(overview, "1/2", `${ctx.label} room overview count after the first mission`);
  }
  console.log(`${ctx.label}: first object placed, ${ctx.clicks} clicks (+2 typed fields), ${seconds}s automated`);
}

async function run() {
  await waitForJson(`${API_BASE}/health`);
  await waitForOk(`${FRONTEND_BASE}/`);
  const userDataDir = await mkdtemp(join(tmpdir(), "ringo-first-run-"));
  const chrome = spawn(CHROME_BIN, ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", `--remote-debugging-port=${DEBUG_PORT}`, `--user-data-dir=${userDataDir}`, "about:blank"]);
  try {
    chrome.stderr.on("data", () => {});
    chrome.stdout.on("data", () => {});
    await waitForJson(`http://127.0.0.1:${DEBUG_PORT}/json/version`);
    const target = await fetch(`http://127.0.0.1:${DEBUG_PORT}/json/new?about:blank`, { method: "PUT" }).then((r) => r.json());
    const page = createCdpClient(target.webSocketDebuggerUrl);
    await page.waitForOpen();
    await page.send("Runtime.enable");
    await page.send("Page.enable");
    for (const runConfig of RUNS) await runFirstRun(page, runConfig);
    page.close();
  } finally {
    chrome.kill();
    await delay(300);
    await rm(userDataDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
  }
}

run().then(
  () => console.log("First run smoke test passed."),
  (error) => { console.error(error); process.exitCode = 1; },
);
