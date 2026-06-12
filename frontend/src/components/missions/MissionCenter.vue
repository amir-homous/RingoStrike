<template>
  <section class="missionCenter">
    <RingoRewardSequence
      :steps="rewardSequenceSteps"
      :sprite="rewardSequenceSprite"
      @finish="finishRewardSequence"
    />

    <RingoCoach
      v-if="showCoach"
      :message="coachMessage"
      :sprite="guidanceRingo?.sprite_key || guidanceRingo?.mood || localizedRingo?.sprite_key || localizedRingo?.sprite"
      :primary-action="coachPrimaryAction"
      :secondary-action="coachSecondaryAction"
      @action="handleCoachAction"
    />

    <BaseCard
      v-if="coachActionPanel"
      class="coachActionPanel"
      :class="{ complete: !!todaySavedLabel }"
    >
      <div
        v-if="focusMission"
        :id="`mission-${focusMission.mission_id}`"
        class="focusMission coachFocusMission"
      >
        <span>{{ t("missions.ringoSuggestedMission") }}</span>
        <div
          v-if="focusMissionIntensity"
          class="missionIntensity"
          :class="focusMissionIntensity.intensity"
        >
          <span>{{ focusMissionIntensity.label }}</span>
          <small v-if="focusMissionIntensity.detail">{{ focusMissionIntensity.detail }}</small>
        </div>
        <strong>{{ focusMission.title }}</strong>
        <p>{{ focusMission.description }}</p>
        <div v-if="!isTodaySaved" class="missionActions primaryMissionActions">
          <BaseButton
            variant="primary"
            :loading="busyId === focusMission.mission_id && busyAction === 'done'"
            :disabled="focusMission.status === 'done'"
            @click="markDone(focusMission)"
          >
            {{ t("missions.doneCta") }}
          </BaseButton>

          <BaseButton
            variant="secondary"
            :loading="busyId === focusMission.mission_id && busyAction === 'remind'"
            :disabled="focusMission.status === 'done' || focusMission.status === 'remind_later'"
            @click="remindLater(focusMission)"
          >
            {{ focusMission.status === "remind_later" ? t("missions.reminderSet") : t("missions.remindLater") }}
          </BaseButton>

          <BaseButton
            variant="secondary"
            :loading="busyId === focusMission.mission_id && busyAction === 'skip'"
            :disabled="focusMission.status === 'done' || focusMission.status === 'skipped'"
            @click="skipMission(focusMission)"
          >
            {{ focusMission.status === "skipped" ? t("missions.skipped") : t("missions.skip") }}
          </BaseButton>
        </div>

        <div v-if="isReminderPanelOpen(focusMission)" class="remindOptionsPanel">
          <p>{{ t("missions.remindOptions.prompt") }}</p>
          <div class="remindOptions">
            <BaseButton
              v-for="option in reminderOptions"
              :key="option.key"
              variant="secondary"
              :loading="isReminderOptionLoading(focusMission, option.key)"
              :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
              @click="selectReminderOption(focusMission, option)"
            >
              {{ option.label }}
            </BaseButton>
          </div>
        </div>

        <div v-if="isSkipReasonPanelOpen(focusMission)" class="skipReasonPanel">
          <p>{{ t("missions.skipReasons.prompt") }}</p>
          <div class="skipReasons">
            <BaseButton
              v-for="reason in skipReasonOptions"
              :key="reason.key"
              variant="secondary"
              :loading="isSkipReasonLoading(focusMission, reason.key)"
              :disabled="busyAction === 'skip' && busyId === focusMission.mission_id"
              @click="selectSkipReason(focusMission, reason)"
            >
              {{ reason.label }}
            </BaseButton>
          </div>
        </div>
      </div>

      <p v-if="todaySavedLabel" class="todaySaved">
        <strong>{{ todaySavedLabel }}</strong>
        <span>{{ t("missions.todaySavedBody") }}</span>
      </p>

      <p v-if="ringoActionMessage" class="ringoActionHint">
        {{ ringoActionMessage }}
      </p>

      <div v-if="isTodaySaved" class="completedChoices">
        <RouterLink
          v-if="focusMission?.enrollment_id"
          class="missionGuideLink"
          :to="`/enrollment/${focusMission.enrollment_id}`"
        >
          {{ t("missions.detailsCta") }}
        </RouterLink>

        <BaseButton
          v-if="otherMissions.length"
          variant="secondary"
          @click="showOtherMissions = true"
        >
          {{ t("missions.showOtherMissions", { count: otherMissions.length }) }}
        </BaseButton>

        <BaseButton variant="secondary" @click="finishForToday">
          {{ t("missions.finishForToday") }}
        </BaseButton>
      </div>

      <div v-if="guidanceActions.length" class="ringoActionChoices" :aria-label="t('missions.ringoActions.label')">
        <BaseButton
          v-for="action in guidanceActions"
          :key="action.type"
          :variant="action.type === 'start' ? 'primary' : 'secondary'"
          :loading="isGuidanceActionLoading(action)"
          :disabled="isGuidanceActionDisabled(action)"
          @click="handleGuidanceAction(action)"
        >
          {{ guidanceActionLabel(action) }}
        </BaseButton>
      </div>
    </BaseCard>

    <UiState
      :loading="loading"
      :error="!!error"
      :empty="false"
      :loading-title="t('missions.loadingTitle')"
      :loading-text="t('missions.loadingText')"
      :error-title="t('missions.errorTitle')"
      :error-text="error || t('common.pleaseTryAgain')"
      @retry="loadMissions"
    />

    <p v-if="notice" class="missionNotice" :class="noticeType">
      {{ notice }}
    </p>

    <PathSelection
      v-if="!loading && !error && showPathSelection"
      :allow-active-start="ringo?.state === 'path_selected_no_challenge'"
      @started="loadMissions"
    />

    <BaseCard
      v-if="missionGuide"
      class="missionGuide"
      :class="[missionGuide.state, { complete: missionGuide.complete }]"
    >
      <div class="missionGuideCopy">
        <p class="eyebrow compact">{{ t("missions.guideEyebrow") }}</p>
        <h2>{{ missionGuide.title }}</h2>
        <p>{{ missionGuide.body }}</p>
      </div>

      <div class="missionStepper" :aria-label="t('missions.stepperLabel')">
        <span class="step complete">{{ t("missions.steps.path") }}</span>
        <span class="step" :class="{ complete: missionGuide.complete, active: !missionGuide.complete }">
          {{ t("missions.steps.mission") }}
        </span>
        <span class="step" :class="{ complete: missionGuide.complete }">
          {{ t("missions.steps.reward") }}
        </span>
      </div>

      <div
        v-if="focusMission && !coachActionPanel"
        :id="`mission-${focusMission.mission_id}`"
        class="focusMission"
      >
        <span>{{ guidanceMission ? t("missions.ringoSuggestedMission") : t("missions.nextMission") }}</span>
        <div
          v-if="focusMissionIntensity"
          class="missionIntensity"
          :class="focusMissionIntensity.intensity"
        >
          <span>{{ focusMissionIntensity.label }}</span>
          <small v-if="focusMissionIntensity.detail">{{ focusMissionIntensity.detail }}</small>
        </div>
        <strong>{{ focusMission.title }}</strong>
        <p>{{ focusMission.description }}</p>
        <div v-if="!isTodaySaved" class="missionActions primaryMissionActions">
          <BaseButton
            variant="primary"
            :loading="busyId === focusMission.mission_id && busyAction === 'done'"
            :disabled="focusMission.status === 'done'"
            @click="markDone(focusMission)"
          >
            {{ t("missions.doneCta") }}
          </BaseButton>

          <BaseButton
            variant="secondary"
            :loading="busyId === focusMission.mission_id && busyAction === 'remind'"
            :disabled="focusMission.status === 'done' || focusMission.status === 'remind_later'"
            @click="remindLater(focusMission)"
          >
            {{ focusMission.status === "remind_later" ? t("missions.reminderSet") : t("missions.remindLater") }}
          </BaseButton>

          <BaseButton
            variant="secondary"
            :loading="busyId === focusMission.mission_id && busyAction === 'skip'"
            :disabled="focusMission.status === 'done' || focusMission.status === 'skipped'"
            @click="skipMission(focusMission)"
          >
            {{ focusMission.status === "skipped" ? t("missions.skipped") : t("missions.skip") }}
          </BaseButton>
        </div>

        <div v-if="isReminderPanelOpen(focusMission)" class="remindOptionsPanel">
          <p>{{ t("missions.remindOptions.prompt") }}</p>
          <div class="remindOptions">
            <BaseButton
              v-for="option in reminderOptions"
              :key="option.key"
              variant="secondary"
              :loading="isReminderOptionLoading(focusMission, option.key)"
              :disabled="busyAction === 'remind' && busyId === focusMission.mission_id"
              @click="selectReminderOption(focusMission, option)"
            >
              {{ option.label }}
            </BaseButton>
          </div>
        </div>

        <div v-if="isSkipReasonPanelOpen(focusMission)" class="skipReasonPanel">
          <p>{{ t("missions.skipReasons.prompt") }}</p>
          <div class="skipReasons">
            <BaseButton
              v-for="reason in skipReasonOptions"
              :key="reason.key"
              variant="secondary"
              :loading="isSkipReasonLoading(focusMission, reason.key)"
              :disabled="busyAction === 'skip' && busyId === focusMission.mission_id"
              @click="selectSkipReason(focusMission, reason)"
            >
              {{ reason.label }}
            </BaseButton>
          </div>
        </div>
      </div>

      <div class="missionGuideActions">
        <BaseButton
          v-if="!missionGuide.complete && !isTodaySaved && focusMission && !guidanceActions.length"
          variant="primary"
          @click="focusMissionCard(focusMission)"
        >
          {{ t("missions.focusCta") }}
        </BaseButton>

        <RouterLink
          v-if="focusMission?.enrollment_id"
          class="missionGuideLink"
          :to="`/enrollment/${focusMission.enrollment_id}`"
        >
          {{ t("missions.detailsCta") }}
        </RouterLink>

        <RouterLink
          v-if="missionGuide.complete"
          class="missionGuideLink"
          to="/paths"
        >
          {{ t("missions.nextPathCta") }}
        </RouterLink>
      </div>
    </BaseCard>

    <BaseCard v-if="!loading && !error && otherMissions.length" class="missionList secondaryMissionList">
      <div class="missionListHead">
        <div>
          <p class="eyebrow compact">{{ t("missions.otherEyebrow") }}</p>
          <h2>{{ t("missions.otherTitle") }}</h2>
        </div>
        <BaseButton
          variant="secondary"
          @click="showOtherMissions = !showOtherMissions"
        >
          {{ showOtherMissions ? t("missions.hideOtherMissions") : t("missions.showOtherMissions", { count: otherMissions.length }) }}
        </BaseButton>
      </div>

      <div v-if="showOtherMissions" class="missionItems">
        <article
          v-for="mission in otherMissions"
          :key="mission.mission_id"
          :id="`mission-${mission.mission_id}`"
          class="missionItem"
          :class="[mission.status, { focus: focusMission?.mission_id === mission.mission_id }]"
        >
          <div>
            <p class="missionMeta">
              {{ mission.challenge_name }} · {{ t(`missions.status.${mission.status}`) }}
            </p>
            <h3>{{ mission.title }}</h3>
            <p>{{ mission.description }}</p>
            <small v-if="mission.ringo_message">{{ mission.ringo_message }}</small>
          </div>

          <div class="missionActions">
            <BaseButton
              variant="primary"
              :loading="busyId === mission.mission_id && busyAction === 'done'"
              :disabled="mission.status === 'done'"
              @click="markDone(mission)"
            >
              {{ t("missions.doneCta") }}
            </BaseButton>

            <BaseButton
              variant="secondary"
              :loading="busyId === mission.mission_id && busyAction === 'remind'"
              :disabled="mission.status === 'done' || mission.status === 'remind_later'"
              @click="remindLater(mission)"
            >
              {{ mission.status === "remind_later" ? t("missions.reminderSet") : t("missions.remindLater") }}
            </BaseButton>

            <BaseButton
              variant="secondary"
              :loading="busyId === mission.mission_id && busyAction === 'skip'"
              :disabled="mission.status === 'done' || mission.status === 'skipped'"
              @click="skipMission(mission)"
            >
              {{ mission.status === "skipped" ? t("missions.skipped") : t("missions.skip") }}
            </BaseButton>
          </div>

          <div v-if="isReminderPanelOpen(mission)" class="remindOptionsPanel">
            <p>{{ t("missions.remindOptions.prompt") }}</p>
            <div class="remindOptions">
              <BaseButton
                v-for="option in reminderOptions"
                :key="option.key"
                variant="secondary"
                :loading="isReminderOptionLoading(mission, option.key)"
                :disabled="busyAction === 'remind' && busyId === mission.mission_id"
                @click="selectReminderOption(mission, option)"
              >
                {{ option.label }}
              </BaseButton>
            </div>
          </div>

          <div v-if="isSkipReasonPanelOpen(mission)" class="skipReasonPanel">
            <p>{{ t("missions.skipReasons.prompt") }}</p>
            <div class="skipReasons">
              <BaseButton
                v-for="reason in skipReasonOptions"
                :key="reason.key"
                variant="secondary"
                :loading="isSkipReasonLoading(mission, reason.key)"
                :disabled="busyAction === 'skip' && busyId === mission.mission_id"
                @click="selectSkipReason(mission, reason)"
              >
                {{ reason.label }}
              </BaseButton>
            </div>
          </div>
        </article>
      </div>

      <p v-else class="otherMissionHint">
        {{ t(isTodaySaved ? "missions.optionalOtherHint" : "missions.otherHint", { count: otherMissions.length }) }}
      </p>
    </BaseCard>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import RingoCoach from "@/components/ringo/RingoCoach.vue";
