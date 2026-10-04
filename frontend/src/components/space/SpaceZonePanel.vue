<template>
  <aside class="zonePanel">
    <div class="panelHead">
      <div class="panelTitleWrap">
        <span v-if="pathIcon" class="iconFrame panelIconFrame" aria-hidden="true">
          <img :src="pathIcon" alt="" class="pathIcon" />
        </span>
        <div>
          <p class="panelKicker">{{ zone.path_key }}</p>
          <h3>{{ zone.title }}</h3>
        </div>
      </div>

      <button type="button" class="closeButton" @click="$emit('close')">
        {{ t("space.close") }}
      </button>
    </div>

    <div class="panelSection">
      <span class="sectionLabel">
        {{ t("space.unlockedCount", { count: unlockedCount }) }}
      </span>
      <div v-if="zone.unlocked_objects.length" class="panelObjects">
        <SpaceObject
          v-for="reward in zone.unlocked_objects"
          :key="reward.key"
          :reward="reward"
        />
      </div>
      <p v-else class="emptyText">{{ t("space.noUnlocked") }}</p>
    </div>

    <div class="panelSection">
      <span class="sectionLabel">
        {{ t("space.lockedPreviewCount", { count: lockedPreviewCount }) }}
      </span>
      <p v-if="zone.locked_preview_objects.length" class="hintText">
        {{ t("space.lockedPreviewHint") }}
      </p>
      <div v-if="zone.locked_preview_objects.length" class="panelObjects">
        <SpaceObject
          v-for="reward in zone.locked_preview_objects.slice(0, 3)"
          :key="reward.key"
          :reward="reward"
        />
      </div>
      <p v-else class="emptyText">{{ t("space.zoneComplete") }}</p>
    </div>

    <p v-if="zone.next_reward" class="nextReward">
      {{ nextRewardText }}
    </p>

    <div v-if="zone.action" class="panelSection zoneAction" :class="zone.action.state">
      <span class="sectionLabel">{{ t("space.zoneAction.label") }}</span>
      <strong>{{ zone.action.title }}</strong>
      <p>{{ zone.action.text }}</p>
      <p class="flowHint">{{ actionFlowHint }}</p>

      <div class="actionRow">
        <button
          type="button"
          class="actionLink primary"
          @click="$emit('change-mode', zone.action.primaryMode || 'zone')"
        >
          {{ zone.action.primaryLabel }}
        </button>
        <button
          v-if="zone.action.secondaryMode"
          type="button"
          class="actionLink secondary"
          @click="$emit('change-mode', zone.action.secondaryMode)"
        >
          {{ zone.action.secondaryLabel }}
        </button>
        <RouterLink
          v-else-if="zone.action.secondaryTo"
          class="actionLink secondary"
          :to="zone.action.secondaryTo"
        >
          {{ zone.action.secondaryLabel }}
        </RouterLink>
      </div>
    </div>

    <div v-if="mode === 'path'" class="panelSection shellPanel">
      <span class="sectionLabel">{{ t("space.shell.pathLabel") }}</span>
      <span class="shellTitleLine">
        <span v-if="pathIcon" class="iconFrame inlineIconFrame" aria-hidden="true">
          <img :src="pathIcon" alt="" class="inlineIcon" />
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
            <img :src="challengeIconFor(challenge)" alt="" class="ladderIcon" />
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
            <img :src="challengeIconFor(selectedPathChallenge)" alt="" class="inlineIcon" />
          </span>
          <strong>{{ selectedPathChallenge.name }}</strong>
        </span>
        <p v-if="selectedPathChallenge.description">{{ selectedPathChallenge.description }}</p>

        <div class="selectedChallengeActions">
          <button
            v-if="!selectedPathChallenge.isJoined"
            type="button"
            class="actionLink primary"
            :disabled="String(startingChallengeId || '') === String(selectedPathChallenge.id || '')"
            @click="$emit('start-challenge', selectedPathChallenge)"
          >
            <span v-if="String(startingChallengeId || '') === String(selectedPathChallenge.id || '')">
              {{ t("space.shell.startingChallenge") }}
            </span>
            <span v-else>{{ t("space.shell.startChallenge") }}</span>
          </button>
        </div>

        <div v-if="selectedMission" class="selectedMissionFocus">
          <span class="sectionLabel">{{ t("space.shell.selectedMissionLabel") }}</span>
          <div class="selectedMissionFocusHead">
            <span
              v-if="selectedMission.iconUrl"
              class="iconFrame selectedMissionIconFrame"
              aria-hidden="true"
            >
              <img :src="selectedMission.iconUrl" alt="" class="selectedMissionIcon" />
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
          <button
            type="button"
            class="actionLink primary shellCheckin"
            :disabled="!missionCanComplete(selectedMission) || selectedMissionLoading"
            @click="$emit('complete-mission', selectedMission)"
          >
            <span v-if="selectedMissionLoading">{{ t("space.shell.checkingIn") }}</span>
            <span v-else>{{ missionActionLabel(selectedMission) }}</span>
          </button>
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
              <img :src="mission.iconUrl" alt="" class="selectedMissionIcon" />
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
      <RouterLink class="fallbackLink" :to="zone.action?.fallbackTo || '/paths'">
        {{ t("space.shell.openFullPath") }}
      </RouterLink>
    </div>

    <div v-if="mode === 'challenge'" class="panelSection shellPanel">
      <span class="sectionLabel">{{ t("space.shell.challengeLabel") }}</span>
      <span class="shellTitleLine">
        <span v-if="challengeIcon" class="iconFrame inlineIconFrame" aria-hidden="true">
          <img :src="challengeIcon" alt="" class="inlineIcon" />
        </span>
        <strong>{{ zone.action?.challenge?.name || t("common.challenge") }}</strong>
      </span>
      <p>{{ challengeStatusText }}</p>
      <div class="miniStats">
        <span>
          <strong>{{ zone.action?.challenge?.streak || 0 }}</strong>
          <small>{{ t("space.shell.streak") }}</small>
        </span>
        <span>
          <strong>{{ zone.action?.challenge?.totalCheckins || 0 }}</strong>
          <small>{{ t("space.shell.checkins") }}</small>
        </span>
      </div>
      <div v-if="challengeMission" class="missionBrief">
        <span
          v-if="challengeMission.iconUrl"
          class="iconFrame missionIconFrame"
          aria-hidden="true"
        >
          <img :src="challengeMission.iconUrl" alt="" class="missionIcon" />
        </span>
        <div>
          <span class="sectionLabel">{{ t("space.shell.todayMission") }}</span>
          <strong>{{ challengeMission.title || t("common.mission") }}</strong>
          <p v-if="challengeMission.description">{{ challengeMission.description }}</p>
          <div class="missionMeta">
            <span>{{ missionIntensityLabel }}</span>
            <span v-if="challengeMission.estimatedMinutes">
              {{ t("space.shell.minutes", { count: challengeMission.estimatedMinutes }) }}
            </span>
            <span v-if="challengeMission.xpReward">
              {{ t("space.shell.xp", { count: challengeMission.xpReward }) }}
            </span>
          </div>
        </div>
      </div>
      <button
        v-if="zone.action?.challenge?.enrollmentId"
        type="button"
        class="actionLink primary shellCheckin"
        :disabled="challengeDone || challengeLoading"
        @click="$emit('checkin', zone.action.challenge.enrollmentId)"
      >
        <span v-if="challengeLoading">{{ t("space.shell.checkingIn") }}</span>
        <span v-else-if="challengeDone">{{ t("space.shell.doneToday") }}</span>
        <span v-else>{{ t("space.shell.checkInToday") }}</span>
      </button>
      <RouterLink class="fallbackLink" :to="zone.action?.fallbackTo || '/challenges'">
        {{ t("space.shell.openFullChallenge") }}
      </RouterLink>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { resolveChallengeIcon, resolvePathIcon } from "@/utils/missionMomentumUtils";
