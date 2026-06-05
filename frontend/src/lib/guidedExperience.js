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

function readStorage(key) {
  if (typeof window === "undefined") return null;

  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key, value) {
  if (typeof window === "undefined") return;

  try {
    window.localStorage.setItem(key, value);
  } catch {
    // Local storage can be unavailable in privacy modes; onboarding remains usable.
  }
}

export function isOnboardingDone() {
  return readStorage(ONBOARDING_DONE_KEY) === "1";
}

export function isOnboardingSkipped() {
  return readStorage(ONBOARDING_SKIPPED_KEY) === "1";
}

export function setIdentityPath(path) {
  if (!IDENTITY_PATHS.includes(path)) return;
  writeStorage(IDENTITY_PATH_KEY, path);
}

export function getIdentityPath() {
  const path = readStorage(IDENTITY_PATH_KEY);
  return IDENTITY_PATHS.includes(path) ? path : "";
}

export function markOnboardingDone(path = "") {
  if (path) setIdentityPath(path);
  writeStorage(ONBOARDING_DONE_KEY, "1");
  writeStorage(ONBOARDING_SKIPPED_KEY, "0");
}

export function markOnboardingSkipped(path = "") {
  if (path) setIdentityPath(path);
  writeStorage(ONBOARDING_SKIPPED_KEY, "1");
}

export function shouldShowOnboardingPrompt() {
  return !isOnboardingDone() && !isOnboardingSkipped();
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
