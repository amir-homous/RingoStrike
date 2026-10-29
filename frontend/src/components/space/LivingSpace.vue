<template>
  <section class="livingSpace">
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

    <div
      v-if="spaceState && !loading && !error"
      class="spaceLayout"
      :class="{ hasPanel: Boolean(workSurfaceZone) }"
    >
      <div class="roomStageShell">
        <!-- Desktop: no head card (the panel already names the room). Below 1160px: one-line title. -->
        <h2 class="roomTitleCompact">{{ t("space.title") }}</h2>

        <RoomScene
          :zones="displayZones"
          :selected-zone-key="materializeZoneKey || visualActiveZone?.zone_key || ''"
          :suggested-zone-key="roomLevel && !materializeZoneKey ? suggestedZone?.zone_key || '' : ''"
          :rest="roomLevel && !materializeZoneKey"
          :today-safe="todaySafe"
          :pending-reward-keys="pendingRewardKeys"
          :materializing="materializing"
          :min-scale="roomPanLayout ? 2 : 1"
          :phone="!roomPanLayout"
          :selected-challenge-id="selectedPathChallengeId"
          :challenge-picked="challengePicked"
          :picked-mission-id="pickedMissionId"
          :object-highlight="objectHighlight"
          :reminder-counts="{ due: dueReminders.length, later: scheduledReminders.length }"
          :explain-pins="explainerOpen"
          @select="selectZone"
          @open-reminders="openReminderList"
          @select-challenge="selectPathChallenge"
          @select-mission="selectTrayMission"
        >
          <!-- Room corner (inline-end): objects chip, new-reward chip and the room info popover. -->
          <template #corner>
            <span class="cornerChip">{{ t("space.objects", { count: unlockedCount }, unlockedCount) }}</span>
            <span v-if="spaceState.has_unseen_rewards" class="cornerChip isNew">{{ t("space.newReward") }}</span>
            <span class="roomInfo" :class="{ open: roomInfoOpen }" @keydown.esc="roomInfoOpen = false">
              <button
                type="button"
                class="roomInfoButton"
                :aria-label="t('space.roomInfoLabel')"
                :aria-expanded="roomInfoOpen ? 'true' : 'false'"
                aria-describedby="room-info-popover"
                @click="roomInfoOpen = !roomInfoOpen"
              >i</button>
              <span id="room-info-popover" role="tooltip" class="roomInfoPopover">{{ t("space.rule") }}</span>
            </span>
          </template>

          <!-- Fallback when the room art cannot load: the previous zone card grid. -->
          <template #fallback>
            <div class="roomStage" :aria-label="t('space.roomLabel')">
              <SpaceZone
                v-for="zone in displayZones"
                :key="zone.zone_key"
                :zone="zone"
                :active="visualActiveZone?.zone_key === zone.zone_key"
                :has-active-selection="hasActiveZoneSelection"
                :feedback="recentRoomFeedback"
                :suggested="roomLevel && suggestedZone?.zone_key === zone.zone_key"
                @select="selectZone"
              />
            </div>
          </template>
        </RoomScene>
      </div>

      <!-- B34 (D68): the clock opens Ringo's panel with every reminder (board 24). -->
      <div v-if="reminderListOpen" ref="reminderListZone" class="roomSafeZone">
        <ReminderListPanel
          :reminders="reminderItems"
          @open="openReminderRow"
          @close="closeReminderList"
        />
      </div>

      <div v-else-if="roomLevel" class="roomSafeZone">
        <RoomOverviewPanel
          :title="roomOverviewGuidance?.title || t('space.title')"
          :text="roomOverviewGuidance?.text || ''"
          :mood="roomMood"
          :tone="todaySafe ? 'safe' : 'neutral'"
          :today-safe="todaySafe"
          :completed="Number(dailyMomentum.completed || 0)"
          :total="Number(dailyMomentum.total || 0)"
          :due-count="dueReminders.length"
          :scheduled-count="scheduledReminders.length"
          :objects-today="objectsPlacedToday"
          :suggested-zone="suggestedZone"
          @select-zone="selectZone"
        />
      </div>

      <!-- Phones: the zone panel is a bottom sheet over the lower part of the screen (B22). -->
      <div
        v-else-if="workSurfaceZone"
        ref="zoneSheet"
        class="roomSafeZone"
        :class="{ zoneSheet: !roomPanLayout }"
        :role="roomPanLayout ? null : 'dialog'"
        :aria-label="roomPanLayout ? null : workSurfaceZone.title"
        :tabindex="roomPanLayout ? null : -1"
        :style="roomPanLayout || !sheetTop ? null : { '--sheet-top': `${sheetTop}px` }"
        @keydown.esc="!roomPanLayout && closePanel()"
      >
        <SpaceZonePanel
          :mode="workSurfaceMode"
          :first-run="firstRunArrival"
          :explainer="explainerOpen"
          @dismiss-explainer="dismissExplainer"
          :zone="workSurfaceZone"
          :checking-id="checkingId"
          :path-loading="activePathLoading"
          :path-error="activePathError"
          :selected-challenge-id="selectedPathChallengeId"
          :challenge-picked="challengePicked"
          :joined-challenge-id="joinedChallengeId"
          :picked-mission-id="pickedMissionId"
          :completing-mission-id="completingMissionId"
          :starting-challenge-id="startingChallengeId"
          :today-safe="todaySafe"
          :daily-momentum="dailyMomentum"
          :due-reminders="dueReminders"
          :due-reminder-focus="activeDueReminderFocus"
          :future-reminder-count="futureReminderCount"
          :reminders="reminderItems"
          :requested-mission-id="requestedMissionId"
          :now="now"
          :room-feedback="panelRoomFeedback"
          :closable="true"
          @change-mode="changeShellMode"
          @select-challenge="selectPathChallenge"
          @start-challenge="startChallenge"
          @complete-mission="completeMission"
          :user-key="userKey"
          @remind-mission="remindMission"
          @skip-mission="skipMission"
          @focus-reminder="focusReminder"
          @checkin="$emit('checkin', $event)"
          @close="closePanel"
          @highlight-object="objectHighlight = $event"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { formatNumber, numberAwareT } from "@/lib/i18nNumbers";
