import assert from "node:assert/strict";

import {
  applyOptimisticCheckin,
  buildJoinPayload,
  humanizeJoinError,
  isInviteOnlyChallenge,
  submitCheckinFlow,
  submitJoinFlow,
} from "../src/views/challengeFlow.js";
import { hasRoomLink, roomLinkFromSearch, roomLinkPath, withoutRoomLink, zoneForChallenge } from "../src/lib/roomLink.js";

function createRouterRecorder() {
  const pushes = [];

  return {
    pushes,
    router: {
      push(path) {
        pushes.push(path);
      },
    },
  };
}

async function run() {
  assert.equal(isInviteOnlyChallenge({ visibility: "Invite-only" }), true);
  assert.equal(isInviteOnlyChallenge({ visibility: "Public" }), false);
  assert.equal(humanizeJoinError("invalid_join_code"), "Invalid invite code.");
  // B30 S2 (D43): with vue-i18n's t, known codes map to joinErrors.*; unknown text stays readable.
  const fakeT = (key) => `t:${key}`;
  assert.equal(humanizeJoinError("invalid_join_code", fakeT), "t:joinErrors.invalidCode");
  assert.equal(humanizeJoinError("join_code_required", fakeT), "t:joinErrors.codeRequired");
  assert.equal(humanizeJoinError("invite_code_required", fakeT), "t:joinErrors.codeRequired");
  assert.equal(humanizeJoinError("network_down", fakeT), "network down");
  assert.deepEqual(buildJoinPayload({ challenge_id: 1 }, {}), {});
  assert.deepEqual(
    buildJoinPayload(
      { challenge_id: 2, visibility: "Invite-only" },
      { 2: "  launch-code  " },
    ),
    { join_code: "launch-code" },
  );
  assert.throws(
    () => buildJoinPayload({ challenge_id: 2, needs_code: true }, {}),
    /invite_code_required/,
  );

  const { router, pushes } = createRouterRecorder();
  let postedJoin = null;
  const joinResult = await submitJoinFlow({
    apiClient: {
      post: async (path, payload) => {
        postedJoin = { path, payload };
        return { data: { ok: true, enrollment_id: 44 } };
      },
    },
    router,
    challenge: { challenge_id: 9, visibility: "Public" },
  });

  assert.deepEqual(postedJoin, {
    path: "/challenges/9/join",
    payload: {},
  });
  // Joining keeps the user in place by default (join success moment, onboarding, Living Space).
  assert.deepEqual(joinResult, {
    challengeId: 9,
    challengeName: "",
    challengeDescription: "",
    enrollmentId: 44,
    mode: "joined",
    navigated: false,
  });
  assert.deepEqual(pushes, []);

  const navigatingRouter = createRouterRecorder();
  const navigatingResult = await submitJoinFlow({
    apiClient: {
      post: async () => ({ data: { ok: true, enrollment_id: 45, mode: "existing" } }),
    },
    router: navigatingRouter.router,
    challenge: { challenge_id: 11, name: "Daily Strike", visibility: "Public" },
    navigateOnJoin: true,
  });

  assert.deepEqual(navigatingResult, {
    challengeId: 11,
    challengeName: "Daily Strike",
    challengeDescription: "",
    enrollmentId: 45,
    mode: "existing",
    navigated: true,
  });
  assert.deepEqual(navigatingRouter.pushes, ["/enrollment/45"]);

  let reloaded = false;
  const noNavigationResult = await submitJoinFlow({
    apiClient: {
      post: async () => ({ data: { ok: true } }),
    },
    router: createRouterRecorder().router,
    challenge: { challenge_id: 10, visibility: "Public" },
    reload: async () => {
      reloaded = true;
    },
  });

  assert.deepEqual(noNavigationResult, {
    challengeId: 10,
    challengeName: "",
    challengeDescription: "",
    enrollmentId: null,
    mode: "joined",
    navigated: false,
  });
  assert.equal(reloaded, true);

  const optimisticState = {
    challenges: [
      {
        enrollment_id: 101,
        enrollment_name: "Daily Strike",
        today_checked: false,
        current_streak: 2,
      },
    ],
    stats: {
      total_points: 30,
      total_checkins: 3,
      current_streak: 2,
      next_level_xp: 100,
      xp: 30,
      progress_percent: 30,
      level: 1,
    },
    activityEvents: [],
  };

  const snapshot = applyOptimisticCheckin(optimisticState, 101);

  assert.equal(snapshot.oldStats.total_points, 30);
  assert.equal(optimisticState.challenges[0].today_checked, true);
  assert.equal(optimisticState.challenges[0].current_streak, 3);
  assert.equal(optimisticState.stats.total_points, 40);
  assert.equal(optimisticState.stats.total_checkins, 4);
  assert.equal(optimisticState.activityEvents[0].type, "checkin");

  const successState = {
    challenges: [
      {
        enrollment_id: 201,
        enrollment_name: "Move Your Body",
        today_checked: false,
        current_streak: 1,
      },
    ],
    stats: {
      total_points: 20,
      total_checkins: 2,
      current_streak: 1,
      next_level_xp: 100,
      xp: 20,
      progress_percent: 20,
      level: 1,
    },
    activityEvents: [],
    achievements: [],
    error: "",
  };
  const stateSnapshots = [];
  const pulseValues = [];
  const apiCalls = [];

  const result = await submitCheckinFlow({
    apiClient: {
      post: async (path) => {
        apiCalls.push(path);
        return {
          data: {
            rewards: {
              achievements: [{ title: "First Strike" }],
            },
          },
        };
      },
      get: async (path) => {
        apiCalls.push(path);

        if (path === "/me/stats") {
          return {
            data: {
              stats: {
                ...successState.stats,
                total_points: 30,
                level: 2,
              },
            },
          };
        }

        if (path === "/me/activity") {
          return { data: { events: [{ id: "server-event" }] } };
        }

        if (path === "/me/achievements") {
          return { data: { achievements: [{ key: "first_strike" }] } };
        }

        throw new Error(`Unexpected path ${path}`);
      },
    },
    state: successState,
    enrollmentId: 201,
    onStateChange: (state) => {
      stateSnapshots.push({
        checked: state.challenges[0].today_checked,
        points: state.stats.total_points,
        error: state.error,
      });
    },
    setPulse: (value) => pulseValues.push(value),
    schedule: (callback, delay) => {
      assert.equal(delay, 520);
      callback();
    },
  });

  assert.deepEqual(apiCalls, [
    "/me/challenges/201/checkin",
    "/me/stats",
    "/me/activity",
    "/me/achievements",
  ]);
  assert.equal(result.unlocked[0].title, "First Strike");
  assert.equal(successState.stats.level, 2);
  assert.deepEqual(pulseValues, [true, false]);
  assert.deepEqual(stateSnapshots[0], {
    checked: true,
    points: 30,
    error: "",
  });

  const failureState = {
    challenges: [
      {
        enrollment_id: 301,
        enrollment_name: "Learn One Thing",
        today_checked: false,
        current_streak: 5,
      },
    ],
    stats: {
      total_points: 50,
      total_checkins: 5,
      current_streak: 5,
      next_level_xp: 100,
      xp: 50,
      progress_percent: 50,
      level: 1,
    },
    activityEvents: [{ id: "old-event" }],
    achievements: [],
    error: "",
  };

  const failure = await submitCheckinFlow({
    apiClient: {
      post: async () => {
        throw new Error("checkin_failed");
      },
    },
    state: failureState,
    enrollmentId: 301,
    schedule: (callback) => callback(),
  });

  assert.equal(failure.error, "checkin_failed");
  assert.equal(failureState.challenges[0].today_checked, false);
  assert.equal(failureState.challenges[0].current_streak, 5);
  assert.equal(failureState.stats.total_points, 50);
  assert.deepEqual(failureState.activityEvents, [{ id: "old-event" }]);
}

