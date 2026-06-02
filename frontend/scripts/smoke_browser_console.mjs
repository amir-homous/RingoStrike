import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";

const FRONTEND_BASE = process.env.FRONTEND_BASE_URL || "http://localhost:5173";
const API_BASE = process.env.VITE_API_BASE || "http://localhost:5005";
const CHROME_BIN = process.env.CHROME_BIN || "/usr/bin/google-chrome";

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

async function createAuthFixture() {
  const username = `console${Date.now()}`;
  const password = "secret123";

  const registerResponse = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username,
      password,
      name: "Console Smoke User",
      email: `${username}@example.com`,
    }),
  });

  assert.equal(registerResponse.status, 201);
  const registerData = await registerResponse.json();
  const token = registerData.access_token;
  assert.ok(token);

  const authHeaders = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  const challengesResponse = await fetch(`${API_BASE}/challenges`, {
    headers: authHeaders,
  });
  assert.equal(challengesResponse.status, 200);
  const challengesData = await challengesResponse.json();
  const challenge = challengesData.items.find(
    (item) => item.visibility === "public" && !item.is_joined,
  );
  assert.ok(challenge, "Expected at least one public unjoined challenge");

  const joinResponse = await fetch(
    `${API_BASE}/challenges/${challenge.challenge_id}/join`,
    {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({}),
    },
  );
  assert.equal(joinResponse.status, 200);
  const joinData = await joinResponse.json();
  assert.ok(joinData.enrollment_id);

  return {
    token,
    username,
    enrollmentId: joinData.enrollment_id,
  };
}

function isIgnorableRequest(url) {
  return url.includes("/favicon.ico");
}

async function run() {
  await waitForJson(`${API_BASE}/health`);
  await waitForOk(`${FRONTEND_BASE}/`);

  const fixture = await createAuthFixture();
  const userDataDir = await mkdtemp(join(tmpdir(), "ringo-console-pass-"));
  const chrome = spawn(CHROME_BIN, [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--remote-debugging-port=9222",
    `--user-data-dir=${userDataDir}`,
    "about:blank",
  ]);

  try {
    chrome.stderr.on("data", () => {});
    chrome.stdout.on("data", () => {});

    const version = await waitForJson("http://127.0.0.1:9222/json/version");
    const browser = createCdpClient(version.webSocketDebuggerUrl);
    await browser.waitForOpen();

    const target = await fetch(`http://127.0.0.1:9222/json/new?about:blank`, {
      method: "PUT",
    }).then((response) => response.json());

    const page = createCdpClient(target.webSocketDebuggerUrl);
    await page.waitForOpen();

    await page.send("Runtime.enable");
    await page.send("Page.enable");
    await page.send("Network.enable");
    await page.send("Log.enable");
    await page.send("Page.addScriptToEvaluateOnNewDocument", {
      source: `window.localStorage.setItem("ringo_token", ${JSON.stringify(fixture.token)});`,
    });

    let routeIssues = [];

    page.on("Runtime.exceptionThrown", (params) => {
      routeIssues.push(`runtime exception: ${params.exceptionDetails?.text || "unknown"}`);
    });

    page.on("Runtime.consoleAPICalled", (params) => {
      if (params.type !== "error") return;

      const text = params.args
        .map((arg) => arg.value || arg.description || "")
        .filter(Boolean)
        .join(" ");

      routeIssues.push(`console error: ${text || params.type}`);
    });

    page.on("Log.entryAdded", (params) => {
      const entry = params.entry || {};
      if (entry.level !== "error") return;
      if (isIgnorableRequest(entry.url || "")) return;
      routeIssues.push(`log error: ${entry.text || entry.url || "unknown"}`);
    });

    page.on("Network.responseReceived", (params) => {
      const response = params.response || {};
      const url = response.url || "";

      if (isIgnorableRequest(url)) return;
      if (response.status >= 400) {
        routeIssues.push(`request ${response.status}: ${url}`);
      }
    });

    const routes = [
      "/dashboard",
      "/challenges",
      `/enrollment/${fixture.enrollmentId}`,
      `/enrollment/${fixture.enrollmentId}/leaderboard`,
      "/profile",
      `/u/${fixture.username}`,
    ];

    for (const route of routes) {
      routeIssues = [];
      await page.send("Page.navigate", { url: `${FRONTEND_BASE}${route}` });
      await delay(1800);

      if (routeIssues.length) {
        throw new Error(`${route} console pass failed:\n${routeIssues.join("\n")}`);
      }
    }

    page.close();
    browser.close();
  } finally {
    chrome.kill();
    await delay(300);
    await rm(userDataDir, {
      recursive: true,
      force: true,
      maxRetries: 3,
      retryDelay: 100,
    });
  }
}

run();
