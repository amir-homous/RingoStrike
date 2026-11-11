import assert from "node:assert/strict";

import {
  buildJoinPayload,
  humanizeJoinError,
  isInviteOnlyChallenge,
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
