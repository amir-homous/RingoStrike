export const ONBOARDING_DONE_KEY = "ringostrike_onboarding_done";
export const IDENTITY_PATH_KEY = "ringostrike_identity_path";
export const ONBOARDING_SKIPPED_KEY = "ringostrike_onboarding_skipped";

export const PATH_TO_CHALLENGE_NAME = {
  focus: "Deep Work Sprint",
  body: "Move Your Body",
  learning: "Learn One Thing",
  mind: "Mind Reset",
  consistency: "Daily Strike",
};

const CHALLENGE_NAME_TO_PATH = Object.entries(PATH_TO_CHALLENGE_NAME).reduce(
  (result, [path, name]) => {
    result[name.toLowerCase()] = path;
    return result;
  },
  {},
);

export const IDENTITY_PATHS = [
  "focus",
  "body",
  "learning",
  "mind",
  "consistency",
];

export const GUIDED_FEATURE_THRESHOLDS = {
  activity: 3,
  achievements: 5,
  leaderboard: 7,
  publicProfile: 7,
};

export const GUIDED_FEATURE_KEYS = Object.freeze([
  "activity",
  "achievements",
  "leaderboard",
  "publicProfile",
]);

export const REWARD_MOMENT_UNLOCK_KEYS = Object.freeze([
  "activity",
  "achievements",
  "publicProfile",
]);

function readStorage(key, userKey = "") {
  if (typeof window === "undefined") return null;

  try {
    return window.localStorage.getItem(scopedStorageKey(key, userKey));
  } catch {
    return null;
  }
}

function writeStorage(key, value, userKey = "") {
  if (typeof window === "undefined") return;

  try {
    window.localStorage.setItem(scopedStorageKey(key, userKey), value);
  } catch {
    // Local storage can be unavailable in privacy modes; onboarding remains usable.
  }
}

export function isOnboardingDone(userKey = "") {
  return readStorage(ONBOARDING_DONE_KEY, userKey) === "1";
}


export function isOnboardingSkipped(userKey = "") {
  return readStorage(ONBOARDING_SKIPPED_KEY, userKey) === "1";
}

export function hasOnboardingDecision(userKey = "") {
  return isOnboardingDone(userKey) || isOnboardingSkipped(userKey);
}

export function setIdentityPath(path, userKey = "") {
  if (!IDENTITY_PATHS.includes(path)) return;
  writeStorage(IDENTITY_PATH_KEY, path, userKey);
}

export function getIdentityPath(userKey = "") {
  const path = readStorage(IDENTITY_PATH_KEY, userKey);
  return IDENTITY_PATHS.includes(path) ? path : "";
}

export function markOnboardingDone(path = "", userKey = "") {
  if (path) setIdentityPath(path, userKey);
  writeStorage(ONBOARDING_DONE_KEY, "1", userKey);
  writeStorage(ONBOARDING_SKIPPED_KEY, "0", userKey);
}

export function markOnboardingSkipped(path = "", userKey = "") {
  if (path) setIdentityPath(path, userKey);
  writeStorage(ONBOARDING_SKIPPED_KEY, "1", userKey);
  writeStorage(ONBOARDING_DONE_KEY, "0", userKey);
}

export function shouldShowOnboardingPrompt(userKey = "") {
  return !hasOnboardingDecision(userKey);
}

export function hasTodayMissionPayload(payload) {
  const missions = payload?.missions;
  return Array.isArray(missions) && missions.length > 0;
}

export function getSuggestedChallengeName(path) {
  return PATH_TO_CHALLENGE_NAME[path] || PATH_TO_CHALLENGE_NAME.consistency;
}

export function findSuggestedChallenge(challenges, path) {
  const suggestedName = getSuggestedChallengeName(path).toLowerCase();

  return (challenges || []).find((challenge) => {
    return String(challenge?.name || challenge?.challenge_name || "")
      .trim()
      .toLowerCase() === suggestedName;
  }) || null;
}

export function getSuggestedPathChallenge(path, challenges) {
  return findSuggestedChallenge(challenges, path);
}

export function getChallengePathKey(challenge) {
  const name = String(challenge?.name || challenge?.challenge_name || challenge?.enrollment_name || "")
    .trim()
    .toLowerCase();

  return CHALLENGE_NAME_TO_PATH[name] || "";
}

function toCount(value) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, Math.floor(number)) : 0;
}

export function getCheckinCount(stats, dashboardData = {}) {
  const statsCount = toCount(stats?.total_checkins ?? stats?.totalCheckins);
  if (statsCount > 0) return statsCount;

  const challengeCounts = (dashboardData?.challenges || []).map((challenge) =>
    toCount(challenge?.total_checkins ?? challenge?.totalCheckins),
  );

  return Math.max(0, ...challengeCounts);
}

export function isGuidedFeatureUnlocked(featureKey, context = {}) {
  const threshold = GUIDED_FEATURE_THRESHOLDS[featureKey];
  if (threshold == null) return true;

  const checkinCount = context.checkinCount ?? getCheckinCount(
    context.stats,
    context.dashboardData,
  );

  return toCount(checkinCount) >= threshold;
}

export function getGuidedFeatureState({ stats, dashboardData = {} } = {}) {
  const checkinCount = getCheckinCount(stats, dashboardData);
  const features = GUIDED_FEATURE_KEYS.reduce((result, featureKey) => {
    const threshold = GUIDED_FEATURE_THRESHOLDS[featureKey];
    result[featureKey] = {
      key: featureKey,
      threshold,
      unlocked: checkinCount >= threshold,
      remaining: Math.max(0, threshold - checkinCount),
    };
    return result;
  }, {});

  const nextLocked = GUIDED_FEATURE_KEYS
    .map((key) => features[key])
    .find((feature) => !feature.unlocked) || null;

  return {
    checkinCount,
    hasProgress: checkinCount > 0,
    features,
    nextLocked,
  };
}

export function getNewlyUnlockedGuidedFeatures({ oldStats, newStats } = {}) {
  const oldCount = getCheckinCount(oldStats);
  const newCount = getCheckinCount(newStats);

  if (newCount <= oldCount) return [];

  return REWARD_MOMENT_UNLOCK_KEYS.filter((featureKey) => {
    const threshold = GUIDED_FEATURE_THRESHOLDS[featureKey];
    return oldCount < threshold && newCount >= threshold;
  });
}

export function getOnboardingUserKey(user = {}) {
  const userId = user?.user_id ?? user?.id;

  if (userId !== undefined && userId !== null && String(userId).trim()) {
    return `user:${userId}`;
  }

  const username = String(user?.username || "").trim().toLowerCase();

  if (username) {
    return `username:${username}`;
  }

  return "";
}

function scopedStorageKey(baseKey, userKey = "") {
  return userKey ? `${baseKey}:${userKey}` : baseKey;
}
