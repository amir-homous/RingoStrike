<template>
  <AppContainer>
    <AppHeader />

    <div class="enrollmentPage">
      <UiState
        :loading="loading"
        :error="!!error"
        :empty="!loading && !error && !enrollment"
        :loading-title="t('enrollment.loadingTitle')"
        :loading-text="t('enrollment.loadingText')"
        :empty-title="t('enrollment.emptyTitle')"
        :empty-text="t('enrollment.emptyText')"
        :error-title="t('enrollment.errorTitle')"
        :error-text="error || t('common.pleaseTryAgain')"
        @retry="load"
      />

      <div v-if="!loading && !error && enrollment" class="stack-16">
        <section class="heroCard">
          <div class="heroGlow"></div>

          <div class="heroContent">
            <div class="heroMain">
              <div class="eyebrow">
                <span class="pulseDot"></span>
                {{ t("enrollment.guidedEyebrow") }}
              </div>

              <h1 class="heroTitle">
                {{ challenge?.name || enrollment.name || t("common.challenge") }}
              </h1>

              <p v-if="challenge?.description" class="heroDesc">
                {{ challenge.description }}
              </p>

              <p class="missionInstruction">
                {{ enrollment.today_checked ? t("enrollment.missionCompleteInstruction") : t("enrollment.missionReadyInstruction") }}
              </p>

              <div class="missionStepper" :aria-label="t('enrollment.stepperLabel')">
                <div
                  v-for="stepItem in missionSteps"
                  :key="stepItem.key"
                  class="stepItem"
                  :class="stepItem.state"
                >
                  <span class="stepMarker" aria-hidden="true"></span>
                  <span>{{ stepItem.label }}</span>
                </div>
              </div>

              <div class="heroMeta">
                <span class="metaPill">
                  <span class="dot" :class="{ active: enrollment.status === 'Active' }"></span>
                  {{ displayStatus(enrollment.status) }}
                </span>

                <span v-if="durationDays" class="metaPill">
                  {{ t("common.dayChallenge", { count: durationDays }) }}
                </span>

                <span v-if="enrollment.start_date" class="metaPill">
                  {{ t("enrollment.started", { date: formatDate(enrollment.start_date) }) }}
                </span>

                <span v-if="enrollment.reset_timezone" class="metaPill">
                  {{ t("enrollment.reset", { timezone: enrollment.reset_timezone }) }}
                </span>
              </div>
            </div>

            <div class="checkinPanel">
              <div class="checkinStatus" :class="{ done: enrollment.today_checked }">
                <div class="statusIcon">
                  {{ enrollment.today_checked ? "✅" : "⚡" }}
                </div>

                <div>
                  <div class="statusLabel">{{ t("enrollment.todaysStrike") }}</div>
                  <div class="statusValue">
                    {{ enrollment.today_checked ? t("enrollment.completed") : t("enrollment.readySecure") }}
                  </div>
                </div>
              </div>

              <BaseButton
                class="missionCheckin"
                variant="primary"
                :loading="checking"
                :disabled="enrollment.today_checked"
                @click="checkin"
              >
                <span v-if="enrollment.today_checked">{{ t("enrollment.doneToday") }}</span>
                <span v-else>{{ t("enrollment.checkinNow") }}</span>
              </BaseButton>

              <div class="checkinHint">
                {{ enrollment.today_checked ? t("enrollment.protected") : resetHint }}
              </div>
            </div>
          </div>
        </section>

        <section class="dailySummary">
          <div class="summaryItem">
            <span class="summaryLabel">{{ t("enrollment.today") }}</span>
            <strong>{{ enrollment.today_checked ? t("enrollment.secured") : t("common.pending") }}</strong>
          </div>

          <div class="summaryItem">
            <span class="summaryLabel">{{ t("enrollment.streak") }}</span>
            <strong>{{ currentStreak }}</strong>
          </div>

          <div class="summaryItem">
            <span class="summaryLabel">{{ t("enrollment.progress") }}</span>
            <strong>{{ checkinPercent }}%</strong>
          </div>

          <div class="summaryItem">
            <span class="summaryLabel">{{ t("enrollment.resetWindow") }}</span>
            <strong>{{ resetBadgeText }}</strong>
          </div>
        </section>

        <section class="advancedDetails" :class="{ guided: isEarlyEnrollment }">
          <div class="advancedIntro">
            <div>
              <div class="eyebrow compact">{{ t("enrollment.advancedEyebrow") }}</div>
              <h2 class="h2">{{ t("enrollment.advancedTitle") }}</h2>
            </div>

            <p>{{ t("enrollment.advancedText") }}</p>
          </div>

          <section class="insightGrid">
            <BaseCard class="metricCard" :padded="true">
              <div class="metricIcon">⏳</div>
              <div class="metricLabel">{{ t("enrollment.remaining") }}</div>
              <div class="metricValue">{{ remainingDaysText }}</div>
              <div class="metricHint">{{ timingHint }}</div>
            </BaseCard>

            <BaseCard class="metricCard resetMetric" :class="resetUrgencyClass" :padded="true">
              <div class="metricIcon">🌗</div>
              <div class="metricLabel">{{ t("enrollment.dailyReset") }}</div>
              <div class="metricValue resetValue">{{ resetCountdownText }}</div>
              <div class="metricHint">{{ resetHint }}</div>
            </BaseCard>

            <BaseCard class="metricCard" :padded="true">
              <div class="metricIcon">✅</div>
              <div class="metricLabel">{{ t("enrollment.totalCheckins") }}</div>
              <div class="metricValue">{{ totalCheckins }}</div>
              <div class="metricHint">{{ t("enrollment.completedStrikes") }}</div>
            </BaseCard>

            <BaseCard class="metricCard" :padded="true">
              <div class="metricIcon">🔥</div>
              <div class="metricLabel">{{ t("enrollment.currentStreak") }}</div>
              <div class="metricValue">{{ currentStreak }}</div>
              <div class="metricHint">{{ t("enrollment.momentumChain") }}</div>
            </BaseCard>
          </section>

          <BaseCard class="resetCard" :class="resetUrgencyClass" :padded="true">
            <div class="sectionHead">
              <div>
                <div class="eyebrow">{{ t("enrollment.resetWindowEyebrow") }}</div>
                <h2 class="h2">{{ t("enrollment.resetRhythm") }}</h2>
                <div class="caption">
                  {{ t("enrollment.resetCaption") }}
                </div>
              </div>

              <div class="resetBadge">
                {{ resetBadgeText }}
              </div>
            </div>

            <div class="resetGrid">
              <div class="resetInfoBox">
                <span class="resetIcon">⏱</span>
                <div>
                  <div class="caption">{{ t("enrollment.timeUntilReset") }}</div>
                  <strong>{{ resetCountdownText }}</strong>
                </div>
              </div>

              <div class="resetInfoBox">
                <span class="resetIcon">📍</span>
                <div>
                  <div class="caption">{{ t("enrollment.nextReset") }}</div>
                  <strong>{{ formattedNextReset }}</strong>
                </div>
              </div>

              <div class="resetInfoBox">
                <span class="resetIcon">🌍</span>
                <div>
                  <div class="caption">{{ t("enrollment.timezone") }}</div>
                  <strong>{{ enrollment.reset_timezone || "UTC" }}</strong>
                </div>
              </div>
            </div>

            <div class="futureNote">
              <span class="futureIcon">🔔</span>
              <span>
                {{ t("enrollment.futureNote") }}
              </span>
            </div>
          </BaseCard>

          <BaseCard class="timelineCard" :padded="true">
            <div class="sectionHead">
              <div>
                <div class="eyebrow">{{ t("enrollment.timeline") }}</div>
                <h2 class="h2">{{ t("enrollment.timeMomentum") }}</h2>
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
                <div class="caption">{{ t("enrollment.start") }}</div>
                <strong>{{ enrollment.start_date ? formatDate(enrollment.start_date) : "—" }}</strong>
              </div>

              <div>
                <div class="caption">{{ t("enrollment.end") }}</div>
                <strong>{{ enrollment.end_date ? formatDate(enrollment.end_date) : "—" }}</strong>
              </div>

              <div>
                <div class="caption">{{ t("enrollment.checked") }}</div>
                <strong>{{ t("enrollment.checkedDays", { checked: checkedDays, total: totalDays }) }}</strong>
              </div>
            </div>
          </BaseCard>

          <BaseCard class="progressCard" :padded="true">
            <div class="sectionHead">
              <div>
                <div class="eyebrow">{{ t("enrollment.personalProgress") }}</div>
                <h2 class="h2">{{ t("enrollment.consistencyScore") }}</h2>
              </div>

              <div class="scoreBadge">
                {{ checkinPercent }}%
              </div>
            </div>

            <div class="progressMeta">
              <span>{{ t("enrollment.checkedDaysLabel", { count: checkedDays }) }}</span>
              <span class="caption">{{ t("enrollment.totalDaysLabel", { count: totalDays }) }}</span>
            </div>

            <div class="bar">
              <div class="barFill" :style="{ width: checkinPercent + '%', background: barColor }"></div>
            </div>

            <div class="miniStats">
              <div class="miniStat">
                <span>{{ t("enrollment.today") }}</span>
                <strong>{{ enrollment.today_checked ? t("common.done") : t("common.pending") }}</strong>
              </div>

              <div class="miniStat">
                <span>{{ t("enrollment.remaining") }}</span>
                <strong>{{ remainingDaysText }}</strong>
              </div>

              <div class="miniStat">
                <span>{{ t("enrollment.nextResetShort") }}</span>
                <strong>{{ resetCountdownText }}</strong>
              </div>
            </div>
          </BaseCard>

          <section class="contentGrid">
            <div class="stack-12">
              <div class="sectionHead">
                <div class="titleWithIcon">
                  <span class="icon" aria-hidden="true">🏆</span>
                  <div>
                    <h2 class="h2">{{ t("leaderboard.title") }}</h2>
                    <div class="caption">{{ t("enrollment.leaderboardCaption") }}</div>
                  </div>
                </div>

                <router-link class="ctaLink" :to="`/enrollment/${enrollment.enrollment_id}/leaderboard`">
                  {{ t("enrollment.viewFull") }}
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
                    <h2 class="h2">{{ t("enrollment.recentLogs") }}</h2>
                    <div class="caption">{{ t("enrollment.recentLogsCaption") }}</div>
                  </div>
                </div>
              </div>

              <div v-if="recentLogs.length === 0" class="emptyLogs">
                <div class="emptyIcon">🌙</div>
                <div>
                  <strong>{{ t("enrollment.noLogs") }}</strong>
                  <div class="caption">{{ t("enrollment.logsHint") }}</div>
                </div>
              </div>

              <template v-else>
                <ul class="logList">
                  <li v-for="log in visibleLogs" :key="log.daily_log_id" class="logRow">
                    <span class="logDot" aria-hidden="true">✅</span>
                    <div>
                      <div class="logDate">{{ formatDate(log.date) }}</div>
                      <div class="caption">{{ t("enrollment.checkinCompleted") }}</div>
                    </div>
                  </li>
                </ul>

                <button
                  v-if="recentLogs.length > logLimit"
                  type="button"
                  class="showMoreLogs"
                  @click="showAllLogs = !showAllLogs"
                >
                  {{ showAllLogs ? t("enrollment.showFewerLogs") : t("enrollment.showMoreLogs", { count: recentLogs.length - logLimit }) }}
                </button>
              </template>
            </BaseCard>
          </section>
        </section>
      </div>
    </div>

    <RewardMoment
      :open="!!rewardMoment"
      :reward="rewardMoment"
      @close="rewardMoment = null"
    />
  </AppContainer>
</template>

<script setup>
import Leaderboard from "./Leaderboard.vue";

import { onMounted, onUnmounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";
import RewardMoment from "@/components/feedback/RewardMoment.vue";
import { getNewlyUnlockedGuidedFeatures } from "@/lib/guidedExperience";

const route = useRoute();
const { locale, t } = useI18n();

const loading = ref(true);
const checking = ref(false);
const error = ref("");

const enrollment = ref(null);
const challenge = ref(null);
const recentLogs = ref([]);
const rewardMoment = ref(null);

const checkedDays = ref(0);
const totalDays = ref(0);
const now = ref(new Date());
const showAllLogs = ref(false);

const logLimit = 6;

let resetTimer = null;

const visibleLogs = computed(() => {
  if (showAllLogs.value) return recentLogs.value;
  return recentLogs.value.slice(0, logLimit);
});

const durationDays = computed(() => {
  return Number(challenge.value?.duration_days || enrollment.value?.duration_days || totalDays.value || 0);
});

const totalCheckins = computed(() => {
  const value = enrollment.value?.total_checkins ?? enrollment.value?.totalCheckins ?? null;
  if (value != null) return value;
  return checkedDays.value;
});

const totalCheckinNumber = computed(() => {
  const number = Number(totalCheckins.value);
  return Number.isFinite(number) ? Math.max(0, Math.floor(number)) : 0;
});

const isEarlyEnrollment = computed(() => {
  return totalCheckinNumber.value < 3;
});

const currentStreak = computed(() => {
  const value = enrollment.value?.current_streak ?? enrollment.value?.currentStreak ?? null;
  if (value != null) return value;
  return "—";
});

const missionSteps = computed(() => {
  const todayState = enrollment.value?.today_checked ? "complete" : "active";
  const rewardState = enrollment.value?.today_checked ? "complete" : "upcoming";

  return [
    {
      key: "path",
      label: t("enrollment.steps.path"),
      state: "complete",
    },
    {
      key: "today",
      label: t("enrollment.steps.today"),
      state: todayState,
    },
    {
      key: "reward",
      label: t("enrollment.steps.reward"),
      state: rewardState,
    },
  ];
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
  if (value <= 0) return t("enrollment.ended");
  return `${value}d`;
});

const timingHint = computed(() => {
  if (!enrollment.value?.end_date) return t("enrollment.timingMissing");
  if ((enrollment.value?.remaining_days ?? 0) <= 0) return t("enrollment.timelineEnded");
  return t("enrollment.ends", { date: formatDate(enrollment.value.end_date) });
});

const progressText = computed(() => {
  if (!durationDays.value) return t("enrollment.checkinBased");
  if (enrollment.value?.remaining_days == null) return t("common.dayChallenge", { count: durationDays.value });
  return t("enrollment.remainingText", { value: remainingDaysText.value });
});

const nextResetDate = computed(() => {
  if (!enrollment.value?.next_reset_at) return null;

  const date = new Date(enrollment.value.next_reset_at);
  if (Number.isNaN(date.getTime())) return null;

  return date;
});

const resetMsRemaining = computed(() => {
  if (!nextResetDate.value) return null;
  return Math.max(0, nextResetDate.value.getTime() - now.value.getTime());
});

const resetHoursRemaining = computed(() => {
  if (resetMsRemaining.value == null) return null;
  return resetMsRemaining.value / 1000 / 60 / 60;
});

const resetCountdownText = computed(() => {
  if (resetMsRemaining.value == null) return "—";

  const totalMinutes = Math.max(0, Math.floor(resetMsRemaining.value / 1000 / 60));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours <= 0 && minutes <= 0) return t("enrollment.resettingSoon");
  if (hours <= 0) return `${minutes}m`;
  return `${hours}h ${minutes}m`;
});

const resetUrgencyClass = computed(() => {
  if (enrollment.value?.today_checked) return "reset-secure";
  if (resetHoursRemaining.value == null) return "reset-neutral";
  if (resetHoursRemaining.value <= 2) return "reset-urgent";
  if (resetHoursRemaining.value <= 6) return "reset-warning";
  return "reset-calm";
});

const resetBadgeText = computed(() => {
  if (enrollment.value?.today_checked) return t("enrollment.todaySecured");
  if (resetHoursRemaining.value == null) return t("enrollment.resetUnknown");
  if (resetHoursRemaining.value <= 2) return t("enrollment.finalWindow");
  if (resetHoursRemaining.value <= 6) return t("enrollment.resetApproaching");
  return t("enrollment.openWindow");
});

const resetHint = computed(() => {
  if (!nextResetDate.value) return t("enrollment.resetMissing");
  if (enrollment.value?.today_checked) return t("enrollment.strikeSecured");
  if (resetHoursRemaining.value <= 2) return t("enrollment.windowClosing");
  if (resetHoursRemaining.value <= 6) return t("enrollment.goodTime");
  return t("enrollment.utcReset");
});

const formattedNextReset = computed(() => {
  if (!nextResetDate.value) return "—";

  return new Intl.DateTimeFormat(locale.value, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    timeZoneName: "short",
  }).format(nextResetDate.value);
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
    return new Intl.DateTimeFormat(locale.value, {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function displayStatus(value) {
  const raw = String(value || "").trim();
  if (!raw) return t("common.unknown");

  const key = raw.toLowerCase();
  return t(`common.status.${key}`, raw);
}

function buildRewardMomentPayload(rewards, oldStats, newStats) {
  const xpTotal = Number(rewards?.xp_total);
  const oldTotal = Number(oldStats?.total_points ?? oldStats?.xp);
  const xpEarned = Number.isFinite(xpTotal) && Number.isFinite(oldTotal)
    ? Math.max(0, xpTotal - oldTotal)
    : 0;
  const unlocked = Array.isArray(rewards?.achievements) ? rewards.achievements : [];

  if (xpEarned <= 0 && unlocked.length === 0) return null;

  return {
    xpEarned,
    xpTotal: Number.isFinite(xpTotal) ? xpTotal : null,
    achievements: unlocked,
    unlockedFeatures: getNewlyUnlockedGuidedFeatures({
      oldStats,
      newStats,
    }).map((featureKey) => ({
      key: featureKey,
      to: featureKey === "publicProfile" ? "/profile" : "/dashboard",
    })),
    streak: enrollment.value?.current_streak ?? null,
  };
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
  if (enrollment.value?.today_checked) return;

  try {
    checking.value = true;
    error.value = "";
    const id = route.params.id;
    const statsResp = await api.get("/me/stats").catch(() => null);
    const oldStats = statsResp?.data?.stats || null;

    const { data } = await api.post(`/me/challenges/${id}/checkin`);
    const newStatsResp = await api.get("/me/stats").catch(() => null);
    const newStats = newStatsResp?.data?.stats || null;
    await load();

    rewardMoment.value = buildRewardMomentPayload(data?.rewards, oldStats, newStats);
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    checking.value = false;
  }
}

onMounted(() => {
  load();

  resetTimer = window.setInterval(() => {
    now.value = new Date();
  }, 30000);
});

onUnmounted(() => {
  if (resetTimer) {
    window.clearInterval(resetTimer);
  }
});
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
  letter-spacing: 0;
}

.heroDesc {
  max-width: 760px;
  margin: var(--s-16) 0 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.7;
}

.missionInstruction {
  max-width: 720px;
  margin: var(--s-16) 0 0;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(253, 230, 138, 0.18);
  background: rgba(253, 230, 138, 0.065);
  color: rgba(255, 255, 255, 0.76);
  line-height: 1.65;
}

.missionStepper {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: var(--s-20);
}

.stepItem {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(255, 255, 255, 0.045);
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.78rem;
  font-weight: 800;
}

.stepMarker {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.28);
}

.stepItem.complete {
  border-color: rgba(74, 222, 128, 0.22);
  background: rgba(74, 222, 128, 0.075);
  color: rgba(255, 255, 255, 0.78);
}

.stepItem.complete .stepMarker {
  background: #86efac;
  box-shadow: 0 0 16px rgba(134, 239, 172, 0.42);
}

.stepItem.active {
  border-color: rgba(253, 230, 138, 0.26);
  background: rgba(253, 230, 138, 0.085);
  color: rgba(255, 255, 255, 0.88);
}

.stepItem.active .stepMarker {
  background: #fde68a;
  box-shadow: 0 0 18px rgba(253, 230, 138, 0.46);
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 7px;
  color: rgba(110, 229, 255, 0.9);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.pulseDot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #4ade80;
  box-shadow: 0 0 16px rgba(74, 222, 128, 0.7);
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
.ctaLink,
.resetBadge {
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

.checkinHint {
  margin-top: var(--s-12);
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.82rem;
  line-height: 1.45;
}

:deep(.missionCheckin) {
  width: 100%;
  min-height: 56px;
  border-color: rgba(253, 230, 138, 0.44);
  background:
    linear-gradient(135deg, rgba(253, 230, 138, 0.24), rgba(99, 102, 241, 0.24)),
    rgba(99, 102, 241, 0.22);
  box-shadow: 0 16px 42px rgba(99, 102, 241, 0.20);
  font-size: 1rem;
  font-weight: 850;
}

:deep(.missionCheckin:hover) {
  background:
    linear-gradient(135deg, rgba(253, 230, 138, 0.30), rgba(99, 102, 241, 0.30)),
    rgba(99, 102, 241, 0.28);
}

.dailySummary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--s-12);
}

.summaryItem {
  padding: 14px;
  border-radius: 18px;
  background:
    radial-gradient(circle at 100% 0%, rgba(110, 229, 255, 0.065), transparent 36%),
    rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.summaryLabel {
  display: block;
  color: var(--muted2);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.summaryItem strong {
  display: block;
  margin-top: 7px;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1rem;
}

.advancedDetails {
  display: grid;
  gap: var(--s-16);
  margin-top: var(--s-8);
}

.advancedDetails.guided {
  padding-top: var(--s-8);
  opacity: 0.82;
}

.advancedIntro {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: var(--s-16);
  padding: 16px 2px 0;
}

.advancedIntro p {
  max-width: 560px;
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.6;
}

.advancedDetails.guided .insightGrid,
.advancedDetails.guided .resetCard,
.advancedDetails.guided .timelineCard,
.advancedDetails.guided .progressCard,
.advancedDetails.guided .contentGrid {
  filter: saturate(0.9);
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

.metricCard.reset-secure {
  border-color: rgba(74, 222, 128, 0.22);
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.12), transparent 38%),
    rgba(255, 255, 255, 0.025);
}

.metricCard.reset-warning {
  border-color: rgba(255, 228, 168, 0.26);
  background:
    radial-gradient(circle at 0% 0%, rgba(255, 228, 168, 0.14), transparent 38%),
    rgba(255, 255, 255, 0.025);
}

.metricCard.reset-urgent {
  border-color: rgba(239, 68, 68, 0.26);
  background:
    radial-gradient(circle at 0% 0%, rgba(239, 68, 68, 0.14), transparent 38%),
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

.resetValue {
  font-size: 1.55rem;
}

.metricHint {
  margin-top: var(--s-8);
  color: rgba(255, 255, 255, 0.56);
  font-size: 0.82rem;
  line-height: 1.45;
}

.timelineCard,
.progressCard,
.logsCard,
.resetCard {
  background:
    radial-gradient(circle at 0% 0%, rgba(195, 90, 214, 0.07), transparent 35%),
    rgba(255, 255, 255, 0.02);
}

.resetCard.reset-secure {
  border-color: rgba(74, 222, 128, 0.20);
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.10), transparent 35%),
    rgba(255, 255, 255, 0.02);
}

.resetCard.reset-warning {
  border-color: rgba(255, 228, 168, 0.22);
  background:
    radial-gradient(circle at 0% 0%, rgba(255, 228, 168, 0.11), transparent 35%),
    rgba(255, 255, 255, 0.02);
}

.resetCard.reset-urgent {
  border-color: rgba(239, 68, 68, 0.22);
  background:
    radial-gradient(circle at 0% 0%, rgba(239, 68, 68, 0.11), transparent 35%),
    rgba(255, 255, 255, 0.02);
}

.resetBadge {
  padding: 8px 12px;
}

.reset-secure .resetBadge {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.10);
  border-color: rgba(74, 222, 128, 0.18);
}

.reset-warning .resetBadge {
  color: rgba(255, 228, 168, 0.95);
  background: rgba(255, 228, 168, 0.10);
  border-color: rgba(255, 228, 168, 0.18);
}

.reset-urgent .resetBadge {
  color: rgba(255, 150, 150, 0.98);
  background: rgba(239, 68, 68, 0.10);
  border-color: rgba(239, 68, 68, 0.18);
}

.resetGrid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
  margin-top: var(--s-16);
}

.resetInfoBox {
  display: flex;
  align-items: center;
  gap: var(--s-12);
  padding: 13px;
  border-radius: var(--r-12);
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.resetIcon {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.09);
}

.resetInfoBox strong {
  display: block;
  margin-top: 3px;
  color: white;
  font-variant-numeric: tabular-nums;
}

.futureNote {
  display: flex;
  align-items: center;
  gap: var(--s-10);
  margin-top: var(--s-16);
  padding: 13px;
  border-radius: var(--r-12);
  color: rgba(255, 255, 255, 0.62);
  background: rgba(255, 255, 255, 0.028);
  border: 1px dashed rgba(255, 255, 255, 0.10);
  font-size: 0.84rem;
  line-height: 1.5;
}

.futureIcon {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.055);
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
  margin-inline-end: 10px;
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
  margin-inline-end: 10px;
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

.showMoreLogs {
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

.showMoreLogs:hover {
  background: rgba(255, 255, 255, 0.065);
  border-color: rgba(110, 229, 255, 0.25);
}

@media (max-width: 980px) {
  .heroContent,
  .contentGrid {
    grid-template-columns: 1fr;
  }

  .insightGrid,
  .dailySummary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .advancedIntro {
    align-items: start;
    flex-direction: column;
  }

  .resetGrid {
    grid-template-columns: 1fr;
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
  .dailySummary,
  .timelineMeta,
  .miniStats {
    grid-template-columns: 1fr;
  }

  .heroTitle {
    font-size: 2.1rem;
  }

  .missionStepper,
  .stepItem {
    width: 100%;
  }

  .checkinPanel {
    padding: 16px;
  }
}
</style>
