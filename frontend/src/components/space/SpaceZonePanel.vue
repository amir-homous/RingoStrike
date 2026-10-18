<template>
  <aside class="zonePanel" :class="`mode-${mode}`">
    <div class="panelHead">
      <div class="panelTitleWrap">
        <span v-if="pathIcon" class="iconFrame panelIconFrame" aria-hidden="true">
          <img :src="pathIcon" alt="" class="pathIcon iconOnDark" />
        </span>
        <div>
          <p class="panelKicker">{{ zone.pathName || zone.path_key }}</p>
          <h3>{{ zone.title }}</h3>
        </div>
      </div>

      <button v-if="closable" type="button" class="closeButton" @click="$emit('close')">
        {{ t("space.close") }}
      </button>
    </div>

    <section v-if="ringoGuidance" class="ringoGuide" :class="ringoGuidance.tone">
      <RingoMoodFigure
        :mood="ringoGuidance.mood"
        :alt="t('space.ringoGuide.eyebrow')"
        size="sm"
        framed
      />
      <div class="ringoGuideCopy">
        <span class="sectionLabel">{{ t("space.ringoGuide.eyebrow") }}</span>
        <strong>{{ ringoGuidance.title }}</strong>
        <p>{{ ringoGuidance.message }}</p>
        <div v-if="ringoGuidance.actions.length" class="ringoGuideActions">
          <button
            v-for="action in ringoGuidance.actions"
            :key="action.key"
            type="button"
            class="actionLink"
            :class="[action.variant || 'secondary', { compact: action.compact }]"
            :disabled="action.disabled"
            :title="action.hint || action.label"
            :aria-label="action.hint || action.label"
            @click="handleRingoAction(action)"
          >
            <img
              v-if="action.compact && actionIcon(action)"
              :src="actionIcon(action)"
              alt=""
              class="actionIcon iconOnDark"
              aria-hidden="true"
            />
            <span :class="{ srOnly: action.compact }">{{ action.label }}</span>
            <span v-if="action.compact" class="actionTooltip" aria-hidden="true">
              {{ action.hint || action.label }}
            </span>
          </button>
        </div>
        <div v-if="ringoChoicePanel" class="ringoChoicePanel">
          <p>{{ ringoChoicePanel.prompt }}</p>
          <div class="ringoChoiceGrid">
            <button
              v-for="option in ringoChoicePanel.options"
              :key="option.key"
              type="button"
              class="choicePill"
              :disabled="selectedMissionLoading"
              @click="handleRingoChoice(option)"
            >
              {{ option.label }}
            </button>
          </div>
          <button type="button" class="choiceBack" @click="closeRingoChoicePanel">
            {{ t("missions.backToMissionActions") }}
          </button>
        </div>
      </div>
    </section>

    <section
      v-if="roomFeedback"
      class="roomFeedbackPanel"
      :class="roomFeedback.type"
      aria-live="polite"
    >
      <span class="sectionLabel">{{ t("space.feedback.label") }}</span>
      <strong>{{ roomFeedback.title }}</strong>
      <p>{{ roomFeedback.text }}</p>
    </section>

    <nav
      v-if="mode !== 'zone'"
      class="shellStateNav"
      :aria-label="t('space.shell.navLabel')"
    >
      <button
        type="button"
        class="shellStateButton"
        :class="{ active: mode === 'zone' }"
        @click="$emit('change-mode', 'zone')"
      >
        {{ t("space.shell.navZone") }}
      </button>
      <button
        v-if="zone.pathDetail"
        type="button"
        class="shellStateButton"
        :class="{ active: mode === 'path' }"
        @click="$emit('change-mode', 'path')"
      >
        {{ t("space.shell.navPath") }}
      </button>
      <button
        v-if="activeShellChallenge"
        type="button"
        class="shellStateButton"
        :class="{ active: mode === 'challenge' }"
        @click="$emit('change-mode', 'challenge')"
      >
        {{ t("space.shell.navChallenge") }}
      </button>
      <button
        v-if="activeShellMission"
        type="button"
        class="shellStateButton"
        :class="{ active: mode === 'mission' }"
        @click="$emit('change-mode', 'mission')"
      >
        {{ t("space.shell.navMission") }}
      </button>
      <button
        v-if="showRestState"
        type="button"
        class="shellStateButton"
        :class="{ active: mode === 'rest' }"
        @click="$emit('change-mode', 'rest')"
      >
        {{ t("space.shell.navRest") }}
      </button>
    </nav>

    <div class="panelWorkSurface">
      <div v-if="mode === 'rest'" class="panelSection shellPanel restPanel">
        <span class="sectionLabel">{{ t("space.shell.restLabel") }}</span>
        <strong>{{ restMomentText }}</strong>
        <p>{{ t("space.shell.restText") }}</p>

        <div class="restSummaryGrid" :aria-label="t('space.shell.restMomentumLabel')">
          <article
            v-for="item in restSummaryItems"
            :key="item.key"
            class="restSummaryItem"
          >
            <strong>{{ item.value }}</strong>
            <small>{{ item.label }}</small>
          </article>
        </div>

        <div class="restReminderBlock" :class="{ due: dueReminderCount > 0 }">
          <div class="restReminderHead">
            <span class="sectionLabel">{{ t("space.shell.restReminderLabel") }}</span>
            <strong>{{ restReminderSummary }}</strong>
          </div>

          <div v-if="visibleDueReminders.length" class="restReminderList">
            <article
              v-for="reminder in visibleDueReminders"
              :key="reminder.id"
              class="restReminderItem"
            >
              <strong>{{ reminder.title }}</strong>
              <span>
                {{ reminder.challengeName || t("common.challenge") }}
                <template v-if="formattedReminderTime(reminder.reminderAt)">
                  · {{ formattedReminderTime(reminder.reminderAt) }}
                </template>
              </span>
              <button
                v-if="missionForReminder(reminder)"
                type="button"
                class="restReminderAction"
                @click="reviewReminder(reminder)"
              >
                {{ t("space.shell.restReminderReview") }}
              </button>
            </article>
          </div>

          <p v-else class="emptyText">{{ restReminderEmptyText }}</p>
        </div>
      </div>

      <section
        v-if="mode === 'zone'"
        class="zoneProgressSnapshot"
        :class="{ complete: firstRewardUnlocked }"
      >
        <div class="snapshotStats">
          <article class="snapshotItem">
            <span class="sectionLabel">
              {{ t("space.unlockedCount", { count: unlockedCount }) }}
            </span>
            <strong>{{ unlockedCount }}</strong>
            <p>{{ unlockedSummaryText }}</p>
          </article>

          <article class="snapshotItem">
            <span class="sectionLabel">
              {{ t("space.lockedPreviewCount", { count: lockedPreviewCount }) }}
            </span>
            <strong>{{ lockedPreviewCount }}</strong>
            <p>{{ lockedPreviewSummaryText }}</p>
          </article>
        </div>

        <p
          v-if="zone.locked_preview_objects.length"
          class="hintText"
        >
          {{ t("space.lockedPreviewHint") }}
        </p>

        <p
          v-if="firstRewardText"
          class="nextReward"
          :class="{ complete: firstRewardUnlocked }"
        >
          {{ firstRewardText }}
        </p>
      </section>

      <section v-if="mode === 'zone'" class="objectHistoryPanel">
        <div class="sectionHeaderLine">
          <span class="sectionLabel">{{ t("space.objectHistory.label") }}</span>
          <small>
            {{ t("space.objectHistory.summary", {
              saved: unlockedCount,
              preview: lockedPreviewCount,
            }) }}
          </small>
        </div>

        <div v-if="zoneObjectHistoryItems.length" class="objectHistoryList">
          <article
            v-for="item in zoneObjectHistoryItems"
            :key="item.key"
            class="objectHistoryItem"
            :class="item.state"
          >
            <span class="objectHistoryMark" aria-hidden="true">{{ item.mark }}</span>
            <span class="objectHistoryCopy">
              <span class="objectHistoryTitle">
                <strong>{{ item.title }}</strong>
                <em>{{ item.status }}</em>
              </span>
              <span>{{ item.text }}</span>
              <small>{{ item.source }}</small>
            </span>
          </article>
        </div>

        <p v-else class="emptyText">{{ t("space.objectHistory.empty") }}</p>
      </section>

      <div
        v-if="mode === 'zone' && zone.action"
        class="panelSection zoneAction"
        :class="zone.action.state"
      >
        <span class="sectionLabel">{{ t("space.zoneAction.label") }}</span>
        <strong>{{ zone.action.title }}</strong>
        <p>{{ zone.action.text }}</p>
        <p class="flowHint">{{ actionFlowHint }}</p>
      </div>

      <div v-if="mode === 'path'" class="panelSection shellPanel">
      <span class="sectionLabel">{{ t("space.shell.pathLabel") }}</span>
      <span class="shellTitleLine">
        <span v-if="pathIcon" class="iconFrame inlineIconFrame" aria-hidden="true">
          <img :src="pathIcon" alt="" class="inlineIcon iconOnDark" />
        </span>
        <strong>{{ t("space.shell.pathTitle", { path: zone.title }) }}</strong>
      </span>
      <p>{{ t("space.shell.pathText") }}</p>
      <div v-if="pathStats" class="pathStats">
        <span>
          <strong>{{ pathStats.joined }}</strong>
          <small>{{ t("space.shell.joinedChallenges") }}</small>
        </span>
        <span>
          <strong>{{ pathStats.today }}</strong>
          <small>{{ t("space.shell.todayMissions") }}</small>
        </span>
      </div>
      <div
        v-if="pathStats?.progressTotal"
        class="pathProgressBlock"
        :style="{ '--progress-percent': `${pathStats.progressPercent}%` }"
      >
        <div class="pathProgressHead">
          <span>{{ t("space.shell.pathProgress") }}</span>
          <strong>{{ pathStats.progressPercent }}%</strong>
        </div>
        <div class="pathProgressTrack" aria-hidden="true">
          <span></span>
        </div>
        <small>
          {{ t("space.shell.pathProgressCount", {
            done: pathStats.progressDone,
            total: pathStats.progressTotal,
          }) }}
        </small>
      </div>
      <p v-if="pathError" class="pathError">{{ pathError }}</p>
      <p v-else-if="pathLoading" class="emptyText">{{ t("space.shell.pathLoading") }}</p>
      <div v-else-if="pathChallenges.length" class="challengeLadder">
        <div class="ladderHead">
          <strong>{{ t("space.shell.challengeLadder") }}</strong>
          <small>{{ t("space.shell.challengeLadderHint") }}</small>
        </div>

        <article
          v-for="challenge in pathChallenges"
          :key="challenge.id"
          class="ladderItem"
          :class="{
            current: challenge.isCurrent,
            joined: challenge.isJoined,
            done: challenge.todayChecked,
            available: !challenge.isJoined,
            recommended: isRecommendedChallenge(challenge),
            selected: selectedPathChallenge?.id === challenge.id,
          }"
          role="button"
          tabindex="0"
          :aria-pressed="selectedPathChallenge?.id === challenge.id"
          @click="selectChallenge(challenge)"
          @keydown.enter.prevent="selectChallenge(challenge)"
          @keydown.space.prevent="selectChallenge(challenge)"
        >
          <span class="iconFrame ladderIconFrame" aria-hidden="true">
            <img :src="challengeIconFor(challenge)" alt="" class="ladderIcon iconOnDark" />
          </span>

          <div class="ladderCopy">
            <span class="ladderStatus">{{ challengeStatusLabel(challenge) }}</span>
            <strong>{{ challenge.name }}</strong>
            <p v-if="challenge.description">{{ challenge.description }}</p>
            <div class="missionMeta">
              <span>{{ t("paths.stage", { stage: challenge.stage || 1 }) }}</span>
              <span v-if="challenge.missionCount">
                {{ t("space.shell.missionCount", { count: challenge.missionCount }) }}
              </span>
              <span v-if="challenge.estimatedDays">
                {{ t("common.days", { count: challenge.estimatedDays }) }}
              </span>
            </div>
            <div
              v-if="challenge.missionCount"
              class="ladderProgress"
              :style="{ '--progress-percent': `${challengeProgressPercent(challenge)}%` }"
              aria-hidden="true"
            >
              <span></span>
            </div>
            <small v-if="challenge.missionCount" class="progressText">
              {{ challenge.doneCount || 0 }}/{{ challenge.missionCount }}
            </small>
          </div>
        </article>
      </div>
      <div
        v-if="!pathError && !pathLoading && selectedPathChallenge"
        class="selectedChallengePanel"
      >
        <span class="sectionLabel">{{ t("space.shell.selectedChallengeLabel") }}</span>
        <span class="shellTitleLine">
          <span class="iconFrame inlineIconFrame" aria-hidden="true">
            <img :src="challengeIconFor(selectedPathChallenge)" alt="" class="inlineIcon iconOnDark" />
          </span>
          <strong>{{ selectedPathChallenge.name }}</strong>
        </span>
        <p v-if="selectedPathChallenge.description">{{ selectedPathChallenge.description }}</p>

        <div v-if="selectedMission" class="selectedMissionFocus">
          <span class="sectionLabel">{{ t("space.shell.selectedMissionLabel") }}</span>
          <div class="selectedMissionFocusHead">
            <span
              v-if="selectedMission.iconUrl"
              class="iconFrame selectedMissionIconFrame"
              aria-hidden="true"
            >
              <img :src="selectedMission.iconUrl" alt="" class="selectedMissionIcon iconOnDark" />
            </span>
            <div>
              <span class="ladderStatus">{{ missionStatusLabel(selectedMission) }}</span>
              <strong>{{ selectedMission.title }}</strong>
            </div>
          </div>
          <p v-if="selectedMission.description">{{ selectedMission.description }}</p>
          <div class="missionMeta">
            <span>{{ missionIntensityLabelFor(selectedMission) }}</span>
            <span v-if="selectedMission.estimatedMinutes">
              {{ t("space.shell.minutes", { count: selectedMission.estimatedMinutes }) }}
            </span>
            <span v-if="selectedMission.xpReward">
              {{ t("space.shell.xp", { count: selectedMission.xpReward }) }}
            </span>
          </div>
          <p v-if="missionGateText(selectedMission)" class="missionGateText">
            {{ missionGateText(selectedMission) }}
          </p>
        </div>

        <div v-if="visibleSelectedMissions.length" class="selectedMissionList">
          <article
            v-for="mission in visibleSelectedMissions"
            :key="mission.id"
            class="selectedMission"
            :class="[missionStatusClass(mission), { selected: selectedMission?.id === mission.id }]"
            role="button"
            tabindex="0"
            :aria-pressed="selectedMission?.id === mission.id"
            @click="selectMission(mission)"
            @keydown.enter.prevent="selectMission(mission)"
            @keydown.space.prevent="selectMission(mission)"
          >
            <span
              v-if="mission.iconUrl"
              class="iconFrame selectedMissionIconFrame"
              aria-hidden="true"
            >
              <img :src="mission.iconUrl" alt="" class="selectedMissionIcon iconOnDark" />
            </span>
            <div>
              <span class="ladderStatus">{{ missionStatusLabel(mission) }}</span>
              <strong>{{ mission.title }}</strong>
              <p v-if="mission.description">{{ mission.description }}</p>
              <div class="missionMeta">
                <span>{{ missionIntensityLabelFor(mission) }}</span>
                <span v-if="mission.estimatedMinutes">
                  {{ t("space.shell.minutes", { count: mission.estimatedMinutes }) }}
                </span>
                <span v-if="mission.xpReward">
                  {{ t("space.shell.xp", { count: mission.xpReward }) }}
                </span>
              </div>
              <small v-if="missionGateText(mission)" class="missionGateText">
                {{ missionGateText(mission) }}
              </small>
            </div>
          </article>
        </div>
        <p v-if="hiddenMissionCount" class="foldedMissionHint">
          {{ hiddenMissionSummary }}
        </p>
        <p v-else-if="!visibleSelectedMissions.length" class="emptyText">
          {{ t("space.shell.noChallengeMissions") }}
        </p>
      </div>
      <p
        v-else-if="!pathError && !pathLoading && !pathChallenges.length"
        class="emptyText"
      >
        {{ t("space.shell.noPathChallenges") }}
      </p>
      </div>

      <div v-if="mode === 'challenge'" class="panelSection shellPanel">
      <span class="sectionLabel">{{ t("space.shell.challengeLabel") }}</span>
      <span class="shellTitleLine">
        <span v-if="challengeIcon" class="iconFrame inlineIconFrame" aria-hidden="true">
          <img :src="challengeIcon" alt="" class="inlineIcon iconOnDark" />
        </span>
        <strong>{{ activeShellChallenge?.name || t("common.challenge") }}</strong>
      </span>
      <p>{{ challengeStatusText }}</p>
      <div class="miniStats">
        <span>
          <strong>{{ activeShellChallenge?.streak || 0 }}</strong>
          <small>{{ t("space.shell.streak") }}</small>
        </span>
        <span>
          <strong>{{ activeShellChallenge?.totalCheckins || 0 }}</strong>
          <small>{{ t("space.shell.checkins") }}</small>
        </span>
      </div>
      <div v-if="activeShellMission" class="missionBrief">
        <span
          v-if="activeShellMission.iconUrl"
          class="iconFrame missionIconFrame"
          aria-hidden="true"
        >
          <img :src="activeShellMission.iconUrl" alt="" class="missionIcon iconOnDark" />
        </span>
        <div>
          <span class="sectionLabel">{{ t("space.shell.todayMission") }}</span>
          <strong>{{ activeShellMission.title || t("common.mission") }}</strong>
          <p v-if="activeShellMission.description">{{ activeShellMission.description }}</p>
          <div class="missionMeta">
            <span v-if="activeMissionIsDueReminder" class="missionMetaDue">
              {{ t("space.zoneState.reminderDue") }}
            </span>
            <span>{{ missionIntensityLabelFor(activeShellMission) }}</span>
            <span v-if="activeShellMission.estimatedMinutes">
              {{ t("space.shell.minutes", { count: activeShellMission.estimatedMinutes }) }}
            </span>
            <span v-if="activeShellMission.xpReward">
              {{ t("space.shell.xp", { count: activeShellMission.xpReward }) }}
            </span>
          </div>
        </div>
      </div>
      </div>

      <div v-if="mode === 'mission'" class="panelSection shellPanel missionFocusPanel">
      <span class="sectionLabel">{{ t("space.shell.missionLabel") }}</span>
      <span class="shellTitleLine">
        <span
          v-if="activeShellMission?.iconUrl"
          class="iconFrame inlineIconFrame"
          aria-hidden="true"
        >
          <img :src="activeShellMission.iconUrl" alt="" class="inlineIcon iconOnDark" />
        </span>
        <strong>{{ activeShellMission?.title || t("common.mission") }}</strong>
      </span>
      <p class="missionBreadcrumb">
        {{ t("space.shell.missionBreadcrumb", {
          path: zone.title,
          challenge: activeShellChallenge?.name || t("common.challenge"),
        }) }}
      </p>
      <p v-if="activeShellMission?.description">{{ activeShellMission.description }}</p>
      <div v-if="activeShellMission" class="missionMeta">
        <span v-if="activeMissionIsDueReminder" class="missionMetaDue">
          {{ t("space.zoneState.reminderDue") }}
        </span>
        <span>{{ missionIntensityLabelFor(activeShellMission) }}</span>
        <span v-if="activeShellMission.estimatedMinutes">
          {{ t("space.shell.minutes", { count: activeShellMission.estimatedMinutes }) }}
        </span>
        <span v-if="activeShellMission.xpReward">
          {{ t("space.shell.xp", { count: activeShellMission.xpReward }) }}
        </span>
      </div>
      <p v-if="activeShellMission && missionGateTextForShell(activeShellMission)" class="missionGateText">
        {{ missionGateTextForShell(activeShellMission) }}
      </p>
      <p v-else class="flowHint">{{ t("space.shell.missionFocusHint") }}</p>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";
