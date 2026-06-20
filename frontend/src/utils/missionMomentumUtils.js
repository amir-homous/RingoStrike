const pathIconModules = import.meta.glob("../assets/path-icons/*.png", { eager: true, import: "default" });
const challengeIconModules = import.meta.glob("../assets/challenge-icons/*.png", { eager: true, import: "default" });
const missionIconModules = import.meta.glob("../assets/missions-icons/**/*.png", { eager: true, import: "default" });

export function stableGroupKey(prefix, value) {
  return `${prefix}-${String(value || "default").trim().toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
}

export function normalizedMissionIntensity(mission) {
  const value = String(mission?.mission_intensity || "main").toLowerCase();
  return ["main", "tiny", "bonus"].includes(value) ? value : "main";
}

export function normalizedMissionStatus(missionOrStatus) {
  const raw = typeof missionOrStatus === "object"
    ? missionOrStatus?.status
    : missionOrStatus;
  const value = String(raw || "pending")
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");

  if (["done", "complete", "completed"].includes(value)) return "done";
  if (["skipped", "skip"].includes(value)) return "skipped";
  if (["remind_later", "reminder_set", "reminded"].includes(value)) return "remind_later";

  return value || "pending";
}

export function missionHasStatus(mission, ...statuses) {
  return statuses.includes(normalizedMissionStatus(mission));
}

export function reminderTimestamp(mission) {
  if (!mission?.reminder_at) return Number.POSITIVE_INFINITY;

  const timestamp = new Date(mission.reminder_at).getTime();
  return Number.isNaN(timestamp) ? Number.POSITIVE_INFINITY : timestamp;
}

export function isReminderDue(mission) {
  return missionHasStatus(mission, "remind_later") && reminderTimestamp(mission) <= Date.now();
}

export function missionXpValue(mission) {
  const reward = Number(mission?.xp_reward || 0);
  const earned = Number(mission?.xp_earned || 0);
  const amount = Math.max(reward, earned);
  return Number.isFinite(amount) && amount > 0 ? amount : 0;
}

export function summarizeMissions(missions) {
  const items = Array.isArray(missions) ? missions : [];
  const total = items.length;
  const done = items.filter((mission) => missionHasStatus(mission, "done")).length;
  const pending = items.filter((mission) => missionHasStatus(mission, "pending")).length;
  const reminded = items.filter((mission) => missionHasStatus(mission, "remind_later")).length;
  const skipped = items.filter((mission) => missionHasStatus(mission, "skipped")).length;
  const reminderDue = items.filter(isReminderDue).length;
  const futureReminders = items.filter((mission) => {
    return missionHasStatus(mission, "remind_later") && !isReminderDue(mission);
  }).length;
  const minutes = items.reduce((sum, mission) => {
    const value = Number(mission?.estimated_minutes || 0);
    return Number.isFinite(value) && value > 0 ? sum + value : sum;
  }, 0);
  const totalXp = items.reduce((sum, mission) => sum + missionXpValue(mission), 0);
  const earnedXp = items.reduce((sum, mission) => {
    if (!missionHasStatus(mission, "done")) return sum;

    const earned = Number(mission?.xp_earned || 0);
    const amount = Number.isFinite(earned) && earned > 0 ? earned : missionXpValue(mission);
    return sum + amount;
  }, 0);
  const remainingXp = Math.max(0, totalXp - earnedXp);
  const percent = total > 0 ? Math.round((done / total) * 100) : 0;

  return {
    total,
    done,
    pending,
    reminded,
    futureReminders,
    skipped,
    reminderDue,
    minutes,
    xp: totalXp,
    earnedXp,
    totalXp,
    remainingXp,
    percent,
  };
}

export function isGroupRelevant(stats) {
  return Boolean(
    stats?.pending
    || stats?.reminded
    || stats?.reminderDue
    || stats?.futureReminders
    || stats?.skipped
    || (Number(stats?.total || 0) > 0 && Number(stats?.percent || 0) === 100),
  );
}

export function groupStatus(stats) {
  if (stats?.reminderDue) return "reminder_due";
  if (stats?.futureReminders || stats?.reminded) return "reminder_set";
  if (Number(stats?.total || 0) > 0 && Number(stats?.done || 0) === Number(stats?.total || 0)) return "done";
  if (stats?.done > 0) return "in_progress";
  if (stats?.skipped && !stats?.pending) return "skipped";
  if (stats?.pending) return "ready";

  return "optional";
}

export function buildMissionPathGroups(missions, fallbacks = {}) {
  const paths = new Map();
  const fallbackPath = fallbacks.path || "Your path";
  const fallbackChallenge = fallbacks.challenge || "your challenge";

  (Array.isArray(missions) ? missions : []).forEach((mission) => {
    const pathKey = stableGroupKey("path", mission.path_id || mission.path_title || "default");
    const pathTitle = mission.path_title || fallbackPath;
    const pathIconName = pathIconNameFor(mission);
    const challengeKey = stableGroupKey(
      "challenge",
      mission.challenge_id || mission.challenge_name || mission.enrollment_id || "default",
    );
    const challengeTitle = mission.challenge_name || fallbackChallenge;
    const challengeIconName = String(mission.challenge_id || "").trim();

    if (!paths.has(pathKey)) {
      paths.set(pathKey, {
        key: pathKey,
        id: mission.path_id || pathKey,
        pathId: mission.path_id || null,
        title: pathTitle,
        iconUrl: resolvePathIcon(pathIconName),
        color: pathColorFor(mission, pathIconName),
        missions: [],
        challenges: new Map(),
      });
    }

    const path = paths.get(pathKey);
    if (!path.challenges.has(challengeKey)) {
      path.challenges.set(challengeKey, {
        key: challengeKey,
        id: mission.challenge_id || challengeKey,
        challengeId: mission.challenge_id || null,
        title: challengeTitle,
        iconUrl: resolveChallengeIcon(challengeIconName),
        missions: [],
      });
    }

    path.missions.push(mission);
    path.challenges.get(challengeKey).missions.push(mission);
  });

  return Array.from(paths.values()).map((path) => {
    const challenges = Array.from(path.challenges.values()).map((challenge) => {
      const stats = summarizeMissions(challenge.missions);

      return {
        ...challenge,
        stats,
        status: groupStatus(stats),
        relevant: isGroupRelevant(stats),
      };
    });

    const stats = summarizeMissions(path.missions);
    stats.challengeCount = challenges.length;
    stats.completedChallenges = challenges.filter((challenge) => challenge.stats.percent === 100).length;

    return {
      ...path,
      challenges,
      stats,
      status: groupStatus(stats),
      relevant: challenges.some((challenge) => challenge.relevant),
    };
  });
}

export function progressVars(percent, color) {
  return {
    "--progress-percent": `${boundedPercent(percent)}%`,
    "--progress-color": safeColor(color),
  };
}

export function ringVars(percent, color) {
  const percentValue = boundedPercent(percent);
  const circumference = 2 * Math.PI * 42;
  return {
    "--ring-percent": percentValue,
    "--ring-circumference": circumference,
    "--ring-dashoffset": circumference * (1 - (percentValue / 100)),
    "--ring-offset": 100 - percentValue,
    "--ring-color": safeColor(color),
  };
}

export function safeColor(color) {
  const value = String(color || "").trim();
  return /^#[0-9a-f]{3}([0-9a-f]{3})?$/i.test(value) ? value : "#f7d774";
}

export function initialsFor(value) {
  const words = String(value || "").trim().split(/\s+/).filter(Boolean);
  const initials = words.slice(0, 2).map((word) => word.slice(0, 1)).join("");
  return initials || "*";
}

export function missionIconUrl(mission) {
  const candidates = missionIconCandidates(mission);

  for (const candidate of candidates) {
    const icon = iconFromModules(missionIconModules, candidate);
    if (icon) return icon;
  }

  return iconFromModules(missionIconModules, "default_missions_icon");
}

export function pathIconNameFor(mission) {
  const explicit = mission?.path_icon || mission?.pathIcon || mission?.path?.icon;
  if (explicit) return normalizedPathIconName(explicit);

  const title = String(mission?.path_title || "").toLowerCase();
  if (title.includes("fitness") || title.includes("تناسب") || title.includes("حرکت")) return "activity";
  if (title.includes("learning") || title.includes("یادگیری")) return "book";
  if (title.includes("career") || title.includes("شغلی")) return "briefcase";
  if (title.includes("creative") || title.includes("creativity") || title.includes("خلاق")) return "sparkles";
  if (title.includes("sleep") || title.includes("آرامش") || title.includes("خواب")) return "moon";

  return "";
}

export function pathColorFor(mission, iconName = "") {
  const explicit = mission?.path_color || mission?.pathColor || mission?.path?.color;
  if (explicit) return safeColor(explicit);

  const normalizedIcon = normalizedPathIconName(iconName);
  if (normalizedIcon === "activity") return "#4ade80";
  if (normalizedIcon === "book") return "#6ee5ff";
  if (normalizedIcon === "briefcase") return "#818cf8";
  if (normalizedIcon === "sparkles") return "#c35ad6";
  if (normalizedIcon === "moon") return "#f7d774";

  return "#f7d774";
}

function boundedPercent(percent) {
  return Math.min(100, Math.max(0, Number(percent) || 0));
}

function resolvePathIcon(name) {
  return iconFromModules(pathIconModules, name)
    || iconFromModules(pathIconModules, "default_path_icon");
}

function resolveChallengeIcon(challengeId) {
  return iconFromModules(challengeIconModules, challengeId)
    || iconFromModules(challengeIconModules, "default_challenge_icon");
}

function iconFromModules(modules, name) {
  const normalizedName = String(name || "").trim().toLowerCase();
  if (!normalizedName) return "";

  const match = Object.entries(modules).find(([path]) => {
    return path.toLowerCase().endsWith(`/${normalizedName}.png`);
  });

  return match?.[1] || "";
}

function missionIconCandidates(mission) {
  const raw = String(
    mission?.key
    || mission?.mission_key
    || mission?.slug
    || mission?.code
    || "",
  ).trim();
  if (!raw) return [];

  const withoutExtension = raw.replace(/\.[a-z0-9]+$/i, "");
  const hyphenKey = normalizeAssetKey(withoutExtension, "-");
  const underscoreKey = normalizeAssetKey(withoutExtension, "_");

  return Array.from(new Set([
    withoutExtension.toLowerCase(),
    hyphenKey,
    underscoreKey,
  ].filter(Boolean)));
}

function normalizeAssetKey(value, separator = "-") {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[/\\\s]+/g, separator)
    .replace(/[^a-z0-9_-]+/g, separator)
    .replace(/[-_]+/g, separator)
    .replace(new RegExp(`^\\${separator}+|\\${separator}+$`, "g"), "");
}

function normalizedPathIconName(name) {
  const value = String(name || "").trim().toLowerCase();
  if (value === "creativity" || value === "creative") return "sparkles";
  return value;
}
