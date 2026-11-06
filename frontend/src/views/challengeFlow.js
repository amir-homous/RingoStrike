export function isInviteOnlyChallenge(challenge) {
  return String(challenge.visibility || "").toLowerCase() === "invite-only";
}

// Join error codes from POST /challenges/:id/join (and the client-side missing-code check) mapped to
// joinErrors.* in en.js / fa.js (B30 S2, D43).
const JOIN_ERROR_KEYS = Object.freeze({
  invite_code_required: "codeRequired",
  join_code_required: "codeRequired",
  invalid_join_code: "invalidCode",
  invalid_join_code_type: "codeType",
  join_code_too_long: "codeTooLong",
  challenge_private: "private",
  challenge_inactive: "inactive",
  invite_only_not_configured: "inviteNotConfigured",
  challenge_not_found: "notFound",
});

// With t (vue-i18n), known codes are translated; anything else keeps the old readable fallback.
export function humanizeJoinError(message, t) {
  if (!message) return "";
  if (typeof t === "function" && JOIN_ERROR_KEYS[message]) return t(`joinErrors.${JOIN_ERROR_KEYS[message]}`);
  if (message === "invite_code_required") return "Invite code is required.";
  if (message === "join_code_required") return "Invite code is required.";
  if (message === "invalid_join_code") return "Invalid invite code.";
  if (message === "invalid_join_code_type") return "Invite code must be text.";
  if (message === "join_code_too_long") return "Invite code is too long.";
  if (message === "challenge_private") return "This challenge is private.";
  if (message === "challenge_inactive") return "This challenge is not active.";
  if (typeof message === "string") return message.replaceAll("_", " ");
  return String(message);
}

export function buildJoinPayload(challenge, codes = {}) {
  const needsCode = isInviteOnlyChallenge(challenge) || challenge.needs_code;

  if (!needsCode) {
    return {};
  }

  const code = (codes[challenge.challenge_id] || "").trim();

  if (!code) {
    throw new Error("invite_code_required");
  }

  return { join_code: code };
}

export async function submitJoinFlow({
  apiClient,
  router,
  challenge,
  codes = {},
  reload = async () => {},
  navigateOnJoin = false,
}) {
  const payload = buildJoinPayload(challenge, codes);
  const { data } = await apiClient.post(
    `/challenges/${challenge.challenge_id}/join`,
    payload,
  );

  const enrollmentId = data?.enrollment_id || challenge?.enrollment_id || null;
  const result = {
    challengeId: data?.challenge_id || challenge?.challenge_id || null,
    challengeName: challenge?.name || challenge?.challenge_name || challenge?.enrollment_name || "",
    challengeDescription: challenge?.description || challenge?.challenge_description || "",
    enrollmentId,
    mode: data?.mode || (challenge?.is_joined ? "existing" : "joined"),
    navigated: false,
  };

  if (data?.enrollment_id) {
    if (navigateOnJoin && router) {
      router.push(`/enrollment/${data.enrollment_id}`);
      return {
        ...result,
        navigated: true,
      };
    }

    return result;
  }

  await reload();

  return result;
}
