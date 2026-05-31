<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import api from "@/lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";

const route = useRoute();

const props = defineProps({
  id: { type: [String, Number], required: false },
  enrollmentId: { type: [String, Number], required: false },
  embedded: { type: Boolean, default: false },
});

const id = computed(() => {
  const pid = props.enrollmentId ?? props.id;
  const rid = route.params.id;
  const val = pid ?? rid;
  return val == null ? "" : String(val);
});

const overall = ref([]);
const today = ref([]);
const loading = ref(true);
const error = ref("");
const showAllOverall = ref(false);
const showAllToday = ref(false);

const embeddedLimit = 5;
const pageLimit = 12;
const todayLimit = 8;

const errorText = computed(() => {
  if (error.value === "missing_id") {
    return "Invalid leaderboard link (missing enrollment id).";
  }

  return "Try again. If it keeps happening, the API might be down.";
});

const isEmpty = computed(() => {
  return !loading.value && !error.value && overall.value.length === 0;
});

const topThree = computed(() => {
  return overall.value.slice(0, 3);
});

const topStreak = computed(() => {
  if (!overall.value.length) return 0;

  return Math.max(
    ...overall.value.map((row) => Number(row.current_streak || 0))
  );
});

const overallLimit = computed(() => {
  return props.embedded ? embeddedLimit : pageLimit;
});

const visibleOverall = computed(() => {
  if (showAllOverall.value) return overall.value;
  return overall.value.slice(0, overallLimit.value);
});

const visibleToday = computed(() => {
  if (showAllToday.value) return today.value;
  return today.value.slice(0, todayLimit);
});

const hasHiddenOverall = computed(() => {
  return overall.value.length > overallLimit.value;
});

const hasHiddenToday = computed(() => {
  return today.value.length > todayLimit;
});

async function fetchLeaderboard() {
  loading.value = true;
  error.value = "";

  if (!id.value) {
    error.value = "missing_id";
    loading.value = false;
    return;
  }

  try {
    const res = await api.get(`/me/enrollments/${id.value}/leaderboard`);
    overall.value = res.data?.overall || [];
    today.value = res.data?.today || [];
  } catch (err) {
    console.error("Leaderboard error:", err);
    error.value = "failed";
  } finally {
    loading.value = false;
  }
}

onMounted(fetchLeaderboard);
</script>