import SpaceObject from "./SpaceObject.vue";

const props = defineProps({
  zone: { type: Object, required: true },
  mode: { type: String, default: "zone" },
  checkingId: { type: [Number, String, null], default: null },
  pathLoading: { type: Boolean, default: false },
  pathError: { type: String, default: "" },
  selectedChallengeId: { type: [Number, String, null], default: null },
  completingMissionId: { type: [Number, String, null], default: null },
  startingChallengeId: { type: [Number, String, null], default: null },
});

const emit = defineEmits(["change-mode", "select-challenge", "start-challenge", "complete-mission", "checkin", "close"]);

const { t } = useI18n();

const unlockedCount = computed(() => props.zone?.unlocked_objects?.length || 0);
const lockedPreviewCount = computed(() => props.zone?.locked_preview_objects?.length || 0);

const nextRewardText = computed(() => {
  const reward = props.zone?.next_reward;
  if (!reward) return "";

  if (reward.unlock_condition_type === "first_path_mission_done") {
    return t("space.nextRewardFirst", { reward: reward.title });
  }

  return t("space.nextRewardFuture", { reward: reward.title });
});

const challengeStatusText = computed(() => {
  if (props.zone?.action?.challenge?.status === "done_today") {
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
  return resolveChallengeIcon(props.zone?.action?.challenge?.id || "");
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
  if (!missions.length) return null;

  if (selectedMissionId.value) {
    const selected = missions.find((mission) => {
      return String(mission.id || "") === String(selectedMissionId.value || "");
    });

    if (selected) return selected;
  }

  return missions.find((mission) => {
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
  return Boolean(props.zone?.action?.challenge?.todayChecked)
    || props.zone?.action?.challenge?.status === "done_today";
});

const challengeLoading = computed(() => {
  const enrollmentId = props.zone?.action?.challenge?.enrollmentId;
  if (!enrollmentId || props.checkingId == null) return false;

  return String(props.checkingId) === String(enrollmentId);
});

const selectedMissionLoading = computed(() => {
  const missionId = selectedMission.value?.id;
  if (!missionId || props.completingMissionId == null) return false;

  return String(props.completingMissionId) === String(missionId);
});

watch(
  () => selectedPathChallenge.value?.id,
  () => {
    selectedMissionId.value = null;
  },
);

function challengeIconFor(challenge) {
  return resolveChallengeIcon(challenge?.id || "");
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

function missionStatusLabel(mission) {
  const status = String(mission?.status || "pending").toLowerCase();
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

function missionHasUserDecision(mission) {
  return ["done", "completed", "remind_later", "skipped"].includes(missionStatus(mission));
}

function shouldShowMissionInLivingSpace(mission) {
  const intensity = missionIntensity(mission);
  if (intensity === "main") return true;
  if (intensity === "tiny") return missionHasUserDecision(mission);
  if (intensity === "bonus") return true;
  return Boolean(mission.availableToday) || missionHasUserDecision(mission);
}

function missionGateText(mission) {
  const intensity = missionIntensity(mission);

  if (intensity === "tiny" && !missionDone(mission)) {
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
  if (missionIntensity(mission) === "tiny") return false;
  if (missionIntensity(mission) === "bonus" && !mainMissionDone.value) return false;
  if (!mission?.availableToday) return false;
  return !["done", "completed", "locked"].includes(missionStatus(mission));
}

function missionActionLabel(mission) {
  if (!selectedPathChallenge.value?.isJoined) return t("space.shell.startChallengeFirst");
  if (missionIntensity(mission) === "tiny") {
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
</script>

<style scoped>
.zonePanel {
  display: grid;
  gap: 14px;
  min-width: 0;
  padding: 14px;
  border-radius: 20px;
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
  filter: brightness(0) invert(1) drop-shadow(0 5px 8px rgba(0, 0, 0, 0.38));
}

.panelIconFrame {
  width: 36px;
  height: 36px;
}

.pathIcon {
  width: 21px;
  height: 21px;
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

.panelObjects {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
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

.actionRow {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.actionLink {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 7px 11px;
  border-radius: 10px;
  text-decoration: none;
  font-size: 0.78rem;
  font-weight: 850;
  border: 0;
  cursor: pointer;
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
  width: 17px;
  height: 17px;
}

.inlineIconFrame {
  width: 27px;
  height: 27px;
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
  display: flex;
  gap: 10px;
  min-width: 0;
  overflow-x: auto;
  padding: 2px 2px 4px;
  scrollbar-width: thin;
}

.ladderHead {
  display: grid;
  align-content: start;
  gap: 3px;
  min-width: 180px;
  max-width: 220px;
  padding: 9px 2px;
  flex: 0 0 auto;
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
  width: 260px;
  min-width: 232px;
  flex: 0 0 auto;
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
  width: 38px;
  height: 38px;
  border-radius: 50%;
}

.ladderIcon {
  width: 22px;
  height: 22px;
  object-fit: contain;
  filter: brightness(0) invert(1) drop-shadow(0 5px 8px rgba(0, 0, 0, 0.38));
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

.selectedChallengeActions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
  width: 34px;
  height: 34px;
  border-radius: 50%;
}

.selectedMissionIcon {
  width: 20px;
  height: 20px;
  object-fit: contain;
  filter: brightness(0) invert(1) drop-shadow(0 5px 8px rgba(0, 0, 0, 0.38));
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

.fallbackLink {
  justify-self: start;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.78rem;
  font-weight: 850;
  text-decoration: none;
}

.shellCheckin {
  justify-self: start;
}

.shellCheckin:disabled {
  cursor: default;
  opacity: 0.68;
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
  width: 37px;
  height: 37px;
  border-radius: 50%;
}

.missionIcon {
  width: 22px;
  height: 22px;
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

@media (max-width: 720px) {
  .challengeLadder {
    flex-direction: column;
    overflow: visible;
  }

  .ladderHead,
  .ladderItem {
    width: auto;
    max-width: none;
    min-width: 0;
  }
}
</style>
