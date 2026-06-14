<template>
  <section class="missionCenter">
    <RingoRewardSequence
      :steps="rewardSequenceSteps"
      :sprite="rewardSequenceSprite"
      @finish="finishRewardSequence"
    />

    <BaseCard
      v-if="coachActionPanel"
      class="coachActionPanel"
      :class="{ complete: !!todaySavedLabel }"
    >
      <RingoCoach
        v-if="showCoach"
        embedded
        :message="coachMessage"
        :sprite="coachSprite"
        :primary-action="coachPrimaryAction"
        :secondary-action="coachSecondaryAction"
        @action="handleCoachAction"
      />

      <div
        v-if="showFocusMissionCard"
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
        <small v-if="missionStatusCopy(focusMission)" class="missionStatusCopy">
          {{ missionStatusCopy(focusMission) }}
        </small>
        <div v-if="showFocusMissionActions" class="missionActions primaryMissionActions">
          <BaseButton
            variant="primary"
            :loading="busyId === focusMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(focusMission, 'done')"
            @click="markDone(focusMission)"
          >
            {{ t("missions.doneCta") }}
          </BaseButton>

          <BaseButton
            variant="secondary"
            :loading="busyId === focusMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(focusMission, 'done')"
            @click="remindLater(focusMission)"
          >
            {{ missionHasStatus(focusMission, "remind_later") ? t("missions.editReminder") : t("missions.remindLater") }}
          </BaseButton>

          <BaseButton
            v-if="shouldShowFocusSupportAction('make_smaller', focusMission)"
            variant="secondary"
            @click="handleFocusSupportAction('make_smaller', focusMission)"
          >
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>

          <BaseButton
            v-if="shouldShowFocusSupportAction('too_tired', focusMission)"
            variant="secondary"
            @click="handleFocusSupportAction('too_tired', focusMission)"
          >
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>

          <BaseButton
            variant="secondary"
            :loading="busyId === focusMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(focusMission, 'done', 'skipped')"
            @click="skipMission(focusMission)"
          >
            {{ missionHasStatus(focusMission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
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
            <BaseButton variant="secondary" @click="closeReminderPanel">
              {{ t("missions.backToMissionActions") }}
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
            <BaseButton variant="secondary" @click="closeSkipReasonPanel">
              {{ t("missions.backToMissionActions") }}
            </BaseButton>
          </div>
        </div>
      </div>

      <p v-if="todaySavedLabel" class="todaySaved">
        <strong>{{ todaySavedLabel }}</strong>
        <span v-if="showTodaySavedBody">{{ t("missions.todaySavedBody") }}</span>
      </p>

      <section v-if="isTodaySaved && optionalNextMission" class="optionalNextStep">
        <div class="optionalNextCopy">
          <p class="eyebrow compact">{{ t("missions.optionalNextEyebrow") }}</p>
          <h3>{{ t("missions.optionalNextTitle") }}</h3>
          <p>{{ t("missions.optionalNextBody") }}</p>
        </div>

        <div class="optionalNextMission">
          <div
            v-if="optionalNextMissionIntensity"
            class="missionIntensity"
            :class="optionalNextMissionIntensity.intensity"
          >
            <span>{{ optionalNextMissionIntensity.label }}</span>
            <small v-if="optionalNextMissionIntensity.detail">
              {{ optionalNextMissionIntensity.detail }}
            </small>
          </div>
          <strong>{{ optionalNextMission.title }}</strong>
          <p>{{ optionalNextMission.description }}</p>
          <small v-if="optionalNextMission.challenge_name" class="missionStatusCopy">
            {{ optionalNextMission.challenge_name }}
          </small>
        </div>

        <div class="optionalNextActions">
          <BaseButton
            variant="primary"
            :loading="busyId === optionalNextMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(optionalNextMission, 'done')"
            @click="markDone(optionalNextMission)"
          >
            {{ t("missions.doneCta") }}
          </BaseButton>
          <BaseButton
            variant="secondary"
            :loading="busyId === optionalNextMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(optionalNextMission, 'done')"
            @click="remindOptionalNextMission(optionalNextMission)"
          >
            {{ missionHasStatus(optionalNextMission, "remind_later") ? t("missions.editReminder") : t("missions.remindLater") }}
          </BaseButton>
          <BaseButton
            v-if="shouldShowOptionalNextSupportAction('make_smaller', optionalNextMission)"
            variant="secondary"
            @click="handleOptionalNextSupportAction('make_smaller', optionalNextMission)"
          >
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>
          <BaseButton
            v-if="shouldShowOptionalNextSupportAction('too_tired', optionalNextMission)"
            variant="secondary"
            @click="handleOptionalNextSupportAction('too_tired', optionalNextMission)"
          >
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>
          <BaseButton
            variant="secondary"
            :loading="busyId === optionalNextMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(optionalNextMission, 'skipped')"
            @click="skipOptionalNextMission(optionalNextMission)"
          >
            {{ t("missions.skip") }}
          </BaseButton>
          <BaseButton variant="secondary" @click="finishForToday">
            {{ t("missions.finishForToday") }}
          </BaseButton>
        </div>
      </section>

      <div v-if="isTodaySaved" class="completedChoices">
        <RouterLink
          v-if="detailsMission?.enrollment_id"
          class="missionGuideLink"
          :to="`/enrollment/${detailsMission.enrollment_id}`"
        >
          {{ t("missions.detailsCta") }}
        </RouterLink>

        <BaseButton
          v-if="otherMissions.length && !optionalNextSuppressed"
          variant="secondary"
          @click="showOtherMissions = true"
        >
          {{ t("missions.showOtherMissions", { count: otherMissions.length }) }}
        </BaseButton>

        <BaseButton v-if="!optionalNextMission" variant="secondary" @click="finishForToday">
          {{ t("missions.finishForToday") }}
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

    <p v-if="showMissionNotice" class="missionNotice" :class="noticeType">
      {{ notice }}
    </p>

    <PathSelection
      v-if="!loading && !error && showPathSelection"
      :allow-active-start="ringo?.state === 'path_selected_no_challenge'"
      @started="loadMissions"
    />

    <BaseCard
      v-if="missionGuide && !coachActionPanel"
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
        <small v-if="missionStatusCopy(focusMission)" class="missionStatusCopy">
          {{ missionStatusCopy(focusMission) }}
        </small>
        <div v-if="showFocusMissionActions" class="missionActions primaryMissionActions">
          <BaseButton
            variant="primary"
            :loading="busyId === focusMission.mission_id && busyAction === 'done'"
            :disabled="missionHasStatus(focusMission, 'done')"
            @click="markDone(focusMission)"
          >
            {{ t("missions.doneCta") }}
          </BaseButton>

          <BaseButton
            variant="secondary"
            :loading="busyId === focusMission.mission_id && busyAction === 'remind'"
            :disabled="missionHasStatus(focusMission, 'done')"
            @click="remindLater(focusMission)"
          >
            {{ missionHasStatus(focusMission, "remind_later") ? t("missions.editReminder") : t("missions.remindLater") }}
          </BaseButton>

          <BaseButton
            v-if="shouldShowFocusSupportAction('make_smaller', focusMission)"
            variant="secondary"
            @click="handleFocusSupportAction('make_smaller', focusMission)"
          >
            {{ t("missions.ringoActions.make_smaller") }}
          </BaseButton>

          <BaseButton
            v-if="shouldShowFocusSupportAction('too_tired', focusMission)"
            variant="secondary"
            @click="handleFocusSupportAction('too_tired', focusMission)"
          >
            {{ t("missions.ringoActions.too_tired") }}
          </BaseButton>

          <BaseButton
            variant="secondary"
            :loading="busyId === focusMission.mission_id && busyAction === 'skip'"
            :disabled="missionHasStatus(focusMission, 'done', 'skipped')"
            @click="skipMission(focusMission)"
          >
            {{ missionHasStatus(focusMission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
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
            <BaseButton variant="secondary" @click="closeReminderPanel">
              {{ t("missions.backToMissionActions") }}
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
            <BaseButton variant="secondary" @click="closeSkipReasonPanel">
              {{ t("missions.backToMissionActions") }}
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

    <BaseCard v-if="showOtherMissionList" class="missionList secondaryMissionList">
      <div class="missionListHead">
        <div>
          <p class="eyebrow compact">{{ t("missions.otherEyebrow") }}</p>
          <h2>{{ t("missions.otherTitle") }}</h2>
          <p v-if="isTodaySaved" class="otherMissionContext">
            {{ t("missions.optionalOtherContext") }}
          </p>
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
          :class="[
            normalizedMissionStatus(mission.status),
            {
              focus: focusMission?.mission_id === mission.mission_id,
              optionalNext: optionalNextMission && sameMissionId(optionalNextMission.mission_id, mission.mission_id),
            },
          ]"
        >
          <div>
            <div class="missionChips" :aria-label="t('missions.statusChipsLabel')">
              <span
                v-for="chip in missionChips(mission)"
                :key="chip.key"
                class="missionChip"
                :class="chip.type"
              >
                {{ chip.label }}
              </span>
            </div>
            <p class="missionMeta">
              {{ mission.challenge_name }} · {{ missionStatusLabel(mission) }}
            </p>
            <h3>{{ mission.title }}</h3>
            <small v-if="missionParentCopy(mission)" class="missionRelationCopy">
              {{ missionParentCopy(mission) }}
            </small>
            <p>{{ mission.description }}</p>
            <small v-if="missionStatusCopy(mission)" class="missionStatusCopy">
              {{ missionStatusCopy(mission) }}
            </small>
          </div>

          <div v-if="showMissionItemActions(mission)" class="missionActions">
            <BaseButton
              variant="primary"
              :loading="busyId === mission.mission_id && busyAction === 'done'"
              :disabled="missionHasStatus(mission, 'done')"
              @click="markDone(mission)"
            >
              {{ t("missions.doneCta") }}
            </BaseButton>

            <BaseButton
              variant="secondary"
              :loading="busyId === mission.mission_id && busyAction === 'remind'"
              :disabled="missionHasStatus(mission, 'done')"
              @click="remindLater(mission)"
            >
              {{ missionHasStatus(mission, "remind_later") ? t("missions.editReminder") : t("missions.remindLater") }}
            </BaseButton>

            <BaseButton
              variant="secondary"
              :loading="busyId === mission.mission_id && busyAction === 'skip'"
              :disabled="missionHasStatus(mission, 'done', 'skipped')"
              @click="skipMission(mission)"
            >
              {{ missionHasStatus(mission, "skipped") ? t("missions.skipped") : t("missions.skip") }}
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
              <BaseButton variant="secondary" @click="closeReminderPanel">
                {{ t("missions.backToMissionActions") }}
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
              <BaseButton variant="secondary" @click="closeSkipReasonPanel">
                {{ t("missions.backToMissionActions") }}
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
const interactionNarrative = ref(null);
const completionNarrative = ref(null);
const manualFocusMissionId = ref(null);
const showOtherMissions = ref(false);
const reminderPanelMissionId = ref(null);
const busyReminderOption = ref("");
const skipReasonPanelMissionId = ref(null);
const busySkipReason = ref("");
const rewardSequenceSteps = ref([]);
const rewardSequenceSprite = ref("celebration");
const optionalNextSuppressed = ref(false);
const revealedTinyMissionIds = ref(new Set());

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

const SKIP_REASON_OPTIONS = [
  { key: "tooTired", reason: "too_tired" },
  { key: "noTime", reason: "no_time" },
  { key: "tooHard", reason: "too_hard" },
  { key: "notRelevant", reason: "not_relevant" },
  { key: "dontLike", reason: "disliked" },
  { key: "other", reason: "other" },
  { key: "withoutReason", reason: null },
];

const SUPPORTED_AGENDA_ACTIONS = new Set([
  "due_reminder",
  "upcoming_reminder",
  "primary_mission",
  "optional_mission",
  "skipped_optional",
  "done_for_today",
]);

const MISSION_AGENDA_ACTIONS = new Set([
  "due_reminder",
  "upcoming_reminder",
  "primary_mission",
  "optional_mission",
  "skipped_optional",
]);

const showPathSelection = computed(() => {
  return ["new_user_no_path", "path_selected_no_challenge"].includes(ringo.value?.state);
});

const showCoach = computed(() => {
  if (
    interactionNarrative.value
    || completionNarrative.value
    || finishedForTodayNarrative.value
    || dailySummaryNarrative.value
    || agendaNarrative.value
    || guidanceRingo.value
  ) return true;
  return ringo.value?.state && ringo.value.state !== dismissedCoachState.value;
});

const localizedMissions = computed(() => {
  return localizeMissionList(missions.value, locale.value);
});

const localizedRingo = computed(() => {
  return localizeRingoState(ringo.value, localizedMissions.value, locale.value);
});

const guidanceRingo = computed(() => ringoGuidance.value?.ringo || null);

const guidanceAgenda = computed(() => {
  const agenda = ringoGuidance.value?.agenda;
  if (!agenda || typeof agenda !== "object") return null;
  if (!SUPPORTED_AGENDA_ACTIONS.has(agenda.next_action_type)) return null;

  return agenda;
});

const guidanceRingoDay = computed(() => {
  const ringoDay = ringoGuidance.value?.ringo_day;
  return ringoDay && typeof ringoDay === "object" ? ringoDay : null;
});

const preferLocalizedRingo = computed(() => {
  return String(locale.value || "").toLowerCase().startsWith("fa");
});

const backendCoachNarrative = computed(() => {
  const source = guidanceRingo.value || localizedRingo.value || {};

  return {
    message: source.message || "",
    mood: source.sprite_key || source.mood || source.sprite || "idle",
  };
});

const optionalNextNarrative = computed(() => {
  if (!isTodaySaved.value || !optionalNextMission.value) return null;

  return {
    message: t("missions.narrative.optionalNext", { mission: optionalNextMission.value.title }),
    mood: "happy",
  };
});

const finishedForTodayNarrative = computed(() => {
  if (!optionalNextSuppressed.value || !isTodaySaved.value) return null;

  return doneForTodayAgendaNarrative();
});

const dailySummaryNarrative = computed(() => {
  if (!isTodaySaved.value || !localizedMissions.value.length) return null;

  const summary = dailySummary.value;
  const nearestReminder = summary.reminded[0] || null;
  const reminderTime = formattedReminderLabel(nearestReminder?.reminder_at || guidanceAgenda.value?.next_reminder_at);
  const reminderSummaryTime = formattedReminderSummaryLabel(
    nearestReminder?.reminder_at || guidanceAgenda.value?.next_reminder_at,
  );
  const params = {
    done: summary.done.length,
    reminded: summary.reminded.length,
    skipped: summary.skipped.length,
    mission: nearestReminder?.title || t("missions.fallbackMission"),
    time: reminderTime,
    summaryTime: reminderSummaryTime,
  };
  const facts = [];

  if (summary.bonusDone.length) {
    facts.push(t("missions.dailySummary.bonusCompletedFact"));
  } else if (summary.done.length > 1) {
    facts.push(t("missions.dailySummary.multipleDoneFact", params));
  }

  if (nearestReminder) {
    const reminderDue = isReminderDue(nearestReminder);
    const reminderKey = reminderDue
      ? summary.reminded.length > 1
        ? "missions.dailySummary.dueReminderMultiple"
        : "missions.dailySummary.dueReminder"
      : summary.reminded.length > 1
        ? "missions.dailySummary.upcomingReminderMultiple"
        : "missions.dailySummary.upcomingReminder";
    facts.push(t(reminderKey, params));
  }

  if (summary.skipped.length) {
    facts.push(t("missions.dailySummary.skippedFact", params));
  }

  if (facts.length) {
    return {
      message: [
        t("missions.dailySummary.safePrefix"),
        ...facts,
      ].join(" "),
      mood: nearestReminder && isReminderDue(nearestReminder)
        ? "thinking"
        : summary.bonusDone.length || summary.done.length > 1
          ? "proud"
          : summary.skipped.length
            ? "concerned"
            : "calm",
    };
  }

  if (summary.bonusAvailable.length) {
    return {
      message: t("missions.dailySummary.bonusAvailable", params),
      mood: "happy",
    };
  }

  return {
    message: t("missions.dailySummary.allDone", params),
    mood: "sleeping",
  };
});

const agendaNarrative = computed(() => {
  const agenda = guidanceAgenda.value;
  if (!agenda) return null;
  const hasMissionTarget = agenda.next_mission_id !== null && agenda.next_mission_id !== undefined;
  const hasMissionCounts = Number(agenda.pending_count || 0)
    + Number(agenda.reminded_count || 0)
    + Number(agenda.skipped_count || 0)
    + Number(agenda.done_count || 0) > 0;

  if (agenda.next_action_type !== "done_for_today" && !hasMissionTarget) return null;
  if (agenda.next_action_type === "done_for_today" && !agenda.today_saved && !hasMissionCounts) return null;

  const mission = missionForAgenda(agenda);
  const usesMissionTarget = MISSION_AGENDA_ACTIONS.has(agenda.next_action_type);
  const missionIsReachable = mission && isAgendaMissionReachable(mission, agenda.next_action_type);

  if (optionalNextSuppressed.value && agenda.today_saved) {
    return doneForTodayAgendaNarrative();
  }

  if (usesMissionTarget && !missionIsReachable) {
    if (agenda.next_action_type === "skipped_optional") {
      return {
        message: t("missions.agendaNarrative.skippedOptionalGeneric"),
        mood: "concerned",
      };
    }

    if (agenda.today_saved) {
      return doneForTodayAgendaNarrative();
    }

    return null;
  }

  const missionTitle = mission?.title || t("missions.fallbackMission");
  const reminderTime = formattedReminderTime(agenda.next_reminder_at);
  const params = {
    mission: missionTitle,
    time: reminderTime,
  };

  if (agenda.next_action_type === "due_reminder") {
    return {
      message: t(
        agenda.today_saved
          ? "missions.agendaNarrative.dueReminderSaved"
          : "missions.agendaNarrative.dueReminder",
        params,
      ),
      mood: agenda.today_saved ? "happy" : "thinking",
    };
  }

  if (agenda.next_action_type === "upcoming_reminder") {
    return {
      message: reminderTime
        ? t(
          agenda.today_saved
            ? "missions.agendaNarrative.upcomingReminderSavedWithTime"
            : "missions.agendaNarrative.upcomingReminderWithTime",
          params,
        )
        : t(
          agenda.today_saved
            ? "missions.agendaNarrative.upcomingReminderSaved"
            : "missions.agendaNarrative.upcomingReminder",
          params,
        ),
      mood: agenda.today_saved ? "happy" : "calm",
    };
  }

  if (agenda.next_action_type === "primary_mission") {
    return {
      message: t("missions.agendaNarrative.primaryMission", params),
      mood: "focus",
    };
  }

  if (agenda.next_action_type === "optional_mission") {
    return {
      message: t("missions.agendaNarrative.optionalMission", params),
      mood: "happy",
    };
  }

  if (agenda.next_action_type === "skipped_optional") {
    return {
      message: t("missions.agendaNarrative.skippedOptional", params),
      mood: "concerned",
    };
  }

  if (agenda.next_action_type === "done_for_today") {
    return doneForTodayAgendaNarrative();
  }

  return null;
});

const coachNarrative = computed(() => {
  return interactionNarrative.value
    || finishedForTodayNarrative.value
    || dailySummaryNarrative.value
    || completionNarrative.value
    || agendaNarrative.value
    || optionalNextNarrative.value
    || backendCoachNarrative.value
    || {
      message: t("ringoCoach.fallbackMessage"),
      mood: "idle",
    };
});

const coachMessage = computed(() => {
  return coachNarrative.value?.message || t("ringoCoach.fallbackMessage");
});

const coachSprite = computed(() => {
  return coachNarrative.value?.mood || "idle";
});

const hasRingoGuidance = computed(() => !!guidanceRingo.value);

const coachPrimaryAction = computed(() => {
  if (hasRingoGuidance.value || isTodaySaved.value || focusMission.value) return null;

  return localizedRingo.value?.primary_action || null;
});

const coachSecondaryAction = computed(() => {
  if (hasRingoGuidance.value || isTodaySaved.value || focusMission.value) return null;

  return localizedRingo.value?.secondary_action || null;
});

const guidanceMission = computed(() => {
  const mission = ringoGuidance.value?.mission;
  if (!mission?.mission_id) return mission || null;

  const currentMission = localizedMissions.value.find((item) => item.mission_id === mission.mission_id);

  return currentMission ? { ...mission, ...currentMission } : mission;
});

const pendingMissions = computed(() => {
  return localizedMissions.value.filter((mission) => missionHasStatus(mission, "pending"));
});

const deferredMissions = computed(() => {
  return localizedMissions.value.filter((mission) => missionHasStatus(mission, "remind_later"));
});

const skippedMissions = computed(() => {
  return localizedMissions.value.filter((mission) => missionHasStatus(mission, "skipped"));
});

const manualFocusMission = computed(() => {
  if (!manualFocusMissionId.value) return null;

  return localizedMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, manualFocusMissionId.value);
  }) || null;
});

const activeInteractionMission = computed(() => {
  const missionId = manualFocusMissionId.value
    || reminderPanelMissionId.value
    || skipReasonPanelMissionId.value
    || busyId.value;

  if (!missionId) return null;

  return localizedMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, missionId);
  }) || null;
});

