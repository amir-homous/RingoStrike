<template>
  <AppContainer>
    <AppHeader />

    <div class="dashboardStack" :class="{ dashboardRevealActive }">
      <UiState :loading="loading" :error="!!error" :empty="false" :loading-title="t('dashboard.loadingTitle')"
        :loading-text="t('dashboard.loadingText')" :error-title="t('dashboard.errorTitle')"
        :error-text="error || t('common.pleaseTryAgain')" @retry="loadDashboard" />

      <template v-if="!loading && !error">
        <BaseCard v-if="showOnboardingFallback" class="onboardingFallbackCard">
          <div>
            <p class="sectionKicker">{{ t("dashboard.onboardingFallback.eyebrow") }}</p>
            <h2 class="panelTitle">{{ t("dashboard.onboardingFallback.title") }}</h2>
            <p class="panelText">
              {{ t("dashboard.onboardingFallback.text") }}
            </p>
          </div>

          <RouterLink class="primaryLink" to="/onboarding">
            <span>{{ t("dashboard.onboardingFallback.cta") }}</span>
            <span aria-hidden="true">→</span>
          </RouterLink>
        </BaseCard>

        <template v-else>
          <!-- <BaseCard v-if="showFirstRunFocus" class="firstRunFocusCard">
            <div>
              <p class="sectionKicker">{{ t("dashboard.firstRunFocus.eyebrow") }}</p>
              <h2 class="panelTitle">{{ t("dashboard.firstRunFocus.title") }}</h2>
              <p class="panelText">
                {{ t("dashboard.firstRunFocus.text") }}
              </p>

              <div class="firstRunChoices" aria-label="First mission choices">
                <span>{{ t("dashboard.firstRunFocus.done") }}</span>
                <span>{{ t("dashboard.firstRunFocus.smaller") }}</span>
                <span>{{ t("dashboard.firstRunFocus.remind") }}</span>
                <span>{{ t("dashboard.firstRunFocus.skip") }}</span>
              </div>
            </div>

            <button type="button" class="dismissFocusButton" @click="dismissFirstRunFocus">
              {{ t("dashboard.firstRunFocus.dismiss") }}
            </button>
          </BaseCard> -->

          <MissionCenter :key="missionCenterKey" class="missionCenterDataProvider" aria-hidden="true"
            :stats="stats" :first-run-focus="showFirstRunFocus"
            :focus-mode-active="showMissionFocusMode" @checked-in="handleMissionCheckin"
            @loaded="handleMissionCenterLoaded" @first-run-complete="dismissFirstRunFocus"
            @focus-state-change="handleMissionFocusState" @show-dashboard="showDashboardFromFocus" />

          <LivingSpace
            v-if="showLivingSpaceHome"
            class="dashboardRevealItem livingSpaceHomeShell"
            :refresh-key="spaceRefreshKey"
            :challenges="livingSpaceChallenges"
            :missions="livingSpaceMissions"
            :today-safe="livingSpaceTodaySafe"
            :focus-reason="livingSpaceFocusReason"
            :reminder-count="livingSpaceReminderCount"
            :checking-id="checkingId"
            :room-feedback-event="livingSpaceRoomFeedbackEvent"
            :hold-rewards="livingSpaceHoldRewards"
            :materialize-event="livingSpaceMaterializeEvent"
            :telegram-settings="missionCenterStatus.telegram"
            @checkin="checkin"
            @challenge-started="handleLivingSpaceChallengeStarted"
            @mission-completed="handleLivingSpaceMissionCompleted"
          />

        </template>
      </template>
    </div>

    <RewardFeedback :items="rewardToasts" />

    <RewardUnlockMoment
      :open="!!spaceRewardMoment"
      :reward="spaceRewardMoment"
      @close="handleSpaceRewardClose"
    />

    <RingoRewardSequence
      :steps="livingSpaceRewardSequenceSteps"
      :sprite="livingSpaceRewardSequenceSprite"
      @action="handleLivingSpaceRewardSequenceAction"
      @finish="finishLivingSpaceRewardSequence"
    />
  </AppContainer>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import MissionCenter from "@/components/missions/MissionCenter.vue";