import RingoRewardSequence from "@/components/ringo/RingoRewardSequence.vue";
import PathSelection from "@/components/missions/PathSelection.vue";
import {
  localizeMissionList,
  localizeRingoState,
} from "@/lib/ringoContentLocalization";

const { locale, t } = useI18n();
const emit = defineEmits(["checked-in", "loaded"]);

const loading = ref(true);
const error = ref("");
const date = ref("");
const ringo = ref(null);
const ringoGuidance = ref(null);
const missions = ref([]);
const busyId = ref(null);
const busyAction = ref("");
const notice = ref("");
const noticeType = ref("success");
const dismissedCoachState = ref("");
const ringoActionMessage = ref("");
const manualFocusMissionId = ref(null);
const showOtherMissions = ref(false);
const reminderPanelMissionId = ref(null);
const busyReminderOption = ref("");
const skipReasonPanelMissionId = ref(null);
const busySkipReason = ref("");
const rewardSequenceSteps = ref([]);
const rewardSequenceSprite = ref("celebration");

const SUPPORTED_GUIDANCE_ACTIONS = new Set([
  "start",
  "remind_later",
  "make_smaller",
  "too_tired",
  "skip_today",
]);

const SUPPORTED_REWARD_STEP_TYPES = new Set([
  "ringo_message",
  "mission_completed",
  "xp_earned",
  "today_saved",
  "next_choice",
]);