import { findFirstReward } from "@/lib/livingSpaceState";
import { resolveActionIcon } from "@/utils/actionIconUtils";
import { resolveChallengeIcon, resolvePathIcon } from "@/utils/missionMomentumUtils";

const props = defineProps({
  zone: { type: Object, required: true },
  mode: { type: String, default: "zone" },
  checkingId: { type: [Number, String, null], default: null },
  pathLoading: { type: Boolean, default: false },
  pathError: { type: String, default: "" },
  selectedChallengeId: { type: [Number, String, null], default: null },
  completingMissionId: { type: [Number, String, null], default: null },
  startingChallengeId: { type: [Number, String, null], default: null },
  todaySafe: { type: Boolean, default: false },
  dailyMomentum: { type: Object, default: () => ({}) },
  dueReminders: { type: Array, default: () => [] },
  dueReminderFocus: { type: Object, default: null },
  futureReminderCount: { type: Number, default: 0 },
  roomFeedback: { type: Object, default: null },
  closable: { type: Boolean, default: true },
});

const emit = defineEmits([
  "change-mode",
  "select-challenge",
  "start-challenge",
  "complete-mission",
  "remind-mission",
  "skip-mission",
  "checkin",
  "close",
]);

const { t } = useI18n();
const ringoChoicePanel = ref(null);

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

const unlockedCount = computed(() => props.zone?.unlocked_objects?.length || 0);
const lockedPreviewCount = computed(() => props.zone?.locked_preview_objects?.length || 0);

const firstReward = computed(() => findFirstReward(props.zone));

const firstRewardUnlocked = computed(() => Boolean(firstReward.value?.unlocked));

const firstRewardText = computed(() => {
  const reward = firstReward.value;
  if (!reward) return "";

  if (firstRewardUnlocked.value) {
    return t("space.firstRewardPlaced", { reward: reward.title });
  }

  return t("space.firstRewardLocked", { reward: reward.title });
});

const unlockedSummaryText = computed(() => {
  return unlockedCount.value
    ? t("space.zoneSummary.savedText")
    : t("space.noUnlocked");
});

const lockedPreviewSummaryText = computed(() => {
  return lockedPreviewCount.value
    ? t("space.zoneSummary.previewText")
    : t("space.zoneComplete");
});

const zoneObjectHistoryItems = computed(() => {
  const buildItem = (reward, state) => {
    const title = reward?.title || reward?.key || t("space.objectHistory.unknown");
    const description = reward?.description || (
      state === "saved"
        ? t("space.objectHistory.savedText")
        : t("space.objectHistory.previewText")
    );

    return {
      key: `${state}-${reward?.key || title}`,
      mark: String(title).trim().slice(0, 1).toUpperCase(),
      title,
      text: description,
      state,
      status: state === "saved"
        ? t("space.objectUnlocked")
        : t("space.objectLockedPreview"),
      source: state === "saved"
        ? t("space.objectHistory.savedSource")
        : t("space.objectHistory.previewSource"),
    };
  };

  return [
    ...(props.zone?.unlocked_objects || []).map((reward) => buildItem(reward, "saved")),
    ...(props.zone?.locked_preview_objects || []).map((reward) => buildItem(reward, "preview")),
  ];
});

const challengeStatusText = computed(() => {
  if (activeShellChallenge.value?.status === "done_today") {
    return t("space.shell.challengeDoneText");
  }

  return t("space.shell.challengeReadyText");
});

const pathIcon = computed(() => {
  const iconNames = {
    career: "briefcase",
    fitness: "activity",
    learning: "book",
    creativity: "sparkles",
    sleep: "moon",
  };

  return resolvePathIcon(iconNames[props.zone?.path_key] || props.zone?.path_key || "");
});

const challengeIcon = computed(() => {
  return resolveChallengeIcon(activeShellChallenge.value);
});

const pathChallenges = computed(() => {
  return props.zone?.pathDetail?.challenges || [];
});

const pathStats = computed(() => {
  const detail = props.zone?.pathDetail;
  if (!detail) return null;

  const today = Number(detail.todayTotal || 0) > 0
    ? `${detail.todayDone || 0}/${detail.todayTotal || 0}`
    : t("pathsPage.pathCard.noMission");
  const progressTotal = Number(detail.pathProgressTotal || 0);
  const progressDone = Math.min(progressTotal, Math.max(0, Number(detail.pathProgressDone || 0)));
  const progressPercent = progressTotal > 0
    ? Math.round((progressDone / progressTotal) * 100)
    : 0;

  return {
    joined: `${detail.joinedCount || 0}/${detail.totalCount || 0}`,
    today,
    progressDone,
    progressTotal,
    progressPercent,
  };
});

const selectedPathChallenge = computed(() => {
  if (!pathChallenges.value.length) return null;

  const dueChallenge = challengeForReminder(props.dueReminderFocus);
  if (dueChallenge) return dueChallenge;

  if (props.selectedChallengeId) {
    const selected = pathChallenges.value.find((challenge) => {
      return String(challenge.id || "") === String(props.selectedChallengeId || "");
    });

    if (selected) return selected;
  }

  return pathChallenges.value.find((challenge) => challenge.isCurrent)
    || pathChallenges.value.find((challenge) => !challenge.todayChecked && challenge.isJoined)
    || pathChallenges.value.find((challenge) => !challenge.isJoined)
    || pathChallenges.value[0];
});

const selectedMissionId = ref(null);

const visibleSelectedMissions = computed(() => {
  const challenge = selectedPathChallenge.value;
  const missions = challenge?.missions || [];
  if (!missions.length) return [];

  if (!challenge.isJoined) {
    return missions
      .filter((mission) => mission.intensity === "main")
      .slice(0, 1);
  }

  return missions.filter(shouldShowMissionInLivingSpace);
});

const mainMissionDone = computed(() => {
  return (selectedPathChallenge.value?.missions || []).some((mission) => {
    return missionIntensity(mission) === "main" && missionDone(mission);
  });
});

const hiddenMissionCount = computed(() => {
  const total = selectedPathChallenge.value?.missions?.length || 0;
  return Math.max(0, total - visibleSelectedMissions.value.length);
});

const hiddenMissionSummary = computed(() => {
  if (!hiddenMissionCount.value) return "";

  if (!selectedPathChallenge.value?.isJoined) {
    return t("space.shell.foldedPreviewMissions", { count: hiddenMissionCount.value });
  }

  return t("space.shell.foldedFutureMissions", { count: hiddenMissionCount.value });
});

const selectedMission = computed(() => {
  const missions = visibleSelectedMissions.value;

  const dueMission = missionForReminder(props.dueReminderFocus);
  if (dueMission) return dueMission;

  if (!missions.length) return null;

  if (selectedMissionId.value) {
    const selected = missions.find((mission) => {
      return String(mission.id || "") === String(selectedMissionId.value || "");
    });

    if (selected) return selected;
  }

  const decidedTiny = missions.find((mission) => {
    return missionIntensity(mission) === "tiny" && missionHasUserDecision(mission);
  });

  return decidedTiny || missions.find((mission) => {
    return mission.availableToday
      && mission.status === "pending"
      && mission.intensity === "main";
  })
    || missions.find((mission) => missionIntensity(mission) === "main")
    || missions.find((mission) => missionCanComplete(mission))
    || missions.find((mission) => mission.status === "remind_later")
    || missions.find((mission) => mission.availableToday)
    || missions[0];
});

const challengeMission = computed(() => {
  return props.zone?.action?.challenge?.mission || null;
});