import LivingSpace from "@/components/space/LivingSpace.vue";
import RewardFeedback from "@/components/feedback/RewardFeedback.vue";
import RewardUnlockMoment from "@/components/space/RewardUnlockMoment.vue";
import RingoRewardSequence from "@/components/ringo/RingoRewardSequence.vue";
import {
  buildMissionCompletionRewardSteps,
  buildRewardDelta,
  buildRewardSnapshot,
} from "@/utils/rewardSequenceBuilder";
import { loadDashboardData } from "./dashboardFlow";
import { composeMomentSteps, lastSevenDays, missionsDoneToday, momentRewards, utcTodayIso } from "@/lib/dayMoment";
import { numberAwareT } from "@/lib/i18nNumbers";

import {
  submitCheckinFlow,
} from "./challengeFlow";
import {
  getOnboardingUserKey,
  hasOnboardingDecision,
} from "@/lib/guidedExperience";

const props = defineProps({
  firstRunFocus: { type: Boolean, default: false },
});

const route = useRoute();
const router = useRouter();
const { locale, t } = useI18n();

const loading = ref(true);
const checkingId = ref(null);
const showFirstRunFocus = ref(route.query.firstRun === "1");
const error = ref("");
const user = ref(null);
const date = ref("");
const challenges = ref([]);
const stats = ref(null);
const rewardToasts = ref([]);
const spaceRewardMoment = ref(null);
const xpPulse = ref(false);
const activityEvents = ref([]);
const achievements = ref([]);
const missionFocusDismissed = ref(false);
const dashboardRevealActive = ref(false);
const missionFocusState = ref({
  active: true,
  reason: "loading",
  todaySafe: false,
  hasActionableSuggestion: false,
  reminderCount: 0,
});
const missionCenterStatus = ref({
  loaded: false,
  state: "",
  missions: [],
  error: "",
  telegram: null,
});
const missionCenterKey = ref(0);
const spaceRefreshKey = ref(0);
// B21: newly unlocked objects stay ghosts while the Ringo Moment or the reward card is open,
// then materialize in the room after the card closes.
const livingSpaceMaterializeEvent = ref(null);
const livingSpaceRewardSequenceSteps = ref([]);
const livingSpaceRewardSequenceSprite = ref("celebration");
const pendingLivingSpaceRoomFeedback = ref(null);
const pendingLivingSpaceRewardMoment = ref(null);
const livingSpaceRoomFeedbackEvent = ref(null);
const livingSpaceHoldRewards = computed(() => Boolean(
  livingSpaceRewardSequenceSteps.value.length
  || spaceRewardMoment.value
  || pendingLivingSpaceRewardMoment.value,
));
const livingSpaceFrozenState = ref(null);
const showOnboardingFallback = computed(() => {
  if (typeof window === "undefined") return false;

  const userKey = getOnboardingUserKey(user.value);

  if (!userKey) return false;

  return !hasOnboardingDecision(userKey);
});

const livingSpaceChallenges = computed(() => {
  return livingSpaceFrozenState.value?.challenges || challenges.value;
});

const livingSpaceMissions = computed(() => {
  return livingSpaceFrozenState.value?.missions || missionCenterStatus.value.missions;
});

const livingSpaceTodaySafe = computed(() => {
  return livingSpaceFrozenState.value
    ? Boolean(livingSpaceFrozenState.value.todaySafe)
    : Boolean(missionFocusState.value.todaySafe);
});

const livingSpaceFocusReason = computed(() => {
  return livingSpaceFrozenState.value?.focusReason || missionFocusState.value.reason;
});

const livingSpaceReminderCount = computed(() => {
  return livingSpaceFrozenState.value
    ? Number(livingSpaceFrozenState.value.reminderCount || 0)
    : Number(missionFocusState.value.reminderCount || 0);
});

const showMissionFocusMode = computed(() => {
  return Boolean(
    !missionFocusDismissed.value &&
    (showFirstRunFocus.value || missionFocusState.value.active),
  );
});

const showLivingSpaceHome = computed(() => !showOnboardingFallback.value);
function pushToast(text, type = "success") {
  const id = `${Date.now()}-${Math.random()}`;
  rewardToasts.value.push({ id, text, type });

  setTimeout(() => {
    rewardToasts.value = rewardToasts.value.filter((t) => t.id !== id);
  }, 1800);
}

function dismissFirstRunFocus() {
  showFirstRunFocus.value = false;

  const { firstRun, ...restQuery } = route.query;

  router.replace({
    path: "/dashboard",
    query: restQuery,
  });
}