const REMINDER_OPTION_KEYS = [
  "fifteenMinutes",
  "oneHour",
  "evening",
  "tonight",
];

const SKIP_REASON_KEYS = [
  "tooTired",
  "noTime",
  "tooHard",
  "notRelevant",
  "dontLike",
  "other",
  "withoutReason",
];

const showPathSelection = computed(() => {
  return ["new_user_no_path", "path_selected_no_challenge"].includes(ringo.value?.state);
});

const showCoach = computed(() => {
  return ringo.value?.state && ringo.value.state !== dismissedCoachState.value;
});

const localizedMissions = computed(() => {
  return localizeMissionList(missions.value, locale.value);
});

const localizedRingo = computed(() => {
  return localizeRingoState(ringo.value, localizedMissions.value, locale.value);
});

const guidanceRingo = computed(() => ringoGuidance.value?.ringo || null);

const preferLocalizedRingo = computed(() => {
  return String(locale.value || "").toLowerCase().startsWith("fa");
});

const coachMessage = computed(() => {
  return guidanceRingo.value?.message || localizedRingo.value?.message;
});

const hasRingoGuidance = computed(() => !!guidanceRingo.value);

const coachPrimaryAction = computed(() => {
  if (hasRingoGuidance.value || isTodaySaved.value) return null;

  return localizedRingo.value?.primary_action || null;
});

