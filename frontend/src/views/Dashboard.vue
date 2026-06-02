<template>
  <AppContainer>
    <AppHeader />

    <div class="dashboardStack">
      <section class="dashboardHead">
        <div class="headCopy">
          <div class="eyebrow">
            <span class="pulseDot"></span>
            <span>Progression Dashboard</span>
          </div>

          <h1 class="pageTitle">
            Welcome<span v-if="user">, {{ firstName }}</span>
          </h1>

          <p class="pageSubtitle">
            Protect today’s momentum, check your active paths, and keep your progression identity moving.
          </p>

          <div class="headMeta">
            <span v-if="date" class="metaPill">{{ date }}</span>
            <span v-if="stats" class="metaPill">Level {{ stats.level || 1 }}</span>
            <span v-if="stats" class="metaPill">{{ stats.total_points || 0 }} XP</span>
          </div>
        </div>

        <div class="headActions">
          <RouterLink class="primaryLink" to="/challenges">
            <span>Browse Challenges</span>
            <span aria-hidden="true">→</span>
          </RouterLink>

          <BaseButton
            variant="secondary"
            :loading="loggingOut"
            @click="doLogout"
          >
            Logout
          </BaseButton>
        </div>
      </section>

      <UiState
        :loading="loading"
        :error="!!error"
        :empty="false"
        loading-title="Loading dashboard…"
        loading-text="Fetching your active challenges and progress."
        error-title="Couldn’t load dashboard"
        :error-text="error || 'Please try again.'"
        @retry="loadDashboard"
      />

      <template v-if="!loading && !error">
        <section class="todayFocus">
          <div class="focusMain">
            <p class="sectionKicker">Today’s focus</p>
            <h2>{{ todayFocusTitle }}</h2>
            <p>{{ todayFocusText }}</p>
          </div>

          <div class="focusStats">
            <div class="focusStat ready">
              <strong>{{ readyTodayCount }}</strong>
              <span>Ready</span>
            </div>

            <div class="focusStat done">
              <strong>{{ completedTodayCount }}</strong>
              <span>Done</span>
            </div>

            <div class="focusStat streak">
              <strong>{{ stats?.current_streak || 0 }}</strong>
              <span>Streak</span>
            </div>
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

        <BaseCard class="challengePanel">
          <div class="panelHead">
            <div>
              <p class="sectionKicker">Active paths</p>
              <h2 class="panelTitle">Today’s challenges</h2>
              <p class="panelText">
                Start with ready paths first. Completed cards stay visible so you can feel today’s progress is secured.
              </p>
            </div>

            <div class="panelActions">
              <div v-if="challenges.length" class="miniSummary">
                <span>{{ completedTodayCount }}/{{ challenges.length }}</span>
                <small>secured</small>
              </div>

              <RouterLink class="ghostLink" to="/challenges">
                Add path
              </RouterLink>
            </div>
          </div>

          <div v-if="challenges.length" class="list">
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
                {{ showAllChallenges ? "Show fewer" : `Show ${orderedChallenges.length - challengeLimit} more` }}
              </span>
              <span aria-hidden="true">{{ showAllChallenges ? "↑" : "↓" }}</span>
            </button>
          </div>

          <div v-else class="emptyState">
            <div class="emptyIcon">🧩</div>
            <div>
              <h3>No active challenges yet</h3>
              <p>Join one path to start earning XP, building streaks, and unlocking achievements.</p>
              <RouterLink class="ctaLink" to="/challenges">
                <span>Browse challenges</span>
                <span aria-hidden="true">→</span>
              </RouterLink>
            </div>
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
import api from "@/lib/api";
import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";
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
  buildTodayFocus,
  getVisibleDashboardChallenges,
  loadDashboardData,
  orderDashboardChallenges,
} from "./dashboardFlow";

const router = useRouter();

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

const XP_PER_CHECKIN = 10;
const challengeLimit = DASHBOARD_CHALLENGE_LIMIT;

const firstName = computed(() => {
  return String(user.value?.name || "there").trim().split(" ")[0];
});

const completedTodayCount = computed(() => {
  return challenges.value.filter((challenge) => Boolean(challenge.today_checked)).length;
});