const activeShellChallenge = computed(() => {
  const selected = selectedPathChallenge.value;
  if (selected) {
    return {
      id: selected.id,
      enrollmentId: selected.enrollmentId,
      name: selected.name,
      iconKey: selected.iconKey,
      description: selected.description || "",
      status: selected.todayChecked
        ? "done_today"
        : selected.isJoined
          ? "ready_today"
          : "not_started",
      streak: 0,
      totalCheckins: selected.doneCount || 0,
      todayChecked: selected.todayChecked,
      isJoined: selected.isJoined,
      mission: selectedMission.value,
    };
  }

  return props.zone?.action?.challenge || null;
});

const activeShellMission = computed(() => {
  return selectedMission.value
    || activeShellChallenge.value?.mission
    || challengeMission.value
    || null;
});

const activeMissionIsDueReminder = computed(() => {
  return missionIsDueReminder(activeShellMission.value);
});

const missionIntensityLabel = computed(() => {
  const intensity = String(challengeMission.value?.intensity || "main").toLowerCase();
  if (["tiny", "bonus"].includes(intensity)) {
    return t(`space.shell.intensity.${intensity}`);
  }

  return t("space.shell.intensity.main");
});

const actionFlowHint = computed(() => {
  if (props.zone?.action?.state === "not_started") {
    return t("space.shell.flowStartHint");
  }

  if (props.zone?.action?.state === "done_today") {
    return t("space.shell.flowDoneHint");
  }

  return t("space.shell.flowReadyHint");
});

const challengeDone = computed(() => {
  return Boolean(activeShellChallenge.value?.todayChecked)
    || activeShellChallenge.value?.status === "done_today";
});

const challengeLoading = computed(() => {
  const enrollmentId = activeShellChallenge.value?.enrollmentId;
  if (!enrollmentId || props.checkingId == null) return false;

  return String(props.checkingId) === String(enrollmentId);
});

const selectedMissionLoading = computed(() => {
  const missionId = activeShellMission.value?.id;
  if (!missionId || props.completingMissionId == null) return false;

  return String(props.completingMissionId) === String(missionId);
});

const dueReminderCount = computed(() => props.dueReminders.length);

const showRestState = computed(() => {
  return Boolean(
    props.todaySafe
    || dueReminderCount.value > 0
    || Number(props.futureReminderCount || 0) > 0
    || Number(props.dailyMomentum?.total || 0) > 0,
  );
});

const visibleDueReminders = computed(() => props.dueReminders.slice(0, 3));

const primaryDueReminder = computed(() => {
  return (props.dueReminderFocus && missionForReminder(props.dueReminderFocus)
    ? props.dueReminderFocus
    : null)
    || visibleDueReminders.value.find((reminder) => missionForReminder(reminder))
    || visibleDueReminders.value[0]
    || null;
});

const restMomentText = computed(() => {
  if (dueReminderCount.value > 0) {
    return t("space.shell.restMomentDue", { count: dueReminderCount.value });
  }

  if (props.todaySafe) {
    return t("space.shell.restMomentSafe");
  }

  return t("space.shell.restMomentQuiet");
});

const restReminderSummary = computed(() => {
  if (dueReminderCount.value > 0) {
    return t("space.shell.restReminderDue", { count: dueReminderCount.value });
  }

  const futureCount = Number(props.futureReminderCount || 0);
  if (futureCount > 0) {
    return t("space.shell.restReminderFuture", { count: futureCount });
  }

  return t("space.shell.restReminderClear");
});

const restReminderEmptyText = computed(() => {
  if (Number(props.futureReminderCount || 0) > 0) {
    return t("space.shell.restReminderFutureText");
  }

  return t("space.shell.restReminderClearText");
});

const restSummaryItems = computed(() => {
  const momentum = props.dailyMomentum || {};

  return [
    {
      key: "safe",
      value: props.todaySafe
        ? t("space.shell.restSummarySafeValue")
        : t("space.shell.restSummaryOpenValue"),
      label: t("space.shell.restSummarySafeLabel"),
    },
    {
      key: "completed",
      value: Number(momentum.completed || 0),
      label: t("space.shell.restSummaryCompletedLabel"),
    },
    {
      key: "pending",
      value: Number(momentum.pending || 0),
      label: t("space.shell.restSummaryPendingLabel"),
    },
    {
      key: "reminders",
      value: Number(momentum.reminded || momentum.reminderCount || 0),
      label: t("space.shell.restSummaryReminderLabel"),
    },
  ];
});

const ringoGuidance = computed(() => {
  const path = props.zone?.title || t("space.eyebrow");
  const action = props.zone?.action || null;
  const challenge = activeShellChallenge.value;
  const mission = activeShellMission.value;
  const stats = pathStats.value;
  const pathComplete = Boolean(stats?.progressTotal && stats.progressDone >= stats.progressTotal);

  if (modeIs("rest")) {
    return buildRingoGuidance({
      mood: dueReminderCount.value > 0 ? "thinking" : "sleeping",
      tone: dueReminderCount.value > 0 ? "locked" : "done",
      title: dueReminderCount.value > 0
        ? t("space.ringoGuide.restReminderTitle")
        : t("space.ringoGuide.restTitle"),
      message: restMomentText.value,
      actions: dueReminderCount.value > 0
        ? [reminderReviewAction.value || {
          key: "review-path-reminders",
          label: t("space.zoneAction.viewPath"),
          type: "change-mode",
          mode: "path",
        }]
        : nextReviewActions(),
    });
  }

  if (props.roomFeedback) {
    const safeAfterCompletion = props.todaySafe || challengeDone.value || action?.state === "done_today";
    return buildRingoGuidance({
      mood: safeAfterCompletion ? "proud" : "focus",
      tone: safeAfterCompletion ? "done" : "ready",
      title: safeAfterCompletion
        ? t("space.ringoGuide.completionSafeTitle")
        : t("space.ringoGuide.completionNextTitle"),
      message: safeAfterCompletion
        ? t("space.ringoGuide.completionSafeMessage", { path })
        : t("space.ringoGuide.completionNextMessage", { path }),
      actions: safeAfterCompletion
        ? [
          {
            key: "rest-after-completion",
            label: t("space.overview.safeCta"),
            variant: "primary",
            type: "change-mode",
            mode: "rest",
          },
          {
            key: "review-path-after-completion",
            label: t("space.zoneAction.viewPath"),
            type: "change-mode",
            mode: "path",
          },
        ]
        : [{
          key: "continue-after-completion",
          label: t("space.zoneAction.continueMission"),
          variant: "primary",
          type: "change-mode",
          mode: "mission",
        }],
    });
  }

  if ((modeIs("path") || modeIs("mission")) && challenge) {
    if (!challenge.isJoined) {
      return buildRingoGuidance({
        mood: "thinking",
        tone: "start",
        title: t("space.ringoGuide.challengePreviewTitle"),
        message: t("space.ringoGuide.challengePreviewMessage", {
          challenge: challenge.name || t("common.challenge"),
          path,
        }),
        actions: [{
          key: "start-selected-challenge",
          label: t("space.shell.startChallenge"),
          variant: "primary",
          disabled: String(props.startingChallengeId || "") === String(challenge.id || ""),
          type: "start-challenge",
          challenge,
        }],
      });
    }

    if (modeIs("mission") && mission) {
      const gate = missionGateTextForShell(mission);
      if (gate) {
        return buildRingoGuidance({
          mood: missionIntensity(mission) === "bonus" ? "explaining" : "thinking",
          tone: "locked",
          title: t("space.ringoGuide.lockedTitle"),
          message: gate,
          actions: [{
            key: "review-path",
            label: t("space.zoneAction.viewPath"),
            type: "change-mode",
            mode: "path",
          }],
        });
      }

      if (missionDone(mission)) {
        return buildRingoGuidance({
          mood: "proud",
          tone: "done",
          title: t("space.ringoGuide.missionDoneTitle"),
          message: t("space.ringoGuide.missionDoneMessage", {
            mission: mission.title || t("common.mission"),
          }),
          actions: nextReviewActions(),
        });
      }

      if (missionCanCompleteInShell(mission)) {
        return buildRingoGuidance({
          mood: missionIntensity(mission) === "bonus" ? "happy" : "focus",
          tone: missionIntensity(mission) === "bonus" ? "bonus" : "ready",
          title: missionIntensity(mission) === "bonus"
            ? t("space.ringoGuide.bonusReadyTitle")
            : t("space.ringoGuide.missionFocusTitle"),
          message: t(
            missionIntensity(mission) === "bonus"
              ? "space.ringoGuide.bonusReadyMessage"
              : "space.ringoGuide.missionFocusMessage",
            { mission: mission.title || t("common.mission") },
          ),
          actions: missionGuideActions(mission),
        });
      }
    }
  }

  if (modeIs("challenge") && challengeDone.value) {
    return buildRingoGuidance({
      mood: "proud",
      tone: "done",
      title: t("space.ringoGuide.todaySafeTitle"),
      message: t("space.ringoGuide.todaySafeMessage", { path }),
      actions: nextReviewActions(),
    });
  }

  if (pathComplete) {
    return buildRingoGuidance({
      mood: "victory",
      tone: "clear",
      title: t("space.ringoGuide.pathClearTitle"),
      message: t("space.ringoGuide.pathClearMessage", { path }),
      actions: nextReviewActions(),
    });
  }

  if (action?.state === "done_today") {
    return buildRingoGuidance({
      mood: "proud",
      tone: "done",
      title: t("space.ringoGuide.todaySafeTitle"),
      message: t("space.ringoGuide.todaySafeMessage", { path }),
      actions: nextReviewActions(),
    });
  }

  if (action?.state === "not_started") {
    return buildRingoGuidance({
      mood: "welcome",
      tone: "start",
      title: t("space.ringoGuide.startTitle"),
      message: t("space.ringoGuide.startMessage", { path }),
      actions: [{
        key: "open-path-panel",
        label: action.primaryLabel || t("space.zoneAction.startPath"),
        variant: "primary",
        type: "change-mode",
        mode: action.primaryMode || "path",
      }],
    });
  }

  if (action?.state === "ready_today") {
    return buildRingoGuidance({
      mood: "focus",
      tone: "ready",
      title: t("space.ringoGuide.readyTitle"),
      message: t("space.ringoGuide.readyMessage", { path }),
      actions: [{
        key: "continue-action",
        label: action.primaryLabel || t("space.zoneAction.continueMission"),
        variant: "primary",
        type: "change-mode",
        mode: action.primaryMode || "challenge",
      }],
    });
  }

  return buildRingoGuidance({
    mood: "thinking",
    tone: "neutral",
    title: t("space.ringoGuide.fallbackTitle"),
    message: t("space.ringoGuide.fallbackMessage", { path }),
    actions: nextReviewActions(),
  });
});