const focusMission = computed(() => {
  return activeInteractionMission.value
    || primaryReminderMission()
    || guidanceMission.value
    || pendingMissions.value[0]
    || skippedMissions.value[0]
    || deferredMissions.value[0]
    || localizedMissions.value[0]
    || null;
});

const focusMissionIntensity = computed(() => buildMissionIntensityMeta(focusMission.value, {
  optionalContext: isTodaySaved.value && !missionHasStatus(focusMission.value, "done"),
}));

const rawOtherMissions = computed(() => {
  if (!focusMission.value?.mission_id || !isFocusMissionRendered()) return localizedMissions.value;

  return localizedMissions.value.filter((mission) => {
    return !sameMissionId(mission.mission_id, focusMission.value.mission_id);
  });
});

const effectiveMissionRepresentatives = computed(() => {
  const representatives = [];
  const groups = new Map();

  localizedMissions.value.forEach((mission) => {
    const rootId = missionGroupRootId(mission);
    if (!rootId) return;

    if (!groups.has(rootId)) groups.set(rootId, []);
    groups.get(rootId).push(mission);
  });

  groups.forEach((items) => {
    const mainMission = items.find((mission) => normalizedMissionIntensity(mission) === "main") || null;
    const tinyMissions = items.filter((mission) => normalizedMissionIntensity(mission) === "tiny");
    const bonusMissions = items.filter((mission) => normalizedMissionIntensity(mission) === "bonus");
    const effectiveTiny = tinyMissions.find((mission) => {
      return missionHasStatus(mission, "remind_later", "done");
    }) || tinyMissions.find((mission) => {
      return isTinyMissionRevealed(mission) && missionHasStatus(mission, "pending", "skipped");
    }) || null;

    if (mainMission && missionHasStatus(mainMission, "done")) {
      representatives.push(mainMission);
      bonusMissions
        .filter((mission) => missionHasStatus(mission, "pending", "done", "remind_later", "skipped"))
        .forEach((mission) => representatives.push(mission));
      return;
    }

    if (effectiveTiny && missionHasStatus(effectiveTiny, "done", "remind_later")) {
      representatives.push(effectiveTiny);
      return;
    }

    if (mainMission) {
      representatives.push(mainMission);
      return;
    }

    if (effectiveTiny) {
      representatives.push(effectiveTiny);
      return;
    }

    const fallbackMission = items.find((mission) => {
      return missionHasStatus(mission, "remind_later", "done", "pending", "skipped");
    });

    if (fallbackMission) representatives.push(fallbackMission);
  });

  return representatives;
});

