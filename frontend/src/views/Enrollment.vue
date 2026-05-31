<template>
  <AppContainer>
    <AppHeader />

    <div class="enrollmentPage">
      <UiState
        :loading="loading"
        :error="!!error"
        :empty="!loading && !error && !enrollment"
        loading-title="Loading enrollment…"
        loading-text="Fetching challenge and your progress."
        empty-title="Enrollment not found"
        empty-text="This enrollment might be invalid or you don’t have access."
        error-title="Couldn’t load enrollment"
        :error-text="error || 'Please try again.'"
        @retry="load"
      />

      <div v-if="!loading && !error && enrollment" class="stack-16">
        <section class="heroCard">
          <div class="heroGlow"></div>

          <div class="heroContent">
            <div class="heroMain">
              <div class="eyebrow">Challenge Command Center</div>
              <h1 class="heroTitle">{{ challenge?.name || enrollment.name || "Challenge" }}</h1>

              <p v-if="challenge?.description" class="heroDesc">
                {{ challenge.description }}
              </p>

              <div class="heroMeta">
                <span class="metaPill">
                  <span class="dot" :class="{ active: enrollment.status === 'Active' }"></span>
                  {{ enrollment.status || "Unknown" }}
                </span>

                <span v-if="durationDays" class="metaPill">
                  {{ durationDays }} day challenge
                </span>

                <span v-if="enrollment.start_date" class="metaPill">
                  Started {{ formatDate(enrollment.start_date) }}
                </span>
              </div>
            </div>

            <div class="checkinPanel">
              <div class="checkinStatus" :class="{ done: enrollment.today_checked }">
                <div class="statusIcon">{{ enrollment.today_checked ? "✅" : "⚡" }}</div>
                <div>
                  <div class="statusLabel">Today’s Strike</div>
                  <div class="statusValue">
                    {{ enrollment.today_checked ? "Completed" : "Not checked in" }}
                  </div>
                </div>
              </div>

              <BaseButton
                variant="primary"
                :loading="checking"
                :disabled="enrollment.today_checked"
                @click="checkin"
              >
                <span v-if="enrollment.today_checked">Done for today</span>
                <span v-else>Check in now</span>
              </BaseButton>
            </div>
          </div>
        </section>

        <section class="insightGrid">
          <BaseCard class="metricCard" :padded="true">
            <div class="metricIcon">⏳</div>
            <div class="metricLabel">Remaining</div>
            <div class="metricValue">{{ remainingDaysText }}</div>
            <div class="metricHint">{{ timingHint }}</div>
          </BaseCard>

          <BaseCard class="metricCard" :padded="true">
            <div class="metricIcon">✅</div>
            <div class="metricLabel">Total Check-ins</div>
            <div class="metricValue">{{ totalCheckins }}</div>
            <div class="metricHint">Completed strikes in this challenge.</div>
          </BaseCard>

          <BaseCard class="metricCard" :padded="true">
            <div class="metricIcon">🔥</div>
            <div class="metricLabel">Current Streak</div>
            <div class="metricValue">{{ currentStreak }}</div>
            <div class="metricHint">Your active momentum chain.</div>
          </BaseCard>

          <BaseCard class="metricCard" :padded="true">
            <div class="metricIcon">📈</div>
            <div class="metricLabel">Timeline Progress</div>
            <div class="metricValue">{{ timelinePercent }}%</div>
            <div class="metricHint">Based on challenge duration.</div>
          </BaseCard>
        </section>

        <BaseCard class="timelineCard" :padded="true">
          <div class="sectionHead">
            <div>
              <div class="eyebrow">Challenge Timeline</div>
              <h2 class="h2">Time & Momentum</h2>
            </div>

            <div class="timelineBadge">
              {{ progressText }}
            </div>
          </div>

          <div class="timelineBar">
            <div class="timelineFill" :style="{ width: timelinePercent + '%' }"></div>
            <div class="timelinePulse" :style="{ left: timelinePercent + '%' }"></div>
          </div>

          <div class="timelineMeta">
            <div>
              <div class="caption">Start</div>
              <strong>{{ enrollment.start_date ? formatDate(enrollment.start_date) : "—" }}</strong>
            </div>

            <div>
              <div class="caption">End</div>
              <strong>{{ enrollment.end_date ? formatDate(enrollment.end_date) : "—" }}</strong>
            </div>

            <div>
              <div class="caption">Checked</div>
              <strong>{{ checkedDays }} / {{ totalDays }} days</strong>
            </div>
          </div>
        </BaseCard>

        <BaseCard class="progressCard" :padded="true">
          <div class="sectionHead">
            <div>
              <div class="eyebrow">Personal Progress</div>
              <h2 class="h2">Consistency Score</h2>
            </div>

            <div class="scoreBadge">
              {{ checkinPercent }}%
            </div>
          </div>

          <div class="progressMeta">
            <span>{{ checkedDays }} checked days</span>
            <span class="caption">{{ totalDays }} total challenge days</span>
          </div>

          <div class="bar">
            <div class="barFill" :style="{ width: checkinPercent + '%', background: barColor }"></div>
          </div>

          <div class="miniStats">
            <div class="miniStat">
              <span>Today</span>
              <strong>{{ enrollment.today_checked ? "Done" : "Pending" }}</strong>
            </div>

            <div class="miniStat">
              <span>Remaining</span>
              <strong>{{ remainingDaysText }}</strong>
            </div>

            <div class="miniStat">
              <span>Streak</span>
              <strong>{{ currentStreak }}</strong>
            </div>
          </div>
        </BaseCard>

        <section class="contentGrid">
          <div class="stack-12">
            <div class="sectionHead">
              <div class="titleWithIcon">
                <span class="icon" aria-hidden="true">🏆</span>
                <div>
                  <h2 class="h2">Leaderboard</h2>
                  <div class="caption">See how your consistency compares.</div>
                </div>
              </div>

              <router-link class="ctaLink" :to="`/enrollment/${enrollment.enrollment_id}/leaderboard`">
                View Full
                <span class="arrow">→</span>
              </router-link>
            </div>

            <Leaderboard :enrollment-id="enrollment.enrollment_id" embedded />
          </div>

          <BaseCard class="logsCard" :padded="true">
            <div class="sectionHead">
              <div class="titleWithIcon">
                <span class="icon" aria-hidden="true">🗓️</span>
                <div>
                  <h2 class="h2">Recent Logs</h2>
                  <div class="caption">Your latest challenge activity.</div>
                </div>
              </div>
            </div>

            <div v-if="recentLogs.length === 0" class="emptyLogs">
              <div class="emptyIcon">🌙</div>
              <div>
                <strong>No logs yet</strong>
                <div class="caption">Your check-ins will appear here.</div>
              </div>
            </div>

            <ul v-else class="logList">
              <li v-for="log in recentLogs" :key="log.daily_log_id" class="logRow">
                <span class="logDot" aria-hidden="true">✅</span>
                <div>
                  <div class="logDate">{{ formatDate(log.date) }}</div>
                  <div class="caption">Check-in completed</div>
                </div>
              </li>
            </ul>
          </BaseCard>
        </section>
      </div>
    </div>
  </AppContainer>
