import assert from "node:assert/strict";

import {
  buildProfileSettingsForm,
  buildProfileSettingsPayload,
  countUnlockedAchievements,
  getProfileIdentityStatus,
  getProfileTitleText,
  getProfileVisibilityHint,
  getProfileVisibilityLabel,
  loadPrivateProfileData,
  loadProfileSettings,
  saveProfileSettings,
} from "../src/views/profileFlow.js";

function createApiClient(fixtures, calls) {
  return {
    async get(path) {
      calls.push(path);

      if (Object.prototype.hasOwnProperty.call(fixtures, path)) {
        const value = fixtures[path];

        if (value instanceof Error) {
          throw value;
        }

        return { data: value };
      }

      throw new Error(`Unhandled API path: ${path}`);
    },
    async patch(path, payload) {
      calls.push({ path, payload });
      return { data: { ok: true } };
    },
  };
}

async function run() {
  const publicProfile = {
    profile_visibility: "public",
    title: { label: "Momentum Builder" },
  };
  const privateProfile = {
    profile_visibility: "private",
    title: "Private Striker",
  };

  assert.equal(getProfileVisibilityLabel(publicProfile), "Public");
  assert.equal(getProfileVisibilityLabel(privateProfile), "Private");
  assert.equal(getProfileVisibilityHint(privateProfile), "Only you can view the public profile data.");
  assert.equal(getProfileIdentityStatus(publicProfile).title, "Public identity is active");
  assert.equal(getProfileIdentityStatus(privateProfile).title, "Private progression mode");
  assert.equal(getProfileTitleText(publicProfile), "Momentum Builder");
  assert.equal(getProfileTitleText(privateProfile), "Private Striker");
  assert.equal(getProfileTitleText({ title: { key: "starter" } }), "starter");
  assert.equal(countUnlockedAchievements([{ unlocked: true }, { unlocked: false }]), 1);

  const calls = [];
  const data = await loadPrivateProfileData(
    createApiClient(
      {
        "/me/profile": {
          ok: true,
          profile: {
            username: "profileuser",
            bio: "Building daily momentum.",
          },
        },
        "/me/consistency": {
          ok: true,
          days: [{ date: "2026-06-02", count: 1 }],
        },
        "/me/achievements": {
          ok: true,
          achievements: [{ key: "first_strike", unlocked: true }],
        },
        "/me/activity": {
          ok: true,
          events: [{ id: "activity-1" }],
        },
      },
      calls,
    ),
  );

  assert.deepEqual(calls, [
    "/me/profile",
    "/me/consistency",
    "/me/achievements",
    "/me/activity",
  ]);
  assert.equal(data.profile.username, "profileuser");
  assert.equal(data.consistency.length, 1);
  assert.equal(data.achievements.length, 1);
  assert.equal(data.activityEvents.length, 1);

  const emptyData = await loadPrivateProfileData(
    createApiClient(
      {
        "/me/profile": { ok: true },
        "/me/consistency": { ok: true },
        "/me/achievements": { ok: true },
        "/me/activity": { ok: true },
      },
      [],
    ),
  );

  assert.equal(emptyData.profile, null);
  assert.deepEqual(emptyData.consistency, []);
  assert.deepEqual(emptyData.achievements, []);
  assert.deepEqual(emptyData.activityEvents, []);

  await assert.rejects(
    () =>
      loadPrivateProfileData(
        createApiClient(
          {
            "/me/profile": new Error("profile unavailable"),
            "/me/consistency": { ok: true },
            "/me/achievements": { ok: true },
            "/me/activity": { ok: true },
          },
          [],
        ),
      ),
    /profile unavailable/,
  );

  assert.deepEqual(
    buildProfileSettingsForm({
      bio: "Hello",
      avatar_url: "/avatars/avatar-1.png",
      profile_visibility: "private",
    }),
    {
      bio: "Hello",
      avatar_url: "/avatars/avatar-1.png",
      profile_visibility: "private",
    },
  );
  assert.deepEqual(buildProfileSettingsForm({}), {
    bio: "",
    avatar_url: "",
    profile_visibility: "public",
  });
  assert.deepEqual(
    buildProfileSettingsPayload({ bio: "Only bio" }),
    { bio: "Only bio" },
  );
  assert.deepEqual(
    buildProfileSettingsPayload({
      bio: "Bio",
      avatar_url: "",
      profile_visibility: "public",
      ignored: "field",
    }),
    {
      bio: "Bio",
      avatar_url: "",
      profile_visibility: "public",
    },
  );

  const settingsCalls = [];
  const settingsForm = await loadProfileSettings(
    createApiClient(
      {
        "/me/profile": {
          ok: true,
          profile: {
            bio: "Settings bio",
            avatar_url: "/avatars/avatar-2.png",
            profile_visibility: "private",
          },
        },
      },
      settingsCalls,
    ),
  );

  assert.deepEqual(settingsCalls, ["/me/profile"]);
  assert.deepEqual(settingsForm, {
    bio: "Settings bio",
    avatar_url: "/avatars/avatar-2.png",
    profile_visibility: "private",
  });

  const saveCalls = [];
  await saveProfileSettings(
    createApiClient({}, saveCalls),
    {
      profile_visibility: "private",
    },
  );

  assert.deepEqual(saveCalls, [
    {
      path: "/api/me/profile/settings",
      payload: {
        profile_visibility: "private",
      },
    },
  ]);
}

run();