<template>
  <div v-if="embedded" class="leaderboardBlock embedded stack-16">
    <BaseCard>
      <UiState
        :loading="loading"
        :error="!!error"
        :empty="isEmpty"
        loading-title="Loading leaderboard…"
        loading-text="Getting the latest rankings."
        empty-title="No leaderboard data yet"
        empty-text="Once people check in, rankings will show here."
        error-title="Couldn’t load leaderboard"
        :error-text="errorText"
        @retry="fetchLeaderboard"
      />

      <div v-if="!loading && !error && overall.length" class="leaderboardPanel">
        <div class="panelHeader">
          <div>
            <div class="eyebrow">Overall Ranking</div>
            <h2 class="panelTitle">Challenge Standings</h2>
            <div class="caption">
              Top consistency signals for this challenge.
            </div>
          </div>

          <div class="panelMetric">
            <span class="metricValue">{{ overall.length }}</span>
            <span class="metricLabel">Players</span>
          </div>
        </div>

        <div class="tableWrap">
          <table class="table">
            <thead>
              <tr>
                <th class="col-rank">Rank</th>
                <th>User</th>
                <th class="col-status">Today</th>
                <th class="col-num">Total</th>
                <th class="col-num">Streak</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="(row, index) in visibleOverall"
                :key="row.enrollment_id || index"
                :class="{ topRank: (row.rank ?? index + 1) <= 3 }"
              >
                <td class="rank">
                  <span class="rankPill">#{{ row.rank ?? index + 1 }}</span>
                </td>

                <td class="user">
                  <div class="userCell">
                    <div class="avatarRing">
                      {{ (row.name || row.username || "?").slice(0, 1).toUpperCase() }}
                    </div>
                    <div>
                      <div class="uname">{{ row.name || "Unknown" }}</div>
                      <div class="caption" v-if="row.username">@{{ row.username }}</div>
                    </div>
                  </div>
                </td>

                <td class="status">
                  <span :class="['todayBadge', row.today_checked ? 'done' : 'pending']">
                    {{ row.today_checked ? "Done" : "Pending" }}
                  </span>
                </td>

                <td class="num">{{ row.total_checkins ?? 0 }}</td>
                <td class="num streakNum">{{ row.current_streak ?? 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <button
          v-if="hasHiddenOverall"
          type="button"
          class="showMoreButton"
          @click="showAllOverall = !showAllOverall"
        >
          {{ showAllOverall ? "Show fewer" : `Show ${overall.length - overallLimit} more` }}
        </button>
      </div>
    </BaseCard>
  </div>

  <AppContainer v-else>
    <AppHeader />

    <div class="leaderboardBlock stack-16">
      <section class="heroCard">
        <div class="heroGlow"></div>

        <div class="heroContent">
          <div class="titleWithIcon">
            <span class="icon" aria-hidden="true">🏆</span>
            <div>
              <div class="eyebrow">Social Momentum</div>
              <h1 class="h1">Leaderboard</h1>
              <div class="caption">
                Ranked by total check-ins, streak strength, and consistency.
              </div>
            </div>
          </div>

          <div class="heroStats">
            <div class="heroStat">
              <span class="heroStatValue">{{ overall.length }}</span>
              <span class="heroStatLabel">Players</span>
            </div>

            <div class="heroStat done">
              <span class="heroStatValue">{{ today.length }}</span>
              <span class="heroStatLabel">Done Today</span>
            </div>

            <div class="heroStat streak">
              <span class="heroStatValue">{{ topStreak }}</span>
              <span class="heroStatLabel">Top Streak</span>
            </div>
          </div>
        </div>
      </section>

      <BaseCard>
        <UiState
          :loading="loading"
          :error="!!error"
          :empty="isEmpty"
          loading-title="Loading leaderboard…"
          loading-text="Getting the latest rankings."
          empty-title="No leaderboard data yet"
          empty-text="Once people check in, rankings will show here."
          error-title="Couldn’t load leaderboard"
          :error-text="errorText"
          @retry="fetchLeaderboard"
        />

        <div v-if="!loading && !error && overall.length" class="leaderboardPanel">
          <div class="panelHeader">
            <div>
              <div class="eyebrow">Overall Ranking</div>
              <h2 class="panelTitle">Challenge Standings</h2>
              <div class="caption">
                Overall ranking rewards consistency over noisy competition.
              </div>
            </div>

            <div class="rulesChip">
              Total → Streak → Name
            </div>
          </div>

          <div class="podium" v-if="topThree.length >= 3">
            <div
              v-for="row in topThree"
              :key="`podium-${row.enrollment_id}`"
              :class="['podiumCard', `rank-${row.rank}`]"
            >
              <div class="podiumRank">#{{ row.rank }}</div>
              <div class="podiumAvatar">
                {{ (row.name || row.username || "?").slice(0, 1).toUpperCase() }}
              </div>
              <div class="podiumName">{{ row.name || "Unknown" }}</div>
              <div class="podiumMeta" v-if="row.username">@{{ row.username }}</div>
              <div class="podiumStats">
                <span>{{ row.total_checkins ?? 0 }} checks</span>
                <span>{{ row.current_streak ?? 0 }} streak</span>
              </div>
            </div>
          </div>

          <div class="tableWrap">
            <table class="table">
              <thead>
                <tr>
                  <th class="col-rank">Rank</th>
                  <th>User</th>
                  <th class="col-status">Today</th>
                  <th class="col-num">Total</th>
                  <th class="col-num">Streak</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="(row, index) in visibleOverall"
                  :key="row.enrollment_id || index"
                  :class="{ topRank: (row.rank ?? index + 1) <= 3 }"
                >
                  <td class="rank">
                    <span class="rankPill">#{{ row.rank ?? index + 1 }}</span>
                  </td>

                  <td class="user">
                    <div class="userCell">
                      <div class="avatarRing">
                        {{ (row.name || row.username || "?").slice(0, 1).toUpperCase() }}
                      </div>
                      <div>
                        <div class="uname">{{ row.name || "Unknown" }}</div>
                        <div class="caption" v-if="row.username">@{{ row.username }}</div>
                      </div>
                    </div>
                  </td>

                  <td class="status">
                    <span :class="['todayBadge', row.today_checked ? 'done' : 'pending']">
                      {{ row.today_checked ? "Done" : "Pending" }}
                    </span>
                  </td>

                  <td class="num">{{ row.total_checkins ?? 0 }}</td>
                  <td class="num streakNum">{{ row.current_streak ?? 0 }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <button
            v-if="hasHiddenOverall"
            type="button"
            class="showMoreButton"
            @click="showAllOverall = !showAllOverall"
          >
            {{ showAllOverall ? "Show fewer standings" : `Show ${overall.length - pageLimit} more standings` }}
          </button>

          <div class="rankingNote">
            <span>ℹ️</span>
            <span>
              Ranking currently prioritizes total check-ins, then streak strength, then name ordering.
            </span>
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <section class="todaySection">
          <div class="panelHeader">
            <div>
              <div class="eyebrow">Daily Momentum</div>
              <h2 class="panelTitle">Today’s Strike</h2>
              <div class="caption">Users who have checked in today.</div>
            </div>

            <div class="panelMetric">
              <span class="metricValue">{{ today.length }}</span>
              <span class="metricLabel">Done Today</span>
            </div>
          </div>

          <div v-if="!loading && !error && today.length" class="tableWrap compact">
            <table class="table">
              <thead>
                <tr>
                  <th class="col-rank">Rank</th>
                  <th>User</th>
                  <th class="col-num">Total</th>
                  <th class="col-num">Streak</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="(row, index) in visibleToday" :key="row.enrollment_id || index">
                  <td class="rank">
                    <span class="rankPill active">#{{ row.rank ?? index + 1 }}</span>
                  </td>

                  <td class="user">
                    <div class="userCell">
                      <div class="avatarRing active">
                        {{ (row.name || row.username || "?").slice(0, 1).toUpperCase() }}
                      </div>
                      <div>
                        <div class="uname">{{ row.name || "Unknown" }}</div>
                        <div class="caption" v-if="row.username">@{{ row.username }}</div>
                      </div>
                    </div>
                  </td>

                  <td class="num">{{ row.total_checkins ?? 0 }}</td>
                  <td class="num streakNum">{{ row.current_streak ?? 0 }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <button
            v-if="hasHiddenToday"
            type="button"
            class="showMoreButton"
            @click="showAllToday = !showAllToday"
          >
            {{ showAllToday ? "Show fewer today" : `Show ${today.length - todayLimit} more today` }}
          </button>

          <div v-else-if="!loading && !error && !today.length" class="todayEmpty">
            <div class="emptyIcon">🌙</div>
            <div>
              <div class="emptyTitle">No strikes yet today</div>
              <div class="caption">The daily board will activate after the first check-in.</div>
            </div>
          </div>
        </section>
      </BaseCard>
    </div>
  </AppContainer>
</template>

<style scoped>
.leaderboardBlock {
  position: relative;
}

.heroCard {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 28px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background:
    radial-gradient(circle at 15% 20%, rgba(110, 229, 255, 0.16), transparent 34%),
    radial-gradient(circle at 85% 10%, rgba(195, 90, 214, 0.16), transparent 32%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.025));
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.28);
}

.heroGlow {
  position: absolute;
  inset: -80px;
  background:
    linear-gradient(90deg, transparent, rgba(110, 229, 255, 0.08), transparent),
    radial-gradient(circle, rgba(255, 255, 255, 0.08), transparent 55%);
  opacity: 0.75;
  pointer-events: none;
}

.heroContent {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s-20);
}

.titleWithIcon {
  display: flex;
  align-items: center;
  gap: var(--s-16);
}

.icon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 18px;
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.18), transparent 36%),
    rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    0 12px 30px rgba(0, 0, 0, 0.22);
}