watch(
  () => selectedPathChallenge.value?.id,
  () => {
    selectedMissionId.value = null;
    closeRingoChoicePanel();
  },
);

watch(
  () => [props.mode, selectedMission.value?.id],
  () => {
    closeRingoChoicePanel();
  },
);

function buildRingoGuidance({ mood, tone, title, message, actions = [] }) {
  return {
    mood,
    tone,
    title,
    message,
    actions: actions.filter(Boolean),
  };
}

function modeIs(value) {
  return props.mode === value;
}

function nextReviewActions() {
  return [{
    key: "review-path",
    label: t("space.zoneAction.viewPath"),
    type: "change-mode",
    mode: "path",
  }];
}

const reminderReviewAction = computed(() => {
  const reminder = primaryDueReminder.value;
  const mission = missionForReminder(reminder);
  if (!mission) return null;

  return {
    key: "review-due-reminder",
    label: t("space.shell.restReminderReview"),
    variant: "primary",
    type: "review-reminder",
    mission,
  };
});

function handleRingoAction(action) {
  if (!action || action.disabled) return;

  if (action.type === "start-challenge") {
    emit("start-challenge", action.challenge);
    return;
  }

  if (action.type === "complete-mission") {
    emit("complete-mission", action.mission);
    return;
  }

  if (action.type === "make-smaller") {
    closeRingoChoicePanel();
    selectedMissionId.value = action.mission?.id || null;
    emit("change-mode", "mission");
    return;
  }

  if (action.type === "review-reminder") {
    reviewReminder({ id: action.mission?.id });
    return;
  }

  if (action.type === "remind-mission") {
    openRingoChoicePanel("reminder", action.mission);
    return;
  }

  if (action.type === "skip-mission") {
    openRingoChoicePanel("skip", action.mission);
    return;
  }

  emit("change-mode", action.mode || "zone");
}

function missionForReminder(reminder) {
  const reminderId = String(reminder?.id || "");
  if (!reminderId) return null;

  const selectedChallengeMissions = selectedPathChallenge.value?.missions || [];

  return visibleSelectedMissions.value.find((mission) => {
    return String(mission?.id || "") === reminderId;
  }) || selectedChallengeMissions.find((mission) => {
    return String(mission?.id || "") === reminderId;
  }) || (activeShellMission.value && String(activeShellMission.value.id || "") === reminderId
    ? activeShellMission.value
    : null);
}

function challengeForReminder(reminder) {
  if (!reminder) return null;

  const reminderChallengeId = String(reminder.challengeId || "");
  const reminderEnrollmentId = String(reminder.enrollmentId || "");
  if (!reminderChallengeId && !reminderEnrollmentId) return null;

  return pathChallenges.value.find((challenge) => {
    return (reminderChallengeId && String(challenge?.id || "") === reminderChallengeId)
      || (reminderEnrollmentId && String(challenge?.enrollmentId || "") === reminderEnrollmentId);
  }) || null;
}

function reviewReminder(reminder) {
  const mission = missionForReminder(reminder);
  if (mission?.id) {
    selectedMissionId.value = mission.id;
  }
  emit("change-mode", mission ? "mission" : "path");
}

function actionIcon(action) {
  return resolveActionIcon(action?.iconKey || action?.type || "");
}

function openRingoChoicePanel(type, mission) {
  if (!mission?.id) return;

  if (type === "reminder") {
    ringoChoicePanel.value = {
      type,
      mission,
      prompt: t("missions.remindOptions.prompt"),
      options: REMINDER_OPTION_KEYS.map((key) => ({
        key,
        label: t(`missions.remindOptions.${key}`),
        reminderAt: reminderAtForOption(key).toISOString(),
      })),
    };
    return;
  }

  if (type === "skip") {
    ringoChoicePanel.value = {
      type,
      mission,
      prompt: t("missions.skipReasons.prompt"),
      options: SKIP_REASON_OPTIONS.map((option) => ({
        ...option,
        label: t(`missions.skipReasons.${option.key}`),
      })),
    };
  }
}

function closeRingoChoicePanel() {
  ringoChoicePanel.value = null;
}

function handleRingoChoice(option) {
  const panel = ringoChoicePanel.value;
  const mission = panel?.mission;
  if (!panel || !mission || selectedMissionLoading.value) return;

  if (panel.type === "reminder") {
    closeRingoChoicePanel();
    emit("remind-mission", {
      mission,
      reminderAt: option?.reminderAt,
      optionKey: option?.key || "",
    });
    return;
  }

  if (panel.type === "skip") {
    closeRingoChoicePanel();
    emit("skip-mission", {
      mission,
      reason: option?.reason || null,
      reasonKey: option?.key || "",
    });
  }
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

  return new Date(now.getTime() + 2 * 60 * 60 * 1000);
}

function challengeIconFor(challenge) {
  return resolveChallengeIcon(challenge);
}

function challengeStatusLabel(challenge) {
  if (challenge?.todayChecked) return t("space.shell.statusDoneToday");
  if (challenge?.isCurrent) return t("space.shell.statusCurrent");
  if (challenge?.isJoined) return t("space.shell.statusJoined");

  if (isRecommendedChallenge(challenge)) {
    return t("space.shell.statusRecommended");
  }

  return t("space.shell.statusAvailable");
}

function isRecommendedChallenge(challenge) {
  const nextChallengeId = props.zone?.pathDetail?.nextChallengeId;
  return Boolean(nextChallengeId && String(nextChallengeId) === String(challenge?.id));
}

function selectChallenge(challenge) {
  emit("select-challenge", challenge);
}

function challengeProgressPercent(challenge) {
  const total = Number(challenge?.missionCount || 0);
  if (!total) return 0;

  const done = Math.min(total, Math.max(0, Number(challenge?.doneCount || 0)));
  return Math.round((done / total) * 100);
}

function missionIsDueReminder(mission) {
  const reminderId = String(props.dueReminderFocus?.id || "");
  return Boolean(reminderId) && String(mission?.id || "") === reminderId;
}

function missionStatusLabel(mission) {
  const status = String(mission?.status || "pending").toLowerCase();
  if (missionIsDueReminder(mission)) return t("space.zoneState.reminderDue");
  if (missionGateText(mission)) return t("space.shell.statusLocked");
  if (status === "done" || status === "completed") return t("common.done");
  if (status === "locked") return t("space.shell.statusLocked");
  if (status === "skipped") return t("missions.status.skipped");
  if (status === "remind_later") return t("missions.status.remind_later");

  return t("common.pending");
}

function missionIntensity(mission) {
  return String(mission?.intensity || "main").toLowerCase();
}

function missionStatus(mission) {
  return String(mission?.status || "pending").toLowerCase();
}

function missionDone(mission) {
  return ["done", "completed"].includes(missionStatus(mission));
}

function missionSkipped(mission) {
  return missionStatus(mission) === "skipped";
}

function missionHasReminder(mission) {
  return missionStatus(mission) === "remind_later";
}

function missionHasUserDecision(mission) {
  return ["done", "completed", "remind_later", "skipped"].includes(missionStatus(mission));
}

const requestedTinyMission = computed(() => {
  const selectedId = selectedMissionId.value;
  if (!selectedId) return null;

  return (selectedPathChallenge.value?.missions || []).find((mission) => {
    return missionIntensity(mission) === "tiny"
      && String(mission.id || "") === String(selectedId || "");
  }) || null;
});

function isRequestedTinyMission(mission) {
  return Boolean(
    mission?.id
    && requestedTinyMission.value?.id
    && String(mission.id) === String(requestedTinyMission.value.id),
  );
}

function isActiveTinyMission(mission) {
  return missionIntensity(mission) === "tiny"
    && (isRequestedTinyMission(mission) || missionHasUserDecision(mission));
}

function shouldShowMissionInLivingSpace(mission) {
  const intensity = missionIntensity(mission);
  if (intensity === "main") return true;
  if (intensity === "tiny") {
    return isActiveTinyMission(mission);
  }
  if (intensity === "bonus") return true;
  return Boolean(mission.availableToday) || missionHasUserDecision(mission);
}

