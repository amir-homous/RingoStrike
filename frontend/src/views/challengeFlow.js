export const CHECKIN_XP = 10;

export function isInviteOnlyChallenge(challenge) {
  return String(challenge.visibility || "").toLowerCase() === "invite-only";
}

export function humanizeJoinError(message) {
  if (!message) return "";
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
}) {
  const payload = buildJoinPayload(challenge, codes);
  const { data } = await apiClient.post(
    `/challenges/${challenge.challenge_id}/join`,
    payload,
  );

  if (data?.enrollment_id) {
    router.push(`/enrollment/${data.enrollment_id}`);
    return {
      enrollmentId: data.enrollment_id,
      navigated: true,
    };
  }

  await reload();

  return {
    enrollmentId: null,
    navigated: false,
  };
}

export function buildOptimisticCheckinEvents(target, oldLevel, newLevel) {
  const now = new Date().toISOString();
  const eventId = Date.now();

  const events = [
    {
      id: `optimistic-checkin-${eventId}`,
      type: "checkin",
      title: `Completed ${target.enrollment_name}`,
      subtitle: `+${CHECKIN_XP} XP earned`,
      xp_delta: CHECKIN_XP,
      icon: "check",
      created_at: now,
    },
    {
      id: `optimistic-streak-${eventId}`,
      type: "streak",
      title: `${target.current_streak || 1}-day streak maintained`,
      subtitle: "Consistency is compounding",
      icon: "flame",
      created_at: now,
    },
  ];

  if (newLevel > oldLevel) {
    events.push({
      id: `optimistic-level-${eventId}`,
      type: "level_up",
      title: `Reached Level ${newLevel}`,
      subtitle: "Milestone unlocked",
      icon: "level",
      created_at: now,
    });
  }

  return events;
}

export function applyOptimisticCheckin(state, enrollmentId) {
  const target = state.challenges.find(
    (challenge) => challenge.enrollment_id === enrollmentId,
  );

  if (!target || target.today_checked || !state.stats) {
    return null;
  }

  const oldStats = { ...state.stats };
  const oldActivityEvents = [...state.activityEvents];
  const nextStreak = (target.current_streak || 0) + 1;

  state.challenges = state.challenges.map((challenge) => {
    if (challenge.enrollment_id !== enrollmentId) {
      return challenge;
    }

    return {
      ...challenge,
      today_checked: true,
      current_streak: nextStreak,
    };
  });

  state.stats = {
    ...state.stats,
    total_points: state.stats.total_points + CHECKIN_XP,
    total_checkins: state.stats.total_checkins + 1,
    current_streak: Math.max(state.stats.current_streak, nextStreak),
    xp: Math.min(state.stats.next_level_xp, state.stats.xp + CHECKIN_XP),
    progress_percent: Math.min(
      100,
      state.stats.progress_percent + Math.round((CHECKIN_XP / 100) * 100),
    ),
  };

  const optimisticTarget = {
    ...target,
    today_checked: true,
    current_streak: nextStreak,
  };

  state.activityEvents = [
    ...buildOptimisticCheckinEvents(
      optimisticTarget,
      oldStats.level || 1,
      state.stats.level || 1,
    ),
    ...state.activityEvents,
  ];

  return {
    oldStats,
    oldActivityEvents,
    target,
  };
}

export function rollbackOptimisticCheckin(state, enrollmentId, snapshot) {
  if (!snapshot) return;

  state.stats = snapshot.oldStats;
  state.activityEvents = snapshot.oldActivityEvents;
  state.challenges = state.challenges.map((challenge) => {
    if (challenge.enrollment_id !== enrollmentId) {
      return challenge;
    }

    return {
      ...challenge,
      today_checked: false,
      current_streak: Math.max((challenge.current_streak || 1) - 1, 0),
    };
  });
}

export async function submitCheckinFlow({
  apiClient,
  state,
  enrollmentId,
  onStateChange = () => {},
  setPulse = () => {},
  schedule = globalThis.setTimeout,
}) {
  state.error = "";

  const snapshot = applyOptimisticCheckin(state, enrollmentId);

  if (!snapshot) {
    return {
      skipped: true,
      unlocked: [],
      oldStats: null,
    };
  }

  onStateChange(state);
  setPulse(true);
  schedule(() => setPulse(false), 520);

  try {
    const checkinResp = await apiClient.post(
      `/me/challenges/${enrollmentId}/checkin`,
    );
    const unlocked = checkinResp.data?.rewards?.achievements || [];

    const [statsResp, activityResp, achievementsResp] = await Promise.all([
      apiClient.get("/me/stats"),
      apiClient.get("/me/activity"),
      apiClient.get("/me/achievements"),
    ]);

    state.stats = statsResp.data.stats || state.stats;
    state.activityEvents = activityResp.data?.events || state.activityEvents;
    state.achievements = achievementsResp.data?.achievements || state.achievements;

    onStateChange(state);

    return {
      skipped: false,
      unlocked,
      oldStats: snapshot.oldStats,
    };
  } catch (error) {
    rollbackOptimisticCheckin(state, enrollmentId, snapshot);
    state.error = error?.response?.data?.error || error?.message || String(error);
    onStateChange(state);

    return {
      skipped: false,
      unlocked: [],
      oldStats: snapshot.oldStats,
      error: state.error,
    };
  }
}
