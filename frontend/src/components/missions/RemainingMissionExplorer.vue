<template>
  <section class="remainingMissionExplorer">
    <div class="explorerHead">
      <div>
        <p class="eyebrow compact">{{ t("missions.optionalExplorerList.eyebrow") }}</p>
        <h3>{{ t("missions.optionalExplorerList.title") }}</h3>
        <p>{{ t("missions.optionalExplorerList.body") }}</p>
      </div>
      <!-- <BaseButton variant="secondary" @click="$emit('close')">
        {{ t("missions.optionalExplorerList.hide") }}
      </BaseButton> -->
    </div>

    <div v-if="visiblePathGroups.length" class="pathGroups">
      <section v-for="path in visiblePathGroups" :key="path.key" class="pathGroup">
        <button type="button" class="groupToggle pathToggle progressSurface"
          :class="{ selected: activePathKey === path.key, complete: path.stats.percent === 100 }"
          :style="progressVars(path.stats.percent, path.color)" @click="selectPath(path)">
          <span class="iconProgressWrap pathIconRing" :class="{ complete: path.stats.percent === 100 }"
            :style="ringVars(path.stats.percent, path.color)" aria-hidden="true">
            <svg class="iconProgressSvg" viewBox="0 0 80 80" focusable="false">
              <circle class="iconProgressTrack" cx="40" cy="40" r="35" pathLength="100" />
              <circle class="iconProgressValue" cx="40" cy="40" r="35" pathLength="100" />
            </svg>
            <span class="groupIcon pathIcon">
              <img v-if="path.iconUrl" :src="path.iconUrl" :alt="path.title" />
              <span v-else>{{ initialsFor(path.title) }}</span>
            </span>
          </span>
          <span>
            <small>{{ t("missions.optionalExplorerList.pathLabel") }}</small>
            <strong>{{ path.title }}</strong>
            <span class="groupSubtitle">{{ pathSummary(path) }}</span>
            <span class="groupMetaLine">
              <span>{{ t("missions.optionalExplorerList.doneCount", { done: path.stats.done, total: path.stats.total })
              }}</span>
              <span>{{ t("missions.optionalExplorerList.challengeCount", {
                done: path.stats.completedChallenges,
                total: path.stats.challengeCount
              }) }}</span>
              <span v-if="path.stats.reminded">{{ t("missions.optionalExplorerList.reminderCount", {
                count:
                  path.stats.reminded
              }) }}</span>
            </span>
          </span>
          <span class="groupSide">
            <i class="groupStatus progress">{{ path.stats.percent }}%</i>
            <span class="rewardSlot" :class="rewardState(path.stats)">
              <img :src="rewardIcon(path.stats)" alt="" aria-hidden="true" />
              {{ rewardLabel(path.stats) }}
            </span>
            <span class="xpSummary" :class="xpState(path.stats)">
              <strong>{{ xpPrimaryLabel(path.stats) }}</strong>
              <small v-if="xpSecondaryLabel(path.stats)">{{ xpSecondaryLabel(path.stats) }}</small>
            </span>
          </span>
        </button>

        <div v-if="expandedPaths.has(path.key)" class="challengeGroups">
          <section v-for="challenge in path.challenges" :key="challenge.key" class="challengeGroup">
            <button type="button" class="groupToggle challengeToggle progressSurface"
              :class="{ selected: activeChallengeKey === challenge.key, complete: challenge.stats.percent === 100 }"
              :style="progressVars(challenge.stats.percent, path.color)" @click="selectChallenge(path, challenge)">
              <span class="iconProgressWrap challengeIconRing" :class="{ complete: challenge.stats.percent === 100 }"
                :style="ringVars(challenge.stats.percent, path.color)" aria-hidden="true">
                <svg class="iconProgressSvg" viewBox="0 0 80 80" focusable="false">
                  <circle class="iconProgressTrack" cx="40" cy="40" r="35" pathLength="100" />
                  <circle class="iconProgressValue" cx="40" cy="40" r="35" pathLength="100" />
                </svg>
                <span class="groupIcon challengeIcon">
                  <img v-if="challenge.iconUrl" :src="challenge.iconUrl" :alt="challenge.title" />
                  <span v-else>{{ initialsFor(challenge.title) }}</span>
                </span>
              </span>
              <span>
                <small>{{ t("missions.optionalExplorerList.challengeLabel") }}</small>
                <strong>{{ challenge.title }}</strong>
                <span class="groupSubtitle">{{ challengeSummary(challenge) }}</span>
                <span class="groupMetaLine">
                  <span>{{ t("missions.optionalExplorerList.doneCount", {
                    done: challenge.stats.done, total:
                      challenge.stats.total
                  }) }}</span>
                  <span v-if="challenge.stats.pending">{{ t("missions.optionalExplorerList.pendingCount", {
                    count:
                      challenge.stats.pending
                  }) }}</span>
                  <span v-if="challenge.stats.reminded">{{ t("missions.optionalExplorerList.reminderCount", {
                    count:
                      challenge.stats.reminded
                  }) }}</span>
                  <span v-if="challengeStreakLabel(challenge)">{{ challengeStreakLabel(challenge) }}</span>
                </span>
              </span>
              <span class="groupSide">
                <!-- <i class="groupStatus" :class="challenge.status">{{ challenge.statusLabel }}</i> -->
                <i class="groupStatus progress">{{ challenge.stats.percent }}%</i>
                <span class="rewardSlot" :class="rewardState(challenge.stats)">
                  <img :src="rewardIcon(challenge.stats)" alt="" aria-hidden="true" />
                  {{ rewardLabel(challenge.stats) }}
                </span>
                <span class="xpSummary" :class="xpState(challenge.stats)">
                  <strong>{{ xpPrimaryLabel(challenge.stats) }}</strong>
                  <small v-if="xpSecondaryLabel(challenge.stats)">{{ xpSecondaryLabel(challenge.stats) }}</small>
                </span>
              </span>
            </button>

            <div v-if="expandedChallenges.has(challenge.key)" class="missionRows">
              <button v-for="mission in challenge.missions" :key="mission.mission_id" type="button"
                class="missionChoiceRow" :class="[
                  `intensity-${normalizedIntensity(mission)}`,
                  `status-${missionVisualState(mission)}`,
                  { selected: isSelected(mission) },
                ]" @click="$emit('select', mission)">
                <span class="missionChoiceIcon" :class="{ fallback: !missionIconUrl(mission) }" aria-hidden="true">
                  <img v-if="missionIconUrl(mission)" :src="missionIconUrl(mission)" alt="" />
                  <span v-else>{{ initialsFor(missionTitle(mission)) }}</span>
                </span>
                <span class="missionChoiceCopy">
                  <strong>{{ missionTitle(mission) }}</strong>
                  <small v-if="missionDescription(mission)">{{ missionDescription(mission) }}</small>
                </span>
                <span class="missionChoiceChips">
                  <span class="choiceChip intensity" :class="normalizedIntensity(mission)">{{ intensityLabel(mission)
                    }}</span>
                  <span class="choiceChip status" :class="missionVisualState(mission)">{{ missionStatusLabel(mission)
                    }}</span>
                  <span v-if="xpLabel(mission)" class="choiceChip xp">{{ xpLabel(mission) }}</span>
                  <span v-if="timeLabel(mission)" class="choiceChip time">{{ timeLabel(mission) }}</span>
                  <span v-if="reminderLabel(mission)" class="choiceChip reminder"
                    :class="missionReminderState(mission)">
                    {{ reminderLabel(mission) }}
                  </span>
                </span>
              </button>
            </div>
          </section>
        </div>
      </section>
    </div>

    <div v-else class="optionalExplorerEmpty">
      <p class="eyebrow compact">{{ t("missions.optionalExplorerList.eyebrow") }}</p>
      <h3>{{ t("missions.optionalExplorerList.emptyTitle") }}</h3>
      <p>{{ t("missions.optionalExplorerList.emptyBody") }}</p>
    </div>

    <div class="explorerActions">
      <BaseButton variant="primary" @click="$emit('finish')">
        {{ t("missions.finishForToday") }}
      </BaseButton>
      <BaseButton v-if="activePathKey || activeChallengeKey" variant="secondary" @click="resetSelection">
        {{ t("missions.backToOptionalChoices") }}
      </BaseButton>
      <BaseButton variant="secondary" @click="$emit('close')">
        {{ t("missions.optionalExplorerList.hide") }}
      </BaseButton>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import BaseButton from "@/components/ui/BaseButton.vue";