const coachSecondaryAction = computed(() => {
  if (hasRingoGuidance.value || isTodaySaved.value) return null;

  return localizedRingo.value?.secondary_action || null;
});

const guidanceMission = computed(() => {
  const mission = ringoGuidance.value?.mission;
  if (!mission?.mission_id) return mission || null;

  const currentMission = localizedMissions.value.find((item) => item.mission_id === mission.mission_id);

  return currentMission ? { ...mission, ...currentMission } : mission;
});

const pendingMissions = computed(() => {
  return localizedMissions.value.filter((mission) => mission.status === "pending");
});

const deferredMissions = computed(() => {
  return localizedMissions.value.filter((mission) => mission.status === "remind_later");
});

const skippedMissions = computed(() => {
  return localizedMissions.value.filter((mission) => mission.status === "skipped");
});

const manualFocusMission = computed(() => {
  if (!manualFocusMissionId.value) return null;

  return localizedMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, manualFocusMissionId.value);
  }) || null;
});

const focusMission = computed(() => {
  return manualFocusMission.value
    || guidanceMission.value
    || pendingMissions.value[0]
    || skippedMissions.value[0]
    || deferredMissions.value[0]
    || localizedMissions.value[0]
    || null;
});

const focusMissionIntensity = computed(() => buildMissionIntensityMeta(focusMission.value));

const otherMissions = computed(() => {
  if (!focusMission.value?.mission_id) return localizedMissions.value;

  return localizedMissions.value.filter((mission) => {
    return !sameMissionId(mission.mission_id, focusMission.value.mission_id);
  });
});

const missionGuide = computed(() => {
  if (!localizedMissions.value.length || !focusMission.value) return null;

  const complete = localizedMissions.value.every((mission) => mission.status === "done");
  const hasSkipped = skippedMissions.value.length > 0;
  const hasDeferred = deferredMissions.value.length > 0;
  const hasPending = pendingMissions.value.length > 0;
  const context = {
    path: focusMission.value.path_title || t("missions.fallbackPath"),
    challenge: focusMission.value.challenge_name || t("missions.fallbackChallenge"),
    mission: focusMission.value.title,
  };

  if (complete) {
    return {
      complete: true,
      state: "complete",
      title: t("missions.guideCompleteTitle", context),
      body: t("missions.guideCompleteBody", context),
    };
  }

  if (isTodaySaved.value) {
    return {
      complete: true,
      state: "complete",
      title: t("missions.guideSavedTitle", context),
      body: t("missions.guideSavedBody", context),
    };
  }

  if (!hasPending && hasSkipped) {
    return {
      complete: false,
      state: "skipped",
      title: t("missions.guideSkippedTitle", context),
      body: t("missions.guideSkippedBody", context),
    };
  }

  if (!hasPending && hasDeferred) {
    return {
      complete: false,
      state: "reminder",
      title: t("missions.guideReminderTitle", context),
      body: t("missions.guideReminderBody", context),
    };
  }

  return {
    complete: false,
    state: "active",
    title: t("missions.guideTitle", context),
    body: t("missions.guideBody", context),
  };
});

const todaySavedLabel = computed(() => {
  if (!ringoGuidance.value?.progress?.today_saved) return "";

  return t("missions.todaySaved");
});

const isTodaySaved = computed(() => Boolean(ringoGuidance.value?.progress?.today_saved));

const guidanceActions = computed(() => {
  const actions = Array.isArray(ringoGuidance.value?.actions)
    ? ringoGuidance.value.actions
    : [];

  if (!actions.length || !focusMission.value || missionGuide.value?.complete || isTodaySaved.value) {
    return [];
  }

  const seen = new Set();

  return actions.filter((action) => {
    const type = action?.type;
    if (!SUPPORTED_GUIDANCE_ACTIONS.has(type) || seen.has(type)) return false;
    seen.add(type);
    return true;
  });
});

const coachActionPanel = computed(() => {
  return !!(
    guidanceMission.value
    || guidanceActions.value.length
    || todaySavedLabel.value
    || ringoActionMessage.value
  );
});

const reminderOptions = computed(() => {
  return REMINDER_OPTION_KEYS.map((key) => ({
    key,
    label: t(`missions.remindOptions.${key}`),
  }));
});

const skipReasonOptions = computed(() => {
  return SKIP_REASON_KEYS.map((key) => ({
    key,
    label: t(`missions.skipReasons.${key}`),
  }));
});

async function loadMissions() {
  loading.value = true;
  error.value = "";
  ringoActionMessage.value = "";
  manualFocusMissionId.value = null;
  showOtherMissions.value = false;
  reminderPanelMissionId.value = null;
  skipReasonPanelMissionId.value = null;

  try {
    const [missionsResult, guidanceResult] = await Promise.allSettled([
      api.get("/me/today-missions"),
      api.get("/me/ringo/today"),
    ]);

    if (missionsResult.status === "rejected") {
      throw missionsResult.reason;
    }

    const { data } = missionsResult.value;
    ringoGuidance.value = guidanceResult.status === "fulfilled"
      ? guidanceResult.value?.data || null
      : null;
    date.value = data?.date || "";
    ringo.value = data?.ringo || null;
    if (ringo.value?.state !== dismissedCoachState.value) {
      dismissedCoachState.value = "";
    }
    missions.value = data?.missions || [];
    emit("loaded", {
      error: "",
      ringo: localizedRingo.value,
      missions: localizedMissions.value,
      state: ringo.value?.state || "",
    });
  } catch (e) {
    ringoGuidance.value = null;
    error.value = e?.response?.data?.error || e?.message || String(e);
    emit("loaded", {
      error: error.value,
      ringo: null,
      missions: [],
      state: "error",
    });
  } finally {
    loading.value = false;
  }
}