.eyebrow {
  margin-bottom: 4px;
  color: rgba(110, 229, 255, 0.88);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.heroStats {
  display: flex;
  gap: var(--s-12);
  flex-wrap: wrap;
  justify-content: flex-end;
}

.heroStat,
.panelMetric {
  min-width: 104px;
  padding: 12px 14px;
  border-radius: 18px;
  text-align: right;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.heroStat.done {
  border-color: rgba(74, 222, 128, 0.18);
}

.heroStat.streak {
  border-color: rgba(255, 228, 168, 0.18);
}

.heroStatValue,
.metricValue {
  display: block;
  color: white;
  font-size: 1.45rem;
  font-weight: 850;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.heroStatLabel,
.metricLabel {
  display: block;
  margin-top: 4px;
  color: var(--muted2);
  font-size: 0.72rem;
  font-weight: 700;
}

.leaderboardPanel {
  position: relative;
}

.panelHeader {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--s-16);
  margin-bottom: var(--s-16);
  flex-wrap: wrap;
}

.panelTitle {
  margin: 0;
  font-size: 1.1rem;
  letter-spacing: -0.02em;
}

.rulesChip {
  padding: 7px 11px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.74);
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.09);
  font-size: 0.72rem;
  font-weight: 700;
}

.podium {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
  margin-bottom: var(--s-16);
}

.podiumCard {
  position: relative;
  overflow: hidden;
  min-height: 150px;
  padding: 18px;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background:
    radial-gradient(circle at 50% 0%, rgba(110, 229, 255, 0.13), transparent 42%),
    rgba(255, 255, 255, 0.04);
}

.podiumCard::before {
  content: "";
  position: absolute;
  inset: 0;
  opacity: 0.75;
  pointer-events: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), transparent 42%);
}

.podiumCard.rank-1 {
  border-color: rgba(255, 228, 168, 0.28);
  background:
    radial-gradient(circle at 50% 0%, rgba(255, 228, 168, 0.18), transparent 44%),
    rgba(255, 255, 255, 0.045);
}

