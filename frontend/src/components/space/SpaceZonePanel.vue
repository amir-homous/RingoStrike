<template>
  <aside class="zonePanel" :class="[`card-${cardState}`, { flowActive: Boolean(actionFlow) }]">
    <!-- B27: "Do it now" / "Already did it" replace the panel content (no new route). -->
    <MissionActionFlow
      v-if="actionFlow"
      ref="flowRef"
      :key="`${actionFlow.mode}-${actionFlow.mission?.id}`"
      :mode="actionFlow.mode"
      :mission="actionFlow.mission"
      :zone-title="zone.title"
      :path-key="zone.path_key || ''"
      :user-key="userKey"
      :challenge-key="actionFlow.challengeKey"
      :submitting="flowSubmitting"
      :error="flowError"
      @save="saveActionFlow"
      @cancel="closeActionFlow"
      @close="closeActionFlow"
    />

    <template v-else>
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

    <!-- B30 S3 (D49): the path and challenge list moved into the room (trays); the full path stays
         one quiet link away. -->
    <RouterLink to="/paths" class="fullPathLink quiet">
      {{ t("space.panel.fullPath") }}
    </RouterLink>

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

      <!-- B32 (D60, D61): the zone's five objects; placed and next ones show in the room. -->
      <ObjectTiles
        :tiles="objectTileList"
        :selected-key="objectPick?.key || ''"
        @pick="pickObject"
      />

      <p v-if="objectAnnouncement" class="srOnly" aria-live="polite">{{ objectAnnouncement }}</p>

      <!-- B33 (D65, D66): only this zone's reminders, hidden when it has none. -->
      <section v-if="zoneReminderList.length" class="zoneReminders" :aria-labelledby="`${zone.zone_key}-reminders-title`">
        <div class="zoneRemindersHead">
          <h4 :id="`${zone.zone_key}-reminders-title`">{{ t("space.reminders.zoneTitle") }}</h4>
          <span>{{ zoneReminderSummary }}</span>
        </div>
        <div class="zoneReminderRows">
          <ReminderRow
            v-for="reminder in zoneReminderList"
            :key="reminder.id"
            :reminder="reminder"
            @open="reviewReminder({ ...$event, explicit: true })"
          />
        </div>
      </section>
    </div>
    </template>
  </aside>
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { formatNumber, numberAwareT } from "@/lib/i18nNumbers";
import BonusOfferCard from "./BonusOfferCard.vue";
import RingoActionCard from "./RingoActionCard.vue";
import MissionActionFlow from "./MissionActionFlow.vue";
import ObjectTiles from "./ObjectTiles.vue";
import ReminderRow from "./ReminderRow.vue";
import ZoneTodayStrip from "./ZoneTodayStrip.vue";
import {
  bonusOfferCandidates,
  pickFocusMission,
  ringoCardState,
  shouldOfferBonus,
  todayMainDone,
} from "@/lib/livingSpacePanel";
import { challengeIconCandidates } from "@/lib/challengeIconKeys";
import { reminderSummary, zoneReminders } from "@/lib/reminderRows";
import { customReminderAt, defaultPickerTime } from "@/lib/reminderTime";
import { TILE_STATE, objectCardCopy, objectTiles, tileTapResult } from "@/lib/objectsGrid";
import { zoneObjects } from "@/lib/roomScene";
import roomLayout from "@/assets/room/room_layout.json";
import { findFirstReward } from "@/lib/livingSpaceState";
import { resolvePathIcon } from "@/utils/missionMomentumUtils";

const props = defineProps({
  zone: { type: Object, required: true },
  mode: { type: String, default: "zone" },
  checkingId: { type: [Number, String, null], default: null },
  pathLoading: { type: Boolean, default: false },
  pathError: { type: String, default: "" },
  selectedChallengeId: { type: [Number, String, null], default: null },
  completingMissionId: { type: [Number, String, null], default: null },
  // B27: user scope for the flow's sessionStorage timer and remembered place.
  userKey: { type: String, default: "" },
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
  // B30 S2: the user tapped a challenge (tray icon or row); it wins over a due reminder (D41).
  challengePicked: { type: Boolean, default: false },
  // B30 S2: the challenge just joined from the room (post-join card, D39).
  joinedChallengeId: { type: [Number, String, null], default: null },
  // B30 S3: a paw tapped in the room's mission tray (D51).
  pickedMissionId: { type: [Number, String, null], default: null },
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
  "highlight-object",
]);

