import assert from "node:assert/strict";

import {
  buildTodayFocus,
  getVisibleDashboardChallenges,
  loadDashboardData,
  orderDashboardChallenges,
} from "../src/views/dashboardFlow.js";

function createApiClient(fixtures, calls) {
  return {
    async get(path) {
      calls.push(path);

      if (Object.prototype.hasOwnProperty.call(fixtures, path)) {
        const value = fixtures[path];

        if (value instanceof Error) {
          throw value;
        }

        return { data: value };
      }

      throw new Error(`Unhandled API path: ${path}`);
    },
  };
}

async function run() {
  const representativeChallenges = [
    {
      enrollment_id: 101,
      enrollment_name: "Already Done",
      today_checked: true,
    },
    {
      enrollment_id: 102,
      enrollment_name: "Ready Path",
      today_checked: false,
    },
  ];

  assert.deepEqual(
    orderDashboardChallenges(representativeChallenges).map((challenge) => challenge.enrollment_id),
    [102, 101],
  );
  assert.deepEqual(
    getVisibleDashboardChallenges(
      [
        { enrollment_id: 1, today_checked: false },
        { enrollment_id: 2, today_checked: false },
        { enrollment_id: 3, today_checked: false },
        { enrollment_id: 4, today_checked: false },
        { enrollment_id: 5, today_checked: false },
      ],
      false,
    ).map((challenge) => challenge.enrollment_id),
    [1, 2, 3, 4],
  );
  assert.equal(buildTodayFocus([]).title, "Choose your first path");
  assert.equal(buildTodayFocus([{ today_checked: true }]).title, "All active paths are secured");
  assert.equal(buildTodayFocus([{ today_checked: false }]).title, "One path is waiting");

  const calls = [];
  const apiClient = createApiClient(
    {
      "/me/challenges": {
        ok: true,
        date: "2026-06-02",
        user: { name: "Dashboard User" },
        challenges: representativeChallenges,
      },
      "/me/stats": {
        ok: true,
        user: { name: "Stats User" },
        stats: {
          level: 3,
          total_points: 180,
          current_streak: 6,
        },
      },
      "/me/activity": {
        ok: true,
        events: [{ id: "event-1", type: "checkin" }],
      },
      "/me/achievements": {
        ok: true,
        achievements: [{ key: "first_strike", unlocked: true }],
      },
      "/me/enrollments/101": {
        ok: true,
        challenge: {
          description: "Done path description",
          duration_days: 14,
        },
        enrollment: {
          current_streak: 4,
        },
      },
      "/me/enrollments/102": {
        ok: true,
        challenge: {
          description: "Ready path description",
          duration_days: 30,
        },
        enrollment: {
          current_streak: 2,
        },
      },
    },
    calls,
  );

  const data = await loadDashboardData(apiClient, "fallback-date");

  assert.deepEqual(calls, [
    "/me/challenges",
    "/me/stats",
    "/me/activity",
    "/me/achievements",
    "/me/enrollments/101",
    "/me/enrollments/102",
  ]);
  assert.equal(data.user.name, "Stats User");
  assert.equal(data.date, "2026-06-02");
  assert.equal(data.stats.level, 3);
  assert.equal(data.activityEvents.length, 1);
  assert.equal(data.achievements.length, 1);
  assert.deepEqual(
    data.challenges.map((challenge) => ({
      id: challenge.enrollment_id,
      description: challenge.description,
      duration: challenge.duration_days,
      streak: challenge.current_streak,
    })),
    [
      {
        id: 101,
        description: "Done path description",
        duration: 14,
        streak: 4,
      },
      {
        id: 102,
        description: "Ready path description",
        duration: 30,
        streak: 2,
      },
    ],
  );

  const emptyData = await loadDashboardData(
    createApiClient(
      {
        "/me/challenges": { ok: true, challenges: [] },
        "/me/stats": { ok: true, stats: null },
        "/me/activity": { ok: true },
        "/me/achievements": { ok: true },
      },
      [],
    ),
    "fallback-date",
  );

  assert.deepEqual(emptyData.challenges, []);
  assert.equal(emptyData.date, "fallback-date");

  await assert.rejects(
    () =>
      loadDashboardData(
        createApiClient(
          {
            "/me/challenges": new Error("dashboard unavailable"),
            "/me/stats": { ok: true },
          },
          [],
        ),
        "fallback-date",
      ),
    /dashboard unavailable/,
  );
}

run();
