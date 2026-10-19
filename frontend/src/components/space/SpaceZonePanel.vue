<template>
  <aside class="zonePanel" :class="`card-${cardState}`">
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
        {{ t("space.panel.backToRoom") }}
      </button>
    </div>

    <RingoActionCard
      ref="ringoCardRef"
      :card="ringoCard"
      :collapsed="Boolean(openRow)"
      :choice-panel="ringoChoicePanel"
      :choice-disabled="selectedMissionLoading"
      @action="handleRingoAction"
      @choice="handleRingoChoice"
      @close-choice="closeRingoChoicePanel"
      @expand="openRow = null"
    />

    <p v-if="roomFeedback" class="srOnly" aria-live="polite">
      {{ roomFeedback.title }} {{ roomFeedback.text }}
    </p>

    <div class="panelWorkSurface">
      <BonusOfferCard
        v-if="showBonusOffer"
        :title="currentBonus.mission.title"
        :meta="bonusMeta"
        :can-switch="bonusCandidates.length > 1"
        @accept="acceptBonus"
        @another="nextBonus"
      />

      <ZoneTodayStrip
        :done="todayProgress.done"
        :total="todayProgress.total"
        :main-done="mainMissionDone"
        :first-reward-text="firstRewardText"
        :first-reward-unlocked="firstRewardUnlocked"
      />

      <div class="zoneDetails">
        <ZoneDetailsRow
          :row-id="`${zone.zone_key}-path`"
          :title="t('space.panel.rowPath')"
          :meta="pathStats?.progressTotal ? `${pathStats.progressPercent}%` : ''"
          :open="openRow === 'path'"
          @toggle="toggleRow('path')"
        >
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
          <ChallengeTodayMissions
            v-else-if="challengeItems.length"
            :items="challengeItems"
            @select-challenge="selectChallengeFromList"
            @select-mission="selectMissionFromList"
          />
          <p v-else class="emptyText">{{ t("space.shell.noPathChallenges") }}</p>

          <RouterLink to="/paths" class="fullPathLink">
            {{ t("space.panel.fullPath") }}
          </RouterLink>
        </ZoneDetailsRow>

        <ZoneDetailsRow
          :row-id="`${zone.zone_key}-objects`"
          :title="t('space.panel.rowObjects')"
          :meta="t('space.objectHistory.summary', { saved: unlockedCount, preview: lockedPreviewCount })"
          :open="openRow === 'objects'"
          @toggle="toggleRow('objects')"
        >
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
        </ZoneDetailsRow>

        <ZoneDetailsRow
          v-if="hasReminders"
          :row-id="`${zone.zone_key}-reminders`"
          :title="t('space.panel.rowReminders')"
          :meta="restReminderSummary"
          :open="openRow === 'reminders'"
          @toggle="toggleRow('reminders')"
        >
          <ul class="reminderList">
            <li v-for="reminder in reminders" :key="reminder.id">
              <button
                type="button"
                class="reminderItem"
                :class="{ due: reminder.due }"
                @click="reviewReminder(reminder)"
              >
                <img
                  v-if="bellIcon"
                  :src="bellIcon"
                  alt=""
                  class="reminderBell iconOnDark"
                  aria-hidden="true"
                />
                <span class="reminderCopy">
                  <strong>{{ reminder.title }}</strong>
                  <small v-if="reminder.zoneTitle">
                    {{ t("space.panel.reminderWhere", { zone: reminder.zoneTitle, path: reminder.pathName }) }}
                  </small>
                </span>
                <span class="reminderTime">{{ reminderTimeLabel(reminder) }}</span>
              </button>
            </li>
          </ul>
        </ZoneDetailsRow>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import BonusOfferCard from "./BonusOfferCard.vue";
import ChallengeTodayMissions from "./ChallengeTodayMissions.vue";
import RingoActionCard from "./RingoActionCard.vue";
import ZoneDetailsRow from "./ZoneDetailsRow.vue";
import ZoneTodayStrip from "./ZoneTodayStrip.vue";
import {
  bonusOfferCandidates,
  buildTodayMissionRows,
  pickFocusMission,
  reminderTimeLeft,
  ringoCardState,
  shouldOfferBonus,
  todayMainDone,
} from "@/lib/livingSpacePanel";
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
  reminders: { type: Array, default: () => [] },
  requestedMissionId: { type: [Number, String, null], default: null },
  now: { type: Number, default: () => Date.now() },
});