const curatedOtherMissions = computed(() => {
  const visibleMissionIds = new Set(effectiveMissionRepresentatives.value.map((mission) => String(mission.mission_id)));

  return rawOtherMissions.value.filter((mission) => {
    return visibleMissionIds.has(String(mission.mission_id)) && shouldShowOtherMission(mission);
  });
});

const showOtherMissionList = computed(() => {
  if (loading.value || error.value || !otherMissions.value.length) return false;

  return !isTodaySaved.value || !optionalNextSuppressed.value;
});

const safeOptionalMissions = computed(() => {
  const candidates = effectiveMissionRepresentatives.value.filter((mission) => {
    if (!missionHasStatus(mission, "pending")) return false;
    if (isFocusMissionRendered() && sameMissionId(mission.mission_id, focusMission.value?.mission_id)) return false;

    return true;
  });

  if (!candidates.length) return [];

  const focusChallengeId = focusMission.value?.challenge_id;

  return [...candidates].sort((a, b) => {
    return optionalMissionRank(a, focusChallengeId) - optionalMissionRank(b, focusChallengeId);
  });
});

const optionalNextMission = computed(() => {
  if (!isTodaySaved.value || optionalNextSuppressed.value) return null;

  return safeOptionalMissions.value[0] || null;
});

const otherMissions = computed(() => {
  return curatedOtherMissions.value.filter(shouldShowOtherMissionItem);
});

