<template>
  <AppContainer>
    <AppHeader />

    <div class="dashboardStack">
      <UiState
        :loading="loading"
        :error="!!error"
        :empty="false"
        :loading-title="t('dashboard.loadingTitle')"
        :loading-text="t('dashboard.loadingText')"
        :error-title="t('dashboard.errorTitle')"
        :error-text="error || t('common.pleaseTryAgain')"
        @retry="loadDashboard"
      />

      <template v-if="!loading && !error">
        <TodayMission
          :challenges="challenges"
          :stats="stats"
          :loading="checkingId === missionEnrollmentId"
          @checkin="checkin"
        />

        <section class="dashboardHead supportHead">
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
              <span v-if="date" class="metaPill">{{ date }}</span>
              <span v-if="stats" class="metaPill">{{ t("common.level", { level: stats.level || 1 }) }}</span>
              <span v-if="stats" class="metaPill">{{ t("common.xp", { count: stats.total_points || 0 }) }}</span>
            </div>
          </div>

          <div class="headActions">
            <RouterLink class="primaryLink" to="/challenges">
              <span>{{ t("dashboard.browse") }}</span>
              <span aria-hidden="true">→</span>
            </RouterLink>

            <BaseButton
              variant="secondary"
              :loading="loggingOut"
              @click="doLogout"
            >
              {{ t("dashboard.logout") }}
            </BaseButton>
          </div>
        </section>

        <HeroProgressCard
          v-if="stats"
          :user-name="user?.name"
          :stats="stats"
          :animate-pulse="xpPulse"
        />

        <div class="progressGrid" v-if="stats">
          <StatsGrid :stats="stats" />

          <div class="sideCol">
            <NextGoalCard :stats="stats" />
            <RecentProgressFeed :stats="stats" />
          </div>
        </div>

        <BaseCard
          v-if="challenges.length"
          class="challengePanel"
        >
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
            <ChallengeCard
              v-for="c in visibleChallenges"
              :key="c.enrollment_id"
              :challenge="c"
              :loading="checkingId === c.enrollment_id"
              compact
              @checkin="checkin"
            />

            <button
              v-if="hasHiddenChallenges"
              type="button"
              class="showMoreButton"
              @click="showAllChallenges = !showAllChallenges"
            >
              <span>
                {{ showAllChallenges ? t("common.showFewer") : t("common.showMore", { count: orderedChallenges.length - challengeLimit }) }}
              </span>
              <span aria-hidden="true">{{ showAllChallenges ? "↑" : "↓" }}</span>
            </button>
          </div>

        </BaseCard>

        <ActivityTimeline
          :events="activityEvents"
          :loading="loading"
        />

        <AchievementPreview :achievements="achievements" />
      </template>
    </div>

    <RewardFeedback :items="rewardToasts" />
  </AppContainer>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";
import TodayMission from "@/components/dashboard/TodayMission.vue";
import HeroProgressCard from "@/components/progress/HeroProgressCard.vue";
import StatsGrid from "@/components/progress/StatsGrid.vue";
import NextGoalCard from "@/components/progress/NextGoalCard.vue";
import RecentProgressFeed from "@/components/progress/RecentProgressFeed.vue";
import ChallengeCard from "@/components/challenges/ChallengeCard.vue";
import RewardFeedback from "@/components/feedback/RewardFeedback.vue";
import ActivityTimeline from "@/components/activity/ActivityTimeline.vue";
import AchievementPreview from "@/components/achievements/AchievementPreview.vue";
import {
  DASHBOARD_CHALLENGE_LIMIT,
  getVisibleDashboardChallenges,
  loadDashboardData,
  orderDashboardChallenges,
} from "./dashboardFlow";
import {
  CHECKIN_XP,
  submitCheckinFlow,
} from "./challengeFlow";

const router = useRouter();
const { t } = useI18n();

const loading = ref(true);
const loggingOut = ref(false);
const checkingId = ref(null);
const error = ref("");
const user = ref(null);
const date = ref("");
const challenges = ref([]);
const stats = ref(null);
const rewardToasts = ref([]);
const xpPulse = ref(false);
const activityEvents = ref([]);
const achievements = ref([]);
const showAllChallenges = ref(false);

const XP_PER_CHECKIN = CHECKIN_XP;
const challengeLimit = DASHBOARD_CHALLENGE_LIMIT;

const firstName = computed(() => {
  return String(user.value?.name || "there").trim().split(" ")[0];
});

const completedTodayCount = computed(() => {
  return challenges.value.filter((challenge) => Boolean(challenge.today_checked)).length;
});

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
  const activeChallenges = challenges.value.filter((challenge) => {
    const status = String(challenge?.status || "active").toLowerCase();
    return status === "active" && challenge?.enrollment_id;
  });
  const ready = activeChallenges.find((challenge) => !challenge.today_checked);

  return (ready || activeChallenges[0])?.enrollment_id || null;
});

function pushToast(text, type = "success") {
  const id = `${Date.now()}-${Math.random()}`;
  rewardToasts.value.push({ id, text, type });

  setTimeout(() => {
    rewardToasts.value = rewardToasts.value.filter((t) => t.id !== id);
  }, 1800);
}

async function loadDashboard() {
  error.value = "";
  loading.value = true;

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
    loading.value = false;
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

    for (const a of result.unlocked) {
      pushToast(`🏆 ${a.title}`, "achievement");
    }

    pushToast(`+${XP_PER_CHECKIN} XP`, "success");
    pushToast(`🔥 ${t("dashboard.streakMaintained")}`, "success");

    if (result.oldStats && stats.value.level > result.oldStats.level) {
      pushToast(`Level Up → Level ${stats.value.level}`, "level");
    }
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    checkingId.value = null;
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

@media (max-width: 980px) {
  .dashboardHead,
  .progressGrid {
    grid-template-columns: 1fr;
  }

  .headActions,
  .panelActions {
    justify-content: flex-start;
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
  .ghostLink {
    width: 100%;
    white-space: normal;
    text-align: center;
  }

}
</style>