const emit = defineEmits([
  "change-mode",
  "select-challenge",
  "start-challenge",
  "complete-mission",
  "remind-mission",
  "skip-mission",
  "focus-reminder",
  "checkin",
  "close",
]);

const { locale, t } = useI18n();
const bellIcon = resolveActionIcon("remindLater");
const ringoChoicePanel = ref(null);
const ringoCardRef = ref(null);
// Accordion: at most one details row open; an open row collapses the Ringo card.
const openRow = ref(null);
// B8: which bonus suggestion is shown, and a focus to apply after switching challenge.
const bonusIndex = ref(0);
const pendingFocusId = ref(null);

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

  return t("space.panel.firstRewardHint", { object: reward.title });
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

const pathChallenges = computed(() => {
  return props.zone?.pathDetail?.challenges || [];
});

const pathStats = computed(() => {
  const detail = props.zone?.pathDetail;
  if (!detail) return null;

  const progressTotal = Number(detail.pathProgressTotal || 0);
  const progressDone = Math.min(progressTotal, Math.max(0, Number(detail.pathProgressDone || 0)));
  const progressPercent = progressTotal > 0
    ? Math.round((progressDone / progressTotal) * 100)
    : 0;

  return {
    progressDone,
    progressTotal,
    progressPercent,
  };
});

