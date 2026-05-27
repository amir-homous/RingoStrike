<template>
  <AppContainer>
    <AppHeader />

    <div class="stack-16">
      <div class="pageHead">
        <div class="stack-8">
          <h1 class="h1">Dashboard</h1>
          <p v-if="user" class="caption">Welcome, <b>{{ user.name }}</b> — {{ date }}</p>
        </div>

        <div class="headActions">
          <RouterLink class="ghostLink" to="/challenges">Browse Challenges</RouterLink>
          <BaseButton variant="secondary" :loading="loggingOut" @click="doLogout">Logout</BaseButton>
        </div>
      </div>

      <UiState :loading="loading" :error="!!error" :empty="false" loading-title="Loading dashboard…"
        loading-text="Fetching your active challenges and progress." error-title="Couldn’t load dashboard"
        :error-text="error || 'Please try again.'" @retry="loadDashboard" />

      <template v-if="!loading && !error">
        <HeroProgressCard v-if="stats" :user-name="user?.name" :stats="stats" :animate-pulse="xpPulse" />

        <div class="progressGrid" v-if="stats">
          <StatsGrid :stats="stats" />
          <div class="stack-12 sideCol">
            <NextGoalCard :stats="stats" />
            <RecentProgressFeed :stats="stats" />
          </div>
        </div>

        <BaseCard>
          <div class="listHead"><h2 class="h2">Active Challenges</h2></div>

          <div v-if="challenges.length" class="list">
            <ChallengeCard
              v-for="c in challenges"
              :key="c.enrollment_id"
              :challenge="c"
              :loading="checkingId === c.enrollment_id"
              @checkin="checkin"
            />
          </div>

          <div v-else class="stack-12">
            <p class="caption">No active challenges yet. Join one to start earning XP.</p>
            <RouterLink class="ctaLink" to="/challenges"><span aria-hidden="true">🧩</span>Browse challenges<span aria-hidden="true">→</span></RouterLink>
          </div>
        </BaseCard>
      </template>
    </div>

    <RewardFeedback :items="rewardToasts" />
  </AppContainer>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../lib/api";
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

const XP_PER_CHECKIN = 10;

function pushToast(text, type = "success") {
  const id = `${Date.now()}-${Math.random()}`;
  rewardToasts.value.push({ id, text, type });
  setTimeout(() => {
    rewardToasts.value = rewardToasts.value.filter((t) => t.id !== id);
  }, 1800);
}

async function hydrateChallengeMeta() {
  const detailCalls = challenges.value.map((c) => api.get(`/me/enrollments/${c.enrollment_id}`));
  const results = await Promise.allSettled(detailCalls);
  challenges.value = challenges.value.map((c, idx) => {
    const rs = results[idx];
    if (rs.status !== "fulfilled") return c;
    const payload = rs.value?.data || {};
    return {
      ...c,
      description: payload.challenge?.description || "",
      duration_days: payload.challenge?.duration_days || null,
      current_streak: payload.enrollment?.current_streak || 0,
    };
  });
}

async function loadDashboard() {
  error.value = "";
  loading.value = true;
  try {
    const [dashboardResp, statsResp] = await Promise.all([api.get("/me/challenges"), api.get("/me/stats")]);
    const dashboardData = dashboardResp.data;
    const statsData = statsResp.data;
    user.value = statsData.user || dashboardData.user || null;
    stats.value = statsData.stats || null;
    challenges.value = (dashboardData.challenges || []).map((c) => ({ ...c }));
    date.value = dashboardData.date || new Date().toLocaleDateString();
    await hydrateChallengeMeta();
  } catch (e) {
    console.error(e);
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function checkin(enrollmentId) {
  const oldStats = stats.value ? { ...stats.value } : null;
  const target = challenges.value.find((c) => c.enrollment_id === enrollmentId);
  if (!target || target.today_checked || !stats.value) return;

  checkingId.value = enrollmentId;
  error.value = "";

  target.today_checked = true;
  target.current_streak = (target.current_streak || 0) + 1;
  stats.value = {
    ...stats.value,
    total_points: stats.value.total_points + XP_PER_CHECKIN,
    total_checkins: stats.value.total_checkins + 1,
    current_streak: Math.max(stats.value.current_streak, (target.current_streak || 0)),
    xp: Math.min(stats.value.next_level_xp, stats.value.xp + XP_PER_CHECKIN),
    progress_percent: Math.min(100, stats.value.progress_percent + Math.round((XP_PER_CHECKIN / 100) * 100)),
  };
  xpPulse.value = true;
  setTimeout(() => (xpPulse.value = false), 520);

  try {
    await api.post(`/me/challenges/${enrollmentId}/checkin`);
    const statsResp = await api.get("/me/stats");
    stats.value = statsResp.data.stats || stats.value;
    pushToast(`+${XP_PER_CHECKIN} XP`, "success");
    pushToast("🔥 Streak maintained", "success");
    if (oldStats && stats.value.level > oldStats.level) {
      pushToast(`Level Up → Level ${stats.value.level}`, "level");
    }
  } catch (e) {
    if (oldStats) stats.value = oldStats;
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
.pageHead,.headActions{display:flex;flex-wrap:wrap}
.pageHead{justify-content:space-between;align-items:flex-end;gap:var(--s-16)}
.headActions{gap:var(--s-12);align-items:center}
.ghostLink,.ctaLink{padding:8px 10px;border-radius:10px;text-decoration:none}
.ghostLink{color:rgba(255,255,255,0.86);border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}
.ghostLink:hover{background:rgba(255,255,255,.06)}
.ctaLink{display:inline-flex;align-items:center;gap:var(--s-8);border:1px solid rgba(99,102,241,.28);background:rgba(99,102,241,.14);color:rgba(255,255,255,.92);font-weight:650}
.list{margin-top:var(--s-16);display:grid;gap:var(--s-12)}
.progressGrid{display:grid;gap:var(--s-12);grid-template-columns:minmax(0,2fr) minmax(0,1fr)}
@media (max-width: 900px){.progressGrid{grid-template-columns:1fr}}
</style>
