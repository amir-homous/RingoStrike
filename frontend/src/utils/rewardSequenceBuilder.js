import { buildMissionPathGroups, normalizedMissionIntensity, missionHasStatus } from "@/utils/missionMomentumUtils";

function safeNumber(value, fallback = null) {
  if (value === null || value === undefined || value === "") return fallback;
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function boundedPercent(value) {
  const number = safeNumber(value, 0);
  return Math.max(0, Math.min(100, Math.round(number)));
}

function calculateNextLevelXp(level) {
  const safeLevel = Math.max(1, Number.parseInt(level, 10) || 1);
  return Math.round(100 * (safeLevel ** 1.5));
}

function calculateLevel(xp) {
  const safeXp = Math.max(0, Number.parseInt(xp, 10) || 0);
  let level = 1;

  while (safeXp >= calculateNextLevelXp(level)) {
    level += 1;
  }

  return level;
}

function calculateProgressPercent(xp, level) {
  const safeXp = Math.max(0, Number.parseInt(xp, 10) || 0);
  const safeLevel = Math.max(1, Number.parseInt(level, 10) || 1);
  const currentLevelFloor = safeLevel <= 1 ? 0 : calculateNextLevelXp(safeLevel - 1);
  const nextLevelXp = calculateNextLevelXp(safeLevel);
  const span = Math.max(1, nextLevelXp - currentLevelFloor);
  const progressed = Math.max(0, safeXp - currentLevelFloor);

  return boundedPercent(Math.floor((progressed / span) * 100));
}

function buildXpSnapshot(stats = {}, completionResult = null) {
  const completionTotal = completionResult?.checkin?.rewards?.xp_total
    ?? completionResult?.rewards?.xp_total;
  const hasCompletionTotal = safeNumber(completionTotal, null) !== null;
  const total = safeNumber(
    completionTotal
      ?? stats?.total_points
      ?? stats?.xp,
  );

  const level = hasCompletionTotal && total !== null
    ? calculateLevel(total)
    : safeNumber(stats?.level, total !== null ? calculateLevel(total) : null);
  const nextLevelXp = hasCompletionTotal && level !== null
    ? calculateNextLevelXp(level)
    : safeNumber(stats?.next_level_xp, level !== null ? calculateNextLevelXp(level) : null);
  const progressPercent = safeNumber(
    hasCompletionTotal ? null : stats?.progress_percent,
    total !== null && level !== null ? calculateProgressPercent(total, level) : null,
  );

  return {
    total,
    level,
    nextLevelXp,
    progressPercent,
  };
}

function mapPathGroups(pathGroups = []) {
  const paths = new Map();
  const challenges = new Map();

  pathGroups.forEach((path) => {
    const pathKey = String(path?.pathId || path?.id || path?.key || "").trim();
    if (pathKey) {
      paths.set(pathKey, {
        key: pathKey,
        pathId: path?.pathId || path?.id || pathKey,
        title: path?.title || "",
        icon: path?.iconUrl || "",
        color: path?.color || "",
        progress: boundedPercent(path?.stats?.percent),
        done: safeNumber(path?.stats?.done, 0),
        total: safeNumber(path?.stats?.total, 0),
      });
    }

    (path?.challenges || []).forEach((challenge) => {
      const challengeKey = String(challenge?.challengeId || challenge?.id || challenge?.key || "").trim();
      if (!challengeKey) return;

      challenges.set(challengeKey, {
        key: challengeKey,
        challengeId: challenge?.challengeId || challenge?.id || challengeKey,
        pathKey,
        title: challenge?.title || "",
        icon: challenge?.iconUrl || "",
        progress: boundedPercent(challenge?.stats?.percent),
        done: safeNumber(challenge?.stats?.done, 0),
        total: safeNumber(challenge?.stats?.total, 0),
      });
    });
  });

  return { paths, challenges };
}

function resolvePathGroups(missions, pathGroups, fallbacks = {}) {
  if (Array.isArray(pathGroups) && pathGroups.length) return pathGroups;
  return buildMissionPathGroups(missions || [], fallbacks);
}

function findMission(missions = [], mission) {
  const missionId = mission?.mission_id;
  if (missionId === null || missionId === undefined) return mission || null;

  return missions.find((item) => String(item?.mission_id) === String(missionId)) || mission || null;
}

export function buildRewardSnapshot({
  missions = [],
  pathGroups = [],
  stats = null,
  guidanceProgress = null,
  mission = null,
  completionResult = null,
  fallbacks = {},
} = {}) {
  const selectedMission = findMission(missions, mission);
  const groups = resolvePathGroups(missions, pathGroups, fallbacks);
  const groupMaps = mapPathGroups(groups);
  const todaySafe = Object.prototype.hasOwnProperty.call(guidanceProgress || {}, "today_saved")
    ? Boolean(guidanceProgress.today_saved)
    : missions.some((item) => normalizedMissionIntensity(item) !== "bonus" && missionHasStatus(item, "done"));

  return {
    todaySafe,
    currentStreak: safeNumber(guidanceProgress?.current_streak ?? stats?.current_streak, null),
    xp: buildXpSnapshot(stats || {}, completionResult),
    mission: selectedMission ? { ...selectedMission } : null,
    paths: groupMaps.paths,
    challenges: groupMaps.challenges,
  };
}

function missionContext(completionResult, fallbackMission) {
  const merged = {
    ...(fallbackMission || {}),
    ...(completionResult?.mission || {}),
  };

  return {
    mission_id: merged.mission_id || fallbackMission?.mission_id || null,
    key: merged.key || merged.mission_key || fallbackMission?.key || fallbackMission?.mission_key || "",
    title: merged.title || fallbackMission?.title || "",
    intensity: normalizedMissionIntensity(merged),
    pathId: String(merged.path_id || fallbackMission?.path_id || "").trim(),
    pathTitle: merged.path_title || fallbackMission?.path_title || "",
    challengeId: String(merged.challenge_id || fallbackMission?.challenge_id || "").trim(),
    challengeTitle: merged.challenge_name || fallbackMission?.challenge_name || "",
    icon: merged.path_icon || fallbackMission?.path_icon || "",
    color: merged.path_color || fallbackMission?.path_color || "",
  };
}

function progressChanged(beforeItem, afterItem) {
  if (!beforeItem || !afterItem) return false;
  return boundedPercent(beforeItem.progress) !== boundedPercent(afterItem.progress)
    || safeNumber(beforeItem.done, 0) !== safeNumber(afterItem.done, 0);
}

function xpAwarded(completionResult) {
  const amount = safeNumber(
    completionResult?.mission?.xp_awarded
      ?? completionResult?.mission?.xp_earned
      ?? completionResult?.xp_awarded
      ?? completionResult?.xp_earned,
    0,
  );
  return amount > 0 ? amount : 0;
}

function alreadyDone(completionResult) {
  return Boolean(completionResult?.mission?.already_done);
}

function translateFallback(key, params = {}) {
  return key.replace(/\{(\w+)\}/g, (_, name) => params[name] ?? "");
}

function translator(t) {
  return typeof t === "function" ? t : translateFallback;
}

function finalChoiceActions(translate) {
  return [{
    key: "finish_today",
    variant: "primary",
    label: translate("missions.finishForToday"),
  }, {
    key: "view_choices",
    variant: "secondary",
    label: translate("missions.dailyMomentum.actions.viewChoices"),
  }];
}

function missionTitleFrom(response) {
  return response?.mission?.title || "";
}

function missionCompletionTitleKey(intensity) {
  if (intensity === "bonus") return "bonusCompleteTitle";
  if (intensity === "tiny") return "tinyCompleteTitle";
  return "completeTitle";
}

function normalizeBackendStep(step = {}, normalized, translate) {
  const rawType = String(step?.type || "default").trim();
  const typeMap = {
    mission_completed: "mission_complete",
    next_choice: "final_choice",
  };
  const type = typeMap[rawType] || rawType;
  const amount = safeNumber(step?.amount, null);
  const xpValue = type === "xp_earned" && !step?.value
    ? translate("ringoRewardSequence.local.xpValue", {
      count: amount || normalized.xpAwarded,
    })
    : "";
  const missionTitle = missionTitleFrom({ mission: normalized.mission });
  const missionTitleKey = missionCompletionTitleKey(normalizedMissionIntensity(normalized.mission));

  return {
    ...step,
    type,
    missionKey: step?.missionKey || step?.mission_key || normalized.mission?.key || normalized.mission?.mission_key || "",
    title: type === "mission_complete"
      ? missionTitle || step?.title || translate("ringoRewardSequence.local.missionFallback")
      : step?.title || "",
    text: step?.text || (type === "mission_complete"
      ? translate(`ringoRewardSequence.staged.${missionTitleKey}`)
      : ""),
    value: step?.value || xpValue,
    sprite: step?.sprite || step?.mood || "",
    actions: type === "final_choice"
      ? finalChoiceActions(translate)
      : step?.actions,
  };
}

export function normalizeMissionCompletionRewardResponse(response = {}, { t } = {}) {
  const translate = translator(t);
  const mission = response?.mission || {};
  const alreadyDoneValue = Boolean(mission?.already_done);
  const xpAwardedValue = Math.max(
    0,
    safeNumber(mission?.xp_awarded ?? mission?.xp_earned ?? response?.xp_awarded ?? response?.xp_earned, 0),
  );
  const backendRewardSequence = Array.isArray(response?.reward_sequence)
    ? response.reward_sequence
    : [];
  const normalized = {
    mission,
    alreadyDone: alreadyDoneValue,
    xpAwarded: xpAwardedValue,
    backendRewardSequence,
    backendSteps: [],
  };

  normalized.backendSteps = backendRewardSequence
    .map((step) => normalizeBackendStep(step, normalized, translate))
    .filter((step) => step?.type && (step.title || step.text || step.value || step.actions?.length));

  return normalized;
}

export function buildRewardDelta(beforeSnapshot, afterSnapshot, completionResult = {}) {
  const mission = missionContext(completionResult, beforeSnapshot?.mission || afterSnapshot?.mission);
  const intensity = mission.intensity;
  const awarded = xpAwarded(completionResult);
  const oldXp = beforeSnapshot?.xp || {};
  const newXp = afterSnapshot?.xp || {};
  const pathBefore = beforeSnapshot?.paths?.get(mission.pathId) || null;
  const pathAfter = afterSnapshot?.paths?.get(mission.pathId) || null;
  const challengeBefore = beforeSnapshot?.challenges?.get(mission.challengeId) || null;
  const challengeAfter = afterSnapshot?.challenges?.get(mission.challengeId) || null;
  const oldLevel = safeNumber(oldXp.level, null);
  const newLevel = safeNumber(newXp.level, null);

  return {
    alreadyDone: alreadyDone(completionResult),
    mission,
    strike: {
      changed: intensity !== "bonus" && beforeSnapshot?.todaySafe === false && afterSnapshot?.todaySafe === true,
      wasSafeBefore: Boolean(beforeSnapshot?.todaySafe),
      isSafeAfter: Boolean(afterSnapshot?.todaySafe),
      oldStreak: safeNumber(beforeSnapshot?.currentStreak, null),
      newStreak: safeNumber(afterSnapshot?.currentStreak, null),
    },
    xp: {
      awarded,
      oldTotal: safeNumber(oldXp.total, null),
      newTotal: safeNumber(newXp.total, null),
      oldProgress: safeNumber(oldXp.progressPercent, null),
      newProgress: safeNumber(newXp.progressPercent, null),
      oldLevel,
      newLevel,
      leveledUp: oldLevel !== null && newLevel !== null && newLevel > oldLevel,
    },
    path: {
      changed: progressChanged(pathBefore, pathAfter),
      pathId: pathAfter?.pathId || pathBefore?.pathId || mission.pathId,
      title: pathAfter?.title || pathBefore?.title || mission.pathTitle,
      icon: pathAfter?.icon || pathBefore?.icon || mission.icon,
      color: pathAfter?.color || pathBefore?.color || mission.color,
      oldProgress: pathBefore ? boundedPercent(pathBefore.progress) : null,
      newProgress: pathAfter ? boundedPercent(pathAfter.progress) : null,
    },
    challenge: {
      changed: progressChanged(challengeBefore, challengeAfter),
      secured: completionResult?.checkin?.ok === true
        && completionResult?.checkin?.already_checked === false
        && completionResult?.checkin?.mode === "created"
        && intensity !== "bonus",
      challengeId: challengeAfter?.challengeId || challengeBefore?.challengeId || mission.challengeId,
      title: challengeAfter?.title || challengeBefore?.title || mission.challengeTitle,
      icon: challengeAfter?.icon || challengeBefore?.icon || "",
      oldProgress: challengeBefore ? boundedPercent(challengeBefore.progress) : null,
      newProgress: challengeAfter ? boundedPercent(challengeAfter.progress) : null,
      oldStreak: safeNumber(beforeSnapshot?.currentStreak, null),
      newStreak: safeNumber(afterSnapshot?.currentStreak, null),
    },
  };
}

function hasProgressPair(item) {
  return item?.oldProgress !== null
    && item?.oldProgress !== undefined
    && item?.newProgress !== null
    && item?.newProgress !== undefined;
}

export function buildRewardSteps(delta, { t } = {}) {
  const translate = translator(t);
  if (!delta || delta.alreadyDone) return [];

  const intensity = delta.mission?.intensity || "main";
  const titleKey = missionCompletionTitleKey(intensity);
  const missionTitle = delta.mission?.title || translate("ringoRewardSequence.local.missionFallback");
  const steps = [{
    type: "mission_complete",
    missionKey: delta.mission?.key || "",
    title: missionTitle,
    text: translate(`ringoRewardSequence.staged.${titleKey}`),
    sprite: intensity === "bonus" ? "happy" : "celebration",
  }];

  if (delta.strike?.changed) {
    steps.push({
      type: "strike_secured",
      title: translate(
        intensity === "tiny"
          ? "ringoRewardSequence.staged.tinyStrikeTitle"
          : "ringoRewardSequence.staged.strikeTitle",
      ),
      text: translate("ringoRewardSequence.staged.strikeText", {
        streak: delta.strike.newStreak ?? 0,
      }),
      value: delta.strike.newStreak !== null && delta.strike.newStreak !== undefined
        ? translate("ringoRewardSequence.staged.streakValue", { count: delta.strike.newStreak })
        : "",
      oldStreak: delta.strike.oldStreak,
      newStreak: delta.strike.newStreak,
      sprite: "proud",
    });
  }

  if (delta.xp?.awarded > 0) {
    steps.push({
      type: "xp_earned",
      title: translate("ringoRewardSequence.staged.xpTitle"),
      text: translate("ringoRewardSequence.staged.xpText"),
      value: translate("ringoRewardSequence.local.xpValue", { count: delta.xp.awarded }),
      progressBar: delta.xp.oldProgress !== null && delta.xp.newProgress !== null
        ? {
          old: delta.xp.oldProgress,
          new: delta.xp.newProgress,
          oldLevel: delta.xp.oldLevel,
          newLevel: delta.xp.newLevel,
        }
        : null,
      meta: delta.xp.newTotal !== null
        ? translate("ringoRewardSequence.staged.totalXp", { count: delta.xp.newTotal })
        : "",
      sprite: "happy",
    });
  }

  if (delta.xp?.leveledUp) {
    steps.push({
      type: "level_up",
      title: translate("ringoRewardSequence.staged.levelTitle", { level: delta.xp.newLevel }),
      text: translate("ringoRewardSequence.staged.levelText"),
      value: translate("common.level", { level: delta.xp.newLevel }),
      sprite: "victory",
    });
  }

  if (delta.path?.changed && hasProgressPair(delta.path)) {
    steps.push({
      type: "path_strengthened",
      pathId: delta.path.pathId,
      pathTitle: delta.path.title,
      title: translate("ringoRewardSequence.staged.pathTitle"),
      text: translate("ringoRewardSequence.staged.pathText", {
        path: delta.path.title || translate("missions.fallbackPath"),
      }),
      value: translate("ringoRewardSequence.staged.progressValue", { percent: delta.path.newProgress }),
      progressBar: {
        old: delta.path.oldProgress,
        new: delta.path.newProgress,
        color: delta.path.color,
      },
      icon: delta.path.icon,
      color: delta.path.color,
      sprite: "encouraging",
    });
  }

  if (delta.challenge?.changed && hasProgressPair(delta.challenge)) {
    steps.push({
      type: "challenge_strengthened",
      challengeId: delta.challenge.challengeId,
      challengeTitle: delta.challenge.title,
      title: translate("ringoRewardSequence.staged.challengeTitle"),
      text: translate("ringoRewardSequence.staged.challengeText", {
        challenge: delta.challenge.title || translate("missions.fallbackChallenge"),
      }),
      value: translate("ringoRewardSequence.staged.progressValue", { percent: delta.challenge.newProgress }),
      progressBar: {
        old: delta.challenge.oldProgress,
        new: delta.challenge.newProgress,
      },
      icon: delta.challenge.icon,
      sprite: "focus",
    });
  }

  if (delta.challenge?.secured) {
    steps.push({
      type: "challenge_secured",
      challengeId: delta.challenge.challengeId,
      challengeTitle: delta.challenge.title,
      title: translate("ringoRewardSequence.staged.challengeSecuredTitle"),
      text: translate("ringoRewardSequence.staged.challengeSecuredText"),
      icon: delta.challenge.icon,
      sprite: "proud",
    });
  }

  steps.push({
    type: "final_choice",
    title: translate("ringoRewardSequence.staged.finalTitle"),
    text: translate("ringoRewardSequence.staged.finalText"),
    sprite: "sleeping",
    actions: finalChoiceActions(translate),
  });

  return steps;
}

function hasStep(steps, type) {
  return steps.some((step) => step?.type === type);
}

function frontendStepByType(steps, type) {
  return steps.find((step) => step?.type === type) || null;
}

function mergeFrontendVisualDetails(steps, frontendSteps) {
  ["mission_complete", "xp_earned", "strike_secured", "path_strengthened", "challenge_strengthened", "challenge_secured"].forEach((type) => {
    const target = steps.find((step) => step?.type === type);
    const source = frontendStepByType(frontendSteps, type);
    if (!target || !source) return;

    [
      "progressBar",
      "meta",
      "icon",
      "color",
      "pathId",
      "pathTitle",
      "challengeId",
      "challengeTitle",
      "oldStreak",
      "newStreak",
      "missionKey",
    ].forEach((key) => {
      if (target[key] === undefined || target[key] === null || target[key] === "") {
        target[key] = source[key];
      }
    });

    if (!target.sprite && source.sprite) {
      target.sprite = source.sprite;
    }

    if (target.progressBar && source.progressBar) {
      ["oldLevel", "newLevel", "color"].forEach((key) => {
        if (target.progressBar[key] === undefined || target.progressBar[key] === null || target.progressBar[key] === "") {
          target.progressBar[key] = source.progressBar[key];
        }
      });
    }
  });
}

function fallbackMissionCompleteStep(normalized, translate) {
  const missionTitle = missionTitleFrom({ mission: normalized.mission })
    || translate("ringoRewardSequence.local.missionFallback");
  const intensity = normalizedMissionIntensity(normalized.mission);
  const titleKey = missionCompletionTitleKey(intensity);

  return {
    type: "mission_complete",
    missionKey: normalized.mission?.key || normalized.mission?.mission_key || "",
    title: missionTitle,
    text: translate(`ringoRewardSequence.staged.${titleKey}`),
    sprite: intensity === "bonus" ? "happy" : "celebration",
  };
}

function fallbackXpStep(normalized, translate) {
  return {
    type: "xp_earned",
    title: translate("ringoRewardSequence.staged.xpTitle"),
    text: translate("ringoRewardSequence.staged.xpText"),
    value: translate("ringoRewardSequence.local.xpValue", { count: normalized.xpAwarded }),
    sprite: "happy",
  };
}

function fallbackFinalChoiceStep(translate) {
  return {
    type: "final_choice",
    title: translate("ringoRewardSequence.staged.finalTitle"),
    text: translate("ringoRewardSequence.staged.finalText"),
    sprite: "sleeping",
    actions: finalChoiceActions(translate),
  };
}

export function buildMissionCompletionRewardSteps(delta, response = {}, { t } = {}) {
  const translate = translator(t);
  const normalized = normalizeMissionCompletionRewardResponse(response, { t });

  if (normalized.alreadyDone) {
    return {
      normalized,
      steps: [],
      frontendSteps: [],
      backendSteps: normalized.backendSteps,
    };
  }

  const frontendSteps = buildRewardSteps(delta, { t });
  const steps = normalized.backendSteps.length
    ? [...normalized.backendSteps]
    : [...frontendSteps];
  mergeFrontendVisualDetails(steps, frontendSteps);

  ["strike_secured", "level_up", "path_strengthened", "challenge_strengthened", "challenge_secured"].forEach((type) => {
    const frontendStep = frontendStepByType(frontendSteps, type);
    if (frontendStep && !hasStep(steps, type)) {
      const finalIndex = steps.findIndex((step) => step?.type === "final_choice");
      if (finalIndex >= 0) steps.splice(finalIndex, 0, frontendStep);
      else steps.push(frontendStep);
    }
  });

  if (hasStep(steps, "strike_secured")) {
    const safetyIndex = steps.findIndex((step) => step?.type === "today_saved");
    if (safetyIndex >= 0) steps.splice(safetyIndex, 1);
  }

  if (normalized.xpAwarded > 0) {
    if (!hasStep(steps, "mission_complete")) {
      steps.unshift(frontendStepByType(frontendSteps, "mission_complete") || fallbackMissionCompleteStep(normalized, translate));
    }

    if (!hasStep(steps, "xp_earned")) {
      const finalIndex = steps.findIndex((step) => step?.type === "final_choice");
      const xpStep = frontendStepByType(frontendSteps, "xp_earned") || fallbackXpStep(normalized, translate);
      if (finalIndex >= 0) steps.splice(finalIndex, 0, xpStep);
      else steps.push(xpStep);
    }
  }

  if (!hasStep(steps, "final_choice")) {
    steps.push(frontendStepByType(frontendSteps, "final_choice") || fallbackFinalChoiceStep(translate));
  }

  return {
    normalized,
    steps,
    frontendSteps,
    backendSteps: normalized.backendSteps,
  };
}