async function runMissionAction(mission, action, request, options = {}) {
  busyId.value = mission.mission_id;
  busyAction.value = action;
  error.value = "";

  try {
    const { data } = await request();
    notice.value = options.successNotice || (action === "done"
      ? data?.checkin?.already_checked
        ? t("missions.alreadySecuredNotice")
        : t("missions.securedNotice")
      : action === "remind"
        ? t("missions.reminderNotice")
        : t("missions.skipNotice"));
    noticeType.value = action === "done"
      ? "success"
      : action === "remind"
        ? "reminder"
        : "muted";

    if (data?.checkin?.ok) {
      emit("checked-in", {
        ...data,
        mission: {
          ...mission,
          ...(data?.mission || {}),
          title: mission.title,
          description: mission.description,
          challenge_name: mission.challenge_name,
          path_title: mission.path_title,
        },
      });
    }

    if (action === "done") {
      rewardSequenceSteps.value = buildRewardSequence(data, mission);
      rewardSequenceSprite.value = data?.checkin?.already_checked ? "happy" : "celebration";
    }

    await loadMissions();
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    busyId.value = null;
    busyAction.value = "";
    busyReminderOption.value = "";
    busySkipReason.value = "";
  }
}

function markDone(mission) {
  return runMissionAction(
    mission,
    "done",
    () => api.post(`/me/missions/${mission.mission_id}/done`, {}),
  );
}

function remindLater(mission) {
  if (!mission || mission.status === "done" || mission.status === "remind_later") return null;

  reminderPanelMissionId.value = mission.mission_id;
  skipReasonPanelMissionId.value = null;
  ringoActionMessage.value = "";
  return focusMissionCard(mission);
}

function fallbackReminderAt() {
  return new Date(Date.now() + 2 * 60 * 60 * 1000);
}

function reminderAtForOption(key) {
  const now = new Date();

  if (key === "fifteenMinutes") {
    return new Date(now.getTime() + 15 * 60 * 1000);
  }

  if (key === "oneHour") {
    return new Date(now.getTime() + 60 * 60 * 1000);
  }

  if (key === "evening" || key === "tonight") {
    const target = new Date(now);
    target.setHours(key === "evening" ? 18 : 21, 0, 0, 0);

    return target > now ? target : fallbackReminderAt();
  }

  return fallbackReminderAt();
}

function isReminderPanelOpen(mission) {
  return !!(
    mission?.mission_id
    && sameMissionId(reminderPanelMissionId.value, mission.mission_id)
    && mission.status !== "done"
    && mission.status !== "remind_later"
  );
}

function isReminderOptionLoading(mission, key) {
  return !!(
    mission?.mission_id
    && busyId.value === mission.mission_id
    && busyAction.value === "remind"
    && busyReminderOption.value === key
  );
}

function selectReminderOption(mission, option) {
  if (!mission) return null;

  busyReminderOption.value = option?.key || "";
  const reminderAt = reminderAtForOption(option?.key).toISOString();
  const successNotice = option?.label
    ? t("missions.remindOptions.confirmation", { time: option.label })
    : t("missions.remindOptions.fallbackConfirmation");

  return runMissionAction(
    mission,
    "remind",
    () => api.post(`/me/missions/${mission.mission_id}/remind-later`, {
      reminder_at: reminderAt,
    }),
    { successNotice },
  );
}

function skipMission(mission) {
  if (!mission || mission.status === "done" || mission.status === "skipped") return null;

  skipReasonPanelMissionId.value = mission.mission_id;
  reminderPanelMissionId.value = null;
  ringoActionMessage.value = "";
  return focusMissionCard(mission);
}

function isSkipReasonPanelOpen(mission) {
  return !!(
    mission?.mission_id
    && sameMissionId(skipReasonPanelMissionId.value, mission.mission_id)
    && mission.status !== "done"
    && mission.status !== "skipped"
  );
}

function isSkipReasonLoading(mission, key) {
  return !!(
    mission?.mission_id
    && busyId.value === mission.mission_id
    && busyAction.value === "skip"
    && busySkipReason.value === key
  );
}

function selectSkipReason(mission, reason) {
  if (!mission) return null;

  busySkipReason.value = reason?.key || "";
  const successNotice = reason?.key && reason.key !== "withoutReason"
    ? t("missions.skipReasons.confirmationWithReason", { reason: reason.label })
    : t("missions.skipReasons.confirmationWithoutReason");

  return runMissionAction(
    mission,
    "skip",
    () => api.post(`/me/missions/${mission.mission_id}/skip`, {}),
    { successNotice },
  );
}

function rewardStepFallbackTitle(type, mission) {
  const titleMap = {
    ringo_message: "ringoTitle",
    mission_completed: "missionFallback",
    xp_earned: "xpTitle",
    today_saved: "todaySavedTitle",
    next_choice: "nextTitle",
  };

  if (type === "mission_completed") {
    return mission?.title || t("ringoRewardSequence.local.missionFallback");
  }

  return t(`ringoRewardSequence.local.${titleMap[type] || "missionFallback"}`);
}

function rewardStepFallbackText(type) {
  const textMap = {
    ringo_message: "ringoText",
    mission_completed: "missionText",
    today_saved: "todaySavedText",
    next_choice: "nextText",
  };

  return textMap[type] ? t(`ringoRewardSequence.local.${textMap[type]}`) : "";
}

function rewardStepValue(step) {
  if (step?.value !== undefined && step?.value !== null && String(step.value).trim()) {
    return String(step.value);
  }

  const amount = Number(step?.amount);
  if (Number.isFinite(amount) && amount > 0) {
    return t("ringoRewardSequence.local.xpValue", { count: amount });
  }

  return "";
}

function backendRewardSequenceSteps(data, mission) {
  const sequence = data?.reward_sequence;
  if (!Array.isArray(sequence)) return [];

  return sequence
    .filter((step) => {
      return step && typeof step === "object" && SUPPORTED_REWARD_STEP_TYPES.has(step.type);
    })
    .map((step) => ({
      type: step.type,
      label: step.label ? String(step.label) : "",
      title: step.title ? String(step.title) : rewardStepFallbackTitle(step.type, mission),
      text: step.text || step.description || step.message
        ? String(step.text || step.description || step.message)
        : rewardStepFallbackText(step.type),
      value: rewardStepValue(step),
      sprite: step.mood || step.sprite_key,
    }))
    .filter((step) => step.title || step.text || step.value);
}

function buildRewardSequence(data, mission) {
  const backendSteps = backendRewardSequenceSteps(data, mission);
  if (backendSteps.length) return backendSteps;

  const completedMission = data?.mission || {};
  const xpEarned = Number(completedMission.xp_earned ?? mission.xp_reward ?? 0);
  const todaySaved = Boolean(data?.checkin?.ok);
  const steps = [
    {
      type: "ringo_message",
      title: t("ringoRewardSequence.local.ringoTitle"),
      text: data?.checkin?.already_checked
        ? t("ringoRewardSequence.local.alreadySaved")
        : t("ringoRewardSequence.local.ringoText"),
      sprite: data?.checkin?.already_checked ? "happy" : "celebration",
    },
    {
      type: "mission_completed",
      title: mission.title || completedMission.title || t("ringoRewardSequence.local.missionFallback"),
      text: t("ringoRewardSequence.local.missionText"),
    },
  ];

  if (xpEarned > 0) {
    steps.push({
      type: "xp_earned",
      title: t("ringoRewardSequence.local.xpTitle"),
      value: t("ringoRewardSequence.local.xpValue", { count: xpEarned }),
    });
  }

  if (todaySaved) {
    steps.push({
      type: "today_saved",
      title: t("ringoRewardSequence.local.todaySavedTitle"),
      text: t("ringoRewardSequence.local.todaySavedText"),
    });
  }

  steps.push({
    type: "next_choice",
    title: t("ringoRewardSequence.local.nextTitle"),
    text: t("ringoRewardSequence.local.nextText"),
  });

  return steps;
}

function finishRewardSequence() {
  rewardSequenceSteps.value = [];
  showOtherMissions.value = false;
}

function finishForToday() {
  showOtherMissions.value = false;
  ringoActionMessage.value = t("missions.finishedForTodayMessage");
}

function guidanceActionLabel(action) {
  return t(`missions.ringoActions.${action.type}`);
}

function missionForGuidanceAction(action) {
  const actionMissionId = action?.mission_id;
  if (actionMissionId) {
    const matchingMission = localizedMissions.value.find((mission) => mission.mission_id === actionMissionId);
    if (matchingMission) return matchingMission;
  }

  if (focusMission.value?.mission_id) {
    const matchingFocus = localizedMissions.value.find((mission) => mission.mission_id === focusMission.value.mission_id);
    return matchingFocus || focusMission.value;
  }

  return null;
}

function isTinyMission(mission) {
  return mission?.mission_intensity === "tiny";
}

function normalizedMissionIntensity(mission) {
  const intensity = mission?.mission_intensity || "main";

  return ["main", "tiny", "bonus"].includes(intensity) ? intensity : "main";
}

function missionEstimatedMinutes(mission) {
  const minutes = Number(mission?.estimated_minutes);

  return Number.isFinite(minutes) && minutes > 0 ? Math.round(minutes) : null;
}

function buildMissionIntensityMeta(mission) {
  if (!mission) return null;

  const intensity = normalizedMissionIntensity(mission);
  const detailParts = [t(`missions.intensity.${intensity}Detail`)];
  const minutes = missionEstimatedMinutes(mission);

  if (minutes) {
    detailParts.push(t("missions.intensity.minutes", { count: minutes }));
  }

  return {
    intensity,
    label: t(`missions.intensity.${intensity}`),
    detail: detailParts.filter(Boolean).join(" · "),
  };
}

function isPendingTinyMission(mission) {
  return isTinyMission(mission) && mission?.status === "pending";
}

function sameMissionId(a, b) {
  if (a === null || a === undefined || b === null || b === undefined) return false;

  return String(a) === String(b);
}

function findTinyMissionFor(mission) {
  if (isPendingTinyMission(mission)) return mission;

  if (mission?.mission_id) {
    const linkedTinyMission = localizedMissions.value.find((item) => {
      return isPendingTinyMission(item) && sameMissionId(item.parent_mission_id, mission.mission_id);
    });

    if (linkedTinyMission) return linkedTinyMission;
  }

  return localizedMissions.value.find(isPendingTinyMission) || null;
}

function isGuidanceActionLoading(action) {
  const mission = missionForGuidanceAction(action);
  if (!mission) return false;

  if (action.type === "remind_later") {
    return busyId.value === mission.mission_id && busyAction.value === "remind";
  }

  if (action.type === "skip_today") {
    return busyId.value === mission.mission_id && busyAction.value === "skip";
  }

  return false;
}

function isGuidanceActionDisabled(action) {
  const mission = missionForGuidanceAction(action);

  if (action.type === "make_smaller" || action.type === "too_tired") return false;
  if (!mission) return action.type !== "make_smaller" && action.type !== "too_tired";
  if (mission.status === "done") return true;
  if (action.type === "remind_later") return mission.status === "remind_later";
  if (action.type === "skip_today") return mission.status === "skipped";

  return false;
}

function focusTinyMissionFromAction(action, messageKey, fallbackMessageKey) {
  const mission = missionForGuidanceAction(action);
  const tinyMission = findTinyMissionFor(mission);

  if (!tinyMission) {
    ringoActionMessage.value = t(fallbackMessageKey);
    return;
  }

  manualFocusMissionId.value = tinyMission.mission_id;
  ringoActionMessage.value = t(messageKey, { mission: tinyMission.title });
  focusMissionCard(tinyMission);
}

function handleGuidanceAction(action) {
  const mission = missionForGuidanceAction(action);

  if (action.type === "make_smaller") {
    focusTinyMissionFromAction(
      action,
      "missions.ringoActions.makeSmallerTinyMessage",
      "missions.ringoActions.makeSmallerMessage",
    );
    return;
  }

  if (action.type === "too_tired") {
    focusTinyMissionFromAction(
      action,
      "missions.ringoActions.tooTiredTinyMessage",
      "missions.ringoActions.tooTiredMessage",
    );
    return;
  }

  if (!mission) return;

  if (action.type === "remind_later") {
    remindLater(mission);
    return;
  }

  if (action.type === "skip_today") {
    skipMission(mission);
    return;
  }

  focusMissionCard(mission);
}

async function focusMissionCard(mission) {
  await nextTick();
  document
    .getElementById(`mission-${mission.mission_id}`)
    ?.scrollIntoView({ behavior: "smooth", block: "center" });
}

function handleCoachAction(action) {
  if (action?.type === "dismiss") {
    dismissedCoachState.value = ringo.value?.state || "";
    return;
  }

  if (!action?.mission_id) return;

  const mission = localizedMissions.value.find((item) => item.mission_id === action.mission_id);

  if (!mission) return;

  if (action.type === "mission_reminder") {
    remindLater(mission);
    return;
  }

  markDone(mission);
}

onMounted(loadMissions);
</script>

<style scoped>
.missionCenter {
  display: grid;
  gap: var(--s-16);
}

.missionList {
  display: grid;
  gap: var(--s-16);
}

.secondaryMissionList {
  gap: var(--s-12);
  border-color: rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.028);
}

.coachActionPanel {
  display: grid;
  gap: var(--s-12);
  margin-top: calc(var(--s-16) * -0.5);
  border-color: rgba(110, 229, 255, 0.16);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.10), transparent 32%),
    rgba(255, 255, 255, 0.035);
}

.coachActionPanel.complete {
  border-color: rgba(74, 222, 128, 0.22);
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.10), transparent 32%),
    rgba(255, 255, 255, 0.035);
}

.missionGuide {
  display: grid;
  gap: var(--s-16);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.12), transparent 36%),
    radial-gradient(circle at 100% 0%, rgba(247, 215, 116, 0.10), transparent 30%),
    rgba(255, 255, 255, 0.04);
}

.missionGuide.complete {
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.12), transparent 34%),
    rgba(255, 255, 255, 0.035);
}

.missionGuide.skipped {
  border-color: rgba(255, 255, 255, 0.14);
  background:
    radial-gradient(circle at 0% 0%, rgba(255, 255, 255, 0.08), transparent 34%),
    rgba(255, 255, 255, 0.032);
}

.missionGuide.reminder {
  border-color: rgba(247, 215, 116, 0.20);
  background:
    radial-gradient(circle at 0% 0%, rgba(247, 215, 116, 0.10), transparent 34%),
    rgba(255, 255, 255, 0.032);
}

.missionGuideCopy h2,
.missionGuideCopy p,
.focusMission p {
  margin: 0;
}

.missionGuideCopy h2 {
  color: rgba(255, 255, 255, 0.96);
  letter-spacing: -0.04em;
}

.missionGuideCopy p {
  margin-top: 8px;
  max-width: 760px;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.65;
}

.missionStepper {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-8);
}

.step {
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.62);
  background: rgba(255, 255, 255, 0.035);
  font-size: var(--cap);
  font-weight: 850;
  text-align: center;
}

.step.complete {
  border-color: rgba(74, 222, 128, 0.24);
  color: rgba(187, 247, 208, 0.95);
  background: rgba(74, 222, 128, 0.07);
}

.step.active {
  border-color: rgba(247, 215, 116, 0.30);
  color: rgba(253, 230, 138, 0.96);
  background: rgba(247, 215, 116, 0.08);
  box-shadow: 0 0 28px rgba(247, 215, 116, 0.08);
}

.focusMission {
  display: grid;
  gap: 6px;
  padding: 14px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 18px;
  background: rgba(5, 10, 18, 0.26);
}

.coachFocusMission {
  border-color: rgba(110, 229, 255, 0.22);
  background: rgba(5, 10, 18, 0.18);
}

.focusMission span {
  color: rgba(110, 229, 255, 0.82);
  font-size: var(--cap);
  font-weight: 900;
}

.focusMission strong {
  color: rgba(255, 255, 255, 0.94);
}