const dailySummary = computed(() => {
  const effectiveMissions = effectiveMissionRepresentatives.value;
  const done = effectiveMissions.filter((mission) => missionHasStatus(mission, "done"));
  const reminded = sortReminderMissions(
    effectiveMissions.filter((mission) => missionHasStatus(mission, "remind_later")),
  );
  const skipped = effectiveMissions.filter((mission) => missionHasStatus(mission, "skipped"));
  const bonusAvailable = otherMissions.value.filter((mission) => {
    return normalizedMissionIntensity(mission) === "bonus" && missionHasStatus(mission, "pending");
  });
  const bonusDone = localizedMissions.value.filter((mission) => {
    return normalizedMissionIntensity(mission) === "bonus" && missionHasStatus(mission, "done");
  });

  return {
    done,
    reminded,
    skipped,
    bonusAvailable,
    bonusDone,
  };
});

const optionalNextMissionIntensity = computed(() => buildMissionIntensityMeta(optionalNextMission.value, {
  optionalContext: true,
}));

const missionContextCount = computed(() => {
  const contexts = new Set();

  localizedMissions.value.forEach((mission) => {
    const contextId = mission?.enrollment_id || mission?.challenge_id || mission?.path_id;
    if (contextId !== null && contextId !== undefined) {
      contexts.add(String(contextId));
    }
  });

  return contexts.size;
});

const allMissionsDone = computed(() => {
  return !!localizedMissions.value.length && localizedMissions.value.every((mission) => {
    return missionHasStatus(mission, "done");
  });
});

const detailsMission = computed(() => {
  if (optionalNextMission.value) return optionalNextMission.value;
  if (showFocusMissionCard.value) return focusMission.value;
  if (allMissionsDone.value && missionContextCount.value > 1) return null;

  return focusMission.value;
});

const showFocusMissionCard = computed(() => {
  return isFocusMissionRendered();
});

