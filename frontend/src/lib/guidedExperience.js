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