function missionGateText(mission) {
  const intensity = missionIntensity(mission);

  if (intensity === "tiny" && !missionDone(mission) && !isActiveTinyMission(mission)) {
    return t("space.shell.tinyLivingSpaceGate");
  }

  if (intensity === "bonus" && !mainMissionDone.value) {
    return t("space.shell.bonusLockedGate");
  }

  if (!mission?.availableToday || missionStatus(mission) === "locked") {
    const days = Number(mission?.unlocksInDays || 0);
    if (days > 1) return t("space.shell.unlocksInDays", { count: days });
    if (days === 1) return t("space.shell.unlocksTomorrow");
    return t("space.shell.missionLockedGate");
  }

  return "";
}

function missionGateTextForShell(mission) {
  if (selectedPathChallenge.value) return missionGateText(mission);

  if (
    missionIntensity(mission) === "tiny"
    && !missionDone(mission)
    && !isActiveTinyMission(mission)
  ) {
    return t("space.shell.tinyLivingSpaceGate");
  }

  return "";
}

function missionStatusClass(mission) {
  if (missionGateText(mission)) return "locked";
  return missionStatus(mission);
}

function missionIntensityLabelFor(mission) {
  const intensity = String(mission?.intensity || "main").toLowerCase();
  if (["tiny", "bonus"].includes(intensity)) {
    return t(`space.shell.intensity.${intensity}`);
  }

  return t("space.shell.intensity.main");
}

function selectMission(mission) {
  selectedMissionId.value = mission?.id || null;
}

function missionCanComplete(mission) {
  if (!selectedPathChallenge.value?.isJoined) return false;
  if (missionIntensity(mission) === "tiny" && !isActiveTinyMission(mission)) return false;
  if (missionIntensity(mission) === "bonus" && !mainMissionDone.value) return false;
  if (!mission?.availableToday) return false;
  return !["done", "completed", "locked"].includes(missionStatus(mission));
}

function missionCanCompleteInShell(mission) {
  if (selectedPathChallenge.value) return missionCanComplete(mission);
  if (!mission?.id) return false;
  if (missionIntensity(mission) === "tiny" && !isActiveTinyMission(mission)) return false;
  if (challengeDone.value || challengeLoading.value) return false;

  return !["done", "completed", "locked", "skipped"].includes(missionStatus(mission));
}

function missionActionLabel(mission) {
  if (!selectedPathChallenge.value?.isJoined) return t("space.shell.startChallengeFirst");
  if (missionIntensity(mission) === "tiny" && !isActiveTinyMission(mission)) {
    return t("space.shell.tinyLockedAction");
  }
  if (missionIntensity(mission) === "bonus" && !mainMissionDone.value) {
    return t("space.shell.bonusLockedAction");
  }
  if (!mission?.availableToday || mission?.status === "locked") return t("space.shell.missionLocked");
  if (missionDone(mission)) {
    return t("space.shell.missionDone");
  }

  return t("space.shell.completeMission");
}

function findTinyMissionFor(mission) {
  if (!mission || missionIntensity(mission) === "tiny") return null;

  return (selectedPathChallenge.value?.missions || []).find((candidate) => {
    return missionIntensity(candidate) === "tiny"
      && String(candidate.parentMissionId || "") === String(mission.id || "")
      && !missionDone(candidate)
      && !missionSkipped(candidate);
  }) || null;
}

function canUseMissionSupportActions(mission) {
  if (!mission?.id) return false;
  if (!selectedPathChallenge.value?.isJoined) return false;
  if (missionDone(mission) || missionSkipped(mission)) return false;
  if (missionGateText(mission)) return false;
  return Boolean(mission.availableToday);
}

function missionGuideActions(mission) {
  const actions = [{
    key: "complete-selected-mission",
    label: missionActionLabel(mission),
    variant: "primary",
    disabled: selectedMissionLoading.value,
    type: "complete-mission",
    mission,
  }];

  if (!canUseMissionSupportActions(mission)) return actions;

  const tinyMission = findTinyMissionFor(mission);
  if (tinyMission) {
    actions.push({
      key: "make-selected-mission-smaller",
      label: t("missions.ringoActions.make_smaller"),
      hint: t("missions.firstRunEducation.smaller.text"),
      variant: "secondary",
      disabled: selectedMissionLoading.value,
      compact: true,
      iconKey: "makeSmaller",
      type: "make-smaller",
      mission: tinyMission,
    });
  }

  actions.push({
    key: "remind-selected-mission",
    label: missionHasReminder(mission) ? t("missions.editReminder") : t("missions.remindLater"),
    hint: t("missions.firstRunEducation.remind.text"),
    variant: "secondary",
    disabled: selectedMissionLoading.value,
    compact: true,
    iconKey: "remindLater",
    type: "remind-mission",
    mission,
  });

  actions.push({
    key: "skip-selected-mission",
    label: t("missions.skip"),
    hint: t("missions.firstRunEducation.skip.text"),
    variant: "secondary",
    disabled: selectedMissionLoading.value,
    compact: true,
    iconKey: "skip",
    type: "skip-mission",
    mission,
  });

  return actions;
}

function formattedReminderTime(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
</script>

<style scoped>
.zonePanel {
  display: grid;
  grid-template-rows: auto auto auto minmax(0, 1fr);
  gap: 14px;
  min-width: 0;
  min-height: 0;
  height: 100%;
  padding: 14px;
  border-radius: 20px;
  overflow: hidden;
  background:
    radial-gradient(circle at 10% 0%, rgba(110, 229, 255, 0.08), transparent 32%),
    radial-gradient(circle at 88% 18%, rgba(247, 215, 116, 0.07), transparent 30%),
    linear-gradient(135deg, rgba(11, 17, 29, 0.88), rgba(5, 10, 18, 0.76));
  border: 1px solid rgba(110, 229, 255, 0.13);
  box-shadow:
    0 18px 50px rgba(0, 0, 0, 0.24),
    inset 0 0 0 1px rgba(255, 255, 255, 0.025);
  backdrop-filter: blur(18px);
}

.zonePanel.mode-zone {
  gap: 11px;
  grid-template-rows: auto auto minmax(0, 1fr);
}

.panelWorkSurface {
  display: grid;
  align-content: start;
  gap: 12px;
  min-width: 0;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-inline-end: 3px;
  scrollbar-width: thin;
}

.panelHead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.panelTitleWrap {
  display: inline-flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
}

.panelSection {
  min-width: 0;
}

.zonePanel > .panelSection:not(.shellPanel):not(.zoneAction) {
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.ringoGuide {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  padding: 10px;
  border-radius: 18px;
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.12), transparent 34%),
    rgba(255, 255, 255, 0.038);
  border: 1px solid rgba(110, 229, 255, 0.13);
}

.ringoGuide.ready {
  border-color: rgba(110, 229, 255, 0.18);
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.16), transparent 36%),
    rgba(110, 229, 255, 0.045);
}

.ringoGuide.start,
.ringoGuide.bonus {
  border-color: rgba(247, 215, 116, 0.16);
  background:
    radial-gradient(circle at 8% 0%, rgba(247, 215, 116, 0.13), transparent 36%),
    rgba(247, 215, 116, 0.045);
}

.ringoGuide.done,
.ringoGuide.clear {
  border-color: rgba(80, 220, 140, 0.18);
  background:
    radial-gradient(circle at 8% 0%, rgba(80, 220, 140, 0.13), transparent 36%),
    rgba(80, 220, 140, 0.045);
}

.ringoGuide.locked {
  border-color: rgba(255, 255, 255, 0.11);
  background:
    radial-gradient(circle at 8% 0%, rgba(255, 255, 255, 0.09), transparent 36%),
    rgba(255, 255, 255, 0.035);
}

.roomFeedbackPanel {
  display: grid;
  gap: 5px;
  padding: 10px;
  border-radius: 15px;
  background:
    radial-gradient(circle at 8% 0%, rgba(247, 215, 116, 0.12), transparent 34%),
    rgba(247, 215, 116, 0.045);
  border: 1px solid rgba(247, 215, 116, 0.16);
}

.roomFeedbackPanel.progress {
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.10), transparent 34%),
    rgba(110, 229, 255, 0.04);
  border-color: rgba(110, 229, 255, 0.14);
}

.roomFeedbackPanel strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.9rem;
}

.roomFeedbackPanel p {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.5;
  font-size: 0.78rem;
}

.ringoGuide :deep(.ringoMood.size-sm) {
  width: 72px;
  height: 72px;
  border-radius: 18px;
}

.ringoGuideCopy {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.ringoGuideCopy strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.92rem;
}

.ringoGuideCopy p {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
  font-size: 0.82rem;
}

.ringoGuideActions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.ringoChoicePanel {
  display: grid;
  gap: 8px;
  margin-top: 4px;
  padding: 9px;
  border-radius: 13px;
  background: rgba(5, 10, 18, 0.28);
  border: 1px solid rgba(110, 229, 255, 0.12);
}

.ringoChoicePanel p {
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.76rem;
}