</template>

<script setup>
import Leaderboard from "./Leaderboard.vue";

import { onMounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import api from "../lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";

const route = useRoute();

const loading = ref(true);
const checking = ref(false);
const error = ref("");

const enrollment = ref(null);
const challenge = ref(null);
const recentLogs = ref([]);

const checkedDays = ref(0);
const totalDays = ref(0);

const durationDays = computed(() => {
  return Number(challenge.value?.duration_days || enrollment.value?.duration_days || totalDays.value || 0);
});

const totalCheckins = computed(() => {
  const value = enrollment.value?.total_checkins ?? enrollment.value?.totalCheckins ?? null;
  if (value != null) return value;
  return checkedDays.value;
});

const currentStreak = computed(() => {
  const value = enrollment.value?.current_streak ?? enrollment.value?.currentStreak ?? null;
  if (value != null) return value;
  return "—";
});

const timelinePercent = computed(() => {
  const value = enrollment.value?.progress_percent;
  if (value != null) return clampPercent(value);

  if (!durationDays.value || enrollment.value?.remaining_days == null) return 0;
  const elapsed = Math.max(0, durationDays.value - enrollment.value.remaining_days);
  return clampPercent(Math.round((elapsed / durationDays.value) * 100));
});

const checkinPercent = computed(() => {
  if (!totalDays.value) return 0;
  return clampPercent(Math.round((checkedDays.value / totalDays.value) * 100));
});

const remainingDaysText = computed(() => {
  const value = enrollment.value?.remaining_days;
  if (value == null) return "—";
  if (value <= 0) return "Ended";
  return `${value}d`;
});

const timingHint = computed(() => {
  if (!enrollment.value?.end_date) return "Timing data is not available yet.";
  if ((enrollment.value?.remaining_days ?? 0) <= 0) return "This challenge timeline has ended.";
  return `Ends ${formatDate(enrollment.value.end_date)}.`;
});

const progressText = computed(() => {
  if (!durationDays.value) return "Progress is based on check-ins.";
  if (enrollment.value?.remaining_days == null) return `${durationDays.value} day challenge.`;
  return `${remainingDaysText.value} remaining`;
});

const barColor = computed(() => {
  if (checkinPercent.value >= 70) return "linear-gradient(90deg, rgba(74,222,128,0.95), rgba(110,229,255,0.95))";
  if (checkinPercent.value >= 35) return "linear-gradient(90deg, rgba(245,158,11,0.95), rgba(255,228,168,0.95))";
  return "linear-gradient(90deg, rgba(239,68,68,0.9), rgba(195,90,214,0.9))";
});

function clampPercent(value) {
  const n = Number(value || 0);
  return Math.max(0, Math.min(100, Math.round(n)));
}

function formatDate(value) {
  if (!value) return "—";

  try {
    return new Intl.DateTimeFormat("en", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

async function load() {
  loading.value = true;
  error.value = "";

  try {
    const id = route.params.id;

    const { data } = await api.get(`/me/enrollments/${id}`);
    enrollment.value = data.enrollment;
    challenge.value = data.challenge;
    recentLogs.value = data.recent_logs || [];

    const days = challenge.value?.duration_days || enrollment.value?.duration_days || 30;
    const hist = await api.get(`/me/challenges/${id}/history?days=${days}`);

    checkedDays.value = hist.data?.summary?.checked_days ?? enrollment.value?.total_checkins ?? 0;
    totalDays.value = hist.data?.summary?.total_days ?? days;
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function checkin() {
  try {
    checking.value = true;
    error.value = "";
    const id = route.params.id;

    await api.post(`/me/challenges/${id}/checkin`);
    await load();
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    checking.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.enrollmentPage {
  position: relative;
}

.heroCard {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background:
    radial-gradient(circle at 12% 18%, rgba(110, 229, 255, 0.18), transparent 34%),
    radial-gradient(circle at 88% 8%, rgba(195, 90, 214, 0.16), transparent 32%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.085), rgba(255, 255, 255, 0.025));
  box-shadow: 0 28px 90px rgba(0, 0, 0, 0.32);
}

.heroGlow {
  position: absolute;
  inset: -90px;
  background:
    linear-gradient(90deg, transparent, rgba(110, 229, 255, 0.07), transparent),
    radial-gradient(circle, rgba(255, 255, 255, 0.07), transparent 58%);
  pointer-events: none;
}

.heroContent {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: var(--s-24);
  align-items: center;
}

.heroTitle {
  margin: 0;
  color: white;
  font-size: clamp(2rem, 4vw, 4rem);
  line-height: 0.95;
  letter-spacing: -0.06em;
}

.heroDesc {
  max-width: 760px;
  margin: var(--s-16) 0 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.7;
}

.eyebrow {
  margin-bottom: 7px;
  color: rgba(110, 229, 255, 0.9);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.heroMeta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  margin-top: var(--s-20);
}

.metaPill,
.timelineBadge,
.scoreBadge,
.ctaLink {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 750;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.metaPill {
  padding: 7px 11px;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.35);
}

.dot.active {
  background: #4ade80;
  box-shadow: 0 0 18px rgba(74, 222, 128, 0.65);
}

.checkinPanel {
  padding: 18px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 20% 0%, rgba(74, 222, 128, 0.12), transparent 38%),
    rgba(0, 0, 0, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.checkinStatus {
  display: flex;
  align-items: center;
  gap: var(--s-12);
  margin-bottom: var(--s-16);
}

.statusIcon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.11);
}

.checkinStatus.done .statusIcon {
  background: rgba(74, 222, 128, 0.12);
  border-color: rgba(74, 222, 128, 0.22);
}

.statusLabel {
  color: var(--muted2);
  font-size: 0.78rem;
  font-weight: 750;
}

.statusValue {
  margin-top: 2px;
  color: white;
  font-weight: 850;
}

.insightGrid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--s-12);
}

.metricCard {
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.09), transparent 38%),
    rgba(255, 255, 255, 0.025);
}

.metricIcon {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  margin-bottom: var(--s-12);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.metricLabel {
  color: var(--muted2);
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.metricValue {
  margin-top: 5px;
  color: white;
  font-size: 1.9rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.04em;
  font-variant-numeric: tabular-nums;
}

.metricHint {
  margin-top: var(--s-8);
  color: rgba(255, 255, 255, 0.56);
  font-size: 0.82rem;
  line-height: 1.45;
}

.timelineCard,
.progressCard,
.logsCard {
  background:
    radial-gradient(circle at 0% 0%, rgba(195, 90, 214, 0.07), transparent 35%),
    rgba(255, 255, 255, 0.02);
}

.sectionHead {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--s-12);
  flex-wrap: wrap;
}

.timelineBadge {
  padding: 8px 12px;
}

.scoreBadge {
  min-width: 64px;
  justify-content: center;
  padding: 8px 12px;
  color: #4ade80;
  background: rgba(74, 222, 128, 0.10);
  border-color: rgba(74, 222, 128, 0.18);
}

.timelineBar,
.bar {
  position: relative;
  height: 13px;
  margin-top: var(--s-16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.075);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.timelineFill,
.barFill {
  height: 100%;
  border-radius: 999px;
  transition: width 220ms ease;
}

.timelineFill {
  background: linear-gradient(90deg, rgba(110, 229, 255, 0.95), rgba(195, 90, 214, 0.95));
}

.timelinePulse {
  position: absolute;
  top: 50%;
  width: 18px;
  height: 18px;
  border-radius: 999px;
  transform: translate(-50%, -50%);
  background: white;
  box-shadow:
    0 0 0 5px rgba(110, 229, 255, 0.16),
    0 0 24px rgba(110, 229, 255, 0.65);
}

.timelineMeta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
  margin-top: var(--s-16);
}

.timelineMeta > div,
.miniStat {
  padding: 12px;
  border-radius: var(--r-12);
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.timelineMeta strong,
.miniStat strong {
  display: block;
  margin-top: 3px;
  color: white;
  font-variant-numeric: tabular-nums;
}

.progressMeta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--s-12);
  flex-wrap: wrap;
  margin-top: var(--s-12);
  opacity: 0.88;
}

.miniStats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
  margin-top: var(--s-16);
}

.miniStat span {
  color: var(--muted2);
  font-size: 0.78rem;
  font-weight: 750;
}

.contentGrid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.7fr);
  gap: var(--s-16);
  align-items: start;
}

