export function getProfileVisibilityLabel(profile) {
  const value = profile?.profile_visibility || profile?.visibility || "public";
  return value === "private" ? "Private" : "Public";
}

export function getProfileVisibilityHint(profile) {
  return getProfileVisibilityLabel(profile) === "Private"
    ? "Only you can view the public profile data."
    : "Your progression identity is shareable.";
}

export function getProfileIdentityStatus(profile) {
  if (getProfileVisibilityLabel(profile) === "Private") {
    return {
      title: "Private progression mode",
      text: "Your profile is protected. You can still build momentum privately and publish later when ready.",
    };
  }

  return {
    title: "Public identity is active",
    text: "Your public profile can communicate consistency, achievements, and identity without exposing private app controls.",
  };
}

export function getProfileTitleText(profile) {
  const title = profile?.title;

  if (!title) return "Progression Builder";
  if (typeof title === "string") return title;

  if (typeof title === "object") {
    return title.label || title.key || "Progression Builder";
  }

  return "Progression Builder";
}

export function countUnlockedAchievements(achievements) {
  return achievements.filter((achievement) => achievement.unlocked).length;
}

export async function loadPrivateProfileData(apiClient) {
  const [profileResp, consistencyResp, achievementsResp, activityResp] =
    await Promise.all([
      apiClient.get("/me/profile"),
      apiClient.get("/me/consistency"),
      apiClient.get("/me/achievements"),
      apiClient.get("/me/activity"),
    ]);

  return {
    profile: profileResp.data?.profile || null,
    consistency: consistencyResp.data?.days || [],
    achievements: achievementsResp.data?.achievements || [],
    activityEvents: activityResp.data?.events || [],
  };
}

export function buildProfileSettingsForm(profile) {
  return {
    bio: profile?.bio || "",
    avatar_url: profile?.avatar_url || "",
    profile_visibility: profile?.profile_visibility || "public",
  };
}

export function buildProfileSettingsPayload(form) {
  const payload = {};

  for (const key of ["bio", "avatar_url", "profile_visibility"]) {
    if (Object.prototype.hasOwnProperty.call(form, key)) {
      payload[key] = form[key];
    }
  }

  return payload;
}

export async function loadProfileSettings(apiClient) {
  const response = await apiClient.get("/me/profile");
  return buildProfileSettingsForm(response.data?.profile || {});
}

export async function saveProfileSettings(apiClient, form) {
  await apiClient.patch(
    "/api/me/profile/settings",
    buildProfileSettingsPayload(form),
  );
}

export async function loadTelegramSettings(apiClient) {
  const response = await apiClient.get("/api/me/telegram/settings");
  return response.data?.settings || null;
}

export async function createTelegramConnectCode(apiClient) {
  const response = await apiClient.post("/api/me/telegram/connect-code");
  return response.data?.connect_code || null;
}

export async function saveTelegramSettings(apiClient, settings) {
  const response = await apiClient.patch(
    "/api/me/telegram/settings",
    {
      reminders_enabled: Boolean(settings?.reminders_enabled),
      daily_checkin_enabled: Boolean(settings?.daily_checkin_enabled),
      streak_risk_enabled: Boolean(settings?.streak_risk_enabled),
      weekly_summary_enabled: Boolean(settings?.weekly_summary_enabled),
    },
  );

  return response.data?.settings || null;
}

export async function disconnectTelegram(apiClient) {
  const response = await apiClient.post("/api/me/telegram/disconnect");
  return response.data?.settings || null;
}