.focusMission p {
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.missionIntensity {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  width: fit-content;
  max-width: 100%;
  padding: 5px 8px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.95);
  background: rgba(110, 229, 255, 0.07);
  font-size: var(--cap);
  font-weight: 850;
  line-height: 1.25;
}

.missionIntensity.tiny {
  border-color: rgba(74, 222, 128, 0.24);
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
}

.missionIntensity.bonus {
  border-color: rgba(247, 215, 116, 0.26);
  color: rgba(253, 230, 138, 0.96);
  background: rgba(247, 215, 116, 0.075);
}

.missionIntensity span,
.missionIntensity small {
  min-width: 0;
  color: inherit;
  font: inherit;
}

.missionIntensity small {
  opacity: 0.78;
}

.todaySaved {
  display: grid;
  gap: 4px;
  margin: 0;
  padding: 11px 13px;
  border: 1px solid rgba(74, 222, 128, 0.24);
  border-radius: 16px;
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
  font-weight: 850;
}

.todaySaved strong,
.todaySaved span {
  min-width: 0;
}

.todaySaved span {
  color: rgba(220, 252, 231, 0.74);
  font-weight: 700;
  line-height: 1.5;
}

.completedChoices {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  align-items: center;
}

.ringoActionHint {
  margin: 0;
  padding: 11px 13px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 16px;
  color: rgba(219, 244, 255, 0.94);
  background: rgba(110, 229, 255, 0.07);
  font-weight: 780;
  line-height: 1.55;
}

.ringoActionChoices {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  align-items: center;
}

.remindOptionsPanel {
  display: grid;
  gap: var(--s-8);
  margin-top: 4px;
  padding: 11px;
  border: 1px solid rgba(247, 215, 116, 0.22);
  border-radius: 16px;
  background: rgba(247, 215, 116, 0.065);
}

.missionItem .remindOptionsPanel {
  grid-column: 1 / -1;
}

.remindOptionsPanel p {
  margin: 0;
  color: rgba(253, 230, 138, 0.95);
  font-weight: 820;
  line-height: 1.45;
}

.remindOptions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
}

.skipReasonPanel {
  display: grid;
  gap: var(--s-8);
  margin-top: 4px;
  padding: 11px;
  border: 1px solid rgba(255, 255, 255, 0.13);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.045);
}

.missionItem .skipReasonPanel {
  grid-column: 1 / -1;
}

.skipReasonPanel p {
  margin: 0;
  color: rgba(255, 255, 255, 0.76);
  font-weight: 780;
  line-height: 1.45;
}

.skipReasons {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
}

.missionGuideActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-10);
  align-items: center;
}

.missionGuideLink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 9px 13px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 15px;
  color: rgba(255, 255, 255, 0.86);
  background: rgba(255, 255, 255, 0.055);
  font-weight: 850;
  text-decoration: none;
}

.missionGuideLink:hover {
  border-color: rgba(110, 229, 255, 0.24);
  background: rgba(255, 255, 255, 0.08);
}

.missionNotice {
  margin: 0;
  padding: 11px 13px;
  border: 1px solid rgba(74, 222, 128, 0.24);
  border-radius: 16px;
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
  font-weight: 780;
}

.missionNotice.reminder {
  border-color: rgba(247, 215, 116, 0.24);
  color: rgba(253, 230, 138, 0.96);
  background: rgba(247, 215, 116, 0.075);
}

.missionNotice.muted {
  border-color: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.045);
}

.missionListHead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--s-16);
}

.missionListHead h2,
.missionListHead p {
  margin: 0;
}

.missionListHead > span {
  color: var(--muted2);
  font-size: var(--cap);
}

.otherMissionHint {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.55;
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.missionItems {
  display: grid;
  gap: var(--s-12);
}

.missionItem {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: center;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.035);
}

.missionItem.done {
  border-color: rgba(74, 222, 128, 0.24);
  background: rgba(74, 222, 128, 0.06);
}

.missionItem.focus {
  border-color: rgba(247, 215, 116, 0.28);
  box-shadow: 0 0 0 1px rgba(247, 215, 116, 0.05), 0 18px 45px rgba(0, 0, 0, 0.16);
}

.missionItem.remind_later {
  border-color: rgba(247, 215, 116, 0.24);
  background: rgba(247, 215, 116, 0.055);
}

.missionItem.skipped {
  opacity: 0.68;
}

.missionItem h3,
.missionItem p {
  margin: 0;
}

.missionItem h3 {
  margin-top: 4px;
}

.missionItem p:not(.missionMeta) {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.missionItem small {
  display: block;
  margin-top: 8px;
  color: rgba(247, 215, 116, 0.82);
}

.missionMeta {
  color: rgba(110, 229, 255, 0.78);
  font-size: var(--cap);
  font-weight: 850;
}

.missionActions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--s-8);
}

.primaryMissionActions {
  justify-content: flex-start;
  margin-top: 4px;
}

@media (max-width: 760px) {
  .missionStepper {
    grid-template-columns: 1fr;
  }

  .missionGuideActions :deep(.btn),
  .ringoActionChoices :deep(.btn),
  .remindOptions :deep(.btn),
  .skipReasons :deep(.btn),
  .completedChoices :deep(.btn),
  .primaryMissionActions :deep(.btn),
  .missionListHead :deep(.btn),
  .missionGuideLink,
  .completedChoices .missionGuideLink {
    width: 100%;
  }

  .missionListHead {
    display: grid;
  }

  .missionItem {
    grid-template-columns: 1fr;
  }

  .missionActions {
    justify-content: stretch;
  }

  .missionActions :deep(.btn) {
    flex: 1 1 100%;
  }
}
</style>
