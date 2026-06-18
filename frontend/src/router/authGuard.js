import {
  getOnboardingUserKey,
  hasOnboardingDecision,
} from "../lib/guidedExperience.js";

export function createAuthGuard(apiClient) {
  return async function authGuard(to) {
    if (to.meta?.requiresAuth === false) {
      return true;
    }

    try {
      const response = await apiClient.get("/me");
      const userKey = getOnboardingUserKey(response?.data);

      if (
        typeof window !== "undefined" &&
        to.path !== "/onboarding" &&
        !hasOnboardingDecision(userKey)
      ) {
        return {
          path: "/onboarding",
          query: { next: to.fullPath },
        };
      }

      return true;
    } catch {
      return { path: "/login", query: { next: to.fullPath } };
    }
  };
}