.ringoChoiceGrid {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.choicePill,
.choiceBack {
  min-height: 30px;
  padding: 6px 9px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-size: 0.72rem;
  font-weight: 850;
}

.choicePill:hover,
.choicePill:focus-visible,
.choiceBack:hover,
.choiceBack:focus-visible {
  color: rgba(255, 255, 255, 0.92);
  background: rgba(110, 229, 255, 0.08);
  border-color: rgba(110, 229, 255, 0.18);
  outline: none;
}

.choicePill:disabled {
  cursor: default;
  opacity: 0.62;
}

.choiceBack {
  width: fit-content;
  color: rgba(255, 255, 255, 0.58);
  background: transparent;
}

.shellStateNav {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 7px;
  min-width: 0;
  padding: 7px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.shellStateButton {
  min-height: 29px;
  padding: 5px 9px;
  border-radius: 9px;
  justify-content: center;
  color: rgba(255, 255, 255, 0.58);
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 0.68rem;
  font-weight: 850;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: center;
}

.shellStateButton:hover,
.shellStateButton:focus-visible,
.shellStateButton.active {
  color: rgba(255, 255, 255, 0.90);
  background: rgba(110, 229, 255, 0.075);
  border-color: rgba(110, 229, 255, 0.16);
  outline: none;
}

.iconFrame {
  display: inline-grid;
  place-items: center;
  overflow: hidden;
  flex: 0 0 auto;
  border-radius: 10px;
  background:
    radial-gradient(circle at 35% 20%, rgba(255, 255, 255, 0.22), transparent 38%),
    rgba(110, 229, 255, 0.10);
  border: 1px solid rgba(110, 229, 255, 0.18);
}

.pathIcon,
.inlineIcon,
.missionIcon {
  display: block;
  object-fit: contain;
  --icon-on-dark-shadow: drop-shadow(0 5px 8px rgba(0, 0, 0, 0.38));
}

.panelIconFrame {
  width: 40px;
  height: 40px;
}

.pathIcon {
  width: 24px;
  height: 24px;
}

.panelKicker,
.sectionLabel {
  display: block;
  margin: 0 0 5px;
  color: rgba(110, 229, 255, 0.72);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.panelHead h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.1rem;
}

.closeButton {
  min-height: 32px;
  padding: 6px 10px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.76);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-weight: 800;
}

.zoneProgressSnapshot {
  display: grid;
  gap: 9px;
  min-width: 0;
  padding: 10px;
  border-radius: 15px;
  background:
    radial-gradient(circle at 10% 0%, rgba(110, 229, 255, 0.06), transparent 30%),
    rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.zoneProgressSnapshot.complete {
  border-color: rgba(80, 220, 140, 0.14);
  background:
    radial-gradient(circle at 10% 0%, rgba(80, 220, 140, 0.08), transparent 32%),
    rgba(255, 255, 255, 0.032);
}

.snapshotStats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  min-width: 0;
}

.snapshotItem {
  display: grid;
  align-content: start;
  gap: 5px;
  min-width: 0;
  padding: 9px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.snapshotItem strong {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.35rem;
  line-height: 1;
}

.snapshotItem p {
  margin: 0;
  color: rgba(255, 255, 255, 0.56);
  line-height: 1.45;
}

.emptyText,
.hintText,
.nextReward {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.55;
}

.hintText {
  margin-bottom: 8px;
  font-size: 0.82rem;
}

.nextReward {
  padding: 10px 11px;
  border-radius: 14px;
  color: rgba(247, 215, 116, 0.88);
  background: rgba(247, 215, 116, 0.055);
  border: 1px solid rgba(247, 215, 116, 0.12);
}

.nextReward.complete {
  color: rgba(122, 245, 176, 0.88);
  background: rgba(80, 220, 140, 0.055);
  border-color: rgba(80, 220, 140, 0.14);
}

.objectHistoryPanel {
  display: grid;
  gap: 10px;
  min-width: 0;
  padding: 11px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.sectionHeaderLine {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-width: 0;
}

.sectionHeaderLine small {
  flex: 0 0 auto;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 800;
  font-size: 0.72rem;
}

.objectHistoryList {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.objectHistoryItem {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 9px;
  min-width: 0;
  padding: 9px;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.objectHistoryItem.saved {
  border-color: rgba(110, 229, 255, 0.18);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.07), transparent 38%),
    rgba(255, 255, 255, 0.035);
}

.objectHistoryItem.preview {
  color: rgba(255, 255, 255, 0.66);
}

.objectHistoryMark {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 9px;
  color: rgba(255, 255, 255, 0.84);
  background: rgba(110, 229, 255, 0.11);
  border: 1px solid rgba(110, 229, 255, 0.2);
  font-weight: 900;
  font-size: 0.78rem;
}

.objectHistoryItem.preview .objectHistoryMark {
  color: rgba(255, 255, 255, 0.48);
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
}

.objectHistoryCopy,
.objectHistoryTitle {
  min-width: 0;
}

.objectHistoryCopy {
  display: grid;
  gap: 4px;
}

.objectHistoryTitle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.objectHistoryTitle strong {
  min-width: 0;
  overflow-wrap: anywhere;
}

.objectHistoryTitle em {
  flex: 0 0 auto;
  color: rgba(110, 229, 255, 0.82);
  font-size: 0.68rem;
  font-style: normal;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.objectHistoryItem.preview .objectHistoryTitle em {
  color: rgba(255, 255, 255, 0.44);
}

.objectHistoryCopy span:not(.objectHistoryTitle),
.objectHistoryCopy small {
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.objectHistoryCopy small {
  color: rgba(255, 255, 255, 0.42);
  font-weight: 800;
}

.zoneAction {
  display: grid;
  gap: 8px;
  padding: 11px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.zoneAction.not_started {
  border-color: rgba(247, 215, 116, 0.14);
  background: rgba(247, 215, 116, 0.04);
}

.zoneAction.ready_today {
  border-color: rgba(110, 229, 255, 0.16);
  background: rgba(110, 229, 255, 0.045);
}

.zoneAction.done_today {
  border-color: rgba(80, 220, 140, 0.16);
  background: rgba(80, 220, 140, 0.045);
}

.zoneAction strong {
  color: rgba(255, 255, 255, 0.90);
}

.zoneAction p {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

.flowHint {
  padding: 8px 9px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.66) !important;
  background: rgba(110, 229, 255, 0.055);
  border: 1px solid rgba(110, 229, 255, 0.10);
  font-size: 0.76rem;
}

.missionBreadcrumb {
  color: rgba(110, 229, 255, 0.70) !important;
  font-size: 0.78rem;
  font-weight: 800;
}

.actionLink {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  min-width: 0;
  padding: 7px 11px;
  border-radius: 10px;
  text-decoration: none;
  font-size: 0.78rem;
  font-weight: 850;
  line-height: 1.25;
  overflow-wrap: anywhere;
  text-align: center;
  border: 0;
  cursor: pointer;
}

.actionLink.compact {
  width: 44px;
  min-width: 44px;
  height: 44px;
  min-height: 44px;
  padding: 0;
  border-radius: 999px;
}

.actionIcon {
  width: 22px;
  height: 22px;
  object-fit: contain;
  --icon-on-dark-shadow: drop-shadow(0 4px 7px rgba(0, 0, 0, 0.36));
}

.actionTooltip {
  position: absolute;
  z-index: 4;
  inset-inline-start: 50%;
  bottom: calc(100% + 8px);
  width: max-content;
  max-width: 220px;
  padding: 6px 8px;
  border-radius: 9px;
  color: rgba(255, 255, 255, 0.90);
  background: rgba(8, 13, 22, 0.96);
  border: 1px solid rgba(110, 229, 255, 0.14);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.32);
  font-size: 0.68rem;
  line-height: 1.35;
  opacity: 0;
  pointer-events: none;
  transform: translateX(-50%) translateY(3px);
  transition: opacity 140ms ease, transform 140ms ease;
}

.actionLink:hover .actionTooltip,
.actionLink:focus-visible .actionTooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.actionLink.primary {
  color: rgba(5, 10, 18, 0.95);
  background: rgba(110, 229, 255, 0.88);
}

.actionLink.secondary {
  color: rgba(255, 255, 255, 0.76);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.actionLink:disabled {
  cursor: default;
  opacity: 0.62;
}

.srOnly {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.shellPanel {
  display: grid;
  gap: 10px;
  padding: 12px;
  border-radius: 16px;
  background:
    radial-gradient(circle at 12% 0%, rgba(110, 229, 255, 0.06), transparent 28%),
    rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(110, 229, 255, 0.10);
}

.shellPanel strong {
  color: rgba(255, 255, 255, 0.90);
}

.shellTitleLine {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.inlineIcon {
  width: 20px;
  height: 20px;
}

.inlineIconFrame {
  width: 32px;
  height: 32px;
}

.shellPanel p {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

.miniStats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.miniStats span,
.pathStats span {
  display: grid;
  gap: 2px;
  padding: 9px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.miniStats strong,
.pathStats strong {
  color: rgba(255, 255, 255, 0.90);
}

.miniStats small,
.pathStats small {
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.72rem;
}

.pathStats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.restPanel {
  border-color: rgba(80, 220, 140, 0.13);
  background:
    radial-gradient(circle at 12% 0%, rgba(80, 220, 140, 0.08), transparent 30%),
    rgba(255, 255, 255, 0.032);
}

.restSummaryGrid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.restSummaryItem,
.restReminderItem {
  display: grid;
  gap: 3px;
  min-width: 0;
  padding: 9px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.restSummaryItem strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.92rem;
}

.restSummaryItem small,
.restReminderItem span {
  color: rgba(255, 255, 255, 0.54);
  font-size: 0.7rem;
  line-height: 1.35;
}

.restReminderBlock {
  display: grid;
  gap: 9px;
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.restReminderBlock.due {
  border-color: rgba(247, 215, 116, 0.18);
  background:
    radial-gradient(circle at 12% 0%, rgba(247, 215, 116, 0.10), transparent 34%),
    rgba(247, 215, 116, 0.045);
}

.restReminderHead {
  display: grid;
  gap: 2px;
}

.restReminderHead strong,
.restReminderItem strong {
  color: rgba(255, 255, 255, 0.88);
}

.restReminderList {
  display: grid;
  gap: 7px;
}

.restReminderItem {
  background: rgba(5, 10, 18, 0.22);
}

.restReminderAction {
  justify-self: start;
  min-height: 26px;
  padding: 5px 8px;
  border-radius: 8px;
  color: rgba(5, 10, 18, 0.92);
  background: rgba(110, 229, 255, 0.86);
  border: 1px solid rgba(110, 229, 255, 0.26);
  cursor: pointer;
  font-size: 0.68rem;
  font-weight: 900;
}

.pathProgressBlock {
  display: grid;
  gap: 6px;
  padding: 10px;
  border-radius: 13px;
  background:
    radial-gradient(circle at 12% 0%, rgba(247, 215, 116, 0.11), transparent 38%),
    rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(247, 215, 116, 0.13);
}

.pathProgressHead {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: rgba(255, 255, 255, 0.64);
  font-size: 0.74rem;
  font-weight: 850;
}

.pathProgressHead strong {
  color: rgba(247, 215, 116, 0.94);
  font-size: 0.9rem;
}

.pathProgressTrack {
  position: relative;
  overflow: hidden;
  height: 7px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.075);
}

.pathProgressTrack span {
  display: block;
  width: var(--progress-percent, 0%);
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(110, 229, 255, 0.86), rgba(247, 215, 116, 0.92));
  box-shadow: 0 0 16px rgba(247, 215, 116, 0.20);
}

.pathProgressBlock small {
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.72rem;
}

.pathError {
  padding: 8px 9px;
  border-radius: 10px;
  color: rgba(255, 204, 204, 0.88) !important;
  background: rgba(248, 113, 113, 0.10);
  border: 1px solid rgba(248, 113, 113, 0.16);
}

.challengeLadder {
  display: grid;
  gap: 10px;
  min-width: 0;
  max-height: min(360px, 38vh);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
  scrollbar-width: thin;
}

.ladderHead {
  display: grid;
  align-content: start;
  gap: 3px;
  min-width: 0;
  max-width: none;
  padding: 2px 0;
}

.ladderHead strong {
  font-size: 0.82rem;
}

.ladderHead small {
  color: rgba(255, 255, 255, 0.52);
  line-height: 1.45;
}

.ladderItem {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  width: auto;
  min-width: 0;
  padding: 10px;
  border-radius: 15px;
  text-align: start;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  outline: none;
  transition: transform 160ms ease, border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
}

.ladderItem:hover,
.ladderItem:focus-visible {
  transform: translateY(-1px);
  border-color: rgba(110, 229, 255, 0.22);
  background: rgba(110, 229, 255, 0.052);
}

.ladderItem.joined {
  border-color: rgba(110, 229, 255, 0.12);
}

.ladderItem.available,
.ladderItem.recommended {
  border-color: rgba(247, 215, 116, 0.14);
  background: rgba(247, 215, 116, 0.04);
}

.ladderItem.done {
  border-color: rgba(80, 220, 140, 0.18);
  background: rgba(80, 220, 140, 0.055);
}

.ladderItem.current,
.ladderItem.selected {
  border-color: rgba(110, 229, 255, 0.28);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.09), rgba(247, 215, 116, 0.035)),
    rgba(255, 255, 255, 0.04);
}

.ladderItem.selected {
  box-shadow:
    inset 0 0 0 1px rgba(110, 229, 255, 0.12),
    0 0 22px rgba(110, 229, 255, 0.08);
}

.ladderIconFrame {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.ladderIcon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  --icon-on-dark-shadow: drop-shadow(0 5px 8px rgba(0, 0, 0, 0.38));
}

.ladderCopy {
  display: grid;
  gap: 5px;
  min-width: 0;
}

.ladderCopy strong {
  font-size: 0.9rem;
}

.ladderCopy p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-size: 0.76rem;
}

.ladderStatus {
  color: rgba(110, 229, 255, 0.74);
  font-size: 0.66rem;
  font-weight: 900;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.ladderItem.available .ladderStatus,
.ladderItem.recommended .ladderStatus {
  color: rgba(247, 215, 116, 0.82);
}

.ladderItem.done .ladderStatus,
.selectedMission.done .ladderStatus,
.selectedMission.completed .ladderStatus {
  color: rgba(80, 220, 140, 0.86);
}

.ladderProgress {
  position: relative;
  overflow: hidden;
  height: 5px;
  margin-top: 2px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.10);
}

.ladderProgress span {
  display: block;
  width: var(--progress-percent, 0%);
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(110, 229, 255, 0.92), rgba(247, 215, 116, 0.78));
  box-shadow: 0 0 10px rgba(110, 229, 255, 0.16);
}

.progressText {
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.7rem;
  font-weight: 800;
}

.selectedChallengePanel {
  display: grid;
  gap: 10px;
  padding: 12px;
  border-radius: 16px;
  background: rgba(110, 229, 255, 0.055);
  border: 1px solid rgba(110, 229, 255, 0.16);
}

.selectedMissionFocus {
  display: grid;
  gap: 8px;
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.selectedMissionFocusHead {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 9px;
}

.selectedMissionFocusHead strong {
  display: block;
  margin-top: 2px;
}

.selectedMissionList {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 8px;
}

.selectedMission {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 9px;
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  outline: none;
  transition: border-color 160ms ease, background 160ms ease, box-shadow 160ms ease, transform 160ms ease;
}

.selectedMission:hover,
.selectedMission:focus-visible {
  transform: translateY(-1px);
  border-color: rgba(110, 229, 255, 0.18);
  background: rgba(110, 229, 255, 0.045);
}

.selectedMission.done,
.selectedMission.completed {
  background: rgba(80, 220, 140, 0.08);
  border-color: rgba(80, 220, 140, 0.16);
}

.selectedMission.remind_later,
.selectedMission.skipped {
  background: rgba(247, 215, 116, 0.045);
  border-color: rgba(247, 215, 116, 0.12);
}

.selectedMission.selected {
  border-color: rgba(110, 229, 255, 0.24);
  box-shadow:
    inset 0 0 0 1px rgba(110, 229, 255, 0.10),
    0 0 18px rgba(110, 229, 255, 0.07);
}

.selectedMission.locked {
  cursor: default;
  opacity: 0.64;
  filter: grayscale(0.45);
}

.selectedMissionIconFrame {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.selectedMissionIcon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  --icon-on-dark-shadow: drop-shadow(0 5px 8px rgba(0, 0, 0, 0.38));
}

.selectedMission strong {
  font-size: 0.84rem;
}

.selectedMission p {
  margin-top: 3px;
  font-size: 0.74rem;
}

.missionGateText {
  display: block;
  margin-top: 6px;
  color: rgba(247, 215, 116, 0.76) !important;
  font-size: 0.72rem;
  font-weight: 760;
  line-height: 1.45;
}

.foldedMissionHint {
  margin: 0;
  padding: 8px 9px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.60) !important;
  background: rgba(255, 255, 255, 0.035);
  border: 1px dashed rgba(255, 255, 255, 0.12);
  font-size: 0.74rem;
  line-height: 1.5;
}

.missionBrief {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.09);
}

.missionIconFrame {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.missionIcon {
  width: 24px;
  height: 24px;
}

.missionBrief p {
  margin-top: 5px;
}

.missionMeta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.missionMeta span {
  padding: 4px 7px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.68);
  background: rgba(255, 255, 255, 0.055);
  font-size: 0.7rem;
  font-weight: 800;
}

.missionMeta .missionMetaDue {
  color: rgba(247, 215, 116, 0.98);
  background: rgba(247, 215, 116, 0.10);
}

@media (max-width: 720px) {
  .zonePanel {
    height: auto;
    overflow: visible;
    padding: 12px;
  }

  .panelWorkSurface {
    overflow: visible;
    padding-inline-end: 0;
  }

  .panelHead {
    align-items: stretch;
  }

  .closeButton {
    flex: 0 0 auto;
  }

  .ringoGuide {
    grid-template-columns: 1fr;
  }

  .ringoGuide :deep(.ringoMood.size-sm) {
    width: 64px;
    height: 64px;
  }

  .shellStateNav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .ringoGuideActions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .actionLink {
    width: 100%;
    justify-self: stretch;
  }

  .pathStats,
  .miniStats,
  .restSummaryGrid,
  .snapshotStats {
    grid-template-columns: 1fr;
  }

  .challengeLadder {
    max-height: none;
    flex-direction: column;
    overflow: visible;
  }

  .ladderHead,
  .ladderItem {
    width: auto;
    max-width: none;
    min-width: 0;
  }

  .selectedMissionList {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 420px) {
  .panelHead {
    display: grid;
  }

  .closeButton {
    justify-self: stretch;
  }

  .shellStateNav {
    grid-template-columns: 1fr;
  }
}
</style>
