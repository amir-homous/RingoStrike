export function createAuthGuard(apiClient) {
  return async function authGuard(to) {
    if (to.meta?.requiresAuth === false) {
      return true;
    }

    try {
      await apiClient.get("/me");
      return true;
    } catch {
      return { path: "/login", query: { next: to.fullPath } };
    }
  };
}
