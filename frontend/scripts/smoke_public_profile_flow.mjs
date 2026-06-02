import assert from "node:assert/strict";

import {
  createPublicProfileState,
  getPublicProfileTitleText,
  loadPublicProfileData,
  loadPublicProfileState,
  normalizePublicProfileError,
} from "../src/views/publicProfileFlow.js";

function createApiClient(fixtures, calls) {
  return {
    async get(path) {
      calls.push(path);

      if (Object.prototype.hasOwnProperty.call(fixtures, path)) {
        const value = fixtures[path];

        if (value instanceof Error || value?.response) {
          throw value;
        }

        return { data: value };
      }

      throw new Error(`Unhandled API path: ${path}`);
    },
  };
}

function apiError(code) {
  return {
    response: {
      data: {
        error: code,
      },
    },
  };
}

async function run() {
  assert.deepEqual(createPublicProfileState(), {
    profile: null,
    consistency: [],
    achievements: [],
    isPrivate: false,
    isNotFound: false,
    error: "",
  });
  assert.equal(getPublicProfileTitleText({ title: { label: "Starter" } }), "Starter");
  assert.equal(getPublicProfileTitleText({ title: { key: "builder" } }), "builder");
  assert.equal(getPublicProfileTitleText({ title: "Consistency Pro" }), "Consistency Pro");
  assert.equal(getPublicProfileTitleText({}), "Builder");

  const calls = [];
  const data = await loadPublicProfileData(
    createApiClient(
      {
        "/api/public/profile/alice": {
          ok: true,
          profile: {
            username: "alice",
            name: "Alice",
            title: { label: "Momentum Builder" },
            recent_activity: [{ id: "recent-1" }],
          },
        },
        "/api/public/profile/alice/consistency": {
          ok: true,
          days: [{ date: "2026-06-02", count: 1 }],
        },
        "/api/public/profile/alice/achievements": {
          ok: true,
          achievements: [{ key: "first_strike", unlocked: true }],
        },
      },
      calls,
    ),
    "alice",
  );

  assert.deepEqual(calls, [
    "/api/public/profile/alice",
    "/api/public/profile/alice/consistency",
    "/api/public/profile/alice/achievements",
  ]);
  assert.equal(data.profile.username, "alice");
  assert.equal(data.consistency.length, 1);
  assert.equal(data.achievements.length, 1);
  assert.equal(data.isPrivate, false);
  assert.equal(data.isNotFound, false);
  assert.equal(data.error, "");

  const emptyData = await loadPublicProfileData(
    createApiClient(
      {
        "/api/public/profile/empty": { ok: true },
        "/api/public/profile/empty/consistency": { ok: true },
        "/api/public/profile/empty/achievements": { ok: true },
      },
      [],
    ),
    "empty",
  );

  assert.equal(emptyData.profile, null);
  assert.deepEqual(emptyData.consistency, []);
  assert.deepEqual(emptyData.achievements, []);

  assert.deepEqual(normalizePublicProfileError(apiError("profile_private")), {
    profile: null,
    consistency: [],
    achievements: [],
    isPrivate: true,
    isNotFound: false,
    error: "",
  });
  assert.deepEqual(normalizePublicProfileError(apiError("profile_not_found")), {
    profile: null,
    consistency: [],
    achievements: [],
    isPrivate: false,
    isNotFound: true,
    error: "",
  });
  assert.equal(normalizePublicProfileError(new Error("network down")).error, "network down");

  const privateState = await loadPublicProfileState(
    createApiClient(
      {
        "/api/public/profile/privateuser": apiError("profile_private"),
        "/api/public/profile/privateuser/consistency": { ok: true },
        "/api/public/profile/privateuser/achievements": { ok: true },
      },
      [],
    ),
    "privateuser",
  );

  assert.equal(privateState.isPrivate, true);
  assert.equal(privateState.profile, null);
}

run();