function showDashboardFromFocus() {
  missionFocusDismissed.value = true;
  dashboardRevealActive.value = true;

  if (showFirstRunFocus.value) {
    dismissFirstRunFocus();
  }
}

async function loadDashboard(options = {}) {
  const silent = Boolean(options?.silent);

  error.value = "";

  if (!silent) {
    loading.value = true;
  }

  try {
    const data = await loadDashboardData(api, new Date().toLocaleDateString());

    user.value = data.user;
    stats.value = data.stats;
    challenges.value = data.challenges;
    date.value = data.date;
    activityEvents.value = data.activityEvents;
    achievements.value = data.achievements;
  } catch (e) {
    console.error(e);
    if (!silent) {
      error.value = e?.response?.data?.error || e?.message || String(e);
    }
  } finally {
    if (!silent) {
      loading.value = false;
    }
  }
}


async function checkin(enrollmentId) {
  checkingId.value = enrollmentId;

  try {
    const state = {
      challenges: challenges.value,
      stats: stats.value,
      activityEvents: activityEvents.value,
      achievements: achievements.value,
      error: error.value,
    };

    const syncState = (nextState) => {
      challenges.value = nextState.challenges;
      stats.value = nextState.stats;
      activityEvents.value = nextState.activityEvents;
      achievements.value = nextState.achievements;
      error.value = nextState.error || "";
    };

    const result = await submitCheckinFlow({
      apiClient: api,
      state,
      enrollmentId,
      onStateChange: syncState,
      setPulse: (value) => {
        xpPulse.value = value;
      },
    });

    if (result.skipped || result.error) return;
    missionCenterKey.value += 1;
    spaceRefreshKey.value += 1;

    if (result.livingSpaceReward) {
      spaceRewardMoment.value = result.livingSpaceReward;
    }

    for (const a of result.unlocked) {
      pushToast(`🏆 ${a.title}`, "achievement");
    }

    const oldPoints = Number(result.oldStats?.total_points ?? result.oldStats?.xp);
    const newPoints = Number(stats.value?.total_points ?? stats.value?.xp);
    const xpEarned = Number.isFinite(oldPoints) && Number.isFinite(newPoints)
      ? Math.max(0, newPoints - oldPoints)
      : 0;

    if (xpEarned > 0) {
      pushToast(`+${xpEarned} XP`, "success");
      pushToast(`🔥 ${t("dashboard.streakMaintained")}`, "success");
    }

    if (result.oldStats && stats.value.level > result.oldStats.level) {
      pushToast(`Level Up → Level ${stats.value.level}`, "level");
    }
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    checkingId.value = null;
  }
}

async function handleMissionCheckin(payload = {}) {
  await loadDashboard({ silent: true });

  if (payload?.living_space_reward) {
    spaceRewardMoment.value = payload.living_space_reward;
    spaceRefreshKey.value += 1;
  }
}

async function handleSpaceRewardClose(reward) {
  // B21: the room materializes this reward once the card is gone (announced before the hold ends).
  if (reward?.key) {
    livingSpaceMaterializeEvent.value = { id: `${Date.now()}-${reward.key}`, reward };
  }
  spaceRewardMoment.value = null;

  if (reward?.id) {
    try {
      await api.post(`/me/space/rewards/${reward.id}/seen`);
      if (!pendingLivingSpaceRoomFeedback.value) {
        spaceRefreshKey.value += 1;
      }
    } catch (e) {
      console.warn("Could not mark space reward seen", e);
    }
  }

  flushPendingLivingSpaceRoomFeedback();
}

async function handleLivingSpaceChallengeStarted() {
  await loadDashboard({ silent: true });
  missionCenterKey.value += 1;
  spaceRefreshKey.value += 1;
}

async function handleLivingSpaceMissionCompleted(payload = {}) {
  const action = payload?.living_space_action || "done";

  if (action !== "done") {
    livingSpaceRewardSequenceSteps.value = [];
    pendingLivingSpaceRewardMoment.value = null;
    pendingLivingSpaceRoomFeedback.value = null;
    livingSpaceFrozenState.value = null;
    await loadDashboard({ silent: true });
    missionCenterKey.value += 1;
    spaceRefreshKey.value += 1;
    return;
  }

  const oldStats = stats.value ? { ...stats.value } : null;
  const wasTodaySafe = Boolean(missionFocusState.value.todaySafe);
  livingSpaceFrozenState.value = {
    challenges: challenges.value,
    missions: missionCenterStatus.value.missions,
    todaySafe: missionFocusState.value.todaySafe,
    focusReason: missionFocusState.value.reason,
    reminderCount: missionFocusState.value.reminderCount,
  };
  const beforeSnapshot = buildLivingSpaceRewardSnapshot({
    stats: oldStats,
    mission: payload?.mission,
    todaySafe: wasTodaySafe,
    completionResult: null,
  });

  await loadDashboard({ silent: true });

  pendingLivingSpaceRewardMoment.value = payload?.living_space_reward || null;
  pendingLivingSpaceRoomFeedback.value = payload?.living_space_room_feedback || null;

  const backendSavedToday = Array.isArray(payload?.reward_sequence)
    && payload.reward_sequence.some((step) => step?.type === "today_saved");
  const afterSnapshot = buildLivingSpaceRewardSnapshot({
    stats: stats.value,
    mission: payload?.mission,
    todaySafe: wasTodaySafe || backendSavedToday || Boolean(missionFocusState.value.todaySafe),
    completionResult: payload,
  });
  const rewardDelta = buildRewardDelta(beforeSnapshot, afterSnapshot, payload);
  const rewardResult = buildMissionCompletionRewardSteps(rewardDelta, payload, { t, locale: locale.value });
  // B37 (D72 to D74): the first counted Main or Tiny of the day gets the day moment.
  const firstOfDay = Boolean(rewardDelta?.strike?.changed);
  const day = firstOfDay ? await loadDayMomentData() : null;

  // The reward message ladder: Main and Tiny missions done today, from the list before this
  // completion plus the one just finished.
  const doneToday = missionsDoneToday(livingSpaceFrozenState.value?.missions || [], {
    mission_id: payload?.mission?.mission_id,
    mission_intensity: rewardDelta?.mission?.intensity || "main",
  });

  livingSpaceRewardSequenceSteps.value = composeMomentSteps(rewardResult.steps, {
    intensity: rewardDelta?.mission?.intensity || "main",
    firstOfDay,
    day,
    doneToday,
    // Achievements from the done response; the XP chip adds their XP so it matches the total.
    xpAwarded: rewardDelta?.xp?.awarded ?? null,
    ...momentRewards(payload),
  }, numberAwareT(t, () => locale.value));
  livingSpaceRewardSequenceSprite.value = rewardDelta?.mission?.intensity === "bonus"
    ? "happy"
    : "celebration";

  if (!rewardResult.steps.length) {
    continueLivingSpaceCompletionFeedback();
  }
}

// B37 (D73, D74): the day moment's numbers, read fresh after the check-in. A failed request only
// drops its part (the count and chip from /me/stats, the bar from /me/consistency); nothing is
// invented.
async function loadDayMomentData() {
  const [statsResult, consistencyResult] = await Promise.allSettled([
    api.get("/me/stats"),
    api.get("/me/consistency"),
  ]);
  const fresh = statsResult.status === "fulfilled" ? statsResult.value?.data?.stats || null : null;
  const days = consistencyResult.status === "fulfilled" ? consistencyResult.value?.data?.days : null;
  return {
    streak: fresh?.current_streak ?? null,
    totalDays: fresh?.total_days ?? null,
    week: lastSevenDays(utcTodayIso(), days),
  };
}

function buildLivingSpaceRewardSnapshot({
  stats: snapshotStats = null,
  mission = null,
  todaySafe = false,
  completionResult = null,
} = {}) {
  return buildRewardSnapshot({
    missions: missionCenterStatus.value.missions || [],
    pathGroups: [],
    stats: snapshotStats,
    guidanceProgress: {
      today_saved: Boolean(todaySafe),
      current_streak: snapshotStats?.current_streak ?? null,
    },
    mission,
    completionResult,
    fallbacks: {
      path: t("missions.fallbackPath"),
      challenge: t("missions.fallbackChallenge"),
    },
  });
}

function finishLivingSpaceRewardSequence() {
  livingSpaceRewardSequenceSteps.value = [];
  continueLivingSpaceCompletionFeedback();
}

function handleLivingSpaceRewardSequenceAction(action) {
  finishLivingSpaceRewardSequence();

  if (action?.key === "view_choices") {
    dashboardRevealActive.value = true;
  }
}