.titleWithIcon {
  display: flex;
  align-items: center;
  gap: var(--s-10);
}

.icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.ctaLink {
  padding: 9px 12px;
  text-decoration: none;
}

.ctaLink:hover {
  background: rgba(255, 255, 255, 0.08);
}

.arrow {
  opacity: 0.85;
}

.logList {
  margin: var(--s-16) 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: var(--s-8);
}

.logRow {
  display: flex;
  align-items: center;
  gap: var(--s-10);
  padding: 12px;
  border-radius: var(--r-12);
  border: 1px solid rgba(255, 255, 255, 0.075);
  background: rgba(255, 255, 255, 0.03);
}

.logDot,
.emptyIcon {
  flex: 0 0 auto;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 13px;
  background: rgba(74, 222, 128, 0.12);
  border: 1px solid rgba(74, 222, 128, 0.22);
}

.logDate {
  color: rgba(255, 255, 255, 0.90);
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.emptyLogs {
  display: flex;
  align-items: center;
  gap: var(--s-12);
  margin-top: var(--s-16);
  padding: 16px;
  border-radius: var(--r-12);
  color: var(--muted2);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.emptyLogs .emptyIcon {
  background: rgba(255, 255, 255, 0.055);
  border-color: rgba(255, 255, 255, 0.10);
}

@media (max-width: 980px) {
  .heroContent,
  .contentGrid {
    grid-template-columns: 1fr;
  }

  .insightGrid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .checkinPanel {
    max-width: none;
  }
}

@media (max-width: 640px) {
  .heroCard {
    padding: 22px;
    border-radius: 22px;
  }

  .insightGrid,
  .timelineMeta,
  .miniStats {
    grid-template-columns: 1fr;
  }

  .heroTitle {
    font-size: 2.1rem;
  }
}
</style>