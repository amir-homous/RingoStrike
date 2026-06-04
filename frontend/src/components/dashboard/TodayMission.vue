<template>
  <StartPathEmptyState
    v-if="missionState === 'empty'"
    class="missionStart"
  />

  <section
    v-else
    class="mission"
    :class="{
      complete: missionState === 'complete',
    }"
  >
    <div class="missionGlow" aria-hidden="true"></div>

    <div class="missionMain">
      <div class="missionEyebrow">
        <span class="missionDot" :class="{ secured: missionState === 'complete' }"></span>
        <span>{{ t("dashboard.mission.eyebrow") }}</span>
      </div>

      <p class="missionStep">
        {{ t("dashboard.mission.loop") }}
      </p>

      <h1 class="missionTitle">
        {{ title }}
      </h1>

      <p class="missionText">
        {{ description }}
      </p>

      <div class="missionActions">
        <BaseButton
          v-if="missionState === 'ready'"
          variant="primary"
          :loading="loading"
          @click="$emit('checkin', missionChallenge.enrollment_id)"
        >
          {{ t("dashboard.mission.secureToday") }}
        </BaseButton>

        <RouterLink
          v-else-if="missionState === 'complete' && missionChallenge?.enrollment_id"
          class="missionLink"
          :to="`/enrollment/${missionChallenge.enrollment_id}`"
        >
          <span>{{ t("dashboard.mission.viewPath") }}</span>
          <span aria-hidden="true">→</span>
        </RouterLink>

      </div>
    </div>

    <div class="missionPanel">
      <div v-if="missionChallenge" class="missionPath">
        <span>{{ t("dashboard.mission.activePath") }}</span>
        <strong>{{ challengeName }}</strong>
      </div>

      <div class="missionMetrics">
        <div class="metric">
          <span>{{ t("dashboard.mission.today") }}</span>
          <strong>{{ todayLabel }}</strong>
        </div>

        <div class="metric">
          <span>{{ t("dashboard.mission.streak") }}</span>
          <strong>{{ streakLabel }}</strong>
        </div>

        <div v-if="stats" class="metric wide">
          <span>{{ t("dashboard.mission.progress") }}</span>
          <strong>{{ levelLabel }}</strong>
          <div
            v-if="hasProgress"
            class="progressTrack"
            aria-hidden="true"
          >
            <span :style="{ width: `${progressPercent}%` }"></span>
          </div>
        </div>
      </div>

      <p class="nextStep">
        {{ nextStepText }}
      </p>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import StartPathEmptyState from "@/components/guided/StartPathEmptyState.vue";

const props = defineProps({
  challenges: { type: Array, default: () => [] },
  stats: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

defineEmits(["checkin"]);

const { t } = useI18n();

function isCheckedToday(challenge) {
  const value = challenge?.today_checked ?? challenge?.todayChecked ?? false;

  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value === 1;
  if (typeof value === "string") {
    return ["true", "1", "yes", "done", "checked"].includes(value.toLowerCase());
  }

  return false;
}

const activeChallenges = computed(() => {
  return props.challenges.filter((challenge) => {
    const status = String(challenge?.status || "active").toLowerCase();
    return status === "active" && challenge?.enrollment_id;
  });
});

const missionChallenge = computed(() => {
  const ready = activeChallenges.value.find((challenge) => !isCheckedToday(challenge));

  if (ready) return ready;

  return activeChallenges.value[0] || null;
});

const missionState = computed(() => {
  if (!missionChallenge.value) return "empty";
  return isCheckedToday(missionChallenge.value) ? "complete" : "ready";
});

const challengeName = computed(() => {
  return (
    missionChallenge.value?.enrollment_name ||
    missionChallenge.value?.challenge_name ||
    missionChallenge.value?.name ||
    t("common.challenge")
  );
});

const title = computed(() => {
  if (missionState.value === "empty") return t("dashboard.mission.emptyTitle");
  if (missionState.value === "complete") return t("dashboard.mission.completeTitle");
  return t("dashboard.mission.readyTitle", { challenge: challengeName.value });
});

const description = computed(() => {
  if (missionState.value === "empty") return t("dashboard.mission.emptyText");
  if (missionState.value === "complete") return t("dashboard.mission.completeText");
  return t("dashboard.mission.readyText");
});

const todayLabel = computed(() => {
  if (missionState.value === "empty") return t("dashboard.mission.notStarted");
  if (missionState.value === "complete") return t("dashboard.mission.secured");
  return t("dashboard.mission.ready");
});

const streakValue = computed(() => {
  return missionChallenge.value?.current_streak ?? missionChallenge.value?.currentStreak ?? props.stats?.current_streak ?? 0;
});

const streakLabel = computed(() => {
  return t("dashboard.mission.streakValue", { count: streakValue.value || 0 });
});

const levelLabel = computed(() => {
  return t("dashboard.mission.levelValue", {
    level: props.stats?.level || 1,
    xp: props.stats?.total_points ?? props.stats?.xp ?? 0,
  });
});

const progressPercent = computed(() => {
  const value = Number(props.stats?.progress_percent);

  if (!Number.isFinite(value)) return 0;

  return Math.min(100, Math.max(0, value));
});

const hasProgress = computed(() => {
  return Object.prototype.hasOwnProperty.call(props.stats || {}, "progress_percent");
});

const nextStepText = computed(() => {
  if (missionState.value === "empty") return t("dashboard.mission.emptyNext");
  if (missionState.value === "complete") return t("dashboard.mission.comeBackTomorrow");
  return t("dashboard.mission.readyNext");
});
</script>

<style scoped>
.mission {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.75fr);
  gap: var(--s-20);
  align-items: stretch;
  padding: 26px;
  border-radius: 30px;
  background:
    radial-gradient(circle at 10% 0%, rgba(110, 229, 255, 0.18), transparent 35%),
    radial-gradient(circle at 90% 12%, rgba(195, 90, 214, 0.14), transparent 34%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.025));
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.26);
}

.mission.complete {
  background:
    radial-gradient(circle at 10% 0%, rgba(74, 222, 128, 0.15), transparent 35%),
    radial-gradient(circle at 90% 12%, rgba(110, 229, 255, 0.09), transparent 34%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.022));
}

.missionGlow {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.missionMain,
.missionPanel {
  position: relative;
  z-index: 1;
}

.missionEyebrow,
.missionStep {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px;
  color: rgba(110, 229, 255, 0.88);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.missionStep {
  display: block;
  color: rgba(255, 255, 255, 0.50);
  letter-spacing: 0;
  text-transform: none;
}

.missionDot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #67e8f9;
  box-shadow: 0 0 18px rgba(103, 232, 249, 0.72);
}

.missionDot.secured {
  background: #4ade80;
  box-shadow: 0 0 18px rgba(74, 222, 128, 0.68);
}

.missionTitle {
  max-width: 820px;
  margin: 0;
  color: rgba(255, 255, 255, 0.98);
  font-size: clamp(2rem, 5vw, 4.7rem);
  line-height: 0.97;
}

.missionText {
  max-width: 660px;
  margin: 16px 0 0;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.7;
}

.missionActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-12);
  margin-top: 22px;
}

.missionLink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--s-8);
  min-height: 42px;
  padding: 0 var(--s-16);
  border-radius: var(--r-10);
  color: rgba(255, 255, 255, 0.92);
  text-decoration: none;
  font-weight: 750;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.11);
}

.missionLink.primary {
  background: rgba(99, 102, 241, 0.26);
  border-color: rgba(99, 102, 241, 0.45);
}

.missionPanel {
  display: grid;
  align-content: space-between;
  gap: var(--s-16);
  padding: 18px;
  border-radius: 24px;
  background: rgba(5, 5, 8, 0.34);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.missionPath {
  display: grid;
  gap: 6px;
}

.missionPath span,
.metric span {
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.missionPath strong {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.08rem;
}

.missionMetrics {
  display: grid;
  gap: var(--s-12);
}

.metric {
  display: grid;
  gap: 7px;
  min-height: 72px;
  padding: 13px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.metric strong {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1rem;
}

.progressTrack {
  overflow: hidden;
  height: 7px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.10);
}

.progressTrack span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #67e8f9, #a78bfa);
}

.nextStep {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

@media (max-width: 920px) {
  .mission {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  .mission {
    padding: 18px;
    border-radius: 24px;
  }

  .missionActions,
  .missionLink {
    width: 100%;
  }

  .missionTitle {
    font-size: clamp(2rem, 13vw, 3.15rem);
  }
}
</style>