function continueLivingSpaceCompletionFeedback() {
  if (pendingLivingSpaceRewardMoment.value) {
    spaceRewardMoment.value = pendingLivingSpaceRewardMoment.value;
    pendingLivingSpaceRewardMoment.value = null;
    return;
  }

  flushPendingLivingSpaceRoomFeedback();
}

function flushPendingLivingSpaceRoomFeedback() {
  const feedback = pendingLivingSpaceRoomFeedback.value;
  pendingLivingSpaceRoomFeedback.value = null;
  livingSpaceFrozenState.value = null;
  missionCenterKey.value += 1;
  spaceRefreshKey.value += 1;

  if (!feedback) return;

  livingSpaceRoomFeedbackEvent.value = {
    id: `${Date.now()}-${Math.random()}`,
    feedback,
  };
}



function handleMissionCenterLoaded(payload) {
  missionCenterStatus.value = {
    loaded: true,
    state: payload?.state || "",
    missions: payload?.missions || [],
    error: payload?.error || "",
    telegram: payload?.telegram || null,
  };
}

function handleMissionFocusState(payload) {
  missionFocusState.value = {
    active: Boolean(payload?.active),
    reason: payload?.reason || "",
    todaySafe: Boolean(payload?.todaySafe),
    hasActionableSuggestion: Boolean(payload?.hasActionableSuggestion),
    reminderCount: Number(payload?.reminderCount || 0),
  };

  if (missionFocusState.value.active && !missionFocusDismissed.value) {
    dashboardRevealActive.value = false;
  }
}

onMounted(loadDashboard);
</script>

<style scoped>
.dashboardStack {
  display: grid;
  gap: var(--s-12);
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow-x: visible;
}

.missionCenterDataProvider {
  display: none;
}

.scrollAnchor {
  scroll-margin-top: 110px;
}

.missionFocusProgress {
  position: sticky;
  top: calc(78px + env(safe-area-inset-top));
  z-index: 26;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  min-width: 0;
  max-width: 100%;
  padding: 6px 0 8px;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(6, 11, 20, 0.72), rgba(6, 11, 20, 0.38));
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.16);
  backdrop-filter: blur(14px);
}

.dashboardRevealActive .dashboardRevealItem {
  opacity: 0;
  transform: translateY(10px);
  animation: dashboardReveal 420ms cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.livingSpaceHomeShell {
  width: min(1680px, calc(100vw - 40px));
  max-width: none;
  justify-self: center;
}

@media (min-width: 1400px) {
  .livingSpaceHomeShell {
    width: calc(100vw - 64px);
  }
}

.dashboardRevealActive .dashboardRevealItem:nth-of-type(2) {
  animation-delay: 70ms;
}

.dashboardRevealActive .dashboardRevealItem:nth-of-type(3) {
  animation-delay: 140ms;
}

.dashboardRevealActive .dashboardRevealItem:nth-of-type(n + 4) {
  animation-delay: 210ms;
}

@keyframes dashboardReveal {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dashboardHead {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: end;
  padding: 24px;
  border-radius: 28px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.11), transparent 38%),
    radial-gradient(circle at 92% 10%, rgba(195, 90, 214, 0.10), transparent 35%),
    rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.20);
}

.dashboardHead::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.supportHead {
  padding: 18px 20px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.07), transparent 34%),
    rgba(255, 255, 255, 0.022);
  box-shadow: none;
}

.headCopy,
.headActions {
  position: relative;
  z-index: 1;
}

.eyebrow,
.sectionKicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.pulseDot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #4ade80;
  box-shadow: 0 0 16px rgba(74, 222, 128, 0.7);
}

.pageTitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.97);
  font-size: clamp(2rem, 4vw, 4rem);
  line-height: 0.98;
  letter-spacing: -0.065em;
}

.supportHead .pageTitle {
  font-size: clamp(1.55rem, 3vw, 2.65rem);
  letter-spacing: -0.045em;
}

.pageSubtitle {
  margin: 14px 0 0;
  max-width: 700px;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.7;
}

.headMeta {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin-top: 17px;
}

.metaPill {
  display: inline-flex;
  align-items: center;
  min-height: 31px;
  padding: 7px 11px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.78rem;
  font-weight: 750;
}