const missionGuide = computed(() => {
  if (!localizedMissions.value.length || !focusMission.value) return null;

  const complete = localizedMissions.value.every((mission) => missionHasStatus(mission, "done"));
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

const showTodaySavedBody = computed(() => {
  if (optionalNextMission.value) return true;
  if (finishedForTodayNarrative.value) return false;
  if (agendaNarrative.value?.mood === "sleeping") return false;

  return guidanceAgenda.value?.next_action_type !== "done_for_today";
});

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

const anyMissionActionPanelOpen = computed(() => {
  return !!(reminderPanelMissionId.value || skipReasonPanelMissionId.value);
});

const showFocusMissionActions = computed(() => {
  return !!(
    focusMission.value
    && showFocusMissionCard.value
    && !anyMissionActionPanelOpen.value
    && !missionHasStatus(focusMission.value, "done")
  );
});

const showMissionNotice = computed(() => {
  if (!notice.value) return false;

  return noticeType.value !== "success" && !rewardSequenceSteps.value.length;
});

const coachActionPanel = computed(() => {
  return !!(
    showCoach.value
    || guidanceMission.value
    || guidanceActions.value.length
    || finishedForTodayNarrative.value
    || dailySummaryNarrative.value
    || agendaNarrative.value
    || todaySavedLabel.value
    || interactionNarrative.value
    || completionNarrative.value
  );
});

const reminderOptions = computed(() => {
  return REMINDER_OPTION_KEYS.map((key) => ({
    key,
    label: t(`missions.remindOptions.${key}`),
  }));
});

const skipReasonOptions = computed(() => {
  return SKIP_REASON_OPTIONS.map((option) => ({
    ...option,
    label: t(`missions.skipReasons.${option.key}`),
  }));
});

function clearNarrativeState() {
  interactionNarrative.value = null;
  completionNarrative.value = null;
}

function setNarrative(narrative) {
  const payload = {
    message: narrative?.message || "",
    mood: narrative?.mood || "idle",
  };

  if (narrative?.type === "completion") {
    completionNarrative.value = payload;
    interactionNarrative.value = null;
    return;
  }

  interactionNarrative.value = payload;
}

function setInteractionNarrative(messageKey, mood, params = {}) {
  setNarrative({
    message: t(messageKey, params),
    mood,
    type: "interaction",
  });
}

async function loadMissions() {
  loading.value = true;
  error.value = "";
  clearNarrativeState();
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

    applyMissionResponse(data, mission);
    await loadMissions();
    if (action === "remind") {
      manualFocusMissionId.value = mission.mission_id;
    }
    if (options.narrative) {
      setNarrative(options.narrative);
    } else if (action === "done") {
      completionNarrative.value = {
        message: t("missions.narrative.completed", { mission: mission.title }),
        mood: "proud",
      };
    }
  } catch (e) {
    const errorCode = e?.response?.data?.error || e?.message || String(e);
    if (action === "remind" && errorCode === "reminder_after_next_reset") {
      error.value = "";
      notice.value = t("missions.remindOptions.afterResetBlockedNotice");
      noticeType.value = "reminder";
      setInteractionNarrative("missions.narrative.remindBlockedAfterReset", "thinking");
    } else {
      error.value = errorCode;
    }
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
  if (!mission || missionHasStatus(mission, "done")) return null;

  notice.value = "";
  reminderPanelMissionId.value = mission.mission_id;
  skipReasonPanelMissionId.value = null;
  setInteractionNarrative("missions.narrative.remindOpen", "thinking");
  return focusMissionCard(mission);
}

function fallbackReminderAt() {
  return new Date(Date.now() + 2 * 60 * 60 * 1000);
}

function nextLocalReminderSlot(hour, minute = 0) {
  const now = new Date();
  const target = new Date(now);
  target.setHours(hour, minute, 0, 0);

  if (target <= now) {
    target.setDate(target.getDate() + 1);
  }

  return target;
}

function reminderAtForOption(key) {
  const now = new Date();

  if (key === "fifteenMinutes") {
    return new Date(now.getTime() + 15 * 60 * 1000);
  }

  if (key === "oneHour") {
    return new Date(now.getTime() + 60 * 60 * 1000);
  }

  if (key === "evening") {
    return nextLocalReminderSlot(18, 0);
  }

  if (key === "tonight") {
    return nextLocalReminderSlot(22, 0);
  }

  return fallbackReminderAt();
}

function isReminderPanelOpen(mission) {
  return !!(
    mission?.mission_id
    && sameMissionId(reminderPanelMissionId.value, mission.mission_id)
    && !missionHasStatus(mission, "done")
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
  const reminderAtDate = reminderAtForOption(option?.key);
  const tomorrowSlot = reminderTomorrowSlotKey(reminderAtDate);
  const afterNextReset = isAfterNextRingoReset(reminderAtDate);
  const reminderAt = reminderAtDate.toISOString();
  const timeLabel = formattedReminderTime(reminderAtDate);
  if (afterNextReset) {
    busyReminderOption.value = "";
    notice.value = t("missions.remindOptions.afterResetBlockedNotice");
    noticeType.value = "reminder";
    setInteractionNarrative("missions.narrative.remindBlockedAfterReset", "thinking");
    return null;
  }

  const confirmationKey = afterNextReset
    ? "missions.remindOptions.confirmationAfterReset"
    : option?.key === "evening" && tomorrowSlot === "evening"
    ? "missions.remindOptions.confirmationTomorrowEvening"
    : option?.key === "tonight" && tomorrowSlot === "night"
      ? "missions.remindOptions.confirmationTomorrowNight"
      : "missions.remindOptions.confirmation";
  const narrativeKey = afterNextReset
    ? "missions.narrative.remindConfirmedAfterReset"
    : option?.key === "evening" && tomorrowSlot === "evening"
    ? "missions.narrative.remindConfirmedTomorrowEvening"
    : option?.key === "tonight" && tomorrowSlot === "night"
      ? "missions.narrative.remindConfirmedTomorrowNight"
      : "missions.narrative.remindConfirmed";
  const successNotice = option?.label
    ? t(confirmationKey, { time: option.label, exactTime: timeLabel })
    : t("missions.remindOptions.fallbackConfirmation");

  return runMissionAction(
    mission,
    "remind",
    () => api.post(`/me/missions/${mission.mission_id}/remind-later`, {
      reminder_at: reminderAt,
    }),
    {
      successNotice,
      narrative: {
        message: option?.label
          ? t(narrativeKey, { time: option.label, exactTime: timeLabel })
          : t("missions.narrative.remindConfirmedFallback"),
        mood: "happy",
        type: "interaction",
      },
    },
  );
}

function closeReminderPanel() {
  reminderPanelMissionId.value = null;
  clearNarrativeState();
}

function skipMission(mission) {
  if (!mission || missionHasStatus(mission, "done", "skipped")) return null;

  notice.value = "";
  skipReasonPanelMissionId.value = mission.mission_id;
  reminderPanelMissionId.value = null;
  setInteractionNarrative("missions.narrative.skipOpen", "concerned");
  return focusMissionCard(mission);
}

function isSkipReasonPanelOpen(mission) {
  return !!(
    mission?.mission_id
    && sameMissionId(skipReasonPanelMissionId.value, mission.mission_id)
    && !missionHasStatus(mission, "done", "skipped")
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

function closeSkipReasonPanel() {
  skipReasonPanelMissionId.value = null;
  clearNarrativeState();
}

function selectSkipReason(mission, reason) {
  if (!mission) return null;

  busySkipReason.value = reason?.key || "";
  const successNotice = reason?.key && reason.key !== "withoutReason"
    ? t("missions.skipReasons.confirmationWithReason", { reason: reason.label })
    : t("missions.skipReasons.confirmationWithoutReason");
  const requestBody = reason?.reason ? { reason: reason.reason } : {};

  return runMissionAction(
    mission,
    "skip",
    () => postMissionSkip(mission.mission_id, requestBody),
    {
      successNotice,
      narrative: {
        message: reason?.key && reason.key !== "withoutReason"
          ? t("missions.narrative.skipConfirmedWithReason", { reason: reason.label })
          : t("missions.narrative.skipConfirmedWithoutReason"),
        mood: "concerned",
        type: "interaction",
      },
    },
  );
}

async function postMissionSkip(missionId, body) {
  const hasReason = !!body?.reason;

  try {
    return await api.post(`/me/missions/${missionId}/skip`, body || {});
  } catch (e) {
    const error = e?.response?.data?.error;
    const canRetryWithoutReason = hasReason && [
      "invalid_skip_reason",
      "skip_reason_too_long",
      "unsupported_skip_reason",
    ].includes(error);

    if (!canRetryWithoutReason) {
      throw e;
    }

    return api.post(`/me/missions/${missionId}/skip`, {});
  }
}

function applyMissionResponse(data, fallbackMission) {
  const responseMission = data?.mission;
  const missionId = responseMission?.mission_id || fallbackMission?.mission_id;
  if (!missionId) return;

  missions.value = missions.value.map((mission) => {
    if (!sameMissionId(mission.mission_id, missionId)) return mission;

    return {
      ...mission,
      ...(responseMission || {}),
      title: mission.title,
      description: mission.description,
      challenge_name: mission.challenge_name,
      path_title: mission.path_title,
    };
  });
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
  optionalNextSuppressed.value = true;
  manualFocusMissionId.value = null;
  showOtherMissions.value = false;
  setInteractionNarrative("missions.finishedForTodayMessage", "sleeping");
}

function focusOptionalNextMission(mission) {
  if (!mission) return null;

  manualFocusMissionId.value = mission.mission_id;
  showOtherMissions.value = false;
  return focusMissionCard(mission);
}

function remindOptionalNextMission(mission) {
  if (!mission) return null;

  manualFocusMissionId.value = mission.mission_id;
  showOtherMissions.value = false;
  return remindLater(mission);
}

function skipOptionalNextMission(mission) {
  if (!mission) return null;

  manualFocusMissionId.value = mission.mission_id;
  showOtherMissions.value = false;
  return skipMission(mission);
}

function missionForAgenda(agenda) {
  const missionId = agenda?.next_mission_id;
  if (!missionId) return null;

  return localizedMissions.value.find((mission) => {
    return sameMissionId(mission.mission_id, missionId);
  }) || null;
}

function doneForTodayAgendaNarrative() {
  return {
    message: t("missions.agendaNarrative.doneForToday"),
    mood: "sleeping",
  };
}

function isAgendaMissionReachable(mission, actionType) {
  if (!mission?.mission_id) return false;

  if (actionType === "optional_mission") {
    return !!(
      optionalNextMission.value
      && sameMissionId(mission.mission_id, optionalNextMission.value.mission_id)
    );
  }

  if (sameMissionId(mission.mission_id, focusMission.value?.mission_id)) {
    return showFocusMissionCard.value && !missionHasStatus(mission, "done", "locked");
  }

  if (optionalNextMission.value && sameMissionId(mission.mission_id, optionalNextMission.value.mission_id)) {
    return true;
  }

  return otherMissions.value.some((item) => {
    return sameMissionId(item.mission_id, mission.mission_id)
      && !missionHasStatus(item, "done", "locked");
  });
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

function buildMissionIntensityMeta(mission, options = {}) {
  if (!mission) return null;

  const intensity = normalizedMissionIntensity(mission);
  const optionalContext = Boolean(options.optionalContext);
  const labelKey = optionalContext && intensity === "main"
    ? "missions.intensity.optional"
    : `missions.intensity.${intensity}`;
  const detailKey = optionalContext && intensity === "main"
    ? "missions.intensity.optionalDetail"
    : `missions.intensity.${intensity}Detail`;
  const detailParts = [t(detailKey)];
  const minutes = missionEstimatedMinutes(mission);

  if (minutes) {
    detailParts.push(t("missions.intensity.minutes", { count: minutes }));
  }

  return {
    intensity,
    label: t(labelKey),
    detail: detailParts.filter(Boolean).join(" · "),
  };
}

function parentMissionFor(mission) {
  if (!mission?.parent_mission_id) return null;

  return localizedMissions.value.find((item) => {
    return sameMissionId(item.mission_id, mission.parent_mission_id);
  }) || null;
}

function childMissionsFor(mission) {
  if (!mission?.mission_id) return [];

  return localizedMissions.value.filter((item) => {
    return sameMissionId(item.parent_mission_id, mission.mission_id);
  });
}

function hasDoneTinyChild(mission) {
  return childMissionsFor(mission).some((item) => {
    return isTinyMission(item) && isTinyMissionRevealed(item) && missionHasStatus(item, "done");
  });
}

function hasRepresentativeTinyChild(mission) {
  return childMissionsFor(mission).some((item) => {
    return isTinyMission(item)
      && isTinyMissionRevealed(item)
      && missionHasStatus(item, "done", "remind_later");
  });
}

function isFocusedTinyChildOf(mission) {
  return !!(
    mission?.mission_id
    && isTinyMission(focusMission.value)
    && sameMissionId(focusMission.value?.parent_mission_id, mission.mission_id)
  );
}

function isTinyMissionRevealed(mission) {
  return !!(
    mission?.mission_id
    && revealedTinyMissionIds.value.has(String(mission.mission_id))
  );
}

function missionGroupRootId(mission) {
  if (!mission?.mission_id) return "";

  return String(mission.parent_mission_id || mission.mission_id);
}

function sameMissionGroup(a, b) {
  const aRoot = missionGroupRootId(a);
  const bRoot = missionGroupRootId(b);

  return !!(aRoot && bRoot && aRoot === bRoot);
}

function shouldShowOtherMission(mission) {
  if (!mission?.mission_id) return false;
  if (sameMissionId(mission.mission_id, focusMission.value?.mission_id) && isFocusMissionRendered()) return true;

  const intensity = normalizedMissionIntensity(mission);
  const parentMission = parentMissionFor(mission);

  if (intensity === "main" && (hasRepresentativeTinyChild(mission) || isFocusedTinyChildOf(mission))) {
    return false;
  }

  if (intensity === "tiny") {
    if (!isTinyMissionRevealed(mission)) return false;
    if (parentMission && missionHasStatus(parentMission, "done") && missionHasStatus(mission, "pending")) {
      return false;
    }
    return true;
  }

  if (intensity === "bonus" && parentMission && !missionHasStatus(parentMission, "done")) {
    return false;
  }

  if (intensity === "bonus" && parentMission && hasDoneTinyChild(parentMission)) {
    return false;
  }

  return true;
}

function shouldShowOtherMissionItem(mission) {
  if (!mission?.mission_id) return false;

  if (optionalNextMission.value) {
    if (sameMissionId(mission.mission_id, optionalNextMission.value.mission_id)) return false;
    if (sameMissionGroup(mission, optionalNextMission.value)) return false;
  }

  if (showFocusMissionCard.value && focusMission.value) {
    if (sameMissionId(mission.mission_id, focusMission.value.mission_id)) return false;
    if (sameMissionGroup(mission, focusMission.value)) return false;
  }

  return true;
}

function isFocusMissionRendered() {
  if (!focusMission.value) return false;
  if (!isTodaySaved.value) return true;
  if (missionHasStatus(focusMission.value, "done")) return false;
  if (missionHasStatus(focusMission.value, "remind_later")) return true;

  return !!(
    sameMissionId(focusMission.value.mission_id, manualFocusMissionId.value)
    || isReminderPanelOpen(focusMission.value)
    || isSkipReasonPanelOpen(focusMission.value)
  );
}

function primaryReminderMission() {
  return sortReminderMissions(
    effectiveMissionRepresentatives.value.filter((mission) => {
      return missionHasStatus(mission, "remind_later");
    }),
  )[0] || null;
}

function missionItemIntensity(mission) {
  return buildMissionIntensityMeta(mission, {
    optionalContext: isTodaySaved.value,
  });
}

function missionTypeLabel(mission) {
  const intensity = normalizedMissionIntensity(mission);

  if (intensity === "main") return t("missions.typeChips.main");
  if (intensity === "tiny") return t("missions.typeChips.tiny");
  if (intensity === "bonus") return t("missions.typeChips.bonus");

  return t("missions.typeChips.main");
}

function missionChips(mission) {
  if (!mission) return [];

  const status = normalizedMissionStatus(mission.status);
  const knownStatus = ["pending", "done", "skipped", "remind_later"].includes(status)
    ? status
    : "pending";

  return [
    {
      key: "type",
      type: normalizedMissionIntensity(mission),
      label: missionTypeLabel(mission),
    },
    {
      key: "status",
      type: knownStatus,
      label: t(`missions.status.${knownStatus}`),
    },
  ];
}

function missionParentCopy(mission) {
  const parentMission = parentMissionFor(mission);
  if (!parentMission) return "";

  return t("missions.variantOf", { mission: parentMission.title });
}

function optionalMissionRank(mission, focusChallengeId) {
  const intensity = normalizedMissionIntensity(mission);
  const isDifferentChallenge = !sameMissionId(mission?.challenge_id, focusChallengeId);

  if (intensity === "main" && isDifferentChallenge) return 0;
  if (intensity === "main") return 1;
  if (intensity === "bonus" && isDifferentChallenge) return 2;
  if (intensity === "bonus") return 3;
  if (isDifferentChallenge) return 4;

  return 5;
}

function normalizedMissionStatus(status) {
  const value = String(status || "pending")
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");

  if (["done", "complete", "completed"].includes(value)) return "done";
  if (["skipped", "skip"].includes(value)) return "skipped";
  if (["remind_later", "reminder_set", "reminded"].includes(value)) return "remind_later";

  return value || "pending";
}

function missionHasStatus(mission, ...statuses) {
  const normalized = normalizedMissionStatus(mission?.status);

  return statuses.includes(normalized);
}

function missionStatusLabel(mission) {
  const status = normalizedMissionStatus(mission?.status);
  const knownStatus = ["pending", "done", "skipped", "remind_later", "locked"].includes(status)
    ? status
    : "pending";

  return t(`missions.status.${knownStatus}`);
}

function formattedReminderTime(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat(locale.value || undefined, {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function parsedNextResetAt() {
  const value = guidanceRingoDay.value?.next_reset_at;
  if (!value) return null;

  const reset = new Date(value);
  return Number.isNaN(reset.getTime()) ? null : reset;
}

function isAfterNextRingoReset(value) {
  const reset = parsedNextResetAt();
  if (!reset) return false;

  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return false;

  return date.getTime() >= reset.getTime();
}

function isTomorrowLocalDate(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return false;

  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);

  return date.getFullYear() === tomorrow.getFullYear()
    && date.getMonth() === tomorrow.getMonth()
    && date.getDate() === tomorrow.getDate();
}

function reminderTomorrowSlotKey(date) {
  if (!isTomorrowLocalDate(date)) return "";

  const hour = date.getHours();
  const minute = date.getMinutes();

  if (hour === 18 && minute === 0) return "evening";
  if (hour === 22 && minute === 0) return "night";

  return "default";
}

function formattedReminderLabel(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  const time = formattedReminderTime(value);
  const tomorrowSlot = reminderTomorrowSlotKey(date);

  if (isAfterNextRingoReset(date)) {
    return t("missions.remindOptions.afterReset", { time });
  }

  if (tomorrowSlot === "evening") {
    return t("missions.remindOptions.tomorrowEveningAt", { time });
  }

  if (tomorrowSlot === "night") {
    return t("missions.remindOptions.tomorrowNightAt", { time });
  }

  if (tomorrowSlot === "default") {
    return t("missions.remindOptions.tomorrowAt", { time });
  }

  return time;
}

function formattedReminderSummaryLabel(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  const label = formattedReminderLabel(value);
  if (!label) return "";

  if (isAfterNextRingoReset(date)) {
    return t("missions.remindOptions.afterResetAt", { time: formattedReminderTime(value) });
  }

  return reminderTomorrowSlotKey(date)
    ? label
    : t("missions.remindOptions.atTime", { time: label });
}

function reminderTimestamp(mission) {
  if (!mission?.reminder_at) return Number.POSITIVE_INFINITY;

  const date = new Date(mission.reminder_at);
  const timestamp = date.getTime();

  return Number.isNaN(timestamp) ? Number.POSITIVE_INFINITY : timestamp;
}

function isReminderDue(mission) {
  return reminderTimestamp(mission) <= Date.now();
}

function sortReminderMissions(items) {
  return [...items].sort((a, b) => {
    const aDue = isReminderDue(a);
    const bDue = isReminderDue(b);

    if (aDue !== bDue) return aDue ? -1 : 1;

    return reminderTimestamp(a) - reminderTimestamp(b);
  });
}

function missionStatusCopy(mission) {
  if (!mission) return "";

  const status = normalizedMissionStatus(mission.status);

  if (status === "skipped") {
    return t("missions.statusCopy.skipped");
  }

  if (status === "remind_later") {
    const time = formattedReminderLabel(mission.reminder_at);
    if (isReminderDue(mission)) {
      return time
        ? t("missions.statusCopy.reminderDueWithTime", { time })
        : t("missions.statusCopy.reminderDue");
    }

    return time
      ? t("missions.statusCopy.reminderWithTime", { time })
      : t("missions.statusCopy.reminder");
  }

  if (status === "done") {
    return t("missions.statusCopy.done");
  }

  return mission.ringo_message || "";
}

function isPendingTinyMission(mission) {
  return isTinyMission(mission) && missionHasStatus(mission, "pending");
}

function sameMissionId(a, b) {
  if (a === null || a === undefined || b === null || b === undefined) return false;

  return String(a) === String(b);
}

function findTinyMissionFor(mission) {
  if (isPendingTinyMission(mission)) return mission;

  if (mission?.mission_id) {
    const linkedTinyMission = linkedTinyMissionFor(mission);

    if (linkedTinyMission) return linkedTinyMission;
  }

  return null;
}

function linkedTinyMissionFor(mission) {
  if (!mission?.mission_id) return null;

  return localizedMissions.value.find((item) => {
    return isPendingTinyMission(item) && sameMissionId(item.parent_mission_id, mission.mission_id);
  }) || null;
}

function isGuidanceActionDisabled(action) {
  const mission = missionForGuidanceAction(action);

  if (action.type === "make_smaller" || action.type === "too_tired") return false;
  if (!mission) return action.type !== "make_smaller" && action.type !== "too_tired";
  if (missionHasStatus(mission, "done")) return true;
  if (action.type === "skip_today") return missionHasStatus(mission, "skipped");

  return false;
}

function guidanceActionByType(type) {
  return guidanceActions.value.find((action) => action.type === type) || null;
}

function guidanceActionForMission(type, mission) {
  return guidanceActionByType(type) || {
    type,
    mission_id: mission?.mission_id,
  };
}

function shouldShowFocusSupportAction(type, mission) {
  if (!["make_smaller", "too_tired"].includes(type)) return false;
  if (!mission || missionHasStatus(mission, "done", "skipped", "remind_later")) return false;
  if (normalizedMissionIntensity(mission) !== "main") return false;
  if (!linkedTinyMissionFor(mission)) return false;

  const action = guidanceActionForMission(type, mission);
  if (isGuidanceActionDisabled(action)) return false;

  return true;
}

function handleFocusSupportAction(type, mission) {
  handleGuidanceAction(guidanceActionForMission(type, mission));
}

function shouldShowOptionalNextSupportAction(type, mission) {
  if (!["make_smaller", "too_tired"].includes(type)) return false;
  if (!mission || normalizedMissionIntensity(mission) !== "main") return false;
  if (missionHasStatus(mission, "done", "skipped", "remind_later")) return false;

  return !!linkedTinyMissionFor(mission);
}

function handleOptionalNextSupportAction(type, mission) {
  if (!shouldShowOptionalNextSupportAction(type, mission)) return;

  focusTinyMissionFromAction(
    {
      type,
      mission_id: mission.mission_id,
    },
    type === "too_tired"
      ? "missions.ringoActions.tooTiredTinyMessage"
      : "missions.ringoActions.makeSmallerTinyMessage",
    type === "too_tired"
      ? "missions.ringoActions.tooTiredMessage"
      : "missions.ringoActions.makeSmallerMessage",
  );
}

function showMissionItemActions(mission) {
  return !!(
    mission
    && !isReminderPanelOpen(mission)
    && !isSkipReasonPanelOpen(mission)
  );
}

function focusTinyMissionFromAction(action, messageKey, fallbackMessageKey) {
  const mission = missionForGuidanceAction(action);
  const tinyMission = findTinyMissionFor(mission);

  if (!tinyMission) {
    setInteractionNarrative(fallbackMessageKey, action.type === "too_tired" ? "sleeping" : "thinking");
    return;
  }

  revealedTinyMissionIds.value = new Set([
    ...revealedTinyMissionIds.value,
    String(tinyMission.mission_id),
  ]);
  manualFocusMissionId.value = tinyMission.mission_id;
  setInteractionNarrative(messageKey, action.type === "too_tired" ? "sleeping" : "encouraging", {
    mission: tinyMission.title,
  });
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

.missionStatusCopy {
  display: block;
  margin-top: 2px;
  color: rgba(247, 215, 116, 0.82);
  font-size: 0.86rem;
  font-weight: 720;
  line-height: 1.5;
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

.optionalNextStep {
  display: grid;
  gap: var(--s-10);
  padding: 12px;
  border: 1px solid rgba(247, 215, 116, 0.18);
  border-radius: 18px;
  background: rgba(247, 215, 116, 0.055);
}

.optionalNextCopy h3,
.optionalNextCopy p,
.optionalNextMission p {
  margin: 0;
}

.optionalNextCopy h3 {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1rem;
}

.optionalNextCopy p:not(.eyebrow) {
  margin-top: 5px;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.optionalNextMission {
  display: grid;
  gap: 6px;
  padding: 11px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  background: rgba(5, 10, 18, 0.20);
}

.optionalNextMission strong {
  color: rgba(255, 255, 255, 0.92);
}

.optionalNextMission p {
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.5;
}

.optionalNextActions {
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

.otherMissionContext {
  margin-top: 6px;
  max-width: 620px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.5;
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

.missionItem.optionalNext {
  border-color: rgba(247, 215, 116, 0.24);
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

.missionChips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  margin-bottom: 6px;
}

.missionChip {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.045);
  font-size: var(--cap);
  font-weight: 850;
  line-height: 1.2;
}

.missionChip.main,
.missionChip.pending {
  border-color: rgba(110, 229, 255, 0.18);
  color: rgba(219, 244, 255, 0.92);
  background: rgba(110, 229, 255, 0.07);
}

.missionChip.tiny,
.missionChip.done {
  border-color: rgba(74, 222, 128, 0.22);
  color: rgba(187, 247, 208, 0.94);
  background: rgba(74, 222, 128, 0.07);
}

.missionChip.bonus,
.missionChip.remind_later {
  border-color: rgba(247, 215, 116, 0.24);
  color: rgba(253, 230, 138, 0.94);
  background: rgba(247, 215, 116, 0.07);
}

.missionChip.skipped {
  color: rgba(255, 255, 255, 0.68);
  background: rgba(255, 255, 255, 0.04);
}

.missionItem p:not(.missionMeta) {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.missionRelationCopy {
  display: block;
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.50);
  font-size: var(--cap);
  font-weight: 760;
  line-height: 1.4;
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
  .remindOptions :deep(.btn),
  .skipReasons :deep(.btn),
  .completedChoices :deep(.btn),
  .optionalNextActions :deep(.btn),
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
