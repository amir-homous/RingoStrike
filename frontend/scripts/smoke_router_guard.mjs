import assert from "node:assert/strict";

import { createAuthGuard } from "../src/router/authGuard.js";

function installMemoryWindow(initial = {}) {
  const store = new Map(Object.entries(initial));

  globalThis.window = {
    localStorage: {
      getItem(key) {
        return store.has(key) ? store.get(key) : null;
      },
      setItem(key, value) {
        store.set(key, String(value));
      },
    },
  };

  return store;
}

async function run() {
  delete globalThis.window;

  let calls = 0;
  const publicGuard = createAuthGuard({
    get: async () => {
      calls += 1;
      throw new Error("public routes should not call /me");
    },
  });

  assert.equal(
    await publicGuard({
      fullPath: "/login?next=/dashboard",
      meta: { requiresAuth: false },
    }),
    true,
  );
  assert.equal(calls, 0);

  const authenticatedGuard = createAuthGuard({
    get: async (path) => {
      assert.equal(path, "/me");
      return { data: { ok: true } };
    },
  });

  assert.equal(
    await authenticatedGuard({
      fullPath: "/dashboard",
      meta: { requiresAuth: true },
    }),
    true,
  );

  const unauthenticatedGuard = createAuthGuard({
    get: async (path) => {
      assert.equal(path, "/me");
      throw new Error("unauthorized");
    },
  });

  assert.deepEqual(
    await unauthenticatedGuard({
      fullPath: "/profile?tab=settings",
      meta: { requiresAuth: true },
    }),
    {
      path: "/login",
      query: { next: "/profile?tab=settings" },
    },
  );

  installMemoryWindow();
  const incompleteOnboardingGuard = createAuthGuard({
    get: async (path) => {
      if (path === "/me") return { data: { ok: true } };
      if (path === "/me/today-missions") return { data: { ok: true, missions: [] } };
      throw new Error(`unexpected path ${path}`);
    },
  });

  assert.deepEqual(
    await incompleteOnboardingGuard({
      path: "/dashboard",
      fullPath: "/dashboard",
      meta: { requiresAuth: true },
    }),
    {
      path: "/onboarding",
      query: { next: "/dashboard" },
    },
  );

  installMemoryWindow({ ringostrike_identity_path: "focus" });
  const missionDataGuard = createAuthGuard({
    get: async (path) => {
      if (path === "/me") return { data: { ok: true } };
      throw new Error(`unexpected path ${path}`);
    },
  });

  assert.deepEqual(
    await missionDataGuard({
      path: "/dashboard",
      fullPath: "/dashboard",
      meta: { requiresAuth: true },
    }),
    {
      path: "/onboarding",
      query: { next: "/dashboard" },
    },
  );

  installMemoryWindow({ ringostrike_onboarding_done: "1" });
  const completedOnboardingGuard = createAuthGuard({
    get: async (path) => {
      assert.equal(path, "/me");
      return { data: { ok: true } };
    },
  });

  assert.equal(
    await completedOnboardingGuard({
      path: "/dashboard",
      fullPath: "/dashboard",
      meta: { requiresAuth: true },
    }),
    true,
  );

  installMemoryWindow({ ringostrike_onboarding_done: "1" });
  const legacyGlobalDoneGuard = createAuthGuard({
    get: async (path) => {
      assert.equal(path, "/me");
      return { data: { ok: true, user_id: 200, username: "new_user" } };
    },
  });

  assert.deepEqual(
    await legacyGlobalDoneGuard({
      path: "/dashboard",
      fullPath: "/dashboard",
      meta: { requiresAuth: true },
    }),
    {
      path: "/onboarding",
      query: { next: "/dashboard" },
    },
  );

  installMemoryWindow({ "ringostrike_onboarding_skipped:user:200": "1" });
  const skippedOnboardingGuard = createAuthGuard({
    get: async (path) => {
      assert.equal(path, "/me");
      return { data: { ok: true, user_id: 200, username: "new_user" } };
    },
  });

  assert.equal(
    await skippedOnboardingGuard({
      path: "/dashboard",
      fullPath: "/dashboard",
      meta: { requiresAuth: true },
    }),
    true,
  );
}

run();