import api from "@/lib/api";
import UiState from "@/components/ui/UiState.vue";
import { challengeIconKey } from "@/lib/challengeIconKeys";
import { getChallengePathKey, getOnboardingUserKey, isRoomExplainerSeen, markRoomExplainerSeen } from "@/lib/guidedExperience";
import { shouldShowExplainer } from "@/lib/roomExplainer";
import { localizeSpaceReward, localizeSpaceZone } from "@/lib/livingSpaceCopy";
import {
  dueReminderFocusForZone,
  findDueReminderZone,
  isDueReminderMission,
  normalizeId,
  normalizePathKey,
  normalizedMissionStatus,
  reminderTimestamp,
} from "@/lib/livingSpaceState";
import { localizeChallenge, localizePath } from "@/lib/ringoContentLocalization";
import { createMaterializeQueue, materializeCandidates, materializeTimeline } from "@/lib/roomMaterialize";
import { PATH_ICON_FALLBACK, pathMarkerState, telegramReady } from "@/lib/pathMarker";
import { bonusDoneByChallenge, bonusDoneByPath } from "@/lib/bonusStars";
import { missionReminderChip } from "@/lib/missionTray";
import { missionIconUrl, resolvePathIcon } from "@/utils/missionMomentumUtils";
import { humanizeJoinError, submitJoinFlow } from "@/views/challengeFlow";
import SpaceZone from "./SpaceZone.vue";
import ReminderListPanel from "./ReminderListPanel.vue";
import RoomOverviewPanel from "./RoomOverviewPanel.vue";
import RoomScene from "./RoomScene.vue";
import SpaceZonePanel from "./SpaceZonePanel.vue";

const props = defineProps({
  refreshKey: { type: Number, default: 0 },
  challenges: { type: Array, default: () => [] },
  missions: { type: Array, default: () => [] },
  todaySafe: { type: Boolean, default: false },
  focusReason: { type: String, default: "" },
  reminderCount: { type: Number, default: 0 },
  checkingId: { type: [Number, String, null], default: null },
  roomFeedbackEvent: { type: Object, default: null },
  // B21: true while the Ringo Moment or the reward card is open (newly unlocked objects stay ghosts).
  holdRewards: { type: Boolean, default: false },
  // B21: { id, reward } when a reward card closes; that reward materializes in the room.
  materializeEvent: { type: Object, default: null },
  // B30: { connected, reminders_enabled } from the settings MissionCenter already loads (null = unknown).
  telegramSettings: { type: Object, default: null },
});

const emit = defineEmits(["checkin", "challenge-started", "mission-completed"]);

const { locale, t: baseT, te } = useI18n();
// B10: numbers in copy use the locale's digits; a numeric count picks the plural form.
const t = numberAwareT(baseT, () => locale.value);
const fmt = (value) => formatNumber(value, locale.value);

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
// B30 S2: true after an explicit challenge pick (tray icon or panel row), until the zone changes.
const challengePicked = ref(false);
// B30 S2: the challenge just joined from the room; the card shows the post-join state (D39).
const joinedChallengeId = ref(null);
// B30 S3: the paw tapped in the mission tray (D51).
const pickedMissionId = ref(null);
// B19: room info popover in the room corner (the rule text); click/hover/focus opens, Esc closes.
const roomInfoOpen = ref(false);

// B19: from tablet width (600px) the room is at least x2 (if the height allows) and, when x2 is
// wider than its column, cropped with the camera pan instead of shrinking to x1. Phones keep x1
// and scroll the room inside its own frame (B22 adds the mobile zoom).
const ROOM_PAN_QUERY = "(min-width: 600px)";
const roomPanLayout = ref(false);
let roomPanMedia = null;

function syncRoomPanLayout() {
  roomPanLayout.value = Boolean(roomPanMedia?.matches);
}

// B27: user scope for the split action's flows (timer in sessionStorage, remembered place).
const userKey = ref("");

async function loadUserKey() {
  try {
    const { data } = await api.get("/me");
    userKey.value = getOnboardingUserKey(data) || "";
  } catch {
    userKey.value = "";
  }
}

// B22 phones: the zone panel is a bottom sheet; opening one moves focus into it. The sheet stops
// at the room's bottom edge so the zoomed zone stays visible above it.
const zoneSheet = ref(null);
const sheetTop = ref(0);

function measureSheetTop() {
  if (roomPanLayout.value || typeof document === "undefined") return;
  const bottom = document.querySelector(".livingSpace .roomViewport")?.getBoundingClientRect().bottom || 0;
  sheetTop.value = Math.max(0, Math.round(bottom));
}

// B23: room-level overview after "Back to room" or "Enough for today" (no zone panel open).
const roomLevel = ref(false);
// B24: mission the user asked to focus from the reminder list (may be in another zone).
const requestedMissionId = ref(null);
// Ticks so reminders move from "time left" to due without a reload.
const now = ref(Date.now());
let reminderClock = null;
const startingChallengeId = ref(null);
const completingMissionId = ref(null);
const recentRoomFeedback = ref(null);
let roomFeedbackTimer = null;

const unlockedCount = computed(() => {
  return spaceState.value?.unlocked_objects?.length || 0;
});

const displayZones = computed(() => {
  return (spaceState.value?.zones || []).map((rawZone) => {
    const zone = localizeSpaceZone(rawZone, t, te);
    const pathDetail = buildPathDetail(zone);
    const zonePathKey = normalizePathKey(zone.path_key);
    const dueReminderCount = dueReminderCountByPath.value[zonePathKey] || 0;
    const scheduledReminderCount = scheduledReminderCountByPath.value[zonePathKey] || 0;

    return {
      ...zone,
      pathDetail,
      action: buildZoneAction(zone, pathDetail),
      dueReminderCount,
      scheduledReminderCount,
      // B30: read-only path marker (ring, colour, lit, badge, reminder chip) for the room.
      pathMarker: {
        ...pathMarkerState({
          challenges: pathDetail?.challenges || [],
          color: pathDetail?.color,
          dueCount: dueReminderCount,
          scheduledCount: scheduledReminderCount,
          telegram: telegramReady(props.telegramSettings),
        }),
        title: pathDetail?.title || zone.pathName || zone.title,
        // B36 (D70): Bonus steps finished today in this path (a row of stars under the icon).
        bonusDone: bonusDoneToday.value.byPath[zonePathKey] || 0,
        iconUrl: resolvePathIcon(pathDetail?.icon || PATH_ICON_FALLBACK[zonePathKey] || zonePathKey),
      },
    };
  });
});

const displayActiveZone = computed(() => {
  if (!activeZone.value) return null;

  return displayZones.value.find(
    (zone) => zone.zone_key === activeZone.value.zone_key,
  ) || null;
});

const dueReminderFocus = computed(() => dueReminders.value[0] || null);

const dueReminderZone = computed(() => {
  return findDueReminderZone(dueReminderFocus.value, displayZones.value);
});

const visualActiveZone = computed(() => {
  if (roomLevel.value) return null;
  return displayActiveZone.value || dueReminderZone.value;
});

const hasActiveZoneSelection = computed(() => {
  return Boolean(visualActiveZone.value);
});

const restZone = computed(() => {
  if (!displayActiveZone.value && dueReminderZone.value) return dueReminderZone.value;

  return displayZones.value.find((zone) => zone.action?.state === "done_today")
    || displayZones.value.find((zone) => (zone.unlocked_objects || []).length > 0)
    || displayZones.value[0]
    || null;
});

const shouldShowRestPanel = computed(() => {
  if (activeZone.value) return false;
  if (dueReminderFocus.value) return true;

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
  if (dueReminderZone.value) return dueReminderZone.value;
  if (panelMode.value === "rest") return restZone.value;
  return null;
});

const activeDueReminderFocus = computed(() => {
  const zone = panelZone.value || workSurfaceZone.value;
  return dueReminderFocusForZone(dueReminderFocus.value, dueReminderZone.value, zone);
});

// B23: the zone Ringo suggests next on the room overview (due reminder, ready, or start zone).
const suggestedZone = computed(() => {
  const zones = displayZones.value;
  const due = zones.find((zone) => Number(zone.dueReminderCount || 0) > 0);
  if (due) return due;

  const ready = zones.find((zone) => zone.action?.state === "ready_today");
  const start = zones.find((zone) => zone.action?.state === "not_started");
  const unseen = zones.find((zone) => zone.has_unseen_rewards);

  // After today is safe, suggest looking at what changed rather than more work.
  return props.todaySafe
    ? unseen || ready || start || null
    : ready || start || unseen || null;
});

const roomMood = computed(() => {
  if (dueReminders.value.length) return "thinking";
  return props.todaySafe ? "sleeping" : "welcome";
});

const objectsPlacedToday = computed(() => {
  const today = new Date().toDateString();
  return (spaceState.value?.zones || []).reduce((count, zone) => {
    return count + (zone.unlocked_objects || []).filter((reward) => {
      const unlockedAt = reward?.unlocked_at ? new Date(reward.unlocked_at) : null;
      return unlockedAt && !Number.isNaN(unlockedAt.getTime()) && unlockedAt.toDateString() === today;
    }).length;
  }, 0);
});

const workSurfaceZone = computed(() => {
  return panelZone.value
    || roomOverviewGuidance.value?.zone
    || restZone.value
    || displayZones.value[0]
    || null;
});

const workSurfaceMode = computed(() => {
  if (panelZone.value) return panelMode.value;
  const guidanceMode = roomOverviewGuidance.value?.mode;
  return ["path", "challenge", "mission", "rest"].includes(guidanceMode)
    ? guidanceMode
    : "zone";
});

const activePathId = computed(() => workSurfaceZone.value?.pathDetail?.pathId || "");

const activePathLoading = computed(() => {
  const pathId = activePathId.value;
  return pathId ? Boolean(pathLoading.value[pathId]) : false;
});

const activePathError = computed(() => {
  const pathId = activePathId.value;
  return pathId ? pathErrors.value[pathId] || "" : "";
});

const panelRoomFeedback = computed(() => {
  if (!recentRoomFeedback.value) return null;
  const zoneKey = workSurfaceZone.value?.zone_key || "";
  return String(recentRoomFeedback.value.zoneKey || "") === String(zoneKey)
    ? recentRoomFeedback.value
    : null;
});

const roomOverviewGuidance = computed(() => {
  if (!displayZones.value.length) return null;

  const dueZone = displayZones.value.find((zone) => Number(zone.dueReminderCount || 0) > 0);
  if (dueZone) {
    return {
      state: "reminder",
      zone: dueZone,
      mode: "rest",
      title: t("space.overview.reminderTitle", { path: dueZone.title }),
      text: t("space.overview.reminderText", { count: dueZone.dueReminderCount }),
      cta: t("space.overview.reminderCta"),
    };
  }

  if (props.todaySafe) {
    return {
      state: "safe",
      mode: "rest",
      title: t("space.overview.safeTitle"),
      text: t("space.overview.safeText"),
      cta: t("space.overview.safeCta"),
    };
  }

  const readyZone = displayZones.value.find((zone) => zone.action?.state === "ready_today");
  if (readyZone) {
    return {
      state: "ready",
      zone: readyZone,
      mode: "mission",
      title: t("space.overview.readyTitle", { path: readyZone.title }),
      text: t("space.overview.readyText"),
      cta: t("space.overview.readyCta"),
    };
  }

  const startZone = displayZones.value.find((zone) => zone.action?.state === "not_started");
  if (startZone && unlockedCount.value === 0) {
    return {
      state: "start",
      zone: startZone,
      mode: "path",
      title: t("space.overview.startTitle", { path: startZone.title }),
      text: t("space.overview.startText"),
      cta: t("space.overview.startCta"),
    };
  }

  const progressZone = displayZones.value.find((zone) => (zone.unlocked_objects || []).length > 0)
    || displayZones.value[0];

  return {
    state: "progress",
    zone: progressZone,
    mode: "zone",
    title: t("space.overview.progressTitle"),
    text: t("space.overview.progressText", { count: unlockedCount.value }),
    cta: t("space.overview.progressCta"),
  };
});

async function loadSpace(options = {}) {
  const silent = Boolean(options?.silent || spaceState.value);

  if (!silent) {
    loading.value = true;
  }
  error.value = "";

  try {
    const { data } = await api.get("/me/space");
    spaceState.value = data;
    // B21: unseen, non-backfilled unlocks wait as ghosts until they materialize (once each).
    enqueueMaterialize(materializeCandidates(data?.rewards || []));

    if (activeZone.value) {
      activeZone.value = data.zones.find(
        (zone) => zone.zone_key === activeZone.value.zone_key,
      ) || null;
    }
  } catch (e) {
    if (silent) {
      console.warn("Could not refresh Living Space", e);
    } else {
      error.value = e?.response?.data?.error || e?.message || String(e);
    }
  } finally {
    if (!silent) {
      loading.value = false;
    }
  }

  runMaterializeQueue();
}

