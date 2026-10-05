<template>
  <BaseCard class="livingSpace">
    <div class="spaceHead">
      <div>
        <p class="spaceKicker">{{ t("space.eyebrow") }}</p>
        <h2>{{ t("space.title") }}</h2>
        <p>{{ t("space.subtitle") }}</p>
        <p v-if="spaceState" class="spaceStatus">{{ spaceStatus }}</p>
        <p v-if="spaceState" class="spaceRule">{{ t("space.rule") }}</p>
      </div>

      <div v-if="spaceState" class="spaceMeta">
        <span>{{ t("space.objects", { count: unlockedCount }) }}</span>
        <span v-if="spaceState.has_unseen_rewards">{{ t("space.newReward") }}</span>
      </div>
    </div>

    <UiState
      :loading="loading"
      :error="!!error"
      :empty="false"
      :loading-title="t('space.loadingTitle')"
      :loading-text="t('space.loadingText')"
      :error-title="t('space.errorTitle')"
      :error-text="error || t('common.pleaseTryAgain')"
      @retry="loadSpace"
    />

    <div v-if="spaceState && !loading && !error" class="spaceLayout">
      <div class="roomStage" :aria-label="t('space.roomLabel')">
        <SpaceZone
          v-for="zone in displayZones"
          :key="zone.zone_key"
          :zone="zone"
          :active="panelZone?.zone_key === zone.zone_key"
          @select="selectZone"
        />
      </div>

      <SpaceZonePanel
        v-if="panelZone"
        :mode="panelMode"
        :zone="panelZone"
        :checking-id="checkingId"
        :path-loading="activePathLoading"
        :path-error="activePathError"
        :selected-challenge-id="selectedPathChallengeId"
        :completing-mission-id="completingMissionId"
        :starting-challenge-id="startingChallengeId"
        :today-safe="todaySafe"
        :daily-momentum="dailyMomentum"
        :due-reminders="dueReminders"
        :future-reminder-count="futureReminderCount"
        @change-mode="changeShellMode"
        @select-challenge="selectPathChallenge"
        @start-challenge="startChallenge"
        @complete-mission="completeMission"
        @checkin="$emit('checkin', $event)"
        @close="closePanel"
      />
    </div>
  </BaseCard>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import { getChallengePathKey } from "@/lib/guidedExperience";
import { localizeChallenge, localizePath } from "@/lib/ringoContentLocalization";
import { missionIconUrl } from "@/utils/missionMomentumUtils";
import { humanizeJoinError, submitJoinFlow } from "@/views/challengeFlow";
import SpaceZone from "./SpaceZone.vue";
import SpaceZonePanel from "./SpaceZonePanel.vue";

const props = defineProps({
  refreshKey: { type: Number, default: 0 },
  challenges: { type: Array, default: () => [] },
  missions: { type: Array, default: () => [] },
  todaySafe: { type: Boolean, default: false },
  focusReason: { type: String, default: "" },
  reminderCount: { type: Number, default: 0 },
  checkingId: { type: [Number, String, null], default: null },
});

const emit = defineEmits(["checkin", "challenge-started", "mission-completed"]);

const { locale, t } = useI18n();

const loading = ref(false);
const error = ref("");
const spaceState = ref(null);
const activeZone = ref(null);
const shellMode = ref("zone");
const paths = ref([]);
const pathChallenges = ref({});
const pathSummaries = ref({});
const pathLoading = ref({});
const pathErrors = ref({});
const selectedPathChallengeId = ref(null);
const startingChallengeId = ref(null);
const completingMissionId = ref(null);

const unlockedCount = computed(() => {
  return spaceState.value?.unlocked_objects?.length || 0;
});

const spaceStatus = computed(() => {
  if (!unlockedCount.value) {
    return t("space.emptyStatus");
  }

  if (hasHistoricalRewards.value) {
    return t("space.historyStatus", { count: unlockedCount.value });
  }

  return t("space.progressStatus", { count: unlockedCount.value });
});

const hasHistoricalRewards = computed(() => {
  return (spaceState.value?.unlocked_objects || []).some((reward) => {
    return reward?.source_type === "mission_history";
  });
});

const displayZones = computed(() => {
  return (spaceState.value?.zones || []).map((zone) => {
    const pathDetail = buildPathDetail(zone);
    const zonePathKey = normalizePathKey(zone.path_key);

    return {
      ...zone,
      pathDetail,
      action: buildZoneAction(zone, pathDetail),
      dueReminderCount: dueReminderCountByPath.value[zonePathKey] || 0,
    };
  });
});

const displayActiveZone = computed(() => {
  if (!activeZone.value) return null;

  return displayZones.value.find(
    (zone) => zone.zone_key === activeZone.value.zone_key,
  ) || null;
});

const restZone = computed(() => {
  return displayZones.value.find((zone) => zone.action?.state === "done_today")
    || displayZones.value.find((zone) => (zone.unlocked_objects || []).length > 0)
    || displayZones.value[0]
    || null;
});

const shouldShowRestPanel = computed(() => {
  if (activeZone.value) return false;

  return Boolean(
    props.todaySafe
    || dueReminders.value.length
    || ["rest_mode", "done_for_today", "future_reminder_only"].includes(props.focusReason),
  );
});

const panelMode = computed(() => {
  return shouldShowRestPanel.value ? "rest" : shellMode.value;
});

const panelZone = computed(() => {
  if (displayActiveZone.value) return displayActiveZone.value;
  if (panelMode.value === "rest") return restZone.value;
  return null;
});

const activePathId = computed(() => panelZone.value?.pathDetail?.pathId || "");

const activePathLoading = computed(() => {
  const pathId = activePathId.value;
  return pathId ? Boolean(pathLoading.value[pathId]) : false;
});

const activePathError = computed(() => {
  const pathId = activePathId.value;
  return pathId ? pathErrors.value[pathId] || "" : "";
});

async function loadSpace() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await api.get("/me/space");
    spaceState.value = data;

    if (activeZone.value) {
      activeZone.value = data.zones.find(
        (zone) => zone.zone_key === activeZone.value.zone_key,
      ) || null;
    }
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function loadPaths() {
  try {
    const { data } = await api.get("/paths");
    paths.value = data?.items || [];
  } catch {
    paths.value = [];
  }
}

function selectZone(zone) {
  activeZone.value = zone;
  shellMode.value = "zone";
  selectedPathChallengeId.value = null;
  ensurePathChallenges(zone);
}

function closePanel() {
  activeZone.value = null;
  shellMode.value = "zone";
  selectedPathChallengeId.value = null;
}

function changeShellMode(mode) {
  if (!["zone", "path", "challenge", "mission", "rest"].includes(mode)) return;
  if (mode === "rest") {
    activeZone.value = null;
    shellMode.value = mode;
    selectedPathChallengeId.value = null;
    return;
  }

  if (!activeZone.value && panelZone.value) {
    activeZone.value = panelZone.value;
  }

  shellMode.value = mode;

  if (["path", "challenge", "mission"].includes(mode)) {
    ensurePathChallenges(panelZone.value);
  }
}

function selectPathChallenge(challenge) {
  selectedPathChallengeId.value = challenge?.id || null;
}

function isCheckedToday(challenge) {
  const value = challenge?.today_checked ?? challenge?.todayChecked ?? false;

  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value === 1;
  if (typeof value === "string") {
    return ["true", "1", "yes", "done", "checked"].includes(value.toLowerCase());
  }

  return false;
}

function normalizePathKey(pathKey) {
  const aliases = {
    body: "fitness",
    focus: "career",
    mind: "sleep",
  };

  return aliases[pathKey] || pathKey || "";
}

function challengeName(challenge) {
  const localized = localizeChallenge(challenge, locale.value);

  return localized?.name
    || localized?.challenge_name
    || localized?.enrollment_name
    || challenge?.name
    || challenge?.challenge_name
    || challenge?.enrollment_name
    || t("common.challenge");
}

function buildZoneAction(zone, pathDetail = null) {
  const challenge = props.challenges.find((item) => {
    return normalizePathKey(getChallengePathKey(item)) === normalizePathKey(zone.path_key);
  });

  const pathChallenge = findActivePathChallenge(pathDetail);
  if (pathChallenge?.isJoined) {
    return buildPathChallengeZoneAction(pathChallenge);
  }

  if (!challenge?.enrollment_id) {
    return {
      state: "not_started",
      title: t("space.zoneAction.notStartedTitle"),
      text: t("space.zoneAction.notStartedText"),
      primaryLabel: t("space.zoneAction.startPath"),
      primaryMode: "path",
      fallbackTo: "/paths",
      secondaryLabel: t("space.zoneAction.browseChallenges"),
      secondaryTo: "/challenges",
    };
  }

  const name = challengeName(challenge);
  const mission = findChallengeMission(challenge);

  if (isCheckedToday(challenge)) {
    return {
      state: "done_today",
      title: t("space.zoneAction.doneTitle", { challenge: name }),
      text: t("space.zoneAction.doneText"),
      primaryLabel: t("space.zoneAction.reviewChallenge"),
      primaryMode: "challenge",
      fallbackTo: `/enrollment/${challenge.enrollment_id}`,
      secondaryLabel: t("space.zoneAction.viewPath"),
      secondaryMode: "path",
      secondaryTo: "/paths",
      challenge: {
        id: challenge.challenge_id,
        enrollmentId: challenge.enrollment_id,
        name,
        status: "done_today",
        streak: challenge.current_streak ?? challenge.currentStreak ?? 0,
        totalCheckins: challenge.total_checkins ?? challenge.totalCheckins ?? 0,
        todayChecked: true,
        mission,
      },
    };
  }

  return {
    state: "ready_today",
    title: t("space.zoneAction.readyTitle", { challenge: name }),
    text: t("space.zoneAction.readyText"),
    primaryLabel: t("space.zoneAction.continueMission"),
    primaryMode: "mission",
    fallbackTo: `/enrollment/${challenge.enrollment_id}`,
    secondaryLabel: t("space.zoneAction.viewPath"),
    secondaryMode: "path",
    secondaryTo: "/paths",
    challenge: {
      id: challenge.challenge_id,
      enrollmentId: challenge.enrollment_id,
      name,
      status: "ready_today",
      streak: challenge.current_streak ?? challenge.currentStreak ?? 0,
      totalCheckins: challenge.total_checkins ?? challenge.totalCheckins ?? 0,
      todayChecked: false,
      mission,
    },
  };
}

function findActivePathChallenge(pathDetail) {
  const challenges = pathDetail?.challenges || [];
  if (!challenges.length) return null;

  return challenges.find((challenge) => challenge.isCurrent)
    || challenges.find((challenge) => challenge.isJoined && !challenge.todayChecked)
    || challenges.find((challenge) => challenge.isJoined)
    || null;
}

function buildPathChallengeZoneAction(challenge) {
  const mission = findPathChallengeMission(challenge);

  if (challenge.todayChecked) {
    return {
      state: "done_today",
      title: t("space.zoneAction.doneTitle", { challenge: challenge.name }),
      text: t("space.zoneAction.doneText"),
      primaryLabel: t("space.zoneAction.reviewChallenge"),
      primaryMode: "path",
      fallbackTo: challenge.enrollmentId ? `/enrollment/${challenge.enrollmentId}` : "/paths",
      secondaryLabel: t("space.zoneAction.viewPath"),
      secondaryMode: "path",
      secondaryTo: "/paths",
      challenge: {
        id: challenge.id,
        enrollmentId: challenge.enrollmentId,
        name: challenge.name,
        status: "done_today",
        streak: 0,
        totalCheckins: challenge.doneCount || 0,
        todayChecked: true,
        mission,
      },
    };
  }

  return {
    state: "ready_today",
    title: t("space.zoneAction.readyTitle", { challenge: challenge.name }),
    text: t("space.zoneAction.readyText"),
    primaryLabel: t("space.zoneAction.continueMission"),
    primaryMode: "mission",
    fallbackTo: challenge.enrollmentId ? `/enrollment/${challenge.enrollmentId}` : "/paths",
    secondaryLabel: t("space.zoneAction.viewPath"),
    secondaryMode: "path",
    secondaryTo: "/paths",
    challenge: {
      id: challenge.id,
      enrollmentId: challenge.enrollmentId,
      name: challenge.name,
      status: "ready_today",
      streak: 0,
      totalCheckins: challenge.doneCount || 0,
      todayChecked: false,
      mission,
    },
  };
}

function findPathChallengeMission(challenge) {
  const missions = challenge?.missions || [];
  const mission = missions.find((item) => {
    return item.availableToday
      && item.status === "pending"
      && item.intensity === "main";
  })
    || missions.find((item) => item.availableToday && item.status === "pending")
    || missions.find((item) => ["done", "completed"].includes(String(item.status || "").toLowerCase()))
    || missions[0];

  if (!mission) return null;

  return {
    id: mission.id,
    title: mission.title || "",
    description: mission.description || "",
    status: mission.status || "pending",
    intensity: mission.intensity || "main",
    estimatedMinutes: mission.estimatedMinutes ?? null,
    xpReward: mission.xpReward ?? null,
    iconUrl: mission.iconUrl || "",
  };
}

function findPathForZone(zone) {
  const zonePathKey = normalizePathKey(zone?.path_key);

  return paths.value.find((path) => {
    return normalizePathKey(path?.key || path?.path_key || path?.slug) === zonePathKey;
  }) || null;
}

function buildPathDetail(zone) {
  const path = findPathForZone(zone);
  if (!path?.path_id) return null;

  const localizedPath = localizePath(path, locale.value);
  const rawChallenges = pathChallenges.value[path.path_id] || [];
  const challenges = rawChallenges.map((challenge) => buildPathChallenge(challenge, zone));
  const joinedCount = challenges.filter((challenge) => challenge.isJoined).length;
  const nextChallenge = challenges.find((challenge) => !challenge.isJoined) || null;
  const summary = pathSummaries.value[path.path_id] || {};
  const todayTotal = Number(summary.today_missions_total || 0);
  const todayDone = Number(summary.today_missions_done || 0);
  const pathProgressTotal = challenges.reduce((sum, challenge) => {
    return sum + Number(challenge.missionCount || 0);
  }, 0);
  const pathProgressDone = challenges.reduce((sum, challenge) => {
    return sum + Number(challenge.doneCount || 0);
  }, 0);

  return {
    pathId: path.path_id,
    key: path.key || zone.path_key,
    title: localizedPath?.title || zone.title,
    description: localizedPath?.description || "",
    challenges,
    joinedCount,
    totalCount: challenges.length,
    nextChallengeId: nextChallenge?.id || null,
    selectedChallengeId: selectedPathChallengeId.value,
    todayDone,
    todayTotal,
    pathProgressDone,
    pathProgressTotal,
  };
}

function buildPathChallenge(challenge, zone) {
  const localized = localizeChallenge(challenge, locale.value);
  const isCurrent = String(zone?.action?.challenge?.id || "") === String(challenge?.challenge_id || "");
  const isJoined = Boolean(challenge?.is_joined || challenge?.enrollment_id);
  const todayChecked = Boolean(challenge?.today_checked);
  const missions = Array.isArray(localized?.missions)
    ? localized.missions.map(buildPreviewMission)
    : [];
  const missionProgress = semanticMissionProgress(missions, {
    total: challenge?.today_missions_total,
    done: challenge?.today_missions_done,
  });

  return {
    id: challenge?.challenge_id,
    enrollmentId: challenge?.enrollment_id || null,
    name: localized?.name || localized?.challenge_name || t("common.challenge"),
    description: localized?.ringo_intro || localized?.description || "",
    stage: challenge?.stage || 1,
    isJoined,
    isCurrent,
    todayChecked,
    missionCount: missionProgress.total,
    doneCount: missionProgress.done,
    estimatedDays: Number(challenge?.estimated_days || challenge?.duration_days || 0),
    missions,
  };
}

function buildPreviewMission(mission) {
  const status = mission?.today_status || mission?.status || "pending";

  return {
    id: mission?.mission_id || mission?.id || mission?.key || mission?.title,
    title: mission?.title || t("common.mission"),
    description: mission?.description || "",
    status,
    intensity: mission?.mission_intensity || "main",
    availableToday: Boolean(mission?.available_today),
    parentMissionId: mission?.parent_mission_id ?? null,
    unlocksInDays: mission?.unlocks_in_days ?? null,
    estimatedMinutes: mission?.estimated_minutes ?? null,
    xpReward: mission?.xp_reward ?? null,
    iconUrl: missionIconUrl(mission),
  };
}

function semanticMissionProgress(missions, fallback = {}, options = {}) {
  const groups = new Map();
  const availableOnly = options.availableOnly !== false;

  missions.forEach((mission) => {
    if (availableOnly && !mission.availableToday) return;

    const key = missionProgressKey(mission);
    const group = groups.get(key) || { done: false };
    group.done = group.done || ["done", "completed"].includes(String(mission.status || "").toLowerCase());
    groups.set(key, group);
  });

  if (!groups.size && (fallback.total != null || fallback.done != null)) {
    return {
      total: Number(fallback.total || 0),
      done: Number(fallback.done || 0),
    };
  }

  return {
    total: groups.size,
    done: Array.from(groups.values()).filter((group) => group.done).length,
  };
}

function missionProgressKey(mission) {
  const intensity = String(mission?.intensity || "main").toLowerCase();

  if (intensity === "tiny") {
    return `main:${mission?.parentMissionId || mission?.id || "unknown"}`;
  }

  if (intensity === "main") {
    return `main:${mission?.id || "unknown"}`;
  }

  return `${intensity}:${mission?.id || "unknown"}`;
}

async function ensurePathChallenges(zone = displayActiveZone.value, options = {}) {
  const path = findPathForZone(zone);
  if (!path?.path_id) return;
  if (!options.force && pathChallenges.value[path.path_id]) return;

  await loadPathChallenges(path);
}

const dueReminders = computed(() => {
  return props.missions
    .filter((mission) => {
      return normalizedMissionStatus(mission) === "remind_later"
        && reminderTimestamp(mission) <= Date.now()
        && !mission?.reminder_sent_at;
    })
    .map((mission) => ({
      id: mission?.mission_id || mission?.id || `${mission?.title || "mission"}-${mission?.reminder_at || ""}`,
      title: mission?.title || mission?.mission_title || t("common.mission"),
      challengeName: mission?.challenge_name || mission?.challenge || "",
      pathId: mission?.path_id || null,
      pathKey: missionPathKey(mission),
      reminderAt: mission?.reminder_at || "",
      timestamp: reminderTimestamp(mission),
    }))
    .sort((a, b) => a.timestamp - b.timestamp);
});

const dueReminderCountByPath = computed(() => {
  return dueReminders.value.reduce((counts, reminder) => {
    const key = normalizePathKey(reminder.pathKey);
    if (!key) return counts;

    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {});
});

const futureReminderCount = computed(() => {
  return props.missions.filter((mission) => {
    return normalizedMissionStatus(mission) === "remind_later"
      && reminderTimestamp(mission) > Date.now();
  }).length;
});

const dailyMomentum = computed(() => {
  const missions = props.missions || [];
  const completedCount = missions.filter((mission) => {
    return ["done", "completed"].includes(normalizedMissionStatus(mission));
  }).length;
  const pendingCount = missions.filter((mission) => normalizedMissionStatus(mission) === "pending").length;
  const remindedCount = missions.filter((mission) => normalizedMissionStatus(mission) === "remind_later").length;

  return {
    todaySafe: props.todaySafe,
    total: missions.length,
    completed: completedCount,
    pending: pendingCount,
    reminded: remindedCount,
    due: dueReminders.value.length,
    futureReminders: futureReminderCount.value,
    reminderCount: Number(props.reminderCount || remindedCount || 0),
  };
});

function normalizedMissionStatus(mission) {
  return String(mission?.status || mission?.today_status || "pending").toLowerCase();
}

function missionPathKey(mission) {
  const directKey = normalizePathKey(mission?.path_key || mission?.path || "");
  if (directKey) return directKey;

  const pathId = normalizeId(mission?.path_id);
  if (!pathId) return "";

  const path = paths.value.find((item) => {
    return normalizeId(item?.path_id || item?.id) === pathId;
  });

  return normalizePathKey(path?.key || path?.path_key || path?.slug || "");
}

function reminderTimestamp(mission) {
  if (!mission?.reminder_at) return Number.POSITIVE_INFINITY;

  const date = new Date(mission.reminder_at);
  const timestamp = date.getTime();

  return Number.isNaN(timestamp) ? Number.POSITIVE_INFINITY : timestamp;
}

async function preloadZonePathChallenges(options = {}) {
  const zones = spaceState.value?.zones || [];

  for (const zone of zones) {
    const path = findPathForZone(zone);
    if (!path?.path_id) continue;
    if (!options.force && pathChallenges.value[path.path_id]) continue;
    await loadPathChallenges(path);
  }
}

async function loadPathChallenges(path) {
  const pathId = path?.path_id;
  if (!pathId) return;

  pathLoading.value = { ...pathLoading.value, [pathId]: true };
  pathErrors.value = { ...pathErrors.value, [pathId]: "" };

  try {
    const { data } = await api.get(`/paths/${pathId}/challenges`);
    pathChallenges.value = {
      ...pathChallenges.value,
      [pathId]: data?.items || [],
    };
    pathSummaries.value = {
      ...pathSummaries.value,
      [pathId]: data?.summary || {},
    };
  } catch (e) {
    pathErrors.value = {
      ...pathErrors.value,
      [pathId]: e?.response?.data?.error || e?.message || String(e),
    };
  } finally {
    pathLoading.value = { ...pathLoading.value, [pathId]: false };
  }
}

async function startChallenge(challenge) {
  const pathId = displayActiveZone.value?.pathDetail?.pathId;
  if (!challenge?.id || !pathId) return;

  startingChallengeId.value = challenge.id;

  try {
    await api.post(`/paths/${pathId}/start`, {});
    await submitJoinFlow({
      apiClient: api,
      challenge: { ...challenge, challenge_id: challenge.id },
      reload: async () => {},
    });
    await loadPathChallenges({ path_id: pathId });
    await loadSpace();
    emit("challenge-started", { challengeId: challenge.id, pathId });
  } catch (e) {
    pathErrors.value = {
      ...pathErrors.value,
      [pathId]: humanizeJoinError(e?.response?.data?.error || e?.message || String(e)),
    };
  } finally {
    startingChallengeId.value = null;
  }
}

async function completeMission(mission) {
  const missionId = mission?.id;
  const pathId = displayActiveZone.value?.pathDetail?.pathId;
  if (!missionId || !pathId) return;

  completingMissionId.value = missionId;
  pathErrors.value = { ...pathErrors.value, [pathId]: "" };

  try {
    const { data } = await api.post(`/me/missions/${missionId}/done`, {});
    await loadPathChallenges({ path_id: pathId });
    await loadSpace();
    emit("mission-completed", data || {});
  } catch (e) {
    pathErrors.value = {
      ...pathErrors.value,
      [pathId]: e?.response?.data?.error || e?.message || String(e),
    };
  } finally {
    completingMissionId.value = null;
  }
}

function normalizeId(value) {
  const id = String(value ?? "").trim();
  return id && id !== "null" && id !== "undefined" ? id : "";
}

function missionStatusRank(mission) {
  const status = String(mission?.status || "").toLowerCase();
  const intensity = String(mission?.mission_intensity || "main").toLowerCase();

  if (status === "pending" && intensity === "main") return 0;
  if (status === "pending") return 1;
  if (intensity === "main") return 2;
  return 3;
}

function findChallengeMission(challenge) {
  const enrollmentId = normalizeId(challenge?.enrollment_id);
  const challengeId = normalizeId(challenge?.challenge_id);

  const matches = props.missions
    .filter((mission) => {
      return (enrollmentId && normalizeId(mission?.enrollment_id) === enrollmentId)
        || (challengeId && normalizeId(mission?.challenge_id) === challengeId);
    })
    .sort((a, b) => missionStatusRank(a) - missionStatusRank(b));

  const mission = matches[0];
  if (!mission) return null;

  return {
    id: mission.mission_id || mission.id || null,
    title: mission.title || mission.mission_title || "",
    description: mission.description || mission.mission_description || "",
    status: mission.status || "pending",
    intensity: mission.mission_intensity || "main",
    estimatedMinutes: mission.estimated_minutes ?? mission.estimatedMinutes ?? null,
    xpReward: mission.xp_reward ?? mission.xpReward ?? null,
    iconUrl: missionIconUrl(mission),
  };
}

onMounted(async () => {
  await Promise.all([loadSpace(), loadPaths()]);
  await preloadZonePathChallenges();
});

watch(
  () => props.refreshKey,
  async () => {
    await loadSpace();
    await preloadZonePathChallenges({ force: true });
    if (["path", "challenge", "mission"].includes(shellMode.value)) {
      ensurePathChallenges(displayActiveZone.value, { force: true });
    }
  },
);

watch(
  () => [shellMode.value, displayActiveZone.value?.zone_key, paths.value.length],
  () => {
    if (shellMode.value === "path") {
      ensurePathChallenges(displayActiveZone.value);
    }
  },
);

watch(
  () => [displayActiveZone.value?.zone_key, paths.value.length],
  () => {
    if (displayActiveZone.value) {
      ensurePathChallenges(displayActiveZone.value);
    }
  },
);
</script>

<style scoped>
.livingSpace {
  display: grid;
  gap: var(--s-16);
  padding: 18px;
  overflow: hidden;
  background:
    radial-gradient(circle at 15% 0%, rgba(110, 229, 255, 0.08), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.018));
}

