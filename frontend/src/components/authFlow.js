export function validateAuthForm(form, isLogin) {
  if (!form.username || form.username.length < 3) {
    throw new Error("Username must be at least 3 characters");
  }

  if (!form.password) {
    throw new Error("Password is required");
  }

  if (!isLogin && form.password.length < 6) {
    throw new Error("Password must be at least 6 characters");
  }
}

export function buildAuthPayload(form, isLogin) {
  return {
    username: form.username,
    password: form.password,
    ...(isLogin
      ? {}
      : {
          name: form.name || form.username,
          email: form.email || null,
        }),
  };
}

export function resolveAuthRedirect(route, isLogin = true) {
  const next = route?.query?.next;

  return typeof next === "string" && next.startsWith("/") && !next.startsWith("//")
    ? next
    : isLogin
      ? "/dashboard"
      : "/onboarding";
}

export async function submitAuthFlow({
  apiClient,
  router,
  route,
  form,
  isLogin,
  redirectDelay = 1000,
  schedule = globalThis.setTimeout,
}) {
  validateAuthForm(form, isLogin);

  const endpoint = isLogin ? "/auth/login" : "/auth/register";
  const response = await apiClient.post(
    endpoint,
    buildAuthPayload(form, isLogin),
  );

  const data = response.data || {};

  if (!data.ok) {
    throw new Error(data.error || "Authentication failed");
  }

  const nextPath = resolveAuthRedirect(route, isLogin);

  schedule(() => {
    router.push(nextPath);
  }, redirectDelay);

  return {
    nextPath,
    success: isLogin ? "Login successful!" : "Registration successful!",
  };
}