.headActions,
.panelActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-12);
  align-items: center;
  justify-content: flex-end;
}

.primaryLink,
.ghostLink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--s-8);
  min-height: 40px;
  padding: 10px 15px;
  border-radius: 15px;
  text-decoration: none;
  font-weight: 850;
  white-space: nowrap;
}

.primaryLink {
  color: rgba(255, 255, 255, 0.94);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.17), rgba(195, 90, 214, 0.12)),
    rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(110, 229, 255, 0.22);
}

.ghostLink {
  color: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(255, 255, 255, 0.035);
}

.primaryLink:hover,
.ghostLink:hover {
  background: rgba(255, 255, 255, 0.065);
  border-color: rgba(110, 229, 255, 0.25);
}

.panelTitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  letter-spacing: -0.04em;
}

.panelText {
  margin: 8px 0 0;
  max-width: 720px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.65;
}

.progressGrid {
  display: grid;
  gap: var(--s-12);
  grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
}

.sideCol {
  display: grid;
  gap: var(--s-12);
  align-content: start;
}

.challengePanel {
  background:
    radial-gradient(circle at 0% 0%, rgba(195, 90, 214, 0.055), transparent 32%),
    rgba(255, 255, 255, 0.025);
}

.guidedFeatureCard,
.guidedLockCard {
  display: flex;
  justify-content: space-between;
  gap: var(--s-16);
  align-items: center;
}

.guidedFeatureCard {
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.075), transparent 34%),
    rgba(255, 255, 255, 0.026);
}

.onboardingFallbackCard {
  display: flex;
  justify-content: space-between;
  gap: var(--s-16);
  align-items: center;
  padding: 22px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.10), transparent 34%),
    rgba(255, 255, 255, 0.035);
}

.guidedLockCard {
  justify-content: flex-start;
  padding: 16px;
  border-radius: 22px;
  color: rgba(255, 255, 255, 0.70);
  background: rgba(255, 255, 255, 0.026);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.guidedLockCard strong {
  display: block;
  color: rgba(255, 255, 255, 0.84);
}

.guidedLockCard p {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.56);
}

.lockDot {
  width: 12px;
  height: 12px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: rgba(110, 229, 255, 0.70);
  box-shadow: 0 0 20px rgba(110, 229, 255, 0.30);
}

.panelHead {
  display: flex;
  justify-content: space-between;
  gap: var(--s-16);
  align-items: flex-start;
  flex-wrap: wrap;
}

.panelTitle {
  font-size: 1.35rem;
}

.miniSummary {
  min-width: 82px;
  min-height: 48px;
  display: grid;
  place-items: center;
  padding: 8px 12px;
  border-radius: 16px;
  background: rgba(74, 222, 128, 0.09);
  border: 1px solid rgba(74, 222, 128, 0.16);
}

.miniSummary span {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 950;
}

.miniSummary small {
  color: rgba(255, 255, 255, 0.56);
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.list {
  margin-top: var(--s-16);
  display: grid;
  gap: var(--s-12);
}

.showMoreButton {
  justify-self: center;
  display: inline-flex;
  align-items: center;
  gap: var(--s-8);
  min-height: 40px;
  padding: 10px 15px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-weight: 850;
}

.showMoreButton:hover {
  background: rgba(255, 255, 255, 0.065);
  border-color: rgba(110, 229, 255, 0.25);
}



.dismissFocusButton:hover {
  border-color: rgba(110, 229, 255, 0.26);
  background: rgba(110, 229, 255, 0.08);
}


@media (max-width: 980px) {

  .dashboardHead,
  .missionFocusProgress,
  .progressGrid {
    grid-template-columns: 1fr;
  }

  .headActions,
  .panelActions {
    justify-content: flex-start;
  }

  .guidedFeatureCard,
  .guidedLockCard,
  .onboardingFallbackCard {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 620px) {
  .dashboardHead {
    padding: 18px;
    border-radius: 23px;
  }

  .headActions,
  .panelActions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .primaryLink,
  .ghostLink,
  .missionFocusProgress :deep(.btn) {
    width: 100%;
    white-space: normal;
    text-align: center;
  }



}

@media (prefers-reduced-motion: reduce) {
  .dashboardRevealActive .dashboardRevealItem {
    opacity: 1;
    transform: none;
    animation: none;
  }
}
</style>