.spaceHead {
  display: flex;
  justify-content: space-between;
  gap: var(--s-16);
  align-items: flex-start;
}

.spaceKicker {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.82);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}

.spaceHead h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.42rem;
  line-height: 1.14;
}

.spaceHead p {
  margin: 8px 0 0;
  max-width: 680px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.6;
}

.spaceHead .spaceStatus {
  color: rgba(255, 255, 255, 0.72);
  font-weight: 750;
}

.spaceHead .spaceRule {
  margin-top: 6px;
  color: rgba(110, 229, 255, 0.70);
  font-size: 0.82rem;
  font-weight: 760;
}

.spaceMeta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.spaceMeta span {
  display: inline-flex;
  align-items: center;
  min-height: 31px;
  padding: 7px 10px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.09);
  font-size: 0.76rem;
  font-weight: 850;
}

.spaceLayout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--s-12);
  align-items: start;
}

.roomStage {
  position: relative;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  grid-auto-rows: minmax(120px, auto);
  gap: 10px;
  min-height: 430px;
  padding: 12px;
  border-radius: 10px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.02)),
    linear-gradient(145deg, rgba(10, 18, 30, 0.96), rgba(8, 12, 20, 0.95));
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.roomStage :deep(.zone-work_desk) {
  grid-column: 1 / span 3;
  grid-row: 1;
}

.roomStage :deep(.zone-learning_corner) {
  grid-column: 4 / span 3;
  grid-row: 1;
}

.roomStage :deep(.zone-creative_corner) {
  grid-column: 1 / span 2;
  grid-row: 2;
}

.roomStage :deep(.zone-fitness_corner) {
  grid-column: 3 / span 2;
  grid-row: 2;
}

.roomStage :deep(.zone-sleep_corner) {
  grid-column: 5 / span 2;
  grid-row: 2;
}

@media (max-width: 920px) {
  .spaceHead {
    flex-direction: column;
  }

  .spaceMeta {
    justify-content: flex-start;
  }
}

@media (max-width: 720px) {
  .roomStage {
    grid-template-columns: 1fr;
    grid-auto-rows: auto;
    min-height: 0;
  }

  .roomStage :deep(.spaceZone) {
    grid-column: auto;
    grid-row: auto;
  }
}
</style>