import buildingRewardIcon from "@/assets/icons/building.png";
import giftRewardIcon from "@/assets/icons/gift.png";
import {
  getMissionDisplayDescription,
  getMissionDisplayTitle,
} from "@/lib/missionDisplayCopy";

const props = defineProps({
  missions: { type: Array, default: () => [] },
  selectedMissionId: { type: [String, Number], default: null },
});

const emit = defineEmits(["select", "select-path", "select-challenge", "back", "close", "finish"]);

const { locale, t } = useI18n();

const expandedPaths = ref(new Set());
const expandedChallenges = ref(new Set());
const activePathKey = ref("");
const activeChallengeKey = ref("");
const pathIconModules = import.meta.glob("../../assets/path-icons/*.png", { eager: true, import: "default" });
const challengeIconModules = import.meta.glob("../../assets/challenge-icons/*.png", { eager: true, import: "default" });
const missionIconModules = import.meta.glob("../../assets/missions-icons/**/*.png", { eager: true, import: "default" });

const pathGroups = computed(() => {
  const paths = new Map();

  props.missions.forEach((mission) => {
    const pathKey = stableGroupKey("path", mission.path_id || mission.path_title || "default");
    const pathTitle = mission.path_title || t("missions.fallbackPath");
    const pathIconName = pathIconNameFor(mission);
    const challengeKey = stableGroupKey(
      "challenge",
      mission.challenge_id || mission.challenge_name || mission.enrollment_id || "default",
    );
    const challengeTitle = mission.challenge_name || t("missions.fallbackChallenge");
    const challengeIconName = String(mission.challenge_id || "").trim();

    if (!paths.has(pathKey)) {
      paths.set(pathKey, {
        key: pathKey,
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
        statusLabel: groupStatusLabel(stats),
        relevant: isGroupRelevant(stats),
      };
    });

    const stats = summarizeMissions(path.missions);
    stats.challengeCount = challenges.length;
    stats.completedChallenges = challenges.filter((challenge) => challenge.stats.percent === 100).length;

    return {
      ...path,
      stats,
      challenges,
      relevant: challenges.some((challenge) => challenge.relevant),
    };
  });
});

const displayPathGroups = computed(() => {
  return pathGroups.value.map((path) => {
    const challenges = path.challenges;
    const stats = summarizeMissions(challenges.flatMap((challenge) => challenge.missions));
    stats.challengeCount = challenges.length;
    stats.completedChallenges = challenges.filter((challenge) => challenge.stats.percent === 100).length;

    return {
      ...path,
      challenges,
      stats,
    };
  });
});

const visiblePathGroups = computed(() => {
  if (activeChallengeKey.value) {
    return displayPathGroups.value
      .map((path) => ({
        ...path,
        challenges: path.challenges.filter((challenge) => challenge.key === activeChallengeKey.value),
      }))
      .filter((path) => path.challenges.length);
  }

  if (activePathKey.value) {
    return displayPathGroups.value.filter((path) => path.key === activePathKey.value);
  }

  return displayPathGroups.value;
});

watch(pathGroups, (groups) => {
  const visibleGroups = displayPathGroups.value;
  if (visibleGroups.length === 1) {
    expandedPaths.value = new Set([visibleGroups[0].key]);
    expandedChallenges.value = new Set();
    return;
  }

  expandedPaths.value = new Set();
  expandedChallenges.value = new Set();
}, { immediate: true });

watch(() => props.selectedMissionId, (missionId) => {
  if (!missionId) return;

  const mission = props.missions.find((item) => {
    return String(item.mission_id) === String(missionId);
  });
  if (!mission) return;

  const pathKey = stableGroupKey("path", mission.path_id || mission.path_title || "default");
  const challengeKey = stableGroupKey(
    "challenge",
    mission.challenge_id || mission.challenge_name || mission.enrollment_id || "default",
  );

  expandedPaths.value = new Set([pathKey]);
  expandedChallenges.value = new Set([challengeKey]);
}, { immediate: true });

function stableGroupKey(prefix, value) {
  return `${prefix}-${String(value || "default").trim().toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
}

function togglePath(key) {
  if (expandedPaths.value.has(key)) {
    expandedPaths.value = new Set();
    expandedChallenges.value = new Set();
    return;
  }

  expandedPaths.value = new Set([key]);
  expandedChallenges.value = new Set();
}

function toggleChallenge(key) {
  expandedChallenges.value = expandedChallenges.value.has(key)
    ? new Set()
    : new Set([key]);
}

function selectPath(path) {
  activePathKey.value = path.key;
  activeChallengeKey.value = "";
  expandedPaths.value = new Set([path.key]);
  expandedChallenges.value = new Set();
  emit("select-path", {
    key: path.key,
    title: path.title,
    missions: path.missions,
    stats: path.stats,
  });
}

function selectChallenge(path, challenge) {
  activePathKey.value = path.key;
  activeChallengeKey.value = challenge.key;
  expandedPaths.value = new Set([path.key]);
  expandedChallenges.value = new Set([challenge.key]);
  emit("select-challenge", {
    key: challenge.key,
    title: challenge.title,
    pathTitle: path.title,
    missions: challenge.missions,
    stats: challenge.stats,
  });
}

function resetSelection() {
  activePathKey.value = "";
  activeChallengeKey.value = "";
  expandedChallenges.value = new Set();
  if (displayPathGroups.value.length === 1) {
    expandedPaths.value = new Set([displayPathGroups.value[0].key]);
  } else {
    expandedPaths.value = new Set();
  }
  emit("back");
}

function normalizedIntensity(mission) {
  const value = String(mission?.mission_intensity || "main").toLowerCase();
  return ["main", "tiny", "bonus"].includes(value) ? value : "main";
}

function normalizedStatus(mission) {
  const value = String(mission?.status || "pending").toLowerCase();
  return ["pending", "done", "remind_later", "skipped"].includes(value) ? value : "pending";
}

function missionTitle(mission) {
  return getMissionDisplayTitle(mission, locale.value) || mission?.title || t("missions.fallbackMission");
}

function missionDescription(mission) {
  return getMissionDisplayDescription(mission, locale.value) || mission?.description || "";
}

function intensityLabel(mission) {
  return t(`missions.typeChips.${normalizedIntensity(mission)}`);
}

function statusLabel(mission) {
  return t(`missions.status.${normalizedStatus(mission)}`);
}

function missionVisualState(mission) {
  const status = normalizedStatus(mission);
  if (status === "remind_later") return isReminderDue(mission) ? "reminder-due" : "reminder-waiting";
  if (status === "done") return "done";
  if (status === "skipped") return "skipped";
  return "pending";
}

function missionStatusLabel(mission) {
  const state = missionVisualState(mission);
  if (state === "reminder-due") return t("missions.optionalExplorerList.missionStatus.reminderDue");
  if (state === "reminder-waiting") return t("missions.optionalExplorerList.missionStatus.reminderWaiting");
  if (state === "pending") return t("missions.optionalExplorerList.missionStatus.ready");

  return statusLabel(mission);
}

function xpLabel(mission) {
  const earned = Number(mission?.xp_earned || 0);
  const amount = Math.max(earned, missionXpValue(mission));
  if (!Number.isFinite(amount) || amount <= 0) return "";

  return t("missions.optionalExplorerList.xp", { count: amount });
}

function timeLabel(mission) {
  const minutes = Number(mission?.estimated_minutes || 0);
  if (!Number.isFinite(minutes) || minutes <= 0) return "";

  return t("missionContext.time.minutes", { count: minutes });
}

function reminderLabel(mission) {
  if (!mission?.reminder_at) return "";

  try {
    return new Intl.DateTimeFormat(undefined, {
      hour: "numeric",
      minute: "2-digit",
    }).format(new Date(mission.reminder_at));
  } catch {
    return "";
  }
}

function reminderTimestamp(mission) {
  if (!mission?.reminder_at) return Number.POSITIVE_INFINITY;

  const timestamp = new Date(mission.reminder_at).getTime();
  return Number.isNaN(timestamp) ? Number.POSITIVE_INFINITY : timestamp;
}

function isReminderDue(mission) {
  return normalizedStatus(mission) === "remind_later" && reminderTimestamp(mission) <= Date.now();
}

function missionReminderState(mission) {
  return isReminderDue(mission) ? "due" : "waiting";
}

function summarizeMissions(missions) {
  const items = Array.isArray(missions) ? missions : [];
  const total = items.length;
  const done = items.filter((mission) => normalizedStatus(mission) === "done").length;
  const pending = items.filter((mission) => normalizedStatus(mission) === "pending").length;
  const reminded = items.filter((mission) => normalizedStatus(mission) === "remind_later").length;
  const skipped = items.filter((mission) => normalizedStatus(mission) === "skipped").length;
  const reminderDue = items.filter(isReminderDue).length;
  const futureReminders = items.filter((mission) => {
    return normalizedStatus(mission) === "remind_later" && !isReminderDue(mission);
  }).length;
  const minutes = items.reduce((sum, mission) => {
    const value = Number(mission?.estimated_minutes || 0);
    return Number.isFinite(value) && value > 0 ? sum + value : sum;
  }, 0);
  const totalXp = items.reduce((sum, mission) => {
    return sum + missionXpValue(mission);
  }, 0);
  const earnedXp = items.reduce((sum, mission) => {
    if (normalizedStatus(mission) !== "done") return sum;

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

function missionXpValue(mission) {
  const reward = Number(mission?.xp_reward || 0);
  const earned = Number(mission?.xp_earned || 0);
  const amount = Math.max(reward, earned);
  return Number.isFinite(amount) && amount > 0 ? amount : 0;
}

function isGroupRelevant(stats) {
  return Boolean(
    stats.pending
    || stats.reminded
    || stats.reminderDue
    || stats.futureReminders
    || stats.skipped
    || (stats.total > 0 && stats.percent === 100),
  );
}

function groupStatus(stats) {
  if (stats.reminderDue) return "reminder_due";
  if (stats.futureReminders || stats.reminded) return "reminder_set";
  if (stats.total > 0 && stats.done === stats.total) return "done";
  if (stats.done > 0) return "in_progress";
  if (stats.skipped && !stats.pending) return "skipped";
  if (stats.pending) return "ready";

  return "optional";
}

function groupStatusLabel(stats) {
  return t(`missions.optionalExplorerList.status.${groupStatus(stats)}`);
}

function challengeSummary(challenge) {
  if (challenge.stats.total > 0 && challenge.stats.percent === 100) {
    return t("missions.optionalExplorerList.challengeCompleteToday");
  }

  const parts = [
    challenge.stats.pending === 1
      ? t("missions.optionalExplorerList.oneOptionalStepToday")
      : t("missions.optionalExplorerList.optionalStepsToday", { count: challenge.stats.pending }),
  ];

  if (challenge.stats.xp) {
    parts.push(t("missions.optionalExplorerList.xp", { count: challenge.stats.xp }));
  }

  if (challenge.stats.minutes) {
    parts.push(t("missionContext.time.minutes", { count: challenge.stats.minutes }));
  }

  return parts.join(" · ");
}

function challengeStreakLabel(challenge) {
  const source = challenge?.missions?.find((mission) => {
    return hasOwn(mission, "challenge_streak")
      || hasOwn(mission, "challenge_current_streak")
      || hasOwn(mission, "current_streak")
      || hasOwn(mission, "streak_active")
      || hasOwn(mission, "streak_protected");
  });
  if (!source) return "";

  const count = Number(
    source.challenge_streak
    ?? source.challenge_current_streak
    ?? source.current_streak
    ?? 0,
  );
  const hasCount = Number.isFinite(count) && count > 0;
  const active = Boolean(source.streak_active ?? source.streak_protected ?? hasCount);

  if (active && hasCount) return t("missions.optionalExplorerList.streakOn", { count });
  if (!active && hasCount) return t("missions.optionalExplorerList.streakOff", { count });
  return t("missions.optionalExplorerList.noStreak");
}

function hasOwn(value, key) {
  return Boolean(value) && Object.prototype.hasOwnProperty.call(value, key);
}

function pathSummary(path) {
  if (path.stats.total > 0 && path.stats.percent === 100) {
    return t("missions.optionalExplorerList.pathCompleteToday");
  }

  if (path.stats.pending === 1) {
    return t("missions.optionalExplorerList.oneOptionalStepToday");
  }

  return t("missions.optionalExplorerList.optionalStepsToday", { count: path.stats.pending });
}

function progressVars(percent, color) {
  return {
    "--progress-percent": `${Math.min(100, Math.max(0, Number(percent) || 0))}%`,
    "--progress-color": safeColor(color),
  };
}

function ringVars(percent, color) {
  const boundedPercent = Math.min(100, Math.max(0, Number(percent) || 0));
  return {
    "--ring-percent": boundedPercent,
    "--ring-offset": 100 - boundedPercent,
    "--ring-color": safeColor(color),
  };
}

function safeColor(color) {
  const value = String(color || "").trim();
  return /^#[0-9a-f]{3}([0-9a-f]{3})?$/i.test(value) ? value : "#f7d774";
}

function rewardState(stats) {
  if (Number(stats?.total || 0) > 0 && Number(stats?.percent || 0) >= 100) return "ready";
  if (Number(stats?.done || 0) > 0) return "active";
  return "locked";
}

function rewardLabel(stats) {
  const state = rewardState(stats);
  if (state === "ready") return t("missions.optionalExplorerList.reward.ready");
  return t("missions.optionalExplorerList.reward.active");
}

function rewardIcon(stats) {
  return rewardState(stats) === "ready" ? giftRewardIcon : buildingRewardIcon;
}

function xpState(stats) {
  if (Number(stats?.total || 0) > 0 && Number(stats?.percent || 0) >= 100) return "complete";
  const totalXp = Number(stats?.totalXp || 0);
  const remainingXp = Number(stats?.remainingXp || 0);

  if (totalXp > 0 && remainingXp <= Math.max(5, totalXp * 0.25)) {
    return "near";
  }

  return "progress";
}

function xpPrimaryLabel(stats) {
  const totalXp = Number(stats?.totalXp || 0);
  const earnedXp = Math.min(totalXp, Number(stats?.earnedXp || 0));

  if (Number(stats?.total || 0) > 0 && Number(stats?.percent || 0) >= 100) {
    return t("missions.optionalExplorerList.xpEarned", { total: totalXp });
  }

  return t("missions.optionalExplorerList.xpProgress", { earned: earnedXp, total: totalXp });
}

function xpSecondaryLabel(stats) {
  if (Number(stats?.total || 0) > 0 && Number(stats?.percent || 0) >= 100) return "";

  return t("missions.optionalExplorerList.xpLeft", { count: Math.max(0, Number(stats?.remainingXp || 0)) });
}

function isSelected(mission) {
  return props.selectedMissionId && String(mission.mission_id) === String(props.selectedMissionId);
}

function iconFromModules(modules, name) {
  const normalizedName = String(name || "").trim().toLowerCase();
  if (!normalizedName) return "";

  const match = Object.entries(modules).find(([path]) => {
    return path.toLowerCase().endsWith(`/${normalizedName}.png`);
  });

  return match?.[1] || "";
}

function resolvePathIcon(name) {
  return iconFromModules(pathIconModules, name)
    || iconFromModules(pathIconModules, "default_path_icon");
}

function resolveChallengeIcon(challengeId) {
  return iconFromModules(challengeIconModules, challengeId)
    || iconFromModules(challengeIconModules, "default_challenge_icon");
}

function missionIconUrl(mission) {
  const candidates = missionIconCandidates(mission);

  for (const candidate of candidates) {
    const icon = iconFromModules(missionIconModules, candidate);
    if (icon) return icon;
  }

  return iconFromModules(missionIconModules, "default_missions_icon");
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

function pathIconNameFor(mission) {
  const explicit = mission?.path_icon || mission?.pathIcon || mission?.icon;
  if (explicit) return normalizedPathIconName(explicit);

  const title = String(mission?.path_title || "").toLowerCase();
  if (title.includes("fitness") || title.includes("تناسب") || title.includes("حرکت")) return "activity";
  if (title.includes("learning") || title.includes("یادگیری")) return "book";
  if (title.includes("career") || title.includes("شغلی")) return "briefcase";
  if (title.includes("creative") || title.includes("creativity") || title.includes("خلاق")) return "sparkles";
  if (title.includes("sleep") || title.includes("آرامش") || title.includes("خواب")) return "moon";

  return "";
}

function normalizedPathIconName(name) {
  const value = String(name || "").trim().toLowerCase();
  if (value === "creativity" || value === "creative") return "sparkles";
  return value;
}

function pathColorFor(mission, iconName = "") {
  const explicit = mission?.path_color || mission?.pathColor || mission?.color || mission?.path?.color;
  if (explicit) return safeColor(explicit);

  const normalizedIcon = normalizedPathIconName(iconName);
  if (normalizedIcon === "activity") return "#4ade80";
  if (normalizedIcon === "book") return "#6ee5ff";
  if (normalizedIcon === "briefcase") return "#818cf8";
  if (normalizedIcon === "sparkles") return "#c35ad6";
  if (normalizedIcon === "moon") return "#f7d774";

  return "#f7d774";
}

function initialsFor(value) {
  const words = String(value || "").trim().split(/\s+/).filter(Boolean);
  const initials = words.slice(0, 2).map((word) => word.slice(0, 1)).join("");
  return initials || "•";
}
</script>

<style scoped>
.remainingMissionExplorer {
  display: grid;
  gap: var(--s-16);
  box-sizing: border-box;
  width: 100%;
  max-width: 100%;
  padding: 20px;
  border: 1px solid rgba(110, 229, 255, 0.12);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.64), rgba(5, 10, 18, 0.42));
  overflow: hidden;
}

.explorerHead,
.groupToggle,
.missionChoiceRow,
.pathGroups,
.challengeGroups,
.missionRows {
  min-width: 0;
}

.explorerHead {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-12);
  align-items: flex-start;
  justify-content: space-between;
}

.explorerHead h3,
.explorerHead p {
  margin: 0;
}

.explorerHead h3 {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.05rem;
}

.explorerHead p:not(.eyebrow) {
  margin-top: 5px;
  max-width: 58ch;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.pathGroups,
.challengeGroups,
.missionRows,
.explorerActions {
  display: grid;
  gap: var(--s-8);
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  max-width: 100%;
}

.explorerActions {
  position: static;
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  width: 100%;
  max-width: 100%;
  align-items: center;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.pathGroup,
.challengeGroup {
  display: grid;
  gap: var(--s-8);
  min-width: 0;
  max-width: 100%;
}

.challengeGroups {
  padding-inline-start: 40px;
}

.groupToggle,
.missionChoiceRow {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.09);
  color: inherit;
  background: rgba(255, 255, 255, 0.035);
  text-align: start;
  cursor: pointer;
}

.groupToggle {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) minmax(96px, auto);
  gap: var(--s-12);
  align-items: center;
  padding: 12px;
  border-radius: 14px;
  overflow: hidden;
}

.progressSurface::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(90deg,
      color-mix(in srgb, var(--progress-color, #f7d774) 18%, transparent),
      rgba(110, 229, 255, 0.045));
  clip-path: inset(0 calc(100% - var(--progress-percent, 0%)) 0 0);
  overflow: hidden;
  pointer-events: none;
}

:global(html[dir="rtl"]) .progressSurface::before {
  background: linear-gradient(270deg,
      color-mix(in srgb, var(--progress-color, #f7d774) 18%, transparent),
      rgba(110, 229, 255, 0.045));
  clip-path: inset(0 0 0 calc(100% - var(--progress-percent, 0%)));
}

.progressSurface.complete {
  border-color: rgba(247, 215, 116, 0.24);
  box-shadow: inset 0 0 0 1px rgba(247, 215, 116, 0.06);
}

.progressSurface.complete::before {
  background: linear-gradient(90deg,
      color-mix(in srgb, var(--progress-color, #f7d774) 26%, transparent),
      color-mix(in srgb, var(--progress-color, #f7d774) 10%, transparent));
  clip-path: inset(0);
}

:global(html[dir="rtl"]) .progressSurface.complete::before {
  background: linear-gradient(270deg,
      color-mix(in srgb, var(--progress-color, #f7d774) 26%, transparent),
      color-mix(in srgb, var(--progress-color, #f7d774) 10%, transparent));
  clip-path: inset(0);
}

.pathToggle {
  background: rgba(110, 229, 255, 0.055);
}

.challengeToggle {
  background: rgba(255, 255, 255, 0.028);
}

.groupToggle.selected {
  border-color: rgba(110, 229, 255, 0.25);
  background: rgba(110, 229, 255, 0.08);
}

.groupToggle>span:not(.groupIcon):not(.iconProgressWrap),
.missionChoiceCopy,
.missionChoiceChips {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.iconProgressWrap,
.groupIcon,
.groupSide,
.groupStatus {
  position: relative;
  z-index: 1;
}

.groupToggle small,
.missionChoiceCopy small {
  display: block;
  color: rgba(255, 255, 255, 0.52);
  font-size: var(--cap);
  font-weight: 800;
}

.groupToggle strong,
.missionChoiceCopy strong {
  display: block;
  color: rgba(255, 255, 255, 0.92);
  overflow-wrap: anywhere;
}

.groupSubtitle,
.groupMetaLine {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-width: 0;
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.62);
  font-size: var(--cap);
  font-weight: 780;
  line-height: 1.35;
}

.groupSubtitle {
  display: block;
}

.groupMetaLine span {
  min-width: 0;
  overflow-wrap: anywhere;
}

.groupMetaLine span+span::before {
  content: "·";
  margin-inline-end: 6px;
  color: rgba(255, 255, 255, 0.35);
}

.groupSide {
  display: grid;
  gap: 6px;
  justify-items: end;
  min-width: 136px;
}

:global(html[dir="rtl"]) .groupSide {
  justify-items: start;
}

.groupToggle i {
  display: inline-flex;
  min-width: 44px;
  max-width: 120px;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.92);
  background: rgba(110, 229, 255, 0.10);
  font-style: normal;
  font-size: var(--cap);
  font-weight: 900;
  white-space: nowrap;
}

.rewardSlot {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  min-width: 84px;
  max-width: 150px;
  justify-content: center;
  padding: 5px 8px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.62);
  background: rgba(255, 255, 255, 0.045);
  font-size: var(--cap);
  font-weight: 900;
  line-height: 1.1;
  text-align: center;
  white-space: nowrap;
}

.rewardSlot img {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  object-fit: contain;
  opacity: 0.82;
  filter: brightness(0) invert(1);
}

.rewardSlot.active {
  color: rgba(219, 244, 255, 0.88);
  border-color: rgba(110, 229, 255, 0.16);
  background: rgba(110, 229, 255, 0.075);

}

.rewardSlot.ready {
  color: rgba(46, 46, 45, 0.98);
  border-color: rgba(247, 215, 116, 0.28);
  background: linear-gradient(135deg, rgba(231, 188, 60, 0.16), rgba(247, 215, 116, 0.9));
  box-shadow: 0 0 22px rgba(247, 215, 116, 0.08);

}

.rewardSlot.ready img {
  opacity: 1;
  filter: drop-shadow(0 0 6px rgba(247, 215, 116, 0.36)) saturate(1.12);
  filter: brightness(50%) invert(1);
}

.xpSummary {
  display: grid;
  gap: 2px;
  justify-items: end;
  /* min-width: 116px; */
  padding: 6px 9px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  text-align: end;
}

:global(html[dir="rtl"]) .xpSummary {
  justify-items: start;
  text-align: start;
}

.xpSummary strong,
.xpSummary small {
  display: block;
  line-height: 1.12;
  white-space: nowrap;
}

.xpSummary strong {
  color: rgba(255, 255, 255, 0.86);
  font-size: var(--cap);
  font-weight: 950;
}

.xpSummary small {
  color: rgba(219, 244, 255, 0.58);
  font-size: 0.68rem;
  font-weight: 850;
}

.xpSummary.near {
  border-color: rgba(247, 215, 116, 0.14);
  background: rgba(247, 215, 116, 0.055);
}

.xpSummary.near strong {
  color: rgba(253, 230, 138, 0.94);
}

.xpSummary.complete {
  border-color: rgba(247, 215, 116, 0.22);
  background: linear-gradient(135deg, rgba(247, 215, 116, 0.14), rgba(74, 222, 128, 0.06));
  box-shadow: 0 0 18px rgba(247, 215, 116, 0.07);
}

.xpSummary.complete strong {
  color: rgba(253, 230, 138, 0.98);
}

.groupStatus.reminder_due {
  color: rgba(253, 230, 138, 0.96);
  background: rgba(247, 215, 116, 0.11);
}

.groupStatus.done {
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.10);
}

.groupStatus.skipped {
  color: rgba(255, 255, 255, 0.68);
  background: rgba(255, 255, 255, 0.055);
}

.groupIcon {
  display: inline-grid;
  place-items: center;
  width: 64px;
  height: 64px;
  overflow: hidden;
  padding: 14px;
  font-size: var(--cap);
  font-weight: 950;
}

.iconProgressWrap {
  --ring-color: #f7d774;
  --ring-offset: 100;
  display: inline-grid;
  place-items: center;
  width: 84px;
  height: 84px;
  flex: 0 0 auto;
}

.iconProgressSvg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
  transform: rotate(90deg);
}

.iconProgressTrack,
.iconProgressValue {
  fill: none;
  stroke-linecap: round;
  stroke-width: 5;
}

.iconProgressTrack {
  stroke: rgba(255, 255, 255, 0.105);
}

.iconProgressValue {
  stroke: var(--ring-color);
  stroke-dasharray: 100;
  stroke-dashoffset: var(--ring-offset);
  transition: stroke-dashoffset 180ms ease;
  filter: drop-shadow(0 0 8px color-mix(in srgb, var(--ring-color) 30%, transparent));
}

.iconProgressWrap.complete .iconProgressTrack {
  stroke: rgba(247, 215, 116, 0.16);
}

.iconProgressWrap.complete .iconProgressValue {
  filter: drop-shadow(0 0 12px color-mix(in srgb, var(--ring-color) 42%, transparent));
}

.pathIcon {
  width: 66px;
  height: 66px;
}

.challengeIcon {
  width: 56px;
  height: 56px;
  border-radius: 20px;
  padding: 9px;
}

.challengeIconRing {
  width: 76px;
  height: 76px;
}

.groupIcon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0) invert(1);
}

.missionRows {
  padding-inline-start: 30px;
}

.missionChoiceRow {
  --mission-accent: rgba(110, 229, 255, 0.82);
  --mission-accent-soft: rgba(110, 229, 255, 0.10);
  --mission-accent-border: rgba(110, 229, 255, 0.18);
  display: grid;
  grid-template-columns: 50px minmax(0, 1fr);
  gap: 8px 12px;
  align-items: center;
  padding: 12px;
  border-radius: 14px;
  border-color: var(--mission-accent-border);
  background:
    linear-gradient(135deg, var(--mission-accent-soft), rgba(255, 255, 255, 0.026) 46%),
    rgba(255, 255, 255, 0.028);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.015);
  transition:
    border-color 160ms ease,
    background 160ms ease,
    box-shadow 160ms ease,
    transform 160ms ease;
}

.missionChoiceRow:hover {
  border-color: color-mix(in srgb, var(--mission-accent) 42%, rgba(255, 255, 255, 0.12));
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--mission-accent-soft) 78%, transparent), rgba(255, 255, 255, 0.042) 50%),
    rgba(255, 255, 255, 0.035);
  transform: translateY(-1px);
}

.missionChoiceRow.selected {
  border-color: color-mix(in srgb, var(--mission-accent) 58%, rgba(255, 255, 255, 0.10));
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--mission-accent-soft) 100%, rgba(255, 255, 255, 0.02)), rgba(255, 255, 255, 0.045) 54%),
    rgba(255, 255, 255, 0.045);
  box-shadow:
    inset 0 0 0 1px color-mix(in srgb, var(--mission-accent) 18%, transparent),
    0 0 20px color-mix(in srgb, var(--mission-accent) 10%, transparent);
}

.missionChoiceRow.status-pending {
  --mission-accent: rgba(110, 229, 255, 0.86);
  --mission-accent-soft: rgba(110, 229, 255, 0.09);
  --mission-accent-border: rgba(110, 229, 255, 0.16);
}

.missionChoiceRow.status-done {
  --mission-accent: rgba(74, 222, 128, 0.84);
  --mission-accent-soft: rgba(74, 222, 128, 0.105);
  --mission-accent-border: rgba(74, 222, 128, 0.18);
}

.missionChoiceRow.status-reminder-waiting {
  --mission-accent: rgba(247, 215, 116, 0.78);
  --mission-accent-soft: rgba(247, 215, 116, 0.075);
  --mission-accent-border: rgba(247, 215, 116, 0.15);
}

.missionChoiceRow.status-reminder-due {
  --mission-accent: rgba(253, 230, 138, 0.96);
  --mission-accent-soft: rgba(247, 215, 116, 0.13);
  --mission-accent-border: rgba(247, 215, 116, 0.24);
  box-shadow:
    inset 0 0 0 1px rgba(247, 215, 116, 0.045),
    0 0 18px rgba(247, 215, 116, 0.055);
}

.missionChoiceRow.status-skipped {
  --mission-accent: rgba(148, 163, 184, 0.68);
  --mission-accent-soft: rgba(148, 163, 184, 0.045);
  --mission-accent-border: rgba(148, 163, 184, 0.12);
  opacity: 0.78;
}

.missionChoiceRow.intensity-bonus.status-pending,
.missionChoiceRow.intensity-bonus.status-reminder-waiting {
  --mission-accent: rgba(247, 215, 116, 0.88);
  --mission-accent-soft: rgba(247, 215, 116, 0.09);
  --mission-accent-border: rgba(247, 215, 116, 0.18);
}

.missionChoiceRow.intensity-tiny.status-pending {
  --mission-accent: rgba(125, 211, 252, 0.82);
  --mission-accent-soft: rgba(125, 211, 252, 0.075);
}

.missionChoiceRow.status-done,
.missionChoiceRow.status-skipped {
  transform: none;
}

.missionChoiceIcon {
  position: relative;
  grid-row: 1 / span 2;
  display: inline-grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border: 1px solid color-mix(in srgb, var(--mission-accent) 26%, rgba(255, 255, 255, 0.08));
  border-radius: 14px;
  background:
    radial-gradient(circle at 34% 24%, color-mix(in srgb, var(--mission-accent) 20%, transparent), transparent 42%),
    rgba(255, 255, 255, 0.055);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.025);
  overflow: hidden;
}

.missionChoiceIcon::after {
  content: "";
  position: absolute;
  inset-inline-end: 5px;
  inset-block-end: 5px;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--mission-accent);
  box-shadow: 0 0 10px color-mix(in srgb, var(--mission-accent) 50%, transparent);
}

.missionChoiceIcon img {
  width: 74%;
  height: 74%;
  object-fit: contain;
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.22));
}

.missionChoiceIcon.fallback span {
  color: rgba(255, 255, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 950;
}

.missionChoiceChips {
  grid-column: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  align-items: center;
}

.choiceChip {
  display: inline-flex;
  align-items: center;
  min-height: 23px;
  max-width: 100%;
  padding: 4px 7px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.04);
  font-size: var(--cap);
  font-weight: 850;
  line-height: 1;
  white-space: nowrap;
}

.choiceChip.intensity.main {
  color: rgba(219, 244, 255, 0.88);
  background: rgba(110, 229, 255, 0.065);
}

.choiceChip.intensity.tiny {
  color: rgba(191, 219, 254, 0.9);
  background: rgba(125, 211, 252, 0.065);
}

.choiceChip.intensity.bonus {
  color: rgba(253, 230, 138, 0.94);
  border-color: rgba(247, 215, 116, 0.14);
  background: rgba(247, 215, 116, 0.075);
}

.choiceChip.status {
  color: color-mix(in srgb, var(--mission-accent) 84%, white);
  border-color: color-mix(in srgb, var(--mission-accent) 22%, rgba(255, 255, 255, 0.08));
  background: color-mix(in srgb, var(--mission-accent) 10%, transparent);
}

.choiceChip.status.done {
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.09);
}

.choiceChip.status.reminder-due {
  color: rgba(253, 230, 138, 0.98);
  background: rgba(247, 215, 116, 0.13);
  box-shadow: 0 0 14px rgba(247, 215, 116, 0.07);
}

.choiceChip.status.skipped {
  color: rgba(226, 232, 240, 0.64);
  background: rgba(148, 163, 184, 0.055);
}

.choiceChip.reminder {
  color: rgba(253, 230, 138, 0.9);
  border-color: rgba(247, 215, 116, 0.12);
  background: rgba(247, 215, 116, 0.065);
}

.choiceChip.reminder.due {
  color: rgba(253, 230, 138, 0.98);
  border-color: rgba(247, 215, 116, 0.18);
  background: rgba(247, 215, 116, 0.11);
}

.choiceChip.xp {
  color: rgba(253, 230, 138, 0.94);
  background: rgba(247, 215, 116, 0.08);
}

.selectedMissionContext {
  padding-top: var(--s-8);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

@media (max-width: 720px) {
  .groupToggle {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .groupSide {
    grid-column: 1 / -1;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    justify-items: start;
    min-width: 0;
  }

  .xpSummary {
    min-width: 128px;
    justify-items: start;
    text-align: start;
  }

  .challengeGroups,
  .missionRows {
    padding-inline-start: 20px;
  }
}
</style>
