export const DASHBOARD_CHALLENGE_LIMIT = 4;

export function orderDashboardChallenges(challenges) {
  const ready = challenges.filter((challenge) => !challenge.today_checked);
  const done = challenges.filter((challenge) => Boolean(challenge.today_checked));

  return [...ready, ...done];
}

export function getVisibleDashboardChallenges(
  challenges,
  showAllChallenges = false,
  limit = DASHBOARD_CHALLENGE_LIMIT,
) {
  const ordered = orderDashboardChallenges(challenges);

  return showAllChallenges ? ordered : ordered.slice(0, limit);
}

export function buildTodayFocus(challenges) {
  const readyTodayCount = challenges.filter((challenge) => !challenge.today_checked).length;

  if (!challenges.length) {
    return {
      title: "Choose your first path",
      text: "Start with one simple challenge. The product becomes meaningful when your day has a clear anchor.",
    };
  }

  if (readyTodayCount === 0) {
    return {
      title: "All active paths are secured",
      text: "Today’s check-ins are complete. You can review progress, achievements, or prepare your next path.",
    };
  }

  return {
    title: readyTodayCount === 1
      ? "One path is waiting"
      : `${readyTodayCount} paths are waiting`,
    text: "Focus on ready paths first. Small daily completions compound into streaks, XP, and identity.",
  };
}

export async function loadDashboardData(apiClient, fallbackDate) {
  const [dashboardResp, statsResp] = await Promise.all([
    apiClient.get("/me/challenges"),
    apiClient.get("/me/stats"),
  ]);

  const dashboardData = dashboardResp.data || {};
  const statsData = statsResp.data || {};
  const challenges = (dashboardData.challenges || []).map((challenge) => ({
    ...challenge,
  }));

  const [activityResp, achievementsResp] = await Promise.all([
    apiClient.get("/me/activity"),
    apiClient.get("/me/achievements"),
  ]);

  const detailCalls = challenges.map((challenge) =>
    apiClient.get(`/me/enrollments/${challenge.enrollment_id}`)
  );
  const detailResults = await Promise.allSettled(detailCalls);

  const hydratedChallenges = challenges.map((challenge, index) => {
    const result = detailResults[index];

    if (result.status !== "fulfilled") return challenge;

    const payload = result.value?.data || {};

    return {
      ...challenge,
      description: payload.challenge?.description || "",
      duration_days: payload.challenge?.duration_days || null,
      current_streak: payload.enrollment?.current_streak || 0,
    };
  });

  return {
    user: statsData.user || dashboardData.user || null,
    stats: statsData.stats || null,
    challenges: hydratedChallenges,
    date: dashboardData.date || fallbackDate,
    activityEvents: activityResp.data?.events || [],
    achievements: achievementsResp.data?.achievements || [],
  };
}
