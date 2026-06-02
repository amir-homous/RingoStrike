import assert from "node:assert/strict";

import {
  buildAuthPayload,
  resolveAuthRedirect,
  submitAuthFlow,
  validateAuthForm,
} from "../src/components/authFlow.js";

function createRouterRecorder() {
  const pushes = [];

  return {
    pushes,
    router: {
      push(path) {
        pushes.push(path);
      },
    },
  };
}

async function run() {
  assert.throws(
    () => validateAuthForm({ username: "ab", password: "secret123" }, true),
    /Username must be at least 3 characters/,
  );

  assert.deepEqual(
    buildAuthPayload(
      {
        username: "smokeuser",
        password: "secret123",
        name: "Smoke User",
        email: "smoke@example.com",
      },
      true,
    ),
    {
      username: "smokeuser",
      password: "secret123",
    },
  );

  assert.equal(
    resolveAuthRedirect({ query: { next: "/profile?tab=settings" } }),
    "/profile?tab=settings",
  );
  assert.equal(resolveAuthRedirect({ query: { next: "https://bad.test" } }), "/dashboard");
  assert.equal(resolveAuthRedirect({ query: { next: "//bad.test" } }), "/dashboard");

  let postedEndpoint = null;
  let postedPayload = null;
  let storageWrites = 0;
  const { router, pushes } = createRouterRecorder();

  globalThis.localStorage = {
    setItem() {
      storageWrites += 1;
    },
  };

  const result = await submitAuthFlow({
    apiClient: {
      post: async (endpoint, payload) => {
        postedEndpoint = endpoint;
        postedPayload = payload;
        return { data: { ok: true } };
      },
    },
    router,
    route: { query: { next: "/challenges" } },
    form: {
      username: "smokeuser",
      password: "secret123",
      name: "",
      email: "",
    },
    isLogin: true,
    schedule: (callback, delay) => {
      assert.equal(delay, 1000);
      callback();
    },
  });

  assert.equal(postedEndpoint, "/auth/login");
  assert.deepEqual(postedPayload, {
    username: "smokeuser",
    password: "secret123",
  });
  assert.equal(result.success, "Login successful!");
  assert.equal(result.nextPath, "/challenges");
  assert.deepEqual(pushes, ["/challenges"]);
  assert.equal(storageWrites, 0);

  const registerResult = await submitAuthFlow({
    apiClient: {
      post: async (endpoint, payload) => {
        assert.equal(endpoint, "/auth/register");
        assert.deepEqual(payload, {
          username: "newuser",
          password: "secret123",
          name: "newuser",
          email: null,
        });
        return { data: { ok: true } };
      },
    },
    router: createRouterRecorder().router,
    route: { query: {} },
    form: {
      username: "newuser",
      password: "secret123",
      name: "",
      email: "",
    },
    isLogin: false,
    schedule: (callback) => callback(),
  });

  assert.equal(registerResult.success, "Registration successful!");

  await assert.rejects(
    () =>
      submitAuthFlow({
        apiClient: {
          post: async () => ({ data: { ok: false, error: "invalid_credentials" } }),
        },
        router: createRouterRecorder().router,
        route: { query: {} },
        form: {
          username: "smokeuser",
          password: "wrongpass",
        },
        isLogin: true,
      }),
    /invalid_credentials/,
  );
}

run();
