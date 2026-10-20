import assert from "node:assert/strict";
import { execFileSync, spawn } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

// B27 (#384): split mission action. Drives the real UI and records every POST /done body:
// Flow A with answers, Flow A cancel (no write), Flow A "save without answers", Flow B with an
// exact time, Flow B with no answers. Each completing flow creates exactly one counted check-in
// with the right context, and a double click never submits twice. 1366x768 EN and 390x844 FA.
// With MISSION_ACTION_DB_PATH (the test backend's SQLite file) the stored rows are checked too.

const FRONTEND_BASE = process.env.FRONTEND_BASE_URL || "http://localhost:5173";
const API_BASE = process.env.VITE_API_BASE || "http://localhost:5005";
const CHROME_BIN = process.env.CHROME_BIN || "/usr/bin/google-chrome";
const DEBUG_PORT = Number(process.env.MISSION_ACTION_DEBUG_PORT || 9236);
const DB_PATH = process.env.MISSION_ACTION_DB_PATH || "";
const RUNS = [
  [1366, 768, "en"],
  [1920, 1080, "en"],
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



async function api(path, token, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  return { status: response.status, data: await response.json().catch(() => null) };
}


// A user in the Creative path with its first challenge joined; returns the main mission id.
async function createUser(tag) {
  const username = `${tag}${Date.now() % 1e9}`.slice(0, 18);
  // Sign-ups are rate limited (10 per minute per client); this test makes ~21 users, so wait and retry.
  let register = null;
  for (let attempt = 0; attempt < 15; attempt += 1) {
    register = await api("/auth/register", null, { username, password: "secret123", name: "Mission Action", email: `${username}@example.com` });
    if (register.status !== 429) break;
    await delay(6000);
  }
  assert.equal(register.status, 201);
  const token = register.data.access_token;
  const me = await api("/me", token);
  const paths = await api("/paths", token);
  const creative = (paths.data.items || paths.data).find((path) => path.key === "creativity");
  await api(`/paths/${creative.path_id}/start`, token, {});
  const challenges = await api(`/paths/${creative.path_id}/challenges`, token);
  await api(`/challenges/${challenges.data.items[0].challenge_id}/join`, token, {});
  const missions = (await api("/me/today-missions", token)).data.missions;
  const main = missions.find((mission) => mission.mission_intensity === "main");
  return { token, id: register.data.user_id ?? me.data.user_id, mainId: main.mission_id };
}

function dbRows(userId) {
  if (!DB_PATH) return null;
  const script = `
import json, sqlite3, sys
c = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True); c.row_factory = sqlite3.Row
logs = [dict(r) for r in c.execute("SELECT mission_id, status, performed_at, mode, place_key, place_label, feeling_key, notes, duration_seconds FROM mission_logs WHERE user_id = ?", (int(sys.argv[2]),))]
counted = c.execute("SELECT COUNT(*) FROM checkins WHERE user_id = ? AND status = 'Done' AND is_counted = 1", (int(sys.argv[2]),)).fetchone()[0]
print(json.dumps({"logs": logs, "counted": counted}))`;
  return JSON.parse(execFileSync("python3", ["-c", script, DB_PATH, String(userId)], { encoding: "utf8" }));
}

// Clicks the first visible, enabled element matching a selector (and text, if given).
const CLICK = (selector, text = "") => `(() => {
  const el = [...document.querySelectorAll(${JSON.stringify(selector)})].find((e) => e.offsetParent && !e.disabled && (!${JSON.stringify(text)} || e.innerText.trim().includes(${JSON.stringify(text)})));
  el?.click();
  return Boolean(el);
})()`;

const SET_VALUE = (selector, value) => `(() => {
  const el = document.querySelector(${JSON.stringify(selector)});
  if (!el) return false;
  el.value = ${JSON.stringify(value)};
  el.dispatchEvent(new Event("input", { bubbles: true }));
  return true;
})()`;

// The save area (Save, the quiet button if any, and the caption) is fully visible inside the panel
// or sheet and the viewport, without scrolling the page. Desktop: the page does not scroll at all.
async function assertSaveVisible(page, label, width) {
  const m = await evaluate(page, `(() => {
    const flow = document.querySelector(".missionFlow");
    const panel = flow.closest(".roomSafeZone");
    const actions = flow.querySelector(".flowActions");
    const parts = [...actions.querySelectorAll("button, .flowFooter")].map((el) => el.getBoundingClientRect());
    const p = panel.getBoundingClientRect();
    return {
      top: Math.min(...parts.map((r) => r.top)), bottom: Math.max(...parts.map((r) => r.bottom)),
      panelTop: p.top, panelBottom: p.bottom, vh: innerHeight, scrollY,
      pageOverflow: document.documentElement.scrollHeight - innerHeight,
    };
  })()`);
  assert.ok(m.top >= m.panelTop - 0.5 && m.bottom <= m.panelBottom + 0.5, `${label} save area outside the panel: ${JSON.stringify(m)}`);
  assert.ok(m.top >= 0 && m.bottom <= m.vh + 0.5, `${label} save area outside the viewport: ${JSON.stringify(m)}`);
  assert.equal(m.scrollY, 0, `${label} page scrolled`);
  if (width >= 600) assert.ok(m.pageOverflow <= 0, `${label} page scrolls by ${m.pageOverflow}px`);
}

async function click(page, selector, text, label) {
  let ok = false;
  const started = Date.now();
  while (!ok && Date.now() - started < 10000) {
    ok = await evaluate(page, CLICK(selector, text));
    if (!ok) await delay(150);
  }
  if (!ok) {
    const seen = await evaluate(page, `[...document.querySelectorAll(${JSON.stringify(selector)})].map((e) => ({ text: e.innerText.trim().slice(0, 20), visible: Boolean(e.offsetParent), disabled: e.disabled }))`);
    const shot = await page.send("Page.captureScreenshot", { format: "jpeg", quality: 60 });
    const { writeFileSync } = await import("node:fs");
    writeFileSync(join(tmpdir(), "mission-action-failure.jpg"), Buffer.from(shot.data, "base64"));
    const mounts = await evaluate(page, `JSON.stringify(window.__mounts || []) + " url=" + location.pathname + " t=" + Math.round(performance.now())`);
    assert.fail(`could not click ${label || selector} ${text}: ${JSON.stringify(seen)} mounts=${mounts} (screenshot in ${join(tmpdir(), "mission-action-failure.jpg")})`);
  }
  await delay(250);
}

// Navigates and waits for the new document (the old page is marked stale first), so nothing is
// read from or clicked in the previous page while the new one is still loading.
async function navigate(page, url) {
  await evaluate(page, `window.__staleDocument = true`).catch(() => {});
  await page.send("Page.navigate", { url });
  await waitFor(page, `!window.__staleDocument && document.readyState !== "loading"`);
}

async function openZone(page, user, locale, width, height) {
  await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
  // The auth guard sends the page to /login when /me fails (e.g. a slow dev backend right after
  // the previous test); retry that once, then report what the page shows.
  for (let attempt = 1; ; attempt += 1) {
    await navigate(page, `${FRONTEND_BASE}/login`);
    await evaluate(page, `localStorage.clear(); sessionStorage.clear();
      localStorage.setItem("ringo_token", ${JSON.stringify(user.token)});
      localStorage.setItem("ringostrike_locale", "${locale}");
      localStorage.setItem(${JSON.stringify(`ringostrike_onboarding_done:user:${user.id}`)}, "1"); true`);
    await navigate(page, `${FRONTEND_BASE}/dashboard`);
    try {
      await waitFor(page, `Boolean(document.querySelector('.zoneHitWrap[data-zone="creative_corner"] .zoneHit'))`, 30000);
      break;
    } catch (error) {
      const where = await evaluate(page, `(async () => { const token = localStorage.getItem("ringo_token"); let me = ""; try { const r = await fetch(${JSON.stringify(API_BASE)} + "/me", { headers: { Authorization: "Bearer " + token } }); me = r.status + " " + (await r.text()).slice(0, 120); } catch (e) { me = "fetch error " + e.message; } return location.pathname + " | token=" + (token ? "set" : "none") + " | /me " + me; })()`);
      if (attempt < 2) {
        console.warn(`openZone retry (${where})`);
        continue;
      }
      const shot = await page.send("Page.captureScreenshot", { format: "jpeg", quality: 60 });
      const { writeFileSync } = await import("node:fs");
      writeFileSync(join(tmpdir(), "mission-action-failure.jpg"), Buffer.from(shot.data, "base64"));
      throw new Error(`${error.message} at ${where}`);
    }
  }
  await evaluate(page, `(() => { window.__mounts = []; const mark = () => { for (const sel of [".livingSpace", ".zonePanel", ".missionFlow"]) { const el = document.querySelector(sel); if (el && !el.__seen) { el.__seen = true; window.__mounts.push(sel + "@" + Math.round(performance.now())); } } }; mark(); new MutationObserver(mark).observe(document.body, { childList: true, subtree: true }); return true; })()`);
  await delay(600);
  await evaluate(page, `document.querySelector('.zoneHitWrap[data-zone="creative_corner"] .zoneHit').click(); true`);
  await waitFor(page, `Boolean([...document.querySelectorAll(".splitAction .splitPrimary")].find((b) => b.offsetParent && !b.disabled))`);
}

async function waitForSaved(page, posts, count, label) {
  const started = Date.now();
  while (posts.length < count && Date.now() - started < 10000) await delay(100);
  await delay(400); // a second request from a double click would land here
  assert.equal(posts.length, count, `${label} done requests`);
  await waitFor(page, `!document.querySelector(".missionFlow")`, 10000);
  await delay(700);
}

function checkStored(user, expected, label) {
  const rows = dbRows(user.id);
  if (!rows) return;
  assert.equal(rows.counted, 1, `${label} counted check-ins`);
  const log = rows.logs.find((row) => row.mission_id === user.mainId);
  assert.ok(log && log.status === "done", `${label} main mission done`);
  for (const [key, value] of Object.entries(expected)) assert.equal(log[key], value, `${label} stored ${key}`);
}

async function runViewport(page, posts, [width, height, locale]) {
  const label = `${width}x${height} ${locale}`;
  const fa = locale === "fa";

  // The bar: two real buttons in a group; the primary is on the inline-start side.
  {
    const user = await createUser("maBar");
    await openZone(page, user, locale, width, height);
    const bar = await evaluate(page, `(() => {
      const group = document.querySelector(".splitAction");
      const [primary, secondary] = [...group.querySelectorAll("button")];
      const p = primary.getBoundingClientRect(); const s = secondary.getBoundingClientRect();
      return { role: group.getAttribute("role"), label: group.getAttribute("aria-label"), primaryAria: primary.getAttribute("aria-label"), secondaryAria: secondary.getAttribute("aria-label"), pLeft: p.left, sLeft: s.left, pw: p.width, sw: s.width, h: Math.min(p.height, s.height), dir: document.documentElement.dir || "ltr" };
    })()`);
    assert.equal(bar.role, "group");
    assert.ok(bar.label && bar.primaryAria && bar.secondaryAria, `${label} aria labels`);
    assert.ok(bar.h >= 44, `${label} bar height ${bar.h}`);
    assert.ok(bar.pw > bar.sw * 1.5, `${label} primary about 2/3`);
    assert.equal(bar.dir === "rtl" ? bar.pLeft > bar.sLeft : bar.pLeft < bar.sLeft, true, `${label} primary on the inline-start side`);

    // Flow A cancel: nothing is written and the timer is cleared.
    const beforeCancel = posts.length;
    await click(page, ".splitPrimary", "", "do it now");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow .flowTimer"))`);
    assert.ok(await evaluate(page, `Object.keys(sessionStorage).some((k) => k.startsWith("ringostrike_focus_start:"))`), `${label} timer start stored`);
    await delay(1200);
    await click(page, ".missionFlow .flowQuiet", "", "cancel");
    await waitFor(page, `!document.querySelector(".missionFlow")`);
    await delay(500);
    assert.equal(posts.length, beforeCancel, `${label} cancel wrote nothing`);
    assert.ok(!(await evaluate(page, `Object.keys(sessionStorage).some((k) => k.startsWith("ringostrike_focus_start:"))`)), `${label} timer cleared`);
    const status = (await api("/me/today-missions", user.token)).data.missions.find((m) => m.mission_id === user.mainId).status;
    assert.equal(status, "pending", `${label} mission still pending after cancel`);
  }

  // Flow A with answers (and a double click on Save: one request only).
  {
    const user = await createUser("maNow");
    await openZone(page, user, locale, width, height);
    await click(page, ".splitPrimary", "", "do it now");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow .flowTimer"))`);
    await delay(2200);
    await evaluate(page, SET_VALUE(".missionFlow textarea", "focus note b27"));
    await click(page, ".missionFlow .flowPrimary", "", "done");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow .flowPill"))`);
    await assertSaveVisible(page, `${label} flow A check-out`, width);
    await click(page, ".missionFlow .flowChip", fa ? "باشگاه" : "Gym", "place");
    await click(page, ".missionFlow .flowChip", fa ? "سخت ولی" : "Hard but done", "feeling");
    const beforeA = posts.length;
    await evaluate(page, `(() => { const b = document.querySelector(".missionFlow .flowPrimary"); b.click(); b.click(); return true; })()`);
    await waitForSaved(page, posts, beforeA + 1, `${label} flow A`);
    const sent = posts.slice(beforeA);
    assert.equal(sent.length, 1, `${label} flow A: no double submit`);
    const body = JSON.parse(sent[0].body || "{}");
    assert.equal(body.mode, "now");
    assert.ok(body.duration_seconds >= 2 && body.duration_seconds <= 30, `${label} duration ${body.duration_seconds}`);
    assert.deepEqual({ place: body.place_key, feeling: body.feeling_key, note: body.note }, { place: "gym", feeling: "hard_but_done", note: "focus note b27" });
    assert.ok(await waitFor(page, `Boolean(document.querySelector(".skipButton"))`, 10000) !== false);
    checkStored(user, { mode: "now", place_key: "gym", feeling_key: "hard_but_done", notes: "focus note b27", duration_seconds: body.duration_seconds }, `${label} flow A`);
  }

  // Flow A "save without answers": only mode and duration.
  {
    const user = await createUser("maBare");
    await openZone(page, user, locale, width, height);
    await click(page, ".splitPrimary", "", "do it now");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow .flowTimer"))`);
    await delay(1100);
    await click(page, ".missionFlow .flowPrimary", "", "done");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow .flowPill"))`);
    await click(page, ".missionFlow .flowChip", fa ? "خونه" : "Home", "place (ignored)");
    await assertSaveVisible(page, `${label} flow A check-out (bare)`, width);
    const beforeBare = posts.length;
    await click(page, ".missionFlow .flowQuiet", "", "save without answers");
    await waitForSaved(page, posts, beforeBare + 1, `${label} flow A bare`);
    const body = JSON.parse(posts[beforeBare].body || "{}");
    assert.deepEqual(Object.keys(body).sort(), ["duration_seconds", "mode"], `${label} save without answers sends only mode and duration`);
    checkStored(user, { mode: "now", place_key: null, feeling_key: null, notes: null }, `${label} flow A bare`);
  }

  // Flow B with an exact time inside the server's window.
  {
    const user = await createUser("maExact");
    await openZone(page, user, locale, width, height);
    await click(page, ".splitSecondary", "", "already did it");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow fieldset .flowChip"))`);
    await assertSaveVisible(page, `${label} flow B`, width);
    await waitFor(page, `(() => { const chips = [...document.querySelectorAll(".missionFlow fieldset:first-of-type .flowChip")]; return chips.length === 5 && !chips[4].disabled; })()`, 8000);
    await evaluate(page, `[...document.querySelectorAll(".missionFlow fieldset:first-of-type .flowChip")][4].click(); true`);
    await waitFor(page, `Boolean(document.querySelector('.missionFlow input[type="time"]'))`);
    // One minute ago in local time, unless that crosses the server's day start (then now).
    const local = await evaluate(page, `(() => { const d = new Date(Date.now() - 60000); const start = new Date(); return (d.getUTCDate() === start.getUTCDate() ? d : start).toTimeString().slice(0, 5); })()`);
    await evaluate(page, SET_VALUE('.missionFlow input[type="time"]', local));
    await click(page, ".missionFlow .flowChip", fa ? "بیرون" : "Outside", "place");
    await assertSaveVisible(page, `${label} flow B with exact time and a place`, width);
    const beforeExact = posts.length;
    await click(page, ".missionFlow .flowPrimary", "", "save");
    await waitForSaved(page, posts, beforeExact + 1, `${label} flow B exact`);
    const body = JSON.parse(posts[beforeExact].body || "{}");
    assert.equal(body.mode, "earlier");
    assert.equal(body.place_key, "outside");
    assert.ok(body.performed_at, `${label} performed_at sent`);
    const expected = await evaluate(page, `(() => { const [h, m] = ${JSON.stringify(local)}.split(":").map(Number); const d = new Date(); d.setHours(h, m, 0, 0); return d.toISOString().replace(/\\.\\d{3}Z$/, "Z"); })()`);
    assert.equal(body.performed_at, expected, `${label} exact time as ISO UTC`);
    assert.equal(body.duration_seconds, undefined);
    checkStored(user, { mode: "earlier", performed_at: expected, place_key: "outside" }, `${label} flow B exact`);
  }

  // Flow B with no answers (the remembered place would be preselected: clear it first).
  {
    const user = await createUser("maNone");
    await openZone(page, user, locale, width, height);
    await click(page, ".splitSecondary", "", "already did it");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow .flowPrimary"))`);
    await evaluate(page, `[...document.querySelectorAll(".missionFlow .flowChip.selected")].forEach((chip) => chip.click()); true`);
    const beforeNone = posts.length;
    await click(page, ".missionFlow .flowPrimary", "", "save");
    await waitForSaved(page, posts, beforeNone + 1, `${label} flow B none`);
    const body = JSON.parse(posts[beforeNone].body || "{}");
    assert.deepEqual(body, { mode: "earlier" }, `${label} flow B with no answers`);
    checkStored(user, { mode: "earlier", performed_at: null, place_key: null, feeling_key: null }, `${label} flow B none`);

    // Done for today: the bar is a non-interactive status.
    await navigate(page, `${FRONTEND_BASE}/dashboard`);
    await waitFor(page, `Boolean(document.querySelector('.zoneHitWrap[data-zone="creative_corner"] .zoneHit'))`);
    await delay(600);
    await evaluate(page, `document.querySelector('.zoneHitWrap[data-zone="creative_corner"] .zoneHit').click(); true`);
    await waitFor(page, `Boolean(document.querySelector(".doneStatus"))`, 8000);
    assert.equal(await evaluate(page, `document.querySelectorAll(".splitAction").length`), 0, `${label} no split bar once done`);
  }

  // A 400 from the API keeps the answers and shows a calm inline error; a retry then saves.
  {
    const user = await createUser("maErr");
    await openZone(page, user, locale, width, height);
    await click(page, ".splitSecondary", "", "already did it");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow .flowPrimary"))`);
    await evaluate(page, `[...document.querySelectorAll(".missionFlow .flowChip.selected")].forEach((chip) => chip.click()); true`);
    await click(page, ".missionFlow .flowChip", fa ? "کافه" : "Café", "place");
    await evaluate(page, SET_VALUE(".missionFlow textarea", "keep me"));
    page.failNextDone = true;
    await click(page, ".missionFlow .flowPrimary", "", "save (fails)");
    await waitFor(page, `Boolean(document.querySelector(".missionFlow .flowError"))`, 8000);
    const kept = await evaluate(page, `({ place: document.querySelector(".missionFlow .flowChip.selected")?.innerText.trim() || "", note: document.querySelector(".missionFlow textarea").value, saving: document.querySelector(".missionFlow .flowPrimary").disabled })`);
    assert.deepEqual(kept, { place: fa ? "کافه" : "Café", note: "keep me", saving: false }, `${label} answers kept after a 400`);
    assert.equal((await api("/me/today-missions", user.token)).data.missions.find((m) => m.mission_id === user.mainId).status, "pending");
    const beforeRetry = posts.length;
    await click(page, ".missionFlow .flowPrimary", "", "save (retry)");
    await waitForSaved(page, posts, beforeRetry + 1, `${label} retry after 400`);
    checkStored(user, { mode: "earlier", place_key: "cafe", notes: "keep me" }, `${label} retry after 400`);
  }

  console.log(`${label}: bar, cancel, flow A (answers, bare), flow B (exact, none), 400 keeps answers, done status OK`);
}

async function run() {
  await waitForJson(`${API_BASE}/health`);
  await waitForOk(`${FRONTEND_BASE}/`);
  const userDataDir = await mkdtemp(join(tmpdir(), "ringo-mission-action-"));
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
    await page.send("Network.enable");
    const posts = [];
    // Test-only: fail the next POST /done with a 400 (page.failNextDone), to check the inline error.
    await page.send("Fetch.enable", { patterns: [{ urlPattern: "*/me/missions/*/done", requestStage: "Request" }] });
    page.on("Fetch.requestPaused", async (params) => {
      if (page.failNextDone) {
        page.failNextDone = false;
        const body = Buffer.from(JSON.stringify({ ok: false, error: "invalid_place_key" })).toString("base64");
        await page.send("Fetch.fulfillRequest", {
          requestId: params.requestId,
          responseCode: 400,
          responseHeaders: [{ name: "Content-Type", value: "application/json" }, { name: "Access-Control-Allow-Origin", value: new URL(FRONTEND_BASE).origin }, { name: "Access-Control-Allow-Credentials", value: "true" }],
          body,
        });
        return;
      }
      await page.send("Fetch.continueRequest", { requestId: params.requestId });
    });
    page.on("Network.requestWillBeSent", (params) => {
      const request = params.request || {};
      if (request.method === "POST" && /\/me\/missions\/\d+\/done/.test(request.url)) posts.push({ url: request.url, body: request.postData || "" });
    });
    for (const runConfig of RUNS) await runViewport(page, posts, runConfig);
    page.close();
  } finally {
    chrome.kill();
    await delay(300);
    await rm(userDataDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
  }
}

run().then(
  () => console.log("Mission action smoke test passed."),
  (error) => { console.error(error); process.exitCode = 1; },
);