.podiumCard.rank-2 {
  border-color: rgba(110, 229, 255, 0.20);
}

.podiumCard.rank-3 {
  border-color: rgba(195, 90, 214, 0.20);
}

.podiumRank,
.podiumAvatar,
.podiumName,
.podiumMeta,
.podiumStats {
  position: relative;
  z-index: 1;
}

.podiumRank {
  color: rgba(255, 255, 255, 0.86);
  font-weight: 900;
  font-size: 0.82rem;
}

.podiumAvatar {
  width: 44px;
  height: 44px;
  margin-top: 14px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  color: white;
  font-weight: 900;
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.25), transparent 35%),
    linear-gradient(135deg, rgba(110, 229, 255, 0.32), rgba(195, 90, 214, 0.20));
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.podiumName {
  margin-top: 12px;
  color: white;
  font-weight: 850;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.podiumMeta {
  margin-top: 2px;
  color: var(--muted2);
  font-size: 0.78rem;
}

.podiumStats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.podiumStats span {
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.055);
  font-size: 0.72rem;
  font-weight: 700;
}

.tableWrap {
  margin-top: var(--s-16);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  overflow: hidden;
  overflow-x: auto;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.018));
}

.tableWrap.compact {
  margin-top: 0;
}

.table {
  width: 100%;
  border-collapse: collapse;
  min-width: 640px;
}

thead th {
  text-align: left;
  font-size: var(--cap);
  color: var(--muted2);
  font-weight: 800;
  padding: 13px 14px;
  background: rgba(255, 255, 255, 0.035);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

tbody td {
  padding: 13px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.055);
}

tbody tr {
  transition:
    background 0.18s ease,
    transform 0.18s ease;
}

tbody tr:hover {
  background: rgba(255, 255, 255, 0.035);
}

tbody tr:last-child td {
  border-bottom: 0;
}

tbody tr.topRank {
  background:
    linear-gradient(90deg, rgba(110, 229, 255, 0.055), transparent 55%);
}

.col-rank {
  width: 86px;
}

.col-status {
  width: 120px;
  text-align: center;
}

.col-num {
  width: 110px;
  text-align: right;
}

.rank {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 800;
}

.rankPill {
  display: inline-flex;
  min-width: 46px;
  justify-content: center;
  padding: 5px 9px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.88);
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.09);
  font-variant-numeric: tabular-nums;
}

.rankPill.active {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.10);
  border-color: rgba(74, 222, 128, 0.18);
}

.user {
  max-width: 420px;
}

.userCell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatarRing {
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  color: white;
  font-size: 0.82rem;
  font-weight: 900;
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.20), transparent 35%),
    rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.11);
}

.avatarRing.active {
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.25), transparent 35%),
    rgba(74, 222, 128, 0.12);
  border-color: rgba(74, 222, 128, 0.22);
}

.uname {
  color: rgba(255, 255, 255, 0.92);
  font-weight: 750;
}

.num {
  text-align: right;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.streakNum {
  color: rgba(255, 228, 168, 0.92);
}

.status {
  text-align: center;
}

.todayBadge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 72px;
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 850;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.todayBadge.done {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.10);
  border-color: rgba(74, 222, 128, 0.18);
}

.todayBadge.pending {
  color: var(--muted2);
  background: rgba(255, 255, 255, 0.04);
}

.todaySection {
  position: relative;
}

.todayEmpty {
  display: flex;
  align-items: center;
  gap: var(--s-12);
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.08), transparent 35%),
    rgba(255, 255, 255, 0.03);
  color: var(--muted2);
}

.emptyIcon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.09);
}

.emptyTitle {
  color: rgba(255, 255, 255, 0.86);
  font-weight: 800;
}

.showMoreButton {
  width: 100%;
  min-height: 38px;
  margin-top: var(--s-12);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-weight: 850;
}

.showMoreButton:hover {
  background: rgba(255, 255, 255, 0.065);
  border-color: rgba(110, 229, 255, 0.25);
}

.rankingNote {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin-top: var(--s-12);
  padding: 12px;
  border-radius: var(--r-12);
  color: rgba(255, 255, 255, 0.62);
  background: rgba(255, 255, 255, 0.028);
  border: 1px dashed rgba(255, 255, 255, 0.10);
  font-size: 0.82rem;
  line-height: 1.5;
}

@media (max-width: 760px) {
  .heroContent,
  .panelHeader {
    align-items: flex-start;
    flex-direction: column;
  }

  .heroStats {
    width: 100%;
  }

  .heroStat {
    flex: 1;
    text-align: left;
  }

  .podium {
    grid-template-columns: 1fr;
  }

  .table {
    min-width: 680px;
  }
}
</style>