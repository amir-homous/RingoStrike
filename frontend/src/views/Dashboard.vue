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

          <div v-if="showMissionFocusMode && stats" class="missionFocusProgress">
            <CompactProgressStrip :stats="stats" :today-safe="missionFocusState.todaySafe"
              :reminder-count="missionFocusState.reminderCount" />

            <!-- <BaseButton variant="secondary" @click="showDashboardFromFocus">
              {{ t("dashboard.showDashboard") }}
            </BaseButton> -->
          </div>

          <MissionCenter :key="missionCenterKey" :stats="stats" :first-run-focus="showFirstRunFocus"
            :focus-mode-active="showMissionFocusMode" @checked-in="handleMissionCheckin"
            @loaded="handleMissionCenterLoaded" @first-run-complete="dismissFirstRunFocus"
            @focus-state-change="handleMissionFocusState" @show-dashboard="showDashboardFromFocus" />

          <!-- Legacy Today Mission is now a fallback when Mission Center has no actionable mission. -->
          <div v-if="showFullDashboard && showLegacyTodayMission" id="today-mission"
            class="scrollAnchor dashboardRevealItem">
            <TodayMission :challenges="challenges" :stats="stats" :loading="checkingId === missionEnrollmentId"
              @checkin="checkin" />
          </div>

          <PostCheckinNextAction v-if="showFullDashboard && showPostCheckinAction" class="dashboardRevealItem"
            :enrollment-id="missionEnrollmentId" :all-done="allActiveMissionsDone" />

          <!-- 2. First progress layer: appears after the user has meaningful progress -->
          <HeroProgressCard v-if="showFullDashboard && stats && guidedState.hasProgress" class="dashboardRevealItem"
            :user-name="user?.name" :stats="stats" :animate-pulse="xpPulse" />

          <!-- 3. Progress details: XP, stats, next goal, recent progress -->
          <div v-if="showFullDashboard && stats && guidedState.hasProgress" class="progressGrid dashboardRevealItem">
            <StatsGrid :stats="stats" />

            <div class="sideCol">
              <NextGoalCard :stats="stats" />
              <RecentProgressFeed :stats="stats" />
            </div>
          </div>

          <!-- 4. Active paths: secondary daily management surface -->
          <BaseCard v-if="showFullDashboard && challenges.length" class="challengePanel dashboardRevealItem">
            <div class="panelHead">
              <div>
                <p class="sectionKicker">{{ t("dashboard.activePaths") }}</p>
                <h2 class="panelTitle">{{ t("dashboard.todaysChallenges") }}</h2>
                <p class="panelText">
                  {{ t("dashboard.panelText") }}
                </p>
              </div>

              <div class="panelActions">
                <div v-if="challenges.length" class="miniSummary">
                  <span>{{ completedTodayCount }}/{{ challenges.length }}</span>
                  <small>{{ t("dashboard.secured") }}</small>
                </div>

                <RouterLink class="ghostLink" to="/challenges">
                  {{ t("dashboard.addPath") }}
                </RouterLink>
              </div>
            </div>

            <div class="list">
              <ChallengeCard v-for="c in visibleChallenges" :key="c.enrollment_id" :challenge="c"
                :loading="checkingId === c.enrollment_id" compact @checkin="checkin" />

              <button v-if="hasHiddenChallenges" type="button" class="showMoreButton"
                @click="showAllChallenges = !showAllChallenges">
                <span>
                  {{ showAllChallenges ? t("common.showFewer") : t("common.showMore", {
                    count: orderedChallenges.length -
                      challengeLimit
                  }) }}
                </span>
                <span aria-hidden="true">{{ showAllChallenges ? "↑" : "↓" }}</span>
              </button>
            </div>
          </BaseCard>

          <!-- 5. Next unlock hint: helps the user understand what comes next -->
          <BaseCard v-if="showFullDashboard && guidedState.hasProgress && nextLockedFeature"
            class="guidedLockCard dashboardRevealItem">
            <span class="lockDot" aria-hidden="true"></span>

            <div>
              <strong>{{ t("guidedFeatures.nextTitle", { feature: lockedFeatureLabel }) }}</strong>
              <p>{{ t("guidedFeatures.unlockAfter", { count: nextLockedFeature.threshold }) }}</p>
            </div>
          </BaseCard>

          <!-- 6. Activity: unlocked after early progress -->
          <div v-if="showFullDashboard && guidedState.features.activity.unlocked" id="activity-feed"
            class="scrollAnchor dashboardRevealItem">
            <ActivityTimeline :events="activityEvents" :loading="loading" />
          </div>

          <!-- 7. Achievements: after activity has enough meaning -->
          <AchievementPreview v-if="showFullDashboard && guidedState.features.achievements.unlocked"
            class="dashboardRevealItem" :achievements="achievements" />

          <!-- 8. Leaderboard: lower priority because it is enrollment-scoped for now -->
          <BaseCard v-if="showFullDashboard && showLeaderboardPreview" id="leaderboard"
            class="guidedFeatureCard dashboardRevealItem">
            <div>
              <p class="sectionKicker">{{ t("guidedFeatures.leaderboard.kicker") }}</p>
              <h2 class="panelTitle">{{ t("guidedFeatures.leaderboard.title") }}</h2>
              <p class="panelText">
                {{ t("guidedFeatures.leaderboard.text") }}
              </p>
            </div>

            <RouterLink class="ghostLink" :to="leaderboardTarget">
              {{ t("guidedFeatures.leaderboard.cta") }}
            </RouterLink>
          </BaseCard>

          <!-- 9. Support / account context: useful, but not the main daily action -->
          <section v-if="showFullDashboard" class="dashboardHead supportHead dashboardRevealItem">
            <div class="headCopy">
              <div class="eyebrow">
                <span class="pulseDot"></span>
                <span>{{ t("dashboard.eyebrow") }}</span>
              </div>

              <h1 class="pageTitle">
                {{ user ? t("dashboard.welcomeName", { name: firstName }) : t("dashboard.welcome") }}
              </h1>

              <p class="pageSubtitle">
                {{ t("dashboard.subtitle") }}
              </p>

              <div class="headMeta">
                <span v-if="date" class="metaPill">
                  {{ date }}
                </span>

                <span v-if="stats" class="metaPill">
                  {{ t("common.level", { level: stats.level || 1 }) }}
                </span>

                <span v-if="stats" class="metaPill">
                  {{ t("common.xp", { count: stats.total_points || 0 }) }}
                </span>
              </div>
            </div>

            <div class="headActions">
              <RouterLink class="primaryLink" to="/challenges">
                <span>{{ t("dashboard.browse") }}</span>
                <span aria-hidden="true">→</span>
              </RouterLink>

              <BaseButton variant="secondary" :loading="loggingOut" @click="doLogout">
                {{ t("dashboard.logout") }}
              </BaseButton>
            </div>
          </section>
        </template>
      </template>
    </div>

    <RewardFeedback :items="rewardToasts" />

    <RewardMoment :open="!!rewardMoment" :reward="rewardMoment" @close="rewardMoment = null" />
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
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";
import MissionCenter from "@/components/missions/MissionCenter.vue";
import TodayMission from "@/components/dashboard/TodayMission.vue";
import PostCheckinNextAction from "@/components/guided/PostCheckinNextAction.vue";
import CompactProgressStrip from "@/components/progress/CompactProgressStrip.vue";
import HeroProgressCard from "@/components/progress/HeroProgressCard.vue";
import StatsGrid from "@/components/progress/StatsGrid.vue";
import NextGoalCard from "@/components/progress/NextGoalCard.vue";
import RecentProgressFeed from "@/components/progress/RecentProgressFeed.vue";
import ChallengeCard from "@/components/challenges/ChallengeCard.vue";
import RewardFeedback from "@/components/feedback/RewardFeedback.vue";
import RewardMoment from "@/components/feedback/RewardMoment.vue";
import ActivityTimeline from "@/components/activity/ActivityTimeline.vue";
import AchievementPreview from "@/components/achievements/AchievementPreview.vue";
import {
  DASHBOARD_CHALLENGE_LIMIT,
  getVisibleDashboardChallenges,
  loadDashboardData,
  orderDashboardChallenges,
} from "./dashboardFlow";
import {
  submitCheckinFlow,
} from "./challengeFlow";
import {
  getGuidedFeatureState,
  getNewlyUnlockedGuidedFeatures,
  getOnboardingUserKey,
  hasOnboardingDecision,
} from "@/lib/guidedExperience";

const props = defineProps({
  firstRunFocus: { type: Boolean, default: false },
});

const route = useRoute();
const router = useRouter();
const { t } = useI18n();

const loading = ref(true);
const loggingOut = ref(false);
const checkingId = ref(null);
const showFirstRunFocus = ref(route.query.firstRun === "1");
const error = ref("");
const user = ref(null);
const date = ref("");
const challenges = ref([]);
const stats = ref(null);
const rewardToasts = ref([]);
const rewardMoment = ref(null);
const xpPulse = ref(false);
const activityEvents = ref([]);
const achievements = ref([]);
const showAllChallenges = ref(false);
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
});
const missionCenterKey = ref(0);
const showOnboardingFallback = computed(() => {
  if (typeof window === "undefined") return false;

  const userKey = getOnboardingUserKey(user.value);

  if (!userKey) return false;

  return !hasOnboardingDecision(userKey);
});

const challengeLimit = DASHBOARD_CHALLENGE_LIMIT;

const firstName = computed(() => {
  return String(user.value?.name || "there").trim().split(" ")[0];
});

const completedTodayCount = computed(() => {
  return challenges.value.filter((challenge) => Boolean(challenge.today_checked)).length;
});

const activeChallenges = computed(() => {
  return challenges.value.filter((challenge) => {
    const status = String(challenge?.status || "active").toLowerCase();
    return status === "active" && challenge?.enrollment_id;
  });
});

const activeCompletedTodayCount = computed(() => {
  return activeChallenges.value.filter((challenge) => Boolean(challenge.today_checked)).length;
});

const allActiveMissionsDone = computed(() => {
  return activeChallenges.value.length > 0 &&
    activeCompletedTodayCount.value === activeChallenges.value.length;
});

const showPostCheckinAction = computed(() => {
  return allActiveMissionsDone.value && showLegacyTodayMission.value;
});

const showLegacyTodayMission = computed(() => {
  if (!missionCenterStatus.value.loaded) return false;

  return ["error", "no_mission_today"].includes(missionCenterStatus.value.state);
});

const showMissionFocusMode = computed(() => {
  return Boolean(
    !missionFocusDismissed.value &&
    (showFirstRunFocus.value || missionFocusState.value.active),
  );
});

const showFullDashboard = computed(() => !showMissionFocusMode.value);

const orderedChallenges = computed(() => {
  return orderDashboardChallenges(challenges.value);
});

const visibleChallenges = computed(() => {
  return getVisibleDashboardChallenges(
    challenges.value,
    showAllChallenges.value,
    challengeLimit,
  );
});

const hasHiddenChallenges = computed(() => {
  return orderedChallenges.value.length > challengeLimit;
});

const missionEnrollmentId = computed(() => {
  const ready = activeChallenges.value.find((challenge) => !challenge.today_checked);

  return (ready || activeChallenges.value[0])?.enrollment_id || null;
});

const guidedState = computed(() => {
  return getGuidedFeatureState({
    stats: stats.value,
    dashboardData: { challenges: challenges.value },
  });
});

const leaderboardTarget = computed(() => {
  const enrollmentId = missionEnrollmentId.value;
  return enrollmentId ? `/enrollment/${enrollmentId}/leaderboard` : "";
});

const showLeaderboardPreview = computed(() => {
  return Boolean(
    leaderboardTarget.value &&
    guidedState.value.features.leaderboard.unlocked,
  );
});

const nextLockedFeature = computed(() => {
  return guidedState.value.nextLocked;
});

const lockedFeatureLabel = computed(() => {
  const key = nextLockedFeature.value?.key;
  return key ? t(`guidedFeatures.labels.${key}`) : "";
});


function pushToast(text, type = "success") {
  const id = `${Date.now()}-${Math.random()}`;
  rewardToasts.value.push({ id, text, type });

  setTimeout(() => {
    rewardToasts.value = rewardToasts.value.filter((t) => t.id !== id);
  }, 1800);
}

