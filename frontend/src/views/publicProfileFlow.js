export function getPublicProfileTitleText(profile) {
  const title = profile?.title;

  if (!title) return "Builder";
  if (typeof title === "string") return title;

  if (typeof title === "object") {
    return title.label || title.key || "Builder";
  }

  return "Builder";
}

export function createPublicProfileState() {
  return {
    profile: null,
    consistency: [],
    achievements: [],
    isPrivate: false,
    isNotFound: false,
    error: "",
  };
}

export function normalizePublicProfileError(error) {
  const code = error?.response?.data?.error;

  if (code === "profile_private") {
    return {
      ...createPublicProfileState(),
      isPrivate: true,
    };
  }

  if (code === "profile_not_found") {
    return {
      ...createPublicProfileState(),
      isNotFound: true,
    };
  }

  return {
    ...createPublicProfileState(),
    error: code || error?.message || "Failed loading profile",
  };
}

export async function loadPublicProfileData(apiClient, username) {
  const [profileResp, consistencyResp, achievementsResp] = await Promise.all([
    apiClient.get(`/api/public/profile/${username}`),
    apiClient.get(`/api/public/profile/${username}/consistency`),
    apiClient.get(`/api/public/profile/${username}/achievements`),
  ]);

  return {
    ...createPublicProfileState(),
    profile: profileResp.data?.profile || null,
    consistency: consistencyResp.data?.days || [],
    achievements: achievementsResp.data?.achievements || [],
  };
}

export async function loadPublicProfileState(apiClient, username) {
  try {
    return await loadPublicProfileData(apiClient, username);
  } catch (error) {
    return normalizePublicProfileError(error);
  }
}