const { locale, t: baseT } = useI18n();
const router = useRouter();
// B10: numbers in copy use the locale's digits; a numeric count picks the plural form.
const t = numberAwareT(baseT, () => locale.value);
const fmt = (value) => formatNumber(value, locale.value);
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

  // B32 (D60): the "First object placed" line is gone; the objects grid shows it.
  if (firstRewardUnlocked.value) return "";

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

const todayProgress = computed(() => {
  const detail = props.zone?.pathDetail || {};
  return {
    done: Number(detail.todayDone || 0),
    total: Number(detail.todayTotal || 0),
  };
});

const selectedPathChallenge = computed(() => {
  if (!pathChallenges.value.length) return null;

  const picked = props.challengePicked && props.selectedChallengeId
    ? pathChallenges.value.find((challenge) => String(challenge.id || "") === String(props.selectedChallengeId))
    : null;
  if (picked) return picked;

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
    dueMission: props.challengePicked ? null : missionForReminder(props.dueReminderFocus),
    pickedId: props.pickedMissionId ?? selectedMissionId.value ?? props.requestedMissionId,
    explicitPick: Boolean(props.pickedMissionId),
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

// B33 (D65): this zone's reminders only; the room overview keeps just the counts.
const zoneReminderList = computed(() => zoneReminders(props.reminders, props.zone));
const zoneReminderSummary = computed(() => {
  const { due, later } = reminderSummary(zoneReminderList.value);
  return [
    due ? t("space.reminders.summaryDue", { count: due }) : "",
    later ? t("space.reminders.summaryLater", { count: later }) : "",
  ].filter(Boolean).join(" · ");
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
    explicitPick: props.challengePicked,
    justJoined: Boolean(props.joinedChallengeId)
      && String(props.joinedChallengeId) === String(challenge?.id || ""),
    missionPicked: Boolean(props.pickedMissionId)
      && String(props.pickedMissionId) === String(mission?.id ?? ""),
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

// D41: after an explicit pick a due reminder becomes one line in the card.
const reminderLine = computed(() => {
  if (!props.challengePicked || !props.dueReminders.length) return "";
  const first = props.dueReminders[0];
  return t("space.ringoGuide.reminderLine", { mission: first?.title || t("common.mission") });
});

// B32 (D60 to D63): the objects grid. A tapped tile always answers in Ringo's card; only placed
// objects and the next ghost (when the room draws them) also lift and glow in the room.
const OBJECT_ART = import.meta.glob("../../assets/room/objects/*.png", { eager: true, import: "default" });
const hasObjectArt = (path) => Object.keys(OBJECT_ART).some((file) => file.endsWith(`/${path}`));
const objectPick = ref(null);
let objectNonce = 0;

const objectTileList = computed(() => {
  const zone = props.zone;
  const layoutZone = roomLayout.zones?.[zone?.zone_key];
  const drawn = layoutZone ? zoneObjects(layoutZone, zone, hasObjectArt) : { placed: [], ghost: null };
  const placedKeys = new Set(drawn.placed.map((item) => item.key));
  return objectTiles(zone, {
    inRoom: (reward, state) => (state === TILE_STATE.PLACED ? placedKeys.has(reward.key) : drawn.ghost?.key === reward.key),
  });
});

const objectCard = computed(() => {
  const tile = objectPick.value;
  if (!tile) return null;
  const placed = tile.state === TILE_STATE.PLACED;
  const title = tile.reward?.title || t("space.objectHistory.unknown");
  const body = objectCardCopy(tile, { pathName: props.zone?.pathName || "", locale: locale.value, t });
  return {
    tone: placed ? "objectPlaced" : "objectLater",
    mood: placed ? "happy" : "thinking",
    label: t("space.ringoGuide.eyebrow"),
    title,
    body,
    chips: [{ key: "state", text: placed ? t("space.objectHistory.savedSource") : t("space.objectHistory.previewSource") }],
    secondary: [{ key: "back-to-step", type: "back-to-step", label: t("space.objectGrid.backToStep") }],
    collapsedText: title,
  };
});

const objectAnnouncement = computed(() => (objectCard.value ? `${objectCard.value.title}. ${objectCard.value.body}` : ""));

// Picking a challenge or a paw in the room (or a new mission) leaves the object's story.
watch(
  () => [props.selectedChallengeId, props.pickedMissionId, props.challengePicked],
  () => { objectPick.value = null; },
);

function pickObject(tile) {
  const result = tileTapResult(tile);
  if (!result.card) return;
  // Keep the tile list fresh: the tile object can be stale after a reload of the zone.
  objectPick.value = objectTileList.value.find((item) => item.key === tile.key) || tile;
  openRow.value = null;
  // D61: a locked object answers only in Ringo's card; any earlier room effect ends.
  if (!result.room) {
    emit("highlight-object", null);
    return;
  }
  objectNonce += 1;
  const name = tile.reward?.title || "";
  emit("highlight-object", {
    key: tile.key,
    ghost: tile.state === TILE_STATE.NEXT,
    label: tile.state === TILE_STATE.NEXT ? t("space.objectGrid.ghostLabel", { name }) : name,
    nonce: objectNonce,
  });
}

const ringoCard = computed(() => {
  if (objectCard.value) return objectCard.value;
  let card = baseRingoCard.value;
  // D49: the path list is gone, so its error and loading text live in the card.
  if (props.pathError && !card.note) card = { ...card, note: props.pathError };
  if (!reminderLine.value || cardState.value === "reminder") return card;
  return { ...card, note: card.note ? `${card.note} ${reminderLine.value}` : reminderLine.value };
});

const baseRingoCard = computed(() => {
  const state = cardState.value;
  const path = props.zone?.title || t("space.eyebrow");
  const mission = activeShellMission.value;
  const challenge = selectedPathChallenge.value;
  const missionTitle = mission?.title || t("common.mission");

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
    };
  }

  if (state === "joined") {
    const name = challenge?.name || t("common.challenge");
    return {
      tone: "done",
      mood: "happy",
      label: t("space.ringoGuide.eyebrow"),
      title: t("space.ringoGuide.joinedTitle", { challenge: name }),
      body: t("space.ringoGuide.joinedBody"),
      primary: {
        key: "show-today-step",
        label: t("space.ringoGuide.joinedPrimary"),
        type: "show-step",
        challenge,
      },
      collapsedText: t("space.ringoGuide.joinedTitle", { challenge: name }),
    };
  }

  // D40: an invite-only challenge cannot be joined from the room; the card points to Challenges.
  if (state === "preview" && challenge?.needsCode) {
    const name = challenge?.name || t("common.challenge");
    return {
      tone: "start",
      mood: "thinking",
      label: t("space.ringoGuide.eyebrow"),
      title: t("space.ringoGuide.inviteOnlyTitle"),
      body: t("space.ringoGuide.inviteOnlyMessage", { challenge: name }),
      primary: { key: "open-challenges", label: t("space.ringoGuide.openChallenges"), type: "open-challenges" },
      secondary: [{ key: "not-now", label: t("space.ringoGuide.notNow"), type: "not-now" }],
    };
  }

  // D38: a tapped challenge that is not joined yet: Ringo introduces it, Join is the primary.
  if (state === "preview" && props.challengePicked) {
    const name = challenge?.name || t("common.challenge");
    const days = Number(challenge?.estimatedDays || 0);
    const intro = String(challenge?.description || "").trim();
    return {
      tone: "start",
      mood: "welcome",
      label: t("space.ringoGuide.eyebrow"),
      title: t("space.ringoGuide.challengePreviewTitle"),
      body: [t("space.ringoGuide.challengePreviewMessage", { challenge: name, path }), intro].filter(Boolean).join(" "),
      chips: days > 0 ? [{ key: "days", text: t("space.ringoGuide.daysChip", { count: days }) }] : [],
      note: props.pathError || "",
      primary: {
        key: "join-selected-challenge",
        label: t("space.ringoGuide.joinChallenge"),
        disabled: String(props.startingChallengeId || "") === String(challenge?.id || ""),
        type: "start-challenge",
        challenge,
      },
      secondary: [{ key: "not-now", label: t("space.ringoGuide.notNow"), type: "not-now" }],
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
      doneStatus: true,
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
    };
  }

  if (state === "done") {
    return {
      tone: "done",
      mood: "proud",
      label: t("space.ringoGuide.eyebrow"),
      title: t("space.ringoGuide.missionDoneTitle"),
      body: t("space.ringoGuide.missionDoneMessage", { mission: missionTitle }),
      doneStatus: missionIntensity(mission) === "main",
    };
  }

  // D49: no path list any more, so the fallback card says when challenges are loading or absent.
  if (!pathChallenges.value.length) {
    return {
      tone: "neutral",
      mood: "thinking",
      label: t("space.ringoGuide.eyebrow"),
      title: t("space.ringoGuide.fallbackTitle"),
      body: props.pathLoading ? t("space.shell.pathLoading") : t("space.shell.noPathChallenges"),
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
  };
});

watch(
  () => selectedPathChallenge.value?.id,
  () => {
    selectedMissionId.value = pendingFocusId.value;
    pendingFocusId.value = null;
    closeRingoChoicePanel();
  },
);

// Compared as a string: an array getter would fire on every re-evaluation (the minute tick), closing
// an open choice panel, such as the B35 time field, while the user is still filling it in.
watch(
  () => `${props.mode}|${selectedMission.value?.id ?? ""}`,
  () => {
    closeRingoChoicePanel();
  },
);

watch(
  () => props.zone?.zone_key,
  () => {
    openRow.value = null;
    bonusIndex.value = 0;
    objectPick.value = null;
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
    // B27: main missions get the split action; tiny and bonus keep the single button.
    split: missionIntensity(mission) === "main",
    submitting: selectedMissionLoading.value,
  };
}

// B27 flows. The save goes through the normal completion (and its reward sequence); a failed
// save keeps the user's answers and shows a calm inline error.
const actionFlow = ref(null);
const flowRef = ref(null);
const flowSubmitting = ref(false);
const flowError = ref("");

function openActionFlow(mode, mission) {
  if (!mission?.id) return;
  objectPick.value = null;
  flowError.value = "";
  flowSubmitting.value = false;
  // B31: the challenge picks a challenge-specific focus background or music folder, when one exists.
  const challengeKey = selectedPathChallenge.value?.iconKey
    || challengeIconCandidates(props.zone?.action?.challenge)[0]
    || "";
  actionFlow.value = { mode, mission, challengeKey };
}

function closeActionFlow() {
  if (flowSubmitting.value) return;
  actionFlow.value = null;
  flowError.value = "";
  nextTick(() => ringoCardRef.value?.focusPrimary());
}

function saveActionFlow(context) {
  const mission = actionFlow.value?.mission;
  if (!mission || flowSubmitting.value) return;
  flowSubmitting.value = true;
  flowError.value = "";
  emit("complete-mission", mission, {
    context,
    onResult: (result) => {
      flowSubmitting.value = false;
      if (result?.ok) {
        flowRef.value?.clearTimer();
        actionFlow.value = null;
      } else {
        flowError.value = result?.error || "save_failed";
      }
    },
  });
}

function missionSupportActions(mission, { reminder = false } = {}) {
  if (!canUseMissionSupportActions(mission)) return [];

  const actions = [];
  const tinyMission = findTinyMissionFor(mission);
  if (tinyMission) {
    actions.push({
      key: "make-selected-mission-smaller",
      label: t("space.panel.actionSmaller"),
      shortLabel: t("space.missionAction.smallerShort"),
      disabled: selectedMissionLoading.value,
      iconKey: "makeSmaller",
      type: "make-smaller",
      mission: tinyMission,
    });
  }

  actions.push({
    key: "remind-selected-mission",
    label: reminder ? t("space.panel.actionRemindAgain") : t("space.panel.actionRemind"),
    shortLabel: t("space.missionAction.remindShort"),
    disabled: selectedMissionLoading.value,
    iconKey: "remindLater",
    type: "remind-mission",
    mission,
  });

  actions.push({
    key: "skip-selected-mission",
    label: t("space.panel.actionNotToday"),
    shortLabel: t("space.missionAction.notTodayShort"),
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

  // B32: back from an object's story to today's step.
  if (action.type === "back-to-step") {
    objectPick.value = null;
    nextTick(() => ringoCardRef.value?.focusPrimary());
    return;
  }

  // B30 S2 (D38-D40): "Not now" drops the pick; after joining, show that challenge's step.
  if (action.type === "not-now") {
    emit("select-challenge", null);
    return;
  }

  if (action.type === "show-step") {
    emit("select-challenge", action.challenge);
    return;
  }

  if (action.type === "open-challenges") {
    router.push("/challenges");
    return;
  }

  if (action.type === "start-challenge") {
    emit("start-challenge", action.challenge);
    return;
  }

  if (action.type === "complete-mission") {
    emit("complete-mission", action.mission);
    return;
  }

  if (action.type === "start-focus") {
    openActionFlow("focus", action.mission);
    return;
  }

  if (action.type === "already-did") {
    openActionFlow("earlier", action.mission);
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

function openRingoChoicePanel(type, mission) {
  if (!mission?.id) return;

  if (type === "reminder") {
    ringoChoicePanel.value = {
      type,
      mission,
      prompt: t("missions.remindOptions.prompt"),
      options: [
        ...REMINDER_OPTION_KEYS.map((key) => ({
          key,
          label: t(`missions.remindOptions.${key}`),
          reminderAt: reminderAtForOption(key).toISOString(),
        })),
        // B35 (D69): a custom time today.
        { key: "pickTime", label: t("missions.remindOptions.pickTime"), pickTime: true },
      ],
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

  // B35 (D69): Pick a time. The field opens one hour ahead; a time at or after the day reset
  // (or already past, which means tomorrow) is refused with a gentle line and sets nothing.
  if (panel.type === "reminder" && option?.pickTime) {
    ringoChoicePanel.value = { ...panel, picker: { ...defaultPickerTime(), error: "" } };
    return;
  }

  if (panel.type === "reminder" && option?.key === "back-quick") {
    ringoChoicePanel.value = { ...panel, picker: null };
    return;
  }

  if (panel.type === "reminder" && option?.key === "edit-time") {
    if (panel.picker?.error) ringoChoicePanel.value = { ...panel, picker: { ...panel.picker, error: "" } };
    return;
  }

  if (panel.type === "reminder" && option?.key === "set-time") {
    const result = customReminderAt({ hour: option.hour, minute: option.minute });
    if (!result.ok) {
      ringoChoicePanel.value = { ...panel, picker: { hour: option.hour, minute: option.minute, error: result.reason } };
      return;
    }
    closeRingoChoicePanel();
    emit("remind-mission", { mission, reminderAt: result.at.toISOString(), optionKey: "custom" });
    return;
  }

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
/* Rows: head, Ringo card, the quiet full-path link (D49), then the work surface, which takes the
   rest and scrolls. The link has its own row so it never stretches into the free space. */
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

/* B27: while a flow is open it fills the panel (its body scrolls, Save stays visible). */
.zonePanel.flowActive {
  grid-template-rows: minmax(0, 1fr);
  height: 100%;
  overflow: hidden;
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







/* B33: the zone's reminders (board 25). */
.zoneReminders {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.zoneRemindersHead {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.zoneRemindersHead h4 {
  margin: 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 13px;
  font-weight: 700;
}

.zoneRemindersHead span {
  color: rgba(255, 255, 255, 0.62);
  font-size: 12px;
}

.zoneReminderRows {
  display: grid;
  gap: 8px;
}

.fullPathLink {
  justify-self: start;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.76rem;
  font-weight: 850;
  text-decoration: none;
}

/* D49: a quiet link under the Ringo card; at least 44px tall to tap. */
.fullPathLink.quiet {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  margin-top: -8px;
  padding: 0 4px;
  color: rgba(110, 229, 255, 0.72);
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
