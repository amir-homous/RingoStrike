// Stable challenge icon keys (decision D5).
// Challenges are seeded and upserted by name (backend/services/path_seed_service.py),
// so the icon key is the slug of the English seed name, e.g. "Deep Work Sprint" -> "deep-work-sprint".
// Numeric ids are kept only as a legacy alias for databases seeded before keys existed.

export const LEGACY_CHALLENGE_ICON_IDS = Object.freeze({
  30: "deep-work-sprint",
  31: "move-your-body",
  32: "learn-one-thing",
  33: "mind-reset",
  34: "strength-starter",
  35: "mobility-reset",
  36: "read-five-pages",
  37: "practice-skill",
  38: "portfolio-pulse",
  39: "network-signal",
  40: "creative-spark",
  41: "publish-tiny",
  42: "idea-remix",
  43: "sleep-wind-down",
  44: "morning-recovery",
});

export function challengeIconKey(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function legacyIdKey(value) {
  const id = String(value ?? "").trim();
  return /^\d+$/.test(id) ? LEGACY_CHALLENGE_ICON_IDS[id] || "" : "";
}

// Accepts a challenge-like object, a key/name string, or a numeric id.
// Returns icon keys in priority order: explicit key, seed name, legacy id alias.
export function challengeIconCandidates(ref) {
  if (ref === null || ref === undefined) return [];

  if (typeof ref !== "object") {
    const value = String(ref).trim();
    return [/^\d+$/.test(value) ? legacyIdKey(value) : challengeIconKey(value)].filter(Boolean);
  }

  const candidates = [
    ref.icon_key,
    ref.iconKey,
    ref.challenge_icon_key,
    ref.key,
    ref.slug,
    ref.name,
    ref.challenge_name,
  ].map(challengeIconKey);

  candidates.push(legacyIdKey(ref.challenge_id ?? ref.challengeId ?? ref.id));

  return [...new Set(candidates.filter(Boolean))];
}