const todayProgress = computed(() => {
  const detail = props.zone?.pathDetail || {};
  return {
    done: Number(detail.todayDone || 0),
    total: Number(detail.todayTotal || 0),
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
    || pathChallenges.value.find((challenge) => challenge.isJoined)
    || pathChallenges.value.find((challenge) => !challenge.isJoined)
    || pathChallenges.value[0];
});

const selectedMissionId = ref(null);

// Declared before any watcher whose getter reaches it (watch getters run during setup).
const requestedTinyMission = computed(() => {
  const selectedId = selectedMissionId.value;
  if (!selectedId) return null;

  return (selectedPathChallenge.value?.missions || []).find((mission) => {
    return missionIntensity(mission) === "tiny"
      && String(mission.id || "") === String(selectedId || "");
  }) || null;
});


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

// Today's main step counts as done when the main mission or its tiny substitute is done (spec).
const mainMissionDone = computed(() => {
  return todayMainDone(selectedPathChallenge.value?.missions || []);
});

const selectedMission = computed(() => {
  return pickFocusMission(visibleSelectedMissions.value, {
    dueMission: missionForReminder(props.dueReminderFocus),
    pickedId: selectedMissionId.value ?? props.requestedMissionId,
  });
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

const hasReminders = computed(() => props.reminders.length > 0);

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

const reminderReviewAction = computed(() => {
  const reminder = primaryDueReminder.value;
  if (!reminder) return null;

  return {
    key: "review-due-reminder",
    label: t("space.shell.restReminderReview"),
    type: "review-reminder",
    reminder,
  };
});

const cardState = computed(() => {
  const mission = activeShellMission.value;
  const challenge = selectedPathChallenge.value;

  return ringoCardState({
    dueReminderFocused: activeMissionIsDueReminder.value,
    restMode: props.mode === "rest",
    hasChallenge: Boolean(challenge),
    challengeJoined: Boolean(challenge?.isJoined),
    focusGated: Boolean(mission && missionGateTextForShell(mission)),
    focusCanComplete: Boolean(mission && missionCanCompleteInShell(mission)),
    focusDone: Boolean(mission && missionDone(mission)),
    mainDone: mainMissionDone.value || challengeDone.value,
  });
});

const bonusCandidates = computed(() => bonusOfferCandidates(pathChallenges.value));

const currentBonus = computed(() => {
  const candidates = bonusCandidates.value;
  if (!candidates.length) return null;
  return candidates[bonusIndex.value % candidates.length];
});

const bonusSuppressedByReminder = computed(() => {
  return dueReminderCount.value > 0 && bonusCandidates.value.length > 0;
});

const showBonusOffer = computed(() => {
  return !openRow.value
    && cardState.value === "safe"
    && shouldOfferBonus({
      mainDone: mainMissionDone.value || challengeDone.value,
      dueReminderCount: dueReminderCount.value,
      candidates: bonusCandidates.value,
      focusIsBonus: missionIntensity(activeShellMission.value) === "bonus",
    });
});

const bonusMeta = computed(() => {
  const mission = currentBonus.value?.mission;
  const parts = [
    mission?.estimatedMinutes ? t("space.shell.minutes", { count: mission.estimatedMinutes }) : "",
    t("space.panel.bonusMetaSuffix"),
  ];
  return parts.filter(Boolean).join(" · ");
});

const ringoCard = computed(() => {
  const state = cardState.value;
  const path = props.zone?.title || t("space.eyebrow");
  const mission = activeShellMission.value;
  const challenge = selectedPathChallenge.value;
  const missionTitle = mission?.title || t("common.mission");
  const openPath = {
    key: "open-path-row",
    label: t("space.panel.rowPath"),
    type: "open-row",
    row: "path",
  };

  if (state === "reminder") {
    const title = t("space.panel.reminderTitle", { mission: missionTitle });
    return {
      tone: "reminder",
      mood: "thinking",
      badge: t("space.panel.reminderBadge"),
      title,
      body: t("space.panel.reminderBody"),
      chips: missionChips(mission),
      note: bonusSuppressedByReminder.value ? t("space.panel.reminderPriorityNote") : "",
      primary: completeAction(mission),
      support: missionSupportActions(mission, { reminder: true }),
      collapsedText: title,
    };
  }

  if (state === "rest") {
    return {
      tone: dueReminderCount.value > 0 ? "locked" : "done",
      mood: dueReminderCount.value > 0 ? "thinking" : "sleeping",
      label: t("space.shell.restLabel"),
      title: dueReminderCount.value > 0
        ? t("space.ringoGuide.restReminderTitle")
        : t("space.ringoGuide.restTitle"),
      body: restMomentText.value,
      primary: dueReminderCount.value > 0 ? reminderReviewAction.value : null,
      secondary: [openPath],
    };
  }

  if (state === "preview") {
    const notStarted = props.zone?.action?.state === "not_started" && !props.selectedChallengeId;
    return {
      tone: "start",
      mood: notStarted ? "welcome" : "thinking",
      label: t("space.ringoGuide.eyebrow"),
      title: notStarted
        ? t("space.ringoGuide.startTitle")
        : t("space.ringoGuide.challengePreviewTitle"),
      body: notStarted
        ? t("space.ringoGuide.startMessage", { path })
        : t("space.ringoGuide.challengePreviewMessage", {
          challenge: challenge?.name || t("common.challenge"),
          path,
        }),
      primary: {
        key: "start-selected-challenge",
        label: t("space.shell.startChallenge"),
        disabled: String(props.startingChallengeId || "") === String(challenge?.id || ""),
        type: "start-challenge",
        challenge,
      },
      secondary: [openPath],
    };
  }

  if (state === "mission") {
    const bonus = missionIntensity(mission) === "bonus";
    const title = bonus
      ? t("space.panel.bonusFocusTitle", { mission: missionTitle })
      : t("space.panel.missionTitle", { mission: missionTitle });
    return {
      tone: bonus ? "bonus" : "ready",
      mood: bonus ? "happy" : "focus",
      label: t("space.ringoGuide.eyebrow"),
      title,
      body: bonus
        ? t("space.ringoGuide.bonusReadyMessage", { mission: missionTitle })
        : mission?.estimatedMinutes
          ? t("space.panel.missionBody", { minutes: mission.estimatedMinutes })
          : t("space.ringoGuide.missionFocusMessage", { mission: missionTitle }),
      chips: missionChips(mission),
      primary: completeAction(mission),
      support: missionSupportActions(mission),
      collapsedText: title,
    };
  }

  if (state === "safe") {
    return {
      tone: "safe",
      mood: "proud",
      label: t("space.panel.stateSafe"),
      title: t("space.panel.doneTitle"),
      body: bonusCandidates.value.length
        ? t("space.panel.doneBody")
        : t("space.panel.doneBodyNoBonus"),
      primary: {
        key: "finish-today",
        label: t("space.panel.actionFinishToday"),
        type: "finish-today",
      },
      note: bonusSuppressedByReminder.value ? t("space.panel.reminderPriorityNote") : "",
      collapsedText: t("space.panel.collapsedSafe"),
    };
  }

  if (state === "locked") {
    return {
      tone: "locked",
      mood: missionIntensity(mission) === "bonus" ? "explaining" : "thinking",
      label: t("space.ringoGuide.eyebrow"),
      title: t("space.ringoGuide.lockedTitle"),
      body: missionGateTextForShell(mission),
      secondary: [openPath],
    };
  }

  if (state === "done") {
    return {
      tone: "done",
      mood: "proud",
      label: t("space.ringoGuide.eyebrow"),
      title: t("space.ringoGuide.missionDoneTitle"),
      body: t("space.ringoGuide.missionDoneMessage", { mission: missionTitle }),
      secondary: [openPath],
    };
  }

  const ready = props.zone?.action?.state === "ready_today";
  return {
    tone: ready ? "ready" : "neutral",
    mood: ready ? "focus" : "thinking",
    label: t("space.ringoGuide.eyebrow"),
    title: ready ? t("space.ringoGuide.readyTitle") : t("space.ringoGuide.fallbackTitle"),
    body: ready
      ? t("space.ringoGuide.readyMessage", { path })
      : t("space.ringoGuide.fallbackMessage", { path }),
    secondary: [openPath],
  };
});

const challengeItems = computed(() => {
  const selectedId = selectedPathChallenge.value?.id;

  const rank = (challenge) => {
    if (challenge.isJoined && String(challenge.id || "") === String(selectedId || "")) return 0;
    return challenge.isJoined ? 1 : 2;
  };
  const ordered = pathChallenges.value
    .map((challenge, index) => ({ challenge, index }))
    .sort((a, b) => rank(a.challenge) - rank(b.challenge) || a.index - b.index)
    .map(({ challenge }) => challenge);

  return ordered.map((challenge) => {
    const selected = String(challenge.id || "") === String(selectedId || "");
    const expanded = selected && challenge.isJoined;

    return {
      challenge,
      iconUrl: challengeIconFor(challenge),
      statusLabel: challengeStatusLabel(challenge),
      preview: !challenge.isJoined,
      selected,
      expanded,
      today: expanded
        ? buildTodayMissionRows(challenge.missions || [], {
          focusId: activeShellMission.value?.id,
          requestedTinyId: requestedTinyMission.value?.id,
          dueReminderId: props.dueReminderFocus?.id,
        })
        : null,
    };
  });
});

watch(
  () => selectedPathChallenge.value?.id,
  () => {
    selectedMissionId.value = pendingFocusId.value;
    pendingFocusId.value = null;
    closeRingoChoicePanel();
  },
);

watch(
  () => [props.mode, selectedMission.value?.id],
  () => {
    closeRingoChoicePanel();
  },
);

watch(
  () => props.zone?.zone_key,
  () => {
    openRow.value = null;
    bonusIndex.value = 0;
  },
);

function acceptBonus() {
  const offer = currentBonus.value;
  if (!offer?.mission?.id) return;

  if (String(offer.challenge?.id || "") === String(selectedPathChallenge.value?.id || "")) {
    selectedMissionId.value = offer.mission.id;
  } else {
    pendingFocusId.value = offer.mission.id;
    emit("select-challenge", offer.challenge);
  }
  focusRingoCard();
}

function nextBonus() {
  bonusIndex.value += 1;
}

function missionChips(mission) {
  if (!mission) return [];

  return [
    { key: "intensity", text: missionIntensityLabelFor(mission) },
    mission.estimatedMinutes
      ? { key: "minutes", text: t("space.shell.minutes", { count: mission.estimatedMinutes }) }
      : null,
    mission.xpReward
      ? { key: "xp", text: t("space.shell.xp", { count: mission.xpReward }), ltr: true }
      : null,
  ].filter(Boolean);
}

function completeAction(mission) {
  return {
    key: "complete-selected-mission",
    label: t("space.panel.actionDone"),
    disabled: selectedMissionLoading.value,
    type: "complete-mission",
    mission,
  };
}

function missionSupportActions(mission, { reminder = false } = {}) {
  if (!canUseMissionSupportActions(mission)) return [];

  const actions = [];
  const tinyMission = findTinyMissionFor(mission);
  if (tinyMission) {
    actions.push({
      key: "make-selected-mission-smaller",
      label: t("space.panel.actionSmaller"),
      disabled: selectedMissionLoading.value,
      iconKey: "makeSmaller",
      type: "make-smaller",
      mission: tinyMission,
    });
  }

  actions.push({
    key: "remind-selected-mission",
    label: reminder ? t("space.panel.actionRemindAgain") : t("space.panel.actionRemind"),
    disabled: selectedMissionLoading.value,
    iconKey: "remindLater",
    type: "remind-mission",
    mission,
  });

  actions.push({
    key: "skip-selected-mission",
    label: t("space.panel.actionNotToday"),
    disabled: selectedMissionLoading.value,
    iconKey: "skip",
    type: "skip-mission",
    mission,
  });

  return actions;
}

function toggleRow(row) {
  openRow.value = openRow.value === row ? null : row;
}

function focusRingoCard() {
  nextTick(() => ringoCardRef.value?.focusPrimary());
}

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
    return;
  }

  if (action.type === "review-reminder") {
    reviewReminder(action.reminder);
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

  if (action.type === "finish-today") {
    emit("change-mode", "rest");
    return;
  }

  if (action.type === "open-row") {
    openRow.value = action.row || null;
  }
}

function selectChallengeFromList(challenge) {
  emit("select-challenge", challenge);

  if (!challenge?.isJoined) {
    openRow.value = null;
    focusRingoCard();
  }
}

function selectMissionFromList(mission) {
  if (!mission?.id) return;

  selectedMissionId.value = mission.id;
  openRow.value = null;
  focusRingoCard();
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

// B24: any reminder (due or scheduled, any zone) becomes the Ringo focus.
// LivingSpace opens its zone and challenge; a due reminder still keeps priority.
function reviewReminder(reminder) {
  if (!reminder?.id) return;

  selectedMissionId.value = null;
  openRow.value = null;
  emit("focus-reminder", reminder);
  focusRingoCard();
}

function formatCount(value) {
  return new Intl.NumberFormat(locale.value).format(value);
}

function reminderTimeLabel(reminder) {
  const left = reminderTimeLeft(reminder?.timestamp, props.now);
  if (left.state === "due" || reminder?.due) return t("space.panel.reminderReady");
  if (left.state === "unknown") return t("space.panel.reminderNoTime");

  const hours = formatCount(left.hours);
  const minutes = formatCount(left.minutes);
  if (left.hours && left.minutes) return t("space.panel.timeLeftHoursMinutes", { hours, minutes });
  if (left.hours) return t("space.panel.timeLeftHours", { hours });
  return t("space.panel.timeLeftMinutes", { minutes });
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

function missionIsDueReminder(mission) {
  const reminderId = String(props.dueReminderFocus?.id || "");
  return Boolean(reminderId) && String(mission?.id || "") === reminderId;
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

function missionHasUserDecision(mission) {
  return ["done", "completed", "remind_later", "skipped"].includes(missionStatus(mission));
}

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

function missionIntensityLabelFor(mission) {
  const intensity = String(mission?.intensity || "main").toLowerCase();
  if (["tiny", "bonus"].includes(intensity)) {
    return t(`space.shell.intensity.${intensity}`);
  }

  return t("space.shell.intensity.main");
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
</script>

<style scoped>
.zonePanel {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
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

.pathIcon {
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
  flex: 0 0 auto;
  min-height: 32px;
  white-space: nowrap;
  padding: 6px 10px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.76);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-weight: 800;
}

.emptyText,
.hintText,
.nextReward {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.55;
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




.pathError {
  padding: 8px 9px;
  border-radius: 10px;
  color: rgba(255, 204, 204, 0.88) !important;
  background: rgba(248, 113, 113, 0.10);
  border: 1px solid rgba(248, 113, 113, 0.16);
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

.reminderList {
  display: grid;
  gap: 7px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.reminderItem {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 9px;
  width: 100%;
  min-height: 52px;
  padding: 9px 10px;
  border-radius: 12px;
  color: inherit;
  background: rgba(5, 10, 18, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  text-align: start;
}

.reminderItem.due {
  border-color: rgba(247, 215, 116, 0.22);
  background: rgba(247, 215, 116, 0.05);
}

.reminderItem:hover,
.reminderItem:focus-visible {
  border-color: rgba(110, 229, 255, 0.24);
  outline: none;
}

.reminderBell {
  width: 18px;
  height: 18px;
  object-fit: contain;
  opacity: 0.8;
}

.reminderCopy {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.reminderCopy strong {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.82rem;
}

.reminderCopy small {
  color: rgba(255, 255, 255, 0.54);
  font-size: 0.7rem;
}

.reminderTime {
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  white-space: nowrap;
}

.reminderItem.due .reminderTime {
  color: rgba(247, 215, 116, 0.95);
}

.zoneDetails {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.fullPathLink {
  justify-self: start;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.76rem;
  font-weight: 850;
  text-decoration: none;
}

.fullPathLink:hover,
.fullPathLink:focus-visible {
  text-decoration: underline;
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

}


</style>
