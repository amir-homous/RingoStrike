import assert from "node:assert/strict";

import { createAuthGuard } from "../src/router/authGuard.js";

async function run() {
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
}

run();