// #413: the challenge page sends the user into the room: "Do today's step in your room" opens
// /dashboard?challenge=<id>; a join from the challenge page adds &joined=1 (Ringo's "You joined").
function runRoomLinkSmoke() {
  assert.equal(roomLinkPath({ challengeId: 45 }), "/dashboard?challenge=45");
  assert.equal(roomLinkPath({ challengeId: "45", joined: true }), "/dashboard?challenge=45&joined=1");
  assert.equal(roomLinkPath({ challengeId: null }), "/dashboard", "no id: the plain room");
  assert.equal(roomLinkPath({ challengeId: "45x" }), "/dashboard", "only numeric ids");
  assert.deepEqual(roomLinkFromSearch("?challenge=45&joined=1"), { challengeId: "45", joined: true });
  assert.deepEqual(roomLinkFromSearch("?challenge=45"), { challengeId: "45", joined: false });
  assert.deepEqual(roomLinkFromSearch("?firstRun=1"), { challengeId: null, joined: false });
  assert.deepEqual(roomLinkFromSearch("?challenge=<script>"), { challengeId: null, joined: false });
  // Round trip.
  assert.deepEqual(roomLinkFromSearch(roomLinkPath({ challengeId: 7, joined: true }).split("?")[1]), { challengeId: "7", joined: true });

  const zones = [
    { zone_key: "work_desk", pathDetail: { challenges: [{ id: 30 }, { id: 31 }] } },
    { zone_key: "fitness_corner", pathDetail: { challenges: [{ id: 45 }] } },
    { zone_key: "sleep_corner" },
  ];
  assert.equal(zoneForChallenge(zones, "45")?.zone_key, "fitness_corner");
  assert.equal(zoneForChallenge(zones, 31)?.zone_key, "work_desk");
  assert.equal(zoneForChallenge(zones, "99"), null, "unknown challenge: no corner (the room stays on the overview)");
  assert.equal(zoneForChallenge(zones, null), null);

  // Read once: the room replaces the URL without the link, keeping any other query.
  assert.equal(hasRoomLink({ challenge: "45", joined: "1" }), true);
  assert.equal(hasRoomLink({ joined: "1" }), true, "a stray joined=1 is cleared too");
  assert.equal(hasRoomLink({ firstRun: "1" }), false);
  assert.equal(hasRoomLink(undefined), false);
  assert.deepEqual(withoutRoomLink({ challenge: "45", joined: "1" }), {});
  assert.deepEqual(withoutRoomLink({ challenge: "45", firstRun: "1", tab: "x" }), { firstRun: "1", tab: "x" });
  const original = { challenge: "45" };
  withoutRoomLink(original);
  assert.deepEqual(original, { challenge: "45" }, "the route query object is not mutated");
}

run();
runRoomLinkSmoke();