function buildRewardMomentPayload(rewards, oldStats, challenge, context = {}) {
  const xpTotal = Number(rewards?.xp_total ?? stats.value?.total_points);
  const oldTotal = Number(oldStats?.total_points ?? oldStats?.xp);
  const xpEarned = Number.isFinite(xpTotal) && Number.isFinite(oldTotal)
    ? Math.max(0, xpTotal - oldTotal)
    : 0;
  const unlocked = Array.isArray(rewards?.achievements) ? rewards.achievements : [];
  const mission = context?.mission || null;
  const securedAt = mission?.secured_at || context?.securedAt || new Date().toISOString();
  const missionTitle = mission?.title || challenge?.mission_title || challenge?.name || "";
  const challengeName = mission?.challenge_name || challenge?.name || "";
  const missionSummary = mission?.description || challenge?.description || "";

  if (xpEarned <= 0 && unlocked.length === 0) return null;

  return {
    xpEarned,
    xpTotal: Number.isFinite(xpTotal) ? xpTotal : null,
    achievements: unlocked,
    unlockedFeatures: getNewlyUnlockedGuidedFeatures({
      oldStats,
      newStats: stats.value,
    }).map((featureKey) => ({
      key: featureKey,
      to: featureKey === "publicProfile" && user.value?.username
        ? `/u/${user.value.username}`
        : featureKey === "publicProfile"
          ? "/profile"
          : "/dashboard",
    })),
    streak: challenge?.current_streak ?? stats.value?.current_streak ?? null,
    mission: missionTitle
      ? {
        title: missionTitle,
        challengeName,
        summary: missionSummary,
        securedAt,
        securedDate: mission?.date || date.value || "",
        todayDoneBeforeYou: Number.isFinite(Number(mission?.today_done_before_you))
          ? Number(mission.today_done_before_you)
          : null,
        todayDoneCount: Number.isFinite(Number(mission?.today_done_count))
          ? Number(mission.today_done_count)
          : null,
      }
      : null,
  };
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
    error.value = e?.response?.data?.error || e?.message || String(e);
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

    const checkedChallenge = challenges.value.find(
      (challenge) => challenge.enrollment_id === enrollmentId,
    );
    rewardMoment.value = buildRewardMomentPayload(
      result.rewards,
      result.oldStats,
      checkedChallenge,
      { securedAt: new Date().toISOString() },
    );

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

// async function handleMissionCheckin() {
//   const oldStats = stats.value ? { ...stats.value } : null;

//   await loadDashboard({ silent: true });

//   const oldPoints = Number(oldStats?.total_points ?? oldStats?.xp);
//   const newPoints = Number(stats.value?.total_points ?? stats.value?.xp);
//   const xpEarned = Number.isFinite(oldPoints) && Number.isFinite(newPoints)
//     ? Math.max(0, newPoints - oldPoints)
//     : 0;

//   if (xpEarned > 0) {
//     pushToast(`+${xpEarned} XP`, "success");
//     pushToast(`🔥 ${t("dashboard.streakMaintained")}`, "success");
//   }
// }

async function handleMissionCheckin(payload = {}) {
  const oldStats = stats.value ? { ...stats.value } : null;

  await loadDashboard({ silent: true });

  if (payload?.source === "mission_completion") return;
  if (!oldStats || !stats.value) return;

  if (stats.value.level > oldStats.level) {
    rewardMoment.value = {
      type: "level",
      title: t("dashboard.rewards.levelTitle"),
      text: t("dashboard.rewards.levelText", { level: stats.value.level }),
    };
  }
}



function handleMissionCenterLoaded(payload) {
  missionCenterStatus.value = {
    loaded: true,
    state: payload?.state || "",
    missions: payload?.missions || [],
    error: payload?.error || "",
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

async function doLogout() {
  try {
    loggingOut.value = true;
    await api.post("/auth/logout");
    router.push("/login");
  } finally {
    loggingOut.value = false;
  }
}

onMounted(loadDashboard);
</script>

<style scoped>
.dashboardStack {
  display: grid;
  gap: var(--s-16);
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow-x: clip;
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