// B21: materialize sequence (spec §6). Plays once per newly unlocked reward, after the reward
// card closes (or on load for an unlock that was never seen), each in its own zone in turn.
// Desktop/tablet select the zone (camera pan); phones zoom to it and open the sheet afterwards.
const CAMERA_SETTLE_MS = 320;
const materializeQueue = createMaterializeQueue();
const pendingRewardKeys = ref([]);
const materializing = ref(null);
// B34 (D68): Ringo's reminder list, opened from the clock next to Ringo.
const reminderListOpen = ref(false);
const reminderListZone = ref(null);

function openReminderList() {
  if (!roomLevel.value) closePanel();
  reminderListOpen.value = true;
  // Phones: the list sits under the room; bring it into view.
  nextTick(() => reminderListZone.value?.scrollIntoView?.({ block: "nearest", behavior: "smooth" }));
}

function closeReminderList() {
  reminderListOpen.value = false;
}

function openReminderRow(reminder) {
  reminderListOpen.value = false;
  focusReminder({ ...reminder, explicit: true });
}

// B32 (D62): the object tile just tapped ({ key, ghost, label, nonce }); the room lifts and glows it.
const objectHighlight = ref(null);
const materializeZoneKey = ref("");
let materializeRunning = false;
let materializeTimers = [];
let livingSpaceUnmounted = false;

function enqueueMaterialize(rewards) {
  if (materializeQueue.enqueue(rewards).length) {
    pendingRewardKeys.value = materializeQueue.pendingKeys();
  }
}

function prefersReducedMotion() {
  return typeof window !== "undefined"
    && Boolean(window.matchMedia?.("(prefers-reduced-motion: reduce)").matches);
}

function materializeWait(ms) {
  return new Promise((resolve) => {
    materializeTimers.push(setTimeout(resolve, ms));
  });
}

async function runMaterializeQueue() {
  if (materializeRunning || props.holdRewards || !spaceState.value) return;
  materializeRunning = true;
  let lastZone = null;
  let played = 0;

  try {
    while (!livingSpaceUnmounted && !props.holdRewards) {
      const item = materializeQueue.next();
      if (!item) break;
      const reward = (spaceState.value?.rewards || []).find((entry) => entry.key === item.key);
      // The room has not loaded this unlock yet; the next load retries.
      if (!reward?.unlocked) break;

      // Seen first, so a reload never plays it again (idempotent after the card's own call).
      if (!reward.is_seen && reward.id) {
        await api.post(`/me/space/rewards/${reward.id}/seen`).catch(() => {});
      }

      const zone = displayZones.value.find((entry) => entry.zone_key === reward.zone_key) || null;
      if (zone) {
        lastZone = zone;
        if (roomPanLayout.value) selectZone(zone);
        else materializeZoneKey.value = zone.zone_key;
      }

      const timeline = materializeTimeline({ reducedMotion: prefersReducedMotion() });
      if (timeline.length) {
        // Camera first (the zone light stays off), then the sequence.
        materializing.value = { rewardKey: item.key, zoneKey: reward.zone_key, phase: "camera" };
        await materializeWait(CAMERA_SETTLE_MS);
        for (const step of timeline) {
          if (livingSpaceUnmounted) return;
          materializing.value = { rewardKey: item.key, zoneKey: reward.zone_key, phase: step.name };
          await materializeWait(step.ms);
        }
      }

      materializing.value = null;
      materializeQueue.done(item.key);
      pendingRewardKeys.value = materializeQueue.pendingKeys();
      played += 1;
    }
  } finally {
    materializeRunning = false;
    materializing.value = null;
    if (!livingSpaceUnmounted) {
      // Phones: the sheet opens after the sequence, on the last zone.
      if (materializeZoneKey.value) {
        materializeZoneKey.value = "";
        if (lastZone) selectZone(lastZone);
      }
      // Refresh the "new reward" state now that these rewards are seen.
      if (played) loadSpace({ silent: true });
    }
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
  reminderListOpen.value = false;
  const openingSheet = !roomPanLayout.value && roomLevel.value;
  roomLevel.value = false;
  if (openingSheet) {
    measureSheetTop();
    nextTick(() => zoneSheet.value?.focus({ preventScroll: true }));
  }
  requestedMissionId.value = null;
  objectHighlight.value = null;
  activeZone.value = zone;
  shellMode.value = "zone";
  selectedPathChallengeId.value = null;
  challengePicked.value = false;
  joinedChallengeId.value = null;
  pickedMissionId.value = null;
  ensurePathChallenges(zone);
}

function closePanel() {
  roomLevel.value = true;
  objectHighlight.value = null;
  requestedMissionId.value = null;
  activeZone.value = null;
  shellMode.value = "zone";
  selectedPathChallengeId.value = null;
  challengePicked.value = false;
  joinedChallengeId.value = null;
  pickedMissionId.value = null;
}

// B24: open the reminder's zone and challenge and ask the panel to focus that mission.
function focusReminder(reminder) {
  reminderListOpen.value = false;
  const zoneKey = zoneLabelsByPath.value[normalizePathKey(reminder?.pathKey)]?.zoneKey;
  const zone = displayZones.value.find((item) => item.zone_key === zoneKey) || workSurfaceZone.value;
  if (!zone) return;

  if (roomLevel.value) measureSheetTop();
  roomLevel.value = false;
  activeZone.value = zone;
  shellMode.value = "zone";
  selectedPathChallengeId.value = reminder?.challengeId || null;
  // B33 (D66): a tapped reminder row is an explicit pick of its mission, so it beats a due
  // reminder (D51) and its challenge's mission tray shows with that paw selected.
  const explicit = Boolean(reminder?.explicit && reminder?.challengeId);
  challengePicked.value = explicit;
  joinedChallengeId.value = null;
  pickedMissionId.value = explicit ? reminder.id : null;
  requestedMissionId.value = reminder?.id || null;
  ensurePathChallenges(zone);
}

function changeShellMode(mode) {
  if (!["zone", "path", "challenge", "mission", "rest"].includes(mode)) return;
  if (mode === "rest") {
    roomLevel.value = true;
    requestedMissionId.value = null;
    activeZone.value = null;
    shellMode.value = mode;
    selectedPathChallengeId.value = null;
    challengePicked.value = false;
    joinedChallengeId.value = null;
    pickedMissionId.value = null;
      return;
  }

  if (!activeZone.value && workSurfaceZone.value) {
    activeZone.value = workSurfaceZone.value;
  }

  shellMode.value = mode;

  if (["path", "challenge", "mission"].includes(mode)) {
    ensurePathChallenges(panelZone.value);
  }
}

// An explicit pick (tray icon or panel row) makes the Ringo card answer for that challenge, ahead
// of a due reminder (D14, D41); the reminder becomes one line in the card.
function selectPathChallenge(challenge) {
  selectedPathChallengeId.value = challenge?.id || null;
  challengePicked.value = Boolean(challenge?.id);
  joinedChallengeId.value = null;
  requestedMissionId.value = null;
  pickedMissionId.value = null;
}

// B30 S3: a paw in the mission tray makes that mission the Ringo focus, ahead of a due reminder
// (D51). A locked or done paw only gets Ringo's explanation or the done card (D20, D48).
function selectTrayMission(mission) {
  pickedMissionId.value = mission?.id ?? null;
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
        iconKey: challengeIconKey(challenge.challenge_name || challenge.name),
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
      iconKey: challengeIconKey(challenge.challenge_name || challenge.name),
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
        iconKey: challenge.iconKey,
        status: "done_today",
        streak: challenge.currentStreak || 0,
        totalCheckins: challenge.totalCheckins || challenge.doneCount || 0,
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
      iconKey: challenge.iconKey,
      status: "ready_today",
      streak: challenge.currentStreak || 0,
      totalCheckins: challenge.totalCheckins || challenge.doneCount || 0,
      todayChecked: false,
      mission,
    },
  };
}

function findPathChallengeMission(challenge) {
  const missions = challenge?.missions || [];
  const decidedTiny = missions.find((item) => {
    return String(item.intensity || "").toLowerCase() === "tiny"
      && ["remind_later", "skipped", "done", "completed"].includes(String(item.status || "").toLowerCase());
  });
  const mission = decidedTiny || missions.find((item) => {
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
    color: path.color || "",
    icon: path.icon || "",
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
    iconKey: challengeIconKey(challenge?.name || challenge?.challenge_name),
    name: localized?.name || localized?.challenge_name || t("common.challenge"),
    description: localized?.ringo_intro || localized?.description || "",
    stage: challenge?.stage || 1,
    isJoined,
    isCurrent,
    todayChecked,
    // D40: invite-only challenges are joined on the Challenges page (the code input lives there).
    visibility: challenge?.visibility || "Public",
    needsCode: String(challenge?.visibility || "").toLowerCase() === "invite-only" || Boolean(challenge?.needs_code),
    currentStreak: Number(challenge?.current_streak || challenge?.currentStreak || 0),
    totalCheckins: Number(challenge?.total_checkins || challenge?.totalCheckins || 0),
    missionCount: missionProgress.total,
    doneCount: missionProgress.done,
    estimatedDays: Number(challenge?.estimated_days || challenge?.duration_days || 0),
    // B36 (D70): Bonus finished today in this challenge (stars on its ring).
    bonusDone: bonusDoneToday.value.byChallenge.get(String(challenge?.challenge_id ?? "")) || 0,
    missions,
  };
}

// B30 S3 (D51): today's mission rows by id, for each challenge mission's reminder state. The
// challenge payload has reminder_at only; /me/today-missions (the missions prop) has
// reminder_sent_at too, but only for unlocked missions.
const todayMissionsById = computed(() => {
  return new Map(props.missions.map((mission) => [String(mission?.mission_id ?? mission?.id ?? ""), mission]));
});

function buildPreviewMission(mission) {
  const status = mission?.today_status || mission?.status || "pending";
  const id = mission?.mission_id || mission?.id || mission?.key || mission?.title;
  const todayRow = todayMissionsById.value.get(String(mission?.mission_id ?? mission?.id ?? ""));

  return {
    id,
    reminderAt: todayRow?.reminder_at || mission?.reminder_at || null,
    reminder: missionReminderChip(todayRow, { now: now.value, telegram: telegramReady(props.telegramSettings) }),
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

function toReminderItem(mission) {
  return {
    id: mission?.mission_id || mission?.id || `${mission?.title || "mission"}-${mission?.reminder_at || ""}`,
    title: mission?.title || mission?.mission_title || t("common.mission"),
    challengeName: mission?.challenge_name || mission?.challenge || "",
    // B33 fix: the stable icon key (the name is translated in FA).
    challengeIconKey: mission?.challenge_icon_key || "",
    challengeId: mission?.challenge_id || null,
    enrollmentId: mission?.enrollment_id || null,
    pathId: mission?.path_id || null,
    pathKey: missionPathKey(mission),
    reminderAt: mission?.reminder_at || "",
    timestamp: reminderTimestamp(mission),
  };
}

const dueReminders = computed(() => {
  return props.missions
    .filter((mission) => isDueReminderMission(mission, now.value))
    .map(toReminderItem)
    .sort((a, b) => a.timestamp - b.timestamp);
});

// Reminders set for later today that are not due yet.
const scheduledReminders = computed(() => {
  return props.missions
    .filter((mission) => {
      return normalizedMissionStatus(mission) === "remind_later"
        && reminderTimestamp(mission) > now.value;
    })
    .map(toReminderItem)
    .sort((a, b) => a.timestamp - b.timestamp);
});

const scheduledReminderCountByPath = computed(() => {
  return scheduledReminders.value.reduce((counts, reminder) => {
    const key = normalizePathKey(reminder.pathKey);
    if (!key) return counts;

    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {});
});

// Zone title and path name per path key, for "zone · path" in the reminder list.
const zoneLabelsByPath = computed(() => {
  return (spaceState.value?.zones || []).reduce((labels, rawZone) => {
    const zone = localizeSpaceZone(rawZone, t, te);
    labels[normalizePathKey(zone.path_key)] = {
      zoneKey: zone.zone_key,
      zoneTitle: zone.title,
      pathName: zone.pathName,
    };
    return labels;
  }, {});
});

const reminderItems = computed(() => {
  const label = (reminder) => zoneLabelsByPath.value[normalizePathKey(reminder.pathKey)] || {};

  // B33 (D66): rows show "Telegram off" when Telegram cannot deliver a set reminder.
  const telegram = telegramReady(props.telegramSettings);
  return [
    ...dueReminders.value.map((reminder) => ({ ...reminder, ...label(reminder), due: true, telegram })),
    ...scheduledReminders.value.map((reminder) => ({ ...reminder, ...label(reminder), due: false, telegram })),
  ];
});

const dueReminderCountByPath = computed(() => {
  return dueReminders.value.reduce((counts, reminder) => {
    const key = normalizePathKey(reminder.pathKey);
    if (!key) return counts;

    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {});
});

const futureReminderCount = computed(() => scheduledReminders.value.length);

// B36 (D70): today's finished Bonus steps per challenge and per path, from /me/today-missions
// (daily like the rest, D44).
const bonusDoneToday = computed(() => ({
  byChallenge: bonusDoneByChallenge(props.missions),
  byPath: bonusDoneByPath(props.missions, missionPathKey),
}));

const dailyMomentum = computed(() => {
  const missions = props.missions || [];
  // B11: count like the zone's today strip: a tiny substitute counts only once the user used it
  // (a new user saw "0/3" here but "0/2" in the zone).
  const counted = missions.filter((mission) => {
    return String(mission?.mission_intensity || mission?.intensity || "main").toLowerCase() !== "tiny"
      || ["done", "completed", "remind_later", "skipped"].includes(normalizedMissionStatus(mission));
  });
  const completedCount = counted.filter((mission) => {
    return ["done", "completed"].includes(normalizedMissionStatus(mission));
  }).length;
  const pendingCount = missions.filter((mission) => normalizedMissionStatus(mission) === "pending").length;
  const remindedCount = missions.filter((mission) => normalizedMissionStatus(mission) === "remind_later").length;

  return {
    todaySafe: props.todaySafe,
    total: counted.length,
    completed: completedCount,
    pending: pendingCount,
    reminded: remindedCount,
    due: dueReminders.value.length,
    futureReminders: futureReminderCount.value,
    reminderCount: Number(props.reminderCount || remindedCount || 0),
  };
});

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
  const pathId = workSurfaceZone.value?.pathDetail?.pathId;
  if (!challenge?.id || !pathId) return;

  startingChallengeId.value = challenge.id;
  pathErrors.value = { ...pathErrors.value, [pathId]: "" };

  try {
    await api.post(`/paths/${pathId}/start`, {});
    await submitJoinFlow({
      apiClient: api,
      challenge: { ...challenge, challenge_id: challenge.id },
      reload: async () => {},
    });
    await loadPathChallenges({ path_id: pathId });
    await loadSpace({ silent: true });
    // D39: the card shows the post-join moment for this challenge (no full-screen dialog).
    selectedPathChallengeId.value = challenge.id;
    challengePicked.value = true;
    joinedChallengeId.value = challenge.id;
    emit("challenge-started", { challengeId: challenge.id, pathId });
  } catch (e) {
    pathErrors.value = {
      ...pathErrors.value,
      [pathId]: humanizeJoinError(e?.response?.data?.error || e?.message || String(e), t),
    };
  } finally {
    startingChallengeId.value = null;
  }
}

// B27: the split action's flows send B26 context ({} for the plain button) and get the result
// back, so a failed save keeps the user's answers.
async function completeMission(mission, options = {}) {
  const body = options?.context && typeof options.context === "object" ? options.context : {};
  const result = await mutateMission(
    mission,
    "done",
    (missionId) => api.post(`/me/missions/${missionId}/done`, body),
  );
  options?.onResult?.(result);
}

async function remindMission(payload) {
  const mission = payload?.mission || payload;
  const reminderAt = payload?.reminderAt || reminderAtForLivingSpace();

  await mutateMission(
    mission,
    "remind_later",
    (missionId) => api.post(`/me/missions/${missionId}/remind-later`, {
      reminder_at: reminderAt,
    }),
  );
}

async function skipMission(payload) {
  const mission = payload?.mission || payload;
  const body = payload?.reason ? { reason: payload.reason } : {};

  await mutateMission(
    mission,
    "skip",
    (missionId) => api.post(`/me/missions/${missionId}/skip`, body),
  );
}

function reminderAtForLivingSpace() {
  return new Date(Date.now() + 15 * 60 * 1000).toISOString();
}

async function mutateMission(mission, action, request) {
  const missionId = mission?.id;
  const pathId = workSurfaceZone.value?.pathDetail?.pathId;
  const feedbackZone = workSurfaceZone.value || null;
  if (!missionId || !pathId) return { ok: false, error: "mission_unavailable" };

  completingMissionId.value = missionId;
  pathErrors.value = { ...pathErrors.value, [pathId]: "" };

  try {
    const { data } = await request(missionId);
    if (action !== "done") {
      await loadPathChallenges({ path_id: pathId });
      await loadSpace({ silent: true });
    }
    const roomFeedback = action === "done"
      ? buildRoomFeedback(data, feedbackZone)
      : null;
    emit("mission-completed", {
      ...(data || {}),
      living_space_action: action,
      living_space_room_feedback: roomFeedback,
    });
    return { ok: true };
  } catch (e) {
    const error = e?.response?.data?.error || e?.message || String(e);
    pathErrors.value = {
      ...pathErrors.value,
      [pathId]: error,
    };
    return { ok: false, error };
  } finally {
    completingMissionId.value = null;
  }
}

function buildRoomFeedback(data, zone) {
  const reward = localizeSpaceReward(data?.living_space_reward || null, t, te);
  const zoneKey = reward?.zone_key || zone?.zone_key || "";
  if (!zoneKey) return null;

  return reward
    ? {
      type: "reward",
      zoneKey,
      rewardKey: reward.key || "",
      label: t("space.feedback.rewardLabel"),
      title: t("space.feedback.rewardTitle", {
        reward: reward.title || t("space.firstRewardFallback"),
      }),
      text: t("space.feedback.rewardText", {
        reward: reward.title || t("space.firstRewardFallback"),
        zone: zone?.title || reward.zone_key || t("space.title"),
      }),
    }
    : {
      type: "progress",
      zoneKey,
      rewardKey: "",
      label: t("space.feedback.progressLabel"),
      title: t("space.feedback.progressTitle"),
      text: t("space.feedback.progressText", {
        zone: zone?.title || t("space.title"),
      }),
    };
}

function showRoomFeedback(feedback) {
  if (!feedback?.zoneKey) return;
  recentRoomFeedback.value = feedback;

  if (roomFeedbackTimer) {
    clearTimeout(roomFeedbackTimer);
  }

  roomFeedbackTimer = setTimeout(() => {
    recentRoomFeedback.value = null;
    roomFeedbackTimer = null;
  }, 6500);
}

watch(
  () => props.roomFeedbackEvent,
  async (event) => {
    if (!event?.id || !event?.feedback) return;
    await loadSpace({ silent: true });
    await preloadZonePathChallenges({ force: true });
    if (["path", "challenge", "mission"].includes(shellMode.value)) {
      await ensurePathChallenges(displayActiveZone.value, { force: true });
    }
    showRoomFeedback(event.feedback);
  },
);

function missionStatusRank(mission) {
  const status = String(mission?.status || "").toLowerCase();
  const intensity = String(mission?.mission_intensity || "main").toLowerCase();

  if (intensity === "tiny" && ["remind_later", "skipped", "done", "completed"].includes(status)) return -2;
  if (["remind_later", "skipped"].includes(status)) return -1;
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
  if (typeof window !== "undefined" && window.matchMedia) {
    roomPanMedia = window.matchMedia(ROOM_PAN_QUERY);
    syncRoomPanLayout();
    // Phones start at the room overview (no sheet over the room).
    if (!roomPanLayout.value) roomLevel.value = true;
    roomPanMedia.addEventListener?.("change", syncRoomPanLayout);
  }
  reminderClock = setInterval(() => {
    now.value = Date.now();
  }, 30000);
  await Promise.all([loadSpace(), loadPaths(), loadUserKey()]);
  explainerOpen.value = shouldShowExplainer({ firstRun: firstRunArrival.value, seen: isRoomExplainerSeen(userKey.value) });
  await preloadZonePathChallenges();
  // B11: the first arrival from onboarding (/dashboard?firstRun=1) opens the first mission's zone
  // instead of the room overview. B37 (D78, D83): on desktop too, so the room lands on that corner
  // (its marker and challenge tray carry the explainer's pins).
  if (isFirstRunArrival() && !activeZone.value && (roomPanLayout.value || roomLevel.value)) {
    const zone = suggestedZone.value || workSurfaceZone.value;
    if (zone) selectZone(zone);
  }
});

// B37 (D82): read once on arrival, so Ringo's first card stays until that first step is done.
const firstRunArrival = ref(isFirstRunArrival());

// B37 (D83): "What am I looking at?" under Ringo's first card, with numbered pins in the room.
const explainerOpen = ref(false);

function dismissExplainer() {
  markRoomExplainerSeen(userKey.value);
  explainerOpen.value = false;
}

function isFirstRunArrival() {
  return typeof window !== "undefined" && new URLSearchParams(window.location.search).get("firstRun") === "1";
}

onUnmounted(() => {
  livingSpaceUnmounted = true;
  materializeTimers.forEach((id) => clearTimeout(id));
  materializeTimers = [];
  roomPanMedia?.removeEventListener?.("change", syncRoomPanLayout);
  if (reminderClock) {
    clearInterval(reminderClock);
  }
  if (roomFeedbackTimer) {
    clearTimeout(roomFeedbackTimer);
  }
});

watch(
  () => props.holdRewards,
  (hold) => {
    if (!hold) runMaterializeQueue();
  },
);

watch(
  () => props.materializeEvent,
  async (event) => {
    if (!event?.id || !event?.reward?.key) return;
    enqueueMaterialize([event.reward]);
    await loadSpace({ silent: true });
  },
);

watch(
  () => props.refreshKey,
  async () => {
    await loadSpace({ silent: true });
    await preloadZonePathChallenges({ force: true });
    if (["path", "challenge", "mission"].includes(shellMode.value)) {
      ensurePathChallenges(workSurfaceZone.value, { force: true });
    }
  },
);

watch(
  () => [shellMode.value, workSurfaceZone.value?.zone_key, paths.value.length],
  () => {
    if (shellMode.value === "path") {
      ensurePathChallenges(workSurfaceZone.value);
    }
  },
);

watch(
  () => [workSurfaceZone.value?.zone_key, paths.value.length],
  () => {
    if (workSurfaceZone.value) {
      ensurePathChallenges(workSurfaceZone.value);
    }
  },
);
</script>

<style scoped>
.livingSpace {
  display: grid;
  gap: var(--s-12);
  min-width: 0;
  overflow: visible;
  background:
    radial-gradient(circle at 15% 0%, rgba(110, 229, 255, 0.08), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent);
}

.spaceLayout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--s-12);
  align-items: stretch;
  min-width: 0;
  padding: 12px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 18% 0%, rgba(110, 229, 255, 0.08), transparent 34%),
    radial-gradient(circle at 86% 18%, rgba(247, 215, 116, 0.06), transparent 32%),
    linear-gradient(145deg, rgba(10, 16, 28, 0.94), rgba(5, 9, 16, 0.94));
  border: 1px solid rgba(110, 229, 255, 0.12);
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.30),
    inset 0 0 0 1px rgba(255, 255, 255, 0.025);
}

/*
 * Room + panel layout (B19), desktop >= 1160px: the 380px panel sits at the inline-start side
 * (left in EN, right in FA) and the room fills the rest. Grid areas are logical, so RTL flips the
 * sides; the room art itself is never mirrored (D10). The room scales by whole numbers to fit the
 * column width and the viewport height; when x2 is wider than the column it is clipped and panned.
 */
@media (min-width: 1160px) {
  .spaceLayout.hasPanel {
    grid-template-columns: 380px minmax(0, 1fr);
    grid-template-areas: "panel room";
    padding: 8px;
    gap: 12px;
  }

  /* B27 fix: never taller than the viewport allows (was a fixed 620px, which overflowed the
     page at 1366x768), so the panel never runs past the room column. */
  .spaceLayout.hasPanel .roomStageShell {
    grid-area: room;
    min-height: min(620px, calc(100vh - 190px));
  }

  .spaceLayout.hasPanel .roomSafeZone {
    grid-area: panel;
    min-height: min(620px, calc(100vh - 190px));
  }
}

.roomStageShell {
  display: grid;
  align-content: start;
  gap: 8px;
  min-width: 0;
}

.roomTitleCompact {
  margin: 0;
  padding: 2px 4px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.98rem;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (min-width: 1160px) {
  .roomTitleCompact {
    display: none;
  }
}

.cornerChip {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 3px 9px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.86);
  background: rgba(5, 9, 16, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 0.72rem;
  font-weight: 850;
  white-space: nowrap;
  backdrop-filter: blur(6px);
}

.cornerChip.isNew {
  color: rgba(247, 215, 116, 0.96);
  border-color: rgba(247, 215, 116, 0.3);
}

.roomInfo {
  position: relative;
  display: inline-flex;
}

.roomInfoButton {
  position: relative;
  display: inline-grid;
  place-items: center;
  width: 26px;
  height: 26px;
  padding: 0;
  border-radius: 50%;
  color: rgba(214, 240, 255, 0.92);
  background: rgba(5, 9, 16, 0.72);
  border: 1px solid rgba(110, 229, 255, 0.3);
  font: 900 0.8rem/1 serif;
  font-style: italic;
  cursor: pointer;
  backdrop-filter: blur(6px);
}

/* 44px touch target around the 26px button (inset is from the padding box, inside the 1px border). */
.roomInfoButton::after {
  content: "";
  position: absolute;
  inset: -10px;
}

.roomInfoButton:focus-visible {
  outline: 2px solid rgba(110, 229, 255, 0.8);
  outline-offset: 2px;
}

.roomInfoPopover {
  position: absolute;
  z-index: 5;
  top: calc(100% + 6px);
  inset-inline-end: 0;
  width: max-content;
  max-width: 260px;
  padding: 8px 10px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.88);
  background: rgba(8, 13, 22, 0.96);
  border: 1px solid rgba(110, 229, 255, 0.18);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4);
  font-size: 0.74rem;
  line-height: 1.45;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity 140ms ease;
}

