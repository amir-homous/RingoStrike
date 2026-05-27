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

      <BaseCard class="hero" :class="{ pulse: pulseProgress }">
        <div class="heroHead">
          <div>
            <div class="caption">Mission Progress</div>
            <h2 class="h2">Level {{ level }} • {{ stats.total_points }} XP</h2>
          </div>
          <div class="caption">{{ stats.current_streak }} day streak</div>
        </div>
        <div class="bar"><div class="fill" :style="{ width: xpPercent + '%' }" /></div>
        <div class="heroMeta caption">{{ xpToNext }} XP to next level</div>
      </BaseCard>

      <div class="statsGrid">
        <BaseCard class="stat"><div class="caption">Total XP</div><div class="h2">{{ stats.total_points }}</div></BaseCard>
        <BaseCard class="stat"><div class="caption">Current Streak</div><div class="h2">🔥 {{ stats.current_streak }}</div></BaseCard>
        <BaseCard class="stat"><div class="caption">Longest Streak</div><div class="h2">🏁 {{ stats.longest_streak }}</div></BaseCard>
      </div>

      <BaseCard>
        <UiState :loading="loading" :error="!!error" :empty="!loading && !error && challenges.length === 0"
          loading-title="Loading dashboard…" loading-text="Fetching your active challenges."
          empty-title="No active challenges yet" empty-text="Join a challenge to start checking in daily."
          error-title="Couldn’t load dashboard" :error-text="error || 'Please try again.'" @retry="loadDashboard" />

        <div v-if="!loading && !error && challenges.length" class="list">
          <ChallengeCard
            v-for="c in challenges" :key="c.enrollment_id" :challenge="c"
            :loading="checkingId === c.enrollment_id" @checkin="checkin"
          />
        </div>
      </BaseCard>
    </div>

    <RewardFeedback :items="feedbackItems" />
  </AppContainer>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import api from "../lib/api";
import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";
import ChallengeCard from "@/components/challenges/ChallengeCard.vue";
import RewardFeedback from "@/components/feedback/RewardFeedback.vue";

const router = useRouter();
const loading = ref(true); const loggingOut = ref(false); const checkingId = ref(null); const error = ref("");
const user = ref(null); const date = ref(""); const challenges = ref([]);
const stats = ref({ total_points: 0, current_streak: 0, longest_streak: 0 });
const pulseProgress = ref(false); const feedbackItems = ref([]);

const XP_PER_LEVEL = 100;
const level = computed(() => Math.floor((stats.value.total_points || 0) / XP_PER_LEVEL) + 1);
const xpPercent = computed(() => ((stats.value.total_points || 0) % XP_PER_LEVEL) / XP_PER_LEVEL * 100);
const xpToNext = computed(() => XP_PER_LEVEL - ((stats.value.total_points || 0) % XP_PER_LEVEL));

function enrichChallenges(items = []) {
  return items.map((c) => ({ ...c, xp_reward: 10, streak_text: c.today_checked ? "Streak protected" : "Check in to maintain streak", progress_text: c.today_checked ? "Today's step completed" : "1 action to progress" }));
}

async function loadDashboard() {
  error.value = ""; loading.value = true;
  try {
    const { data } = await api.get("/me/challenges");
    user.value = data.user || null;
    stats.value = data.user?.stats || stats.value;
    challenges.value = enrichChallenges(data.challenges || []);
    date.value = data.date || new Date().toLocaleDateString();
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally { loading.value = false; }
}

function pushFeedback(text, type = "xp") {
  const id = crypto.randomUUID();
  feedbackItems.value.push({ id, text, type });
  setTimeout(() => { feedbackItems.value = feedbackItems.value.filter((x) => x.id !== id); }, 1800);
}

async function checkin(enrollmentId) {
  const idx = challenges.value.findIndex((c) => c.enrollment_id === enrollmentId);
  if (idx < 0) return;
  const oldLevel = level.value;
  checkingId.value = enrollmentId; error.value = "";

  challenges.value[idx] = { ...challenges.value[idx], today_checked: true, streak_text: "Streak maintained", progress_text: "Momentum locked in" };
  stats.value = { ...stats.value, total_points: (stats.value.total_points || 0) + 10, current_streak: (stats.value.current_streak || 0) + 1 };
  pulseProgress.value = true; setTimeout(() => (pulseProgress.value = false), 480);

  try {
    await api.post(`/me/challenges/${enrollmentId}/checkin`);
    pushFeedback("+10 XP", "xp");
    pushFeedback("🔥 Streak maintained", "streak");
    if (level.value > oldLevel) pushFeedback(`Level Up → Level ${level.value}`, "level");
    await loadDashboard();
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
    await loadDashboard();
  } finally { checkingId.value = null; }
}

async function doLogout() { try { loggingOut.value = true; await api.post("/auth/logout"); router.push("/login"); } finally { loggingOut.value = false; } }
onMounted(loadDashboard);
</script>

<style scoped>
.pageHead,.headActions,.heroHead{display:flex;justify-content:space-between;gap:var(--s-12);flex-wrap:wrap}
.pageHead{align-items:flex-end}.headActions,.heroHead{align-items:center}
.ghostLink{color:rgba(255,255,255,.86);padding:8px 10px;border-radius:10px;border:1px solid rgba(255,255,255,.10);background:rgba(255,255,255,.03)}
.hero{background:linear-gradient(180deg,rgba(255,255,255,.12),rgba(255,255,255,.04));border-color:rgba(255,255,255,.15)}
.bar{height:10px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden;margin-top:10px}
.fill{height:100%;background:linear-gradient(90deg,rgba(99,102,241,.9),rgba(129,140,248,.95));transition: width .45s ease}
.pulse .fill{box-shadow:0 0 10px rgba(99,102,241,.65)}
.heroMeta{margin-top:8px}
.statsGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:var(--s-12)}
.stat{padding:var(--s-12)}
.list{margin-top:var(--s-16);display:grid;gap:var(--s-12)}
</style>
