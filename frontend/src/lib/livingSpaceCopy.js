// Display copy for Living Space zones and room objects.
// Backend responses stay unchanged; this maps their stable keys to i18n strings
// and falls back to the backend English text for unknown keys.

function translated(t, te, key, fallback) {
  return key && te(key) ? t(key) : fallback;
}

export function localizeSpaceReward(reward, t, te) {
  if (!reward) return reward;

  const base = `space.roomObjects.${reward.key}`;

  return {
    ...reward,
    title: translated(t, te, `${base}.title`, reward.title),
    description: translated(t, te, `${base}.description`, reward.description),
  };
}

export function spaceZoneTitle(zoneKey, t, te, fallback = "") {
  return translated(t, te, zoneKey ? `space.zoneNames.${zoneKey}` : "", fallback);
}

export function spacePathName(pathKey, t, te) {
  return translated(t, te, pathKey ? `pathContent.${pathKey}.title` : "", pathKey || "");
}

export function localizeSpaceZone(zone, t, te) {
  if (!zone) return zone;

  return {
    ...zone,
    title: spaceZoneTitle(zone.zone_key, t, te, zone.title),
    pathName: spacePathName(zone.path_key, t, te),
    unlocked_objects: (zone.unlocked_objects || []).map((reward) => localizeSpaceReward(reward, t, te)),
    locked_preview_objects: (zone.locked_preview_objects || []).map((reward) => localizeSpaceReward(reward, t, te)),
    next_reward: localizeSpaceReward(zone.next_reward, t, te),
  };
}