.roomInfo.open .roomInfoPopover,
.roomInfo:hover .roomInfoPopover,
.roomInfo:focus-within .roomInfoPopover {
  opacity: 1;
  visibility: visible;
}

@media (prefers-reduced-motion: reduce) {
  .roomInfoPopover {
    transition: none;
  }
}

.roomStage {
  position: relative;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  grid-auto-rows: minmax(150px, auto);
  gap: 10px;
  min-height: 0;
  padding: 12px;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.02)),
    linear-gradient(145deg, rgba(10, 18, 30, 0.96), rgba(8, 12, 20, 0.95));
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.roomSafeZone {
  display: grid;
  min-width: 0;
  height: min(720px, calc(100vh - 190px));
  min-height: min(620px, calc(100vh - 190px));
  max-height: min(720px, calc(100vh - 190px));
  overflow: hidden;
  scrollbar-width: thin;
}

.roomSafeZone :deep(.zonePanel) {
  min-height: 100%;
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

@media (max-width: 720px) {
  .spaceLayout {
    padding: 10px;
    border-radius: 20px;
  }

  .roomStage {
    grid-template-columns: 1fr;
    grid-auto-rows: auto;
    min-height: 0;
  }

  .roomStage :deep(.spaceZone) {
    grid-column: auto;
    grid-row: auto;
  }

  .roomSafeZone {
    height: auto;
    min-height: 0;
    max-height: none;
    overflow: visible;
  }
}

/* B22 phones: the zone panel (v2 content, unchanged) as a bottom sheet over the lower part of
   the screen and the bottom navigation; the zoomed room stays visible above it. */
@media (max-width: 599px) {
  .roomSafeZone.zoneSheet {
    position: fixed;
    z-index: 40;
    inset-inline: 0;
    bottom: 0;
    height: auto;
    min-height: 0;
    /* Below the room (measured when the sheet opens), never less than 40% of the screen. */
    max-height: max(40dvh, calc(100dvh - var(--sheet-top, 42dvh)));
    overflow-x: hidden;
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 6px 8px calc(8px + env(safe-area-inset-bottom));
    border-radius: 20px 20px 0 0;
    background: rgba(5, 9, 16, 0.96);
    border-top: 1px solid rgba(110, 229, 255, 0.18);
    box-shadow: 0 -18px 40px rgba(0, 0, 0, 0.45);
    animation: sheetIn 300ms ease;
  }

  .roomSafeZone.zoneSheet:focus {
    outline: none;
  }

  /* B27: with a flow open the sheet has a fixed height and the flow scrolls inside it, so the
     save area stays visible at the bottom. */
  .roomSafeZone.zoneSheet:has(.missionFlow) {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    height: max(40dvh, calc(100dvh - var(--sheet-top, 42dvh)));
    overflow: hidden;
  }

  /* B31: the focus timer card (with Pause and music) stays whole above Done; the sheet may cover
     more of the room while the timer runs. */
  .roomSafeZone.zoneSheet:has(.flowTimer) {
    height: max(40dvh, calc(100dvh - var(--sheet-top, 42dvh)), min(520px, 88dvh));
    max-height: max(40dvh, calc(100dvh - var(--sheet-top, 42dvh)), min(520px, 88dvh));
  }

  .roomSafeZone.zoneSheet:has(.missionFlow) :deep(.zonePanel) {
    height: 100%;
    min-height: 0;
  }

  /* 44px touch targets for every control in the sheet (panel content unchanged). */
  .roomSafeZone.zoneSheet :deep(button),
  .roomSafeZone.zoneSheet :deep(a) {
    min-width: 44px;
    min-height: 44px;
  }

  .roomSafeZone.zoneSheet::before {
    content: "";
    display: block;
    justify-self: center;
    width: 40px;
    height: 4px;
    margin: 2px auto 6px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.24);
  }
}

@keyframes sheetIn {
  from {
    transform: translateY(40%);
    opacity: 0;
  }
}

@media (max-width: 599px) and (prefers-reduced-motion: reduce) {
  .roomSafeZone.zoneSheet {
    animation: none;
  }
}

/* B37 Fix A: short phones (under 800 px tall) get a tighter sheet top, so Ringo's "Do it now" is
   fully in view at 360x740. Taller phones are unchanged. */
@media (max-width: 599px) and (max-height: 799px) {
  .roomSafeZone.zoneSheet {
    padding-top: 2px;
  }

  .roomSafeZone.zoneSheet::before {
    margin: 2px auto 2px;
  }
}
</style>
