// #413: a link into the room on one challenge's corner and today's step:
// /dashboard?challenge=<id>, plus &joined=1 right after a join (Ringo's "You joined X" card).
// The room resolves the corner from the challenge (its path), with its own selection code.
export function roomLinkPath({ challengeId, joined = false } = {}) {
  const id = String(challengeId ?? "").trim();
  if (!/^\d+$/.test(id)) return "/dashboard";
  return `/dashboard?challenge=${id}${joined ? "&joined=1" : ""}`;
}

export function roomLinkFromSearch(search = "") {
  const params = new URLSearchParams(search || "");
  const id = String(params.get("challenge") || "").trim();
  return {
    challengeId: /^\d+$/.test(id) ? id : null,
    joined: params.get("joined") === "1",
  };
}

// The room's corner (zone) that holds the challenge, from the zones' path challenges.
export function zoneForChallenge(zones = [], challengeId) {
  if (!challengeId) return null;
  return (Array.isArray(zones) ? zones : []).find((zone) => {
    return (zone?.pathDetail?.challenges || []).some((challenge) => String(challenge?.id) === String(challengeId));
  }) || null;
}

// The query without the room link, so a refresh or Back does not re-select the corner or show
// "You joined" again (the room replaces the URL once it has read the link).
export function withoutRoomLink(query = {}) {
  const rest = { ...(query || {}) };
  delete rest.challenge;
  delete rest.joined;
  return rest;
}

export function hasRoomLink(query = {}) {
  return Object.prototype.hasOwnProperty.call(query || {}, "challenge")
    || Object.prototype.hasOwnProperty.call(query || {}, "joined");
}