const readyTodayCount = computed(() => {
  return challenges.value.filter((challenge) => !challenge.today_checked).length;
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

const todayFocusTitle = computed(() => {
  return buildTodayFocus(challenges.value).title;
});

const todayFocusText = computed(() => {
  return buildTodayFocus(challenges.value).text;
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

function buildOptimisticEvents(target, oldLevel, newLevel) {
  const now = new Date().toISOString();

  const events = [
    {
      id: `optimistic-checkin-${Date.now()}`,
      type: "checkin",
      title: `Completed ${target.enrollment_name}`,
      subtitle: `+${XP_PER_CHECKIN} XP earned`,
      xp_delta: XP_PER_CHECKIN,
      icon: "check",
      created_at: now,
    },
    {
      id: `optimistic-streak-${Date.now()}`,
      type: "streak",
      title: `${target.current_streak || 1}-day streak maintained`,
      subtitle: "Consistency is compounding",
      icon: "flame",
      created_at: now,
    },
  ];

  if (newLevel > oldLevel) {
    events.push({
      id: `optimistic-level-${Date.now()}`,
      type: "level_up",
      title: `Reached Level ${newLevel}`,
      subtitle: "Milestone unlocked",
      icon: "level",
      created_at: now,
    });
  }

  return events;
}

async function checkin(enrollmentId) {
  const oldStats = stats.value ? { ...stats.value } : null;
  const target = challenges.value.find((c) => c.enrollment_id === enrollmentId);

  if (!target || target.today_checked || !stats.value) return;

  checkingId.value = enrollmentId;
  error.value = "";

  const oldActivity = [...activityEvents.value];

  target.today_checked = true;
  target.current_streak = (target.current_streak || 0) + 1;

  stats.value = {
    ...stats.value,
    total_points: stats.value.total_points + XP_PER_CHECKIN,
    total_checkins: stats.value.total_checkins + 1,
    current_streak: Math.max(stats.value.current_streak, target.current_streak || 0),
    xp: Math.min(stats.value.next_level_xp, stats.value.xp + XP_PER_CHECKIN),
    progress_percent: Math.min(
      100,
      stats.value.progress_percent + Math.round((XP_PER_CHECKIN / 100) * 100)
    ),
  };

  activityEvents.value = [
    ...buildOptimisticEvents(target, oldStats?.level || 1, stats.value.level || 1),
    ...activityEvents.value,
  ];

  xpPulse.value = true;

  setTimeout(() => {
    xpPulse.value = false;
  }, 520);

  try {
    const checkinResp = await api.post(`/me/challenges/${enrollmentId}/checkin`);

    const unlocked = checkinResp.data?.rewards?.achievements || [];

    for (const a of unlocked) {
      pushToast(`🏆 ${a.title}`, "achievement");
    }

    const [statsResp, activityResp, achievementsResp] = await Promise.all([
      api.get("/me/stats"),
      api.get("/me/activity"),
      api.get("/me/achievements"),
    ]);

    stats.value = statsResp.data.stats || stats.value;
    activityEvents.value = activityResp.data?.events || activityEvents.value;
    achievements.value = achievementsResp.data?.achievements || achievements.value;

    pushToast(`+${XP_PER_CHECKIN} XP`, "success");
    pushToast("🔥 Streak maintained", "success");

    if (oldStats && stats.value.level > oldStats.level) {
      pushToast(`Level Up → Level ${stats.value.level}`, "level");
    }
  } catch (e) {
    if (oldStats) {
      stats.value = oldStats;
    }

    activityEvents.value = oldActivity;

    if (target) {
      target.today_checked = false;
      target.current_streak = Math.max((target.current_streak || 1) - 1, 0);
    }

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
.ghostLink,
.ctaLink {
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

.ghostLink,
.ctaLink {
  color: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(255, 255, 255, 0.035);
}

.primaryLink:hover,
.ghostLink:hover,
.ctaLink:hover {
  background: rgba(255, 255, 255, 0.065);
  border-color: rgba(110, 229, 255, 0.25);
}

.todayFocus {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: center;
  padding: 20px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 0% 50%, rgba(99, 102, 241, 0.10), transparent 35%),
    rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.085);
}

.focusMain h2,
.panelTitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  letter-spacing: -0.04em;
}

.focusMain h2 {
  font-size: 1.35rem;
}

.focusMain p,
.panelText,
.emptyState p {
  margin: 8px 0 0;
  max-width: 720px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.65;
}

.focusStats {
  display: grid;
  grid-template-columns: repeat(3, 86px);
  gap: 10px;
}

.focusStat {
  min-height: 78px;
  display: grid;
  place-items: center;
  padding: 10px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.focusStat strong {
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.35rem;
  line-height: 1;
}

.focusStat span {
  margin-top: 5px;
  color: var(--muted2);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
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

.emptyState {
  display: flex;
  gap: var(--s-16);
  align-items: flex-start;
  margin-top: var(--s-16);
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.emptyIcon {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 17px;
  background: rgba(99, 102, 241, 0.14);
}

.emptyState h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.92);
}

@media (max-width: 980px) {
  .dashboardHead,
  .todayFocus,
  .progressGrid {
    grid-template-columns: 1fr;
  }

  .headActions,
  .panelActions {
    justify-content: flex-start;
  }

  .focusStats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .dashboardHead,
  .todayFocus {
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
  }

  .focusStats {
    grid-template-columns: 1fr;
  }

  .emptyState {
    flex-direction: column;
  }
}
</style>
