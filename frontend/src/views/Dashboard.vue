<template>
  <AppContainer>
    <AppHeader />

    <div class="stack-16">
      <div class="pageHead">
        <div class="stack-8">
          <h1 class="h1">Dashboard</h1>
          <p v-if="user" class="caption">
            Welcome, <b>{{ user.name }}</b> — {{ date }}
          </p>
        </div>

        <div class="headActions">
          <RouterLink class="ghostLink" to="/challenges">Browse Challenges</RouterLink>
          <BaseButton variant="secondary" :loading="loggingOut" @click="doLogout">Logout</BaseButton>
        </div>
      </div>

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
        <HeroProgressCard v-if="stats" :user-name="user?.name" :stats="stats" />

        <div class="progressGrid" v-if="stats">
          <StatsGrid :stats="stats" />
          <div class="stack-12 sideCol">
            <NextGoalCard :stats="stats" />
            <RecentProgressFeed :stats="stats" />
          </div>
        </div>

        <BaseCard>
          <div class="listHead">
            <h2 class="h2">Active Challenges</h2>
          </div>

          <div v-if="challenges.length" class="list">
            <BaseCard v-for="c in challenges" :key="c.enrollment_id" class="itemCard" :padded="true">
              <div class="row">
                <div class="left">
                  <div class="titleRow">
                    <h2 class="h2 title">{{ c.enrollment_name }}</h2>
                    <div class="badges">
                      <span class="badge"><span aria-hidden="true">{{ c.status === 'Active' ? '🟢' : '⚪️' }}</span>{{ c.status || '—' }}</span>
                      <span class="badge" :class="c.today_checked ? 'b-ok' : 'b-wait'">
                        <span aria-hidden="true">{{ c.today_checked ? '✅' : '⏳' }}</span>
                        Today: <b>{{ c.today_checked ? 'Done' : 'Not yet' }}</b>
                      </span>
                    </div>
                  </div>
                </div>
                <div class="right">
                  <RouterLink class="openLink" :to="`/enrollment/${c.enrollment_id}`">Open →</RouterLink>
                  <BaseButton variant="primary" :loading="checkingId === c.enrollment_id" :disabled="c.today_checked" @click="checkin(c.enrollment_id)">
                    <span v-if="c.today_checked">✅ Done</span><span v-else>Check-in</span>
                  </BaseButton>
                </div>
              </div>
            </BaseCard>
          </div>

          <div v-else class="stack-12">
            <p class="caption">No active challenges yet. Join one to start earning XP.</p>
            <RouterLink class="ctaLink" to="/challenges"><span aria-hidden="true">🧩</span>Browse challenges<span aria-hidden="true">→</span></RouterLink>
          </div>
        </BaseCard>
      </template>
    </div>
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

const router = useRouter();
const loading = ref(true);
const loggingOut = ref(false);
const checkingId = ref(null);
const error = ref("");
const user = ref(null);
const date = ref("");
const challenges = ref([]);
const stats = ref(null);

async function loadDashboard() {
  error.value = "";
  loading.value = true;
  try {
    const [dashboardResp, statsResp] = await Promise.all([api.get("/me/challenges"), api.get("/me/stats")]);
    const dashboardData = dashboardResp.data;
    const statsData = statsResp.data;
    user.value = statsData.user || dashboardData.user || null;
    stats.value = statsData.stats || null;
    challenges.value = dashboardData.challenges || [];
    date.value = dashboardData.date || new Date().toLocaleDateString();
  } catch (e) {
    console.error(e);
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function checkin(enrollmentId) {
  try {
    checkingId.value = enrollmentId;
    await api.post(`/me/challenges/${enrollmentId}/checkin`);
    await loadDashboard();
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
.pageHead,.headActions,.row,.badges{display:flex;flex-wrap:wrap}
.pageHead{justify-content:space-between;align-items:flex-end;gap:var(--s-16)}
.headActions{gap:var(--s-12);align-items:center}
.ghostLink,.ctaLink{padding:8px 10px;border-radius:10px;text-decoration:none}
.ghostLink{color:rgba(255,255,255,0.86);border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}
.ghostLink:hover{background:rgba(255,255,255,.06)}
.ctaLink{display:inline-flex;align-items:center;gap:var(--s-8);border:1px solid rgba(99,102,241,.28);background:rgba(99,102,241,.14);color:rgba(255,255,255,.92);font-weight:650}
.list{margin-top:var(--s-16);display:grid;gap:var(--s-12)}
.itemCard{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.08);box-shadow:none}
.row{justify-content:space-between;align-items:center;gap:var(--s-16)}
.left{min-width:0;flex:1}.titleRow{display:flex;flex-direction:column;gap:var(--s-8)}
.title{margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.progressGrid{display:grid;gap:var(--s-12);grid-template-columns:minmax(0,2fr) minmax(0,1fr)}
@media (max-width: 900px){.progressGrid{grid-template-columns:1fr}}
</style>
