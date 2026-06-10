<template>
  <AppContainer>
    <AppHeader />

    <main class="pathsPage">
      <UiState
        :loading="loading"
        :error="!!error"
        :empty="!loading && !error && paths.length === 0"
        :loading-title="t('paths.loadingTitle')"
        :loading-text="t('paths.loadingText')"
        :error-title="t('paths.errorTitle')"
        :error-text="error || t('common.pleaseTryAgain')"
        :empty-title="t('paths.emptyTitle')"
        :empty-text="t('paths.emptyText')"
        @retry="loadPaths"
      />

      <template v-if="!loading && !error && paths.length">
        <RingoCoach
          v-if="pathCoach"
          class="pathCoach"
          :message="pathCoach.message"
          :sprite="pathCoach.sprite_key"
          :primary-action="pathCoach.primary_action"
          :secondary-action="pathCoach.secondary_action"
          @action="handleCoachAction"
        />

        <section class="pathsHero">
          <div>
            <p class="eyebrow">{{ t("pathsPage.eyebrow") }}</p>
            <h1>{{ t("pathsPage.title") }}</h1>
            <p>{{ t("pathsPage.subtitle", { path: selectedPath?.title || t('pathsPage.fallbackPath') }) }}</p>
          </div>

          <div class="pathMetrics" :aria-label="t('pathsPage.metricsLabel')">
            <span>
              <strong>{{ activePathCount }}</strong>
              <small>{{ t("pathsPage.metrics.active") }}</small>
            </span>
            <span>
              <strong>{{ securedPathCount }}</strong>
              <small>{{ t("pathsPage.metrics.secured") }}</small>
            </span>
            <span>
              <strong>{{ availableNextPathCount }}</strong>
              <small>{{ t("pathsPage.metrics.available") }}</small>
            </span>
          </div>
        </section>

        <section class="pathPicker" :aria-label="t('pathsPage.pickPath')">
          <button
            v-for="path in paths"
            :key="path.path_id"
            type="button"
            class="pathButton"
            :class="pathButtonClass(path)"
            @click="selectPath(path)"
          >
            <span
              class="pathIcon"
              :style="{ '--path-color': path.color || '#6ee5ff' }"
            >
              {{ path.icon?.slice(0, 1)?.toUpperCase() || "P" }}
            </span>

            <span class="pathButtonCopy">
              <strong>{{ path.title }}</strong>
              <small>{{ pathButtonLabel(path) }}</small>
            </span>

            <span class="pathButtonMeta">
              <span>
                <strong>{{ pathCardSummary(path).joined }}</strong>
                <small>{{ t("pathsPage.pathCard.joined") }}</small>
              </span>
              <span>
                <strong>{{ pathCardSummary(path).mission }}</strong>
                <small>{{ t("pathsPage.pathCard.today") }}</small>
              </span>
            </span>

            <span class="pathButtonHint">
              {{ pathCardSummary(path).hint }}
            </span>
          </button>
        </section>

        <section v-if="selectedPath" class="pathDetail">
          <BaseCard class="selectedPathCard">
            <div class="detailIntro">
              <p class="eyebrow compact">{{ t("pathsPage.selectedEyebrow") }}</p>
              <h2>{{ selectedPath.title }}</h2>
              <p>{{ selectedPath.description }}</p>

              <div class="pathStatusRow">
                <span>{{ pathButtonLabel(selectedPath) }}</span>
                <span>{{ pathCardSummary(selectedPath).hint }}</span>
              </div>
            </div>

            <div v-if="pathProgress" class="progressPanel" :class="{ complete: pathProgress.todayComplete }">
              <div>
                <p class="eyebrow compact">{{ t("pathsPage.todaySummary") }}</p>
                <h3>{{ pathProgress.title }}</h3>
                <p>{{ pathProgress.body }}</p>
              </div>

              <div v-if="hasUsefulPathStats" class="progressStats">
                <span v-if="todayTotal > 0">
                  <strong>{{ pathSummary.today_missions_done }}/{{ pathSummary.today_missions_total }}</strong>
                  <small>{{ t("pathsPage.missionsDone") }}</small>
                </span>
                <span v-if="pathSummary.joined_challenges > 0">
                  <strong>{{ pathSummary.today_checked_challenges }}/{{ pathSummary.joined_challenges }}</strong>
                  <small>{{ t("pathsPage.challengesSecured") }}</small>
                </span>
              </div>
              <div v-else class="progressEmpty">
                <strong>{{ t("pathsPage.noActiveMissionTitle") }}</strong>
                <small>{{ t("pathsPage.noActiveMissionText") }}</small>
              </div>

              <div class="detailActions">
                <BaseButton
                  v-if="pathProgress.action === 'start'"
                  variant="primary"
                  :loading="starting"
                  @click="startSelectedPath"
                >
                  {{ pathProgress.primaryCta }}
                </BaseButton>

                <BaseButton
                  v-if="pathProgress.action === 'preview'"
                  variant="primary"
                  @click="previewChallengeCard(nextChallenge)"
                >
                  {{ pathProgress.primaryCta }}
                </BaseButton>

                <BaseButton
                  v-if="pathProgress.action === 'startNext'"
                  variant="primary"
                  :loading="startingChallengeId === nextChallenge?.challenge_id"
                  @click="startChallenge(nextChallenge)"
                >
                  {{ pathProgress.primaryCta }}
                </BaseButton>

                <BaseButton
                  v-if="pathProgress.action === 'selectOther'"
                  variant="primary"
                  @click="selectPath(nextUsefulPath)"
                >
                  {{ pathProgress.primaryCta }}
                </BaseButton>

                <RouterLink
                  v-if="pathProgress.action === 'dashboard'"
                  class="detailLink primary"
                  to="/dashboard"
                >
                  {{ pathProgress.primaryCta }}
                </RouterLink>

                <RouterLink
                  v-if="currentChallenge?.enrollment_id && pathProgress.action !== 'preview'"
                  class="detailLink"
                  :to="`/enrollment/${currentChallenge.enrollment_id}`"
                >
                  {{ t("pathsPage.viewDetails") }}
                </RouterLink>
              </div>
            </div>
          </BaseCard>

          <UiState
            :loading="challengesLoading"
            :error="!!challengesError"
            :empty="!challengesLoading && !challengesError && challenges.length === 0"
            :loading-title="t('paths.challengesLoadingTitle')"
            :loading-text="t('paths.challengesLoadingText')"
            :error-title="t('paths.challengesErrorTitle')"
            :error-text="challengesError || t('common.pleaseTryAgain')"
            :empty-title="t('paths.challengesEmptyTitle')"
            :empty-text="t('paths.challengesEmptyText')"
            @retry="loadPathChallenges(selectedPath)"
          />

          <div v-if="!challengesLoading && !challengesError && challenges.length" class="challengeStack">
            <BaseCard
              v-for="challenge in challenges"
              :key="challenge.challenge_id"
              :id="`path-challenge-${challenge.challenge_id}`"
              class="challengePanel"
              :class="{
                joined: challenge.is_joined,
                current: currentChallenge?.challenge_id === challenge.challenge_id,
                secured: challenge.today_checked,
              }"
            >
              <div class="challengeTop">
                <div class="challengeCopy">
                  <div class="challengeKicker">
                    <span>{{ t("paths.stage", { stage: challenge.stage || 1 }) }}</span>
                    <span v-if="challenge.is_joined">
                      {{ challenge.today_checked ? t("pathsPage.securedToday") : t("pathsPage.activeNow") }}
                    </span>
                    <span v-else-if="nextChallenge?.challenge_id === challenge.challenge_id">
                      {{ t("pathsPage.recommendedNext") }}
                    </span>
                  </div>

                  <h3>{{ challenge.name }}</h3>
                  <p>{{ challenge.ringo_intro || challenge.description }}</p>
                </div>

                <div class="challengeSummary">
                  <span class="summaryItem primary">
                    <strong>{{ challenge.is_joined ? t("pathsPage.summary.joined") : t("pathsPage.summary.available") }}</strong>
                    <small>{{ challenge.today_checked ? t("pathsPage.summary.doneToday") : t("pathsPage.summary.nextAction") }}</small>
                  </span>
                  <span class="summaryItem">
                    <strong>{{ challenge.estimated_days || challenge.duration_days || 0 }}</strong>
                    <small>{{ t("pathsPage.summary.estimatedDays") }}</small>
                  </span>
                  <span class="summaryItem">
                    <strong>{{ challenge.today_missions_total || challenge.missions?.length || 0 }}</strong>
                    <small>{{ challenge.is_joined ? t("pathsPage.summary.todayMissions") : t("pathsPage.summary.previewMissions") }}</small>
                  </span>
                </div>
              </div>

              <div v-if="challenge.is_joined" class="challengeProgress">
                <span v-if="challenge.today_missions_total > 0">
                  {{ t("pathsPage.challengeMissionProgress", {
                    done: challenge.today_missions_done || 0,
                    total: challenge.today_missions_total || 0,
                  }) }}
                </span>
                <span v-else>
                  {{ t("pathsPage.noMissionReady") }}
                </span>
                <span>
                  {{ t("pathsPage.totalCheckins", { count: challenge.total_checkins || 0 }) }}
                </span>
              </div>

              <div class="challengeActions">
                <BaseButton
                  v-if="!challenge.is_joined"
                  variant="primary"
                  :loading="startingChallengeId === challenge.challenge_id"
                  @click="startChallenge(challenge)"
                >
                  {{ t("pathsPage.startChallenge") }}
                </BaseButton>

                <RouterLink
                  v-else-if="!challenge.today_checked"
                  class="detailLink primary"
                  to="/dashboard"
                >
                  {{ t("paths.openTodayMission") }}
                </RouterLink>

                <RouterLink
                  v-if="challenge.enrollment_id"
                  class="detailLink"
                  :to="`/enrollment/${challenge.enrollment_id}`"
                >
                  {{ challenge.today_checked ? t("pathsPage.viewCompletedDetails") : t("pathsPage.viewDetails") }}
                </RouterLink>
              </div>

              <div v-if="challenge.missions?.length" class="missionListBlock">
                <div class="missionListHead">
                  <strong>
                    {{ challenge.is_joined ? t("pathsPage.todayMissionList") : t("pathsPage.previewMissionList") }}
                  </strong>
                  <small>
                    {{ challenge.is_joined ? t("pathsPage.todayMissionHelp") : t("pathsPage.previewMissionHelp") }}
                  </small>
                </div>

                <div class="missionList">
                <article
                  v-for="mission in challenge.missions"
                  :key="mission.mission_id"
                  class="missionPreview"
                  :class="[mission.today_status, { preview: !challenge.is_joined }]"
                >
                  <span>{{ missionStatusLabel(mission) }} · {{ mission.xp_reward }} XP</span>
                  <strong>{{ mission.title }}</strong>
                  <p>{{ mission.description }}</p>
                  <small v-if="mission.today_status === 'locked'">
                    {{ missionUnlockLabel(mission) }}
                  </small>
                </article>
                </div>
              </div>
            </BaseCard>
          </div>
        </section>
      </template>
    </main>
  </AppContainer>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import api from "@/lib/api";
import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import RingoCoach from "@/components/ringo/RingoCoach.vue";

const { t } = useI18n();
const router = useRouter();

const paths = ref([]);
const selectedPath = ref(null);
const challenges = ref([]);
const pathSummaries = ref({});
const pathChallengeCounts = ref({});
const pathSummary = ref({
  joined_challenges: 0,
  today_checked_challenges: 0,
  today_missions_done: 0,
  today_missions_total: 0,
});
const loading = ref(true);
const error = ref("");
const challengesLoading = ref(false);
const challengesError = ref("");
const starting = ref(false);
const startingChallengeId = ref(null);

function emptySummary() {
  return {
    joined_challenges: 0,
    today_checked_challenges: 0,
    today_missions_done: 0,
    today_missions_total: 0,
  };
}

async function loadPaths() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await api.get("/paths");
    paths.value = data?.items || [];
    selectedPath.value = paths.value.find((path) => path.user_status === "Active") || paths.value[0] || null;

    await preloadPathSummaries(paths.value);

    if (selectedPath.value) setSelectedPathData(selectedPath.value);
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function selectPath(path) {
  selectedPath.value = path;
  if (pathSummaries.value[path.path_id]) {
    setSelectedPathData(path);
    return;
  }

  await loadPathChallenges(path);
}

async function preloadPathSummaries(pathItems) {
  const results = await Promise.all(
    pathItems.map(async (path) => {
      try {
        const { data } = await api.get(`/paths/${path.path_id}/challenges`);
        return {
          pathId: path.path_id,
          summary: data?.summary || emptySummary(),
          items: data?.items || [],
        };
      } catch {
        return {
          pathId: path.path_id,
          summary: emptySummary(),
          items: [],
        };
      }
    }),
  );

  const nextSummaries = {};
  const nextCounts = {};

  for (const result of results) {
    nextSummaries[result.pathId] = result.summary;
    nextCounts[result.pathId] = {
      total: result.items.length,
      joined: result.items.filter((challenge) => challenge.is_joined).length,
      next: result.items.find((challenge) => !challenge.is_joined)?.name || "",
      items: result.items,
    };
  }

  pathSummaries.value = nextSummaries;
  pathChallengeCounts.value = nextCounts;
}

function setSelectedPathData(path) {
  challenges.value = pathChallengeCounts.value[path.path_id]?.items || [];
  pathSummary.value = pathSummaries.value[path.path_id] || emptySummary();
}

async function loadPathChallenges(path) {
  if (!path?.path_id) return;

  challengesLoading.value = true;
  challengesError.value = "";

  try {
    const { data } = await api.get(`/paths/${path.path_id}/challenges`);
    challenges.value = data?.items || [];
    pathSummary.value = data?.summary || emptySummary();
    pathSummaries.value = {
      ...pathSummaries.value,
      [path.path_id]: pathSummary.value,
    };
    pathChallengeCounts.value = {
      ...pathChallengeCounts.value,
      [path.path_id]: {
        total: challenges.value.length,
        joined: challenges.value.filter((challenge) => challenge.is_joined).length,
        next: challenges.value.find((challenge) => !challenge.is_joined)?.name || "",
        items: challenges.value,
      },
    };
  } catch (e) {
    challengesError.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    challengesLoading.value = false;
  }
}

const joinedChallenges = computed(() => {
  return challenges.value.filter((challenge) => challenge.is_joined);
});

const currentChallenge = computed(() => {
  return joinedChallenges.value.find((challenge) => !challenge.today_checked)
    || joinedChallenges.value[0]
    || null;
});

const nextChallenge = computed(() => {
  return challenges.value.find((challenge) => !challenge.is_joined) || null;
});

const todayTotal = computed(() => Number(pathSummary.value.today_missions_total || 0));
const todayDone = computed(() => Number(pathSummary.value.today_missions_done || 0));
const todayComplete = computed(() => todayTotal.value > 0 && todayDone.value >= todayTotal.value);
const hasUsefulPathStats = computed(() => {
  return todayTotal.value > 0 || Number(pathSummary.value.joined_challenges || 0) > 0;
});

const activePath = computed(() => {
  return paths.value.find((path) => path.user_status === "Active") || null;
});

const activePathCount = computed(() => {
  return paths.value.filter((path) => path.user_status === "Active").length;
});

const securedPathCount = computed(() => {
  return paths.value.filter((path) => {
    const summary = pathSummaries.value[path.path_id] || emptySummary();
    const total = Number(summary.today_missions_total || 0);
    const done = Number(summary.today_missions_done || 0);
    return total > 0 && done >= total;
  }).length;
});

const availableNextPathCount = computed(() => {
  return paths.value.filter((path) => {
    const counts = pathChallengeCounts.value[path.path_id];
    return path.user_status !== "Active" && Boolean(counts?.next);
  }).length;
});

const suggestedOtherPath = computed(() => {
  return paths.value.find((path) => {
    if (path.path_id === selectedPath.value?.path_id) return false;
    if (path.user_status === "Active") return false;
    return Boolean(pathChallengeCounts.value[path.path_id]?.next);
  }) || null;
});

const nextUsefulPath = computed(() => {
  if (suggestedOtherPath.value) return suggestedOtherPath.value;

  const otherPaths = paths.value.filter((path) => path.path_id !== selectedPath.value?.path_id);

  return otherPaths.find((path) => {
    if (path.user_status !== "Active") return false;

    const summary = pathSummaries.value[path.path_id] || emptySummary();
    const total = Number(summary.today_missions_total || 0);
    const done = Number(summary.today_missions_done || 0);

    return total > 0 && done < total;
  })
    || otherPaths.find((path) => Boolean(pathChallengeCounts.value[path.path_id]?.next))
    || null;
});

const lockedMissionsCount = computed(() => {
  return challenges.value.reduce((count, challenge) => {
    return count + (challenge.missions || []).filter((mission) => mission.today_status === "locked").length;
  }, 0);
});

const pathCoach = computed(() => {
  if (!selectedPath.value) return null;

  if (!activePath.value) {
    return {
      sprite_key: "welcome",
      message: t("pathsPage.coach.noActivePath", { path: selectedPath.value.title }),
      primary_action: {
        label: t("paths.startFirstMission", { path: selectedPath.value.title }),
        type: "start_path",
      },
      secondary_action: {
        label: t("pathsPage.coach.comparePaths"),
        type: "dismiss",
      },
    };
  }

  if (selectedPath.value.user_status !== "Active") {
    return {
      sprite_key: "explaining",
      message: t("pathsPage.coach.inactiveSelected", { path: selectedPath.value.title }),
      primary_action: nextChallenge.value
        ? {
          label: t("pathsPage.startChallenge"),
          type: "start_challenge",
          challenge_id: nextChallenge.value.challenge_id,
        }
        : {
          label: t("paths.browseChallenges"),
          type: "route",
          to: "/challenges",
        },
      secondary_action: {
        label: t("pathsPage.coach.backToActive", { path: activePath.value.title }),
        type: "select_path",
        path_id: activePath.value.path_id,
      },
    };
  }

  if (!joinedChallenges.value.length) {
    return {
      sprite_key: "focus",
      message: nextChallenge.value
        ? t("pathsPage.coach.readyToStart", { challenge: nextChallenge.value.name })
        : t("pathsPage.coach.noChallengeYet"),
      primary_action: {
        label: t("paths.startFirstMission", { path: selectedPath.value.title }),
        type: "start_path",
      },
      secondary_action: {
        label: t("paths.browseChallenges"),
        type: "route",
        to: "/challenges",
      },
    };
  }

  if (todayComplete.value && nextChallenge.value) {
    return {
      sprite_key: "celebration",
      message: t("pathsPage.coach.todayDoneWithNext", { challenge: nextChallenge.value.name }),
      primary_action: {
        label: t("pathsPage.startChallenge"),
        type: "start_challenge",
        challenge_id: nextChallenge.value.challenge_id,
      },
      secondary_action: {
        label: t("pathsPage.previewNextChallenge"),
        type: "preview_challenge",
        challenge_id: nextChallenge.value.challenge_id,
      },
    };
  }

  if (todayComplete.value && nextUsefulPath.value) {
    return {
      sprite_key: "celebration",
      message: t("pathsPage.coach.todayDoneSuggestOther", {
        path: nextUsefulPath.value.title,
      }),
      primary_action: {
        label: t("pathsPage.startAnotherPath", { path: nextUsefulPath.value.title }),
        type: "select_path",
        path_id: nextUsefulPath.value.path_id,
      },
      secondary_action: {
        label: t("pathsPage.browseLibrary"),
        type: "route",
        to: "/challenges",
      },
    };
  }

  if (todayComplete.value) {
    return {
      sprite_key: "proud",
      message: lockedMissionsCount.value > 0
        ? t("pathsPage.coach.todayDoneLocked")
        : t("pathsPage.coach.todayDoneAll"),
      primary_action: {
        label: t("pathsPage.browseLibrary"),
        type: "route",
        to: "/challenges",
      },
      secondary_action: null,
    };
  }

  if (todayTotal.value <= 0) {
    return {
      sprite_key: "thinking",
      message: lockedMissionsCount.value > 0
        ? t("pathsPage.coach.waitingForUnlock")
        : t("pathsPage.coach.noMissionToday"),
      primary_action: {
        label: t("pathsPage.openDashboard"),
        type: "route",
        to: "/dashboard",
      },
      secondary_action: nextChallenge.value
        ? {
          label: t("pathsPage.previewNextChallenge"),
          type: "preview_challenge",
          challenge_id: nextChallenge.value.challenge_id,
        }
        : null,
    };
  }

  return {
    sprite_key: "encouraging",
    message: t("pathsPage.coach.continueToday", {
      done: todayDone.value,
      total: todayTotal.value,
    }),
    primary_action: {
      label: t("paths.openTodayMission"),
      type: "route",
      to: "/dashboard",
    },
    secondary_action: currentChallenge.value?.enrollment_id
      ? {
        label: t("pathsPage.viewDetails"),
        type: "route",
        to: `/enrollment/${currentChallenge.value.enrollment_id}`,
      }
      : null,
  };
});

const pathProgress = computed(() => {
  if (!selectedPath.value) return null;

  if (!joinedChallenges.value.length) {
    return {
      todayComplete: false,
      title: t("pathsPage.notStartedTitle", { path: selectedPath.value.title }),
      body: nextChallenge.value
        ? t("pathsPage.notStartedBody", { challenge: nextChallenge.value.name })
        : t("pathsPage.noNextChallenge"),
      primaryCta: t("paths.startFirstMission", { path: selectedPath.value.title }),
      action: "start",
    };
  }

  if (todayComplete.value) {
    if (nextChallenge.value) {
      return {
        todayComplete: true,
        title: t("pathsPage.todayCompleteTitle", { path: selectedPath.value.title }),
        body: t("pathsPage.todayCompleteBodyWithNext", { challenge: nextChallenge.value.name }),
        primaryCta: t("pathsPage.startChallenge"),
        action: "startNext",
      };
    }

    if (nextUsefulPath.value) {
      return {
        todayComplete: true,
        title: t("pathsPage.todayCompleteTitle", { path: selectedPath.value.title }),
        body: t("pathsPage.todayCompleteBodyWithOther", { path: nextUsefulPath.value.title }),
        primaryCta: t("pathsPage.startAnotherPath", { path: nextUsefulPath.value.title }),
        action: "selectOther",
      };
    }

    return {
      todayComplete: true,
      title: t("pathsPage.todayCompleteTitle", { path: selectedPath.value.title }),
      body: nextChallenge.value
        ? t("pathsPage.todayCompleteBodyWithNext", { challenge: nextChallenge.value.name })
        : t("pathsPage.todayCompleteBody"),
      primaryCta: nextChallenge.value
        ? t("pathsPage.previewNextChallenge")
        : t("pathsPage.openDashboard"),
      action: nextChallenge.value ? "preview" : "dashboard",
    };
  }

  return {
    todayComplete: false,
    title: currentChallenge.value
      ? t("pathsPage.currentChallengeTitle", { challenge: currentChallenge.value.name })
      : t("pathsPage.pathActiveTitle", { path: selectedPath.value.title }),
    body: todayTotal.value > 0
      ? t("pathsPage.currentChallengeBody", {
        done: todayDone.value,
        total: todayTotal.value,
      })
      : t("pathsPage.noMissionProgressBody"),
    primaryCta: t("paths.openTodayMission"),
    action: "dashboard",
  };
});

function pathButtonClass(path) {
  const isSelected = selectedPath.value?.path_id === path.path_id;
  const isSelectedComplete = isSelected && todayComplete.value;

  return {
    active: isSelected,
    started: path.user_status === "Active",
    complete: isSelectedComplete,
  };
}

function pathButtonLabel(path) {
  if (selectedPath.value?.path_id === path.path_id && todayComplete.value) {
    return t("pathsPage.securedToday");
  }

  if (path.user_status === "Active") return t("paths.active");
  return t("paths.select");
}

function pathCardSummary(path) {
  const summary = pathSummaries.value[path.path_id] || emptySummary();
  const counts = pathChallengeCounts.value[path.path_id] || { total: 0, joined: 0, next: "" };
  const todayMissionTotal = Number(summary.today_missions_total || 0);
  const todayMissionDone = Number(summary.today_missions_done || 0);
  const joined = Number(summary.joined_challenges || counts.joined || 0);
  const total = Number(counts.total || 0);

  let hint = t("pathsPage.pathCard.readyHint");

  if (path.user_status === "Active" && todayMissionTotal > 0 && todayMissionDone >= todayMissionTotal) {
    hint = counts.next
      ? t("pathsPage.pathCard.doneNextHint", { challenge: counts.next })
      : t("pathsPage.pathCard.doneHint");
  } else if (path.user_status === "Active" && todayMissionTotal > 0) {
    hint = t("pathsPage.pathCard.continueHint", {
      done: todayMissionDone,
      total: todayMissionTotal,
    });
  } else if (joined > 0) {
    hint = t("pathsPage.pathCard.waitingHint");
  } else if (counts.next) {
    hint = t("pathsPage.pathCard.startHint", { challenge: counts.next });
  }

  return {
    joined: `${joined}/${total}`,
    mission: todayMissionTotal > 0
      ? `${todayMissionDone}/${todayMissionTotal}`
      : t("pathsPage.pathCard.noMission"),
    hint,
  };
}

function missionStatusLabel(mission) {
  return t(`missions.status.${mission.today_status || "pending"}`);
}

function missionUnlockLabel(mission) {
  if (!mission.available_today && Number(mission.unlocks_in_days || 0) <= 0) {
    return t("pathsPage.unlocksAfterJoin");
  }

  const days = Number(mission.unlocks_in_days || 0);

  if (days <= 1) return t("pathsPage.unlocksTomorrow");
  return t("pathsPage.unlocksInDays", { count: days });
}

async function previewChallengeCard(challenge) {
  if (!challenge?.challenge_id) return;

  await nextTick();
  document
    .getElementById(`path-challenge-${challenge.challenge_id}`)
    ?.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function handleCoachAction(action) {
  if (!action) return;

  if (action.type === "start_path") {
    await startSelectedPath();
    return;
  }

  if (action.type === "start_challenge") {
    const challenge = challenges.value.find((item) => item.challenge_id === action.challenge_id)
      || nextChallenge.value;
    await startChallenge(challenge);
    return;
  }

  if (action.type === "preview_challenge") {
    const challenge = challenges.value.find((item) => item.challenge_id === action.challenge_id)
      || nextChallenge.value;
    await previewChallengeCard(challenge);
    return;
  }

  if (action.type === "select_path") {
    const path = paths.value.find((item) => item.path_id === action.path_id);
    if (path) await selectPath(path);
  }
}

async function startChallenge(challenge) {
  if (!challenge?.challenge_id) return;

  startingChallengeId.value = challenge.challenge_id;
  error.value = "";

  try {
    if (selectedPath.value?.path_id) {
      await api.post(`/paths/${selectedPath.value.path_id}/start`, {});
    }

    await api.post(`/challenges/${challenge.challenge_id}/join`, {});
    await loadPaths();
    router.push("/dashboard");
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    startingChallengeId.value = null;
  }
}

async function startSelectedPath() {
  if (!selectedPath.value) return;

  starting.value = true;
  error.value = "";

  try {
    const firstChallenge = challenges.value[0];

    if (firstChallenge?.challenge_id) {
      await startChallenge(firstChallenge);
      return;
    }

    await api.post(`/paths/${selectedPath.value.path_id}/start`, {});
    await loadPaths();
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    starting.value = false;
  }
}

onMounted(loadPaths);
</script>

<style scoped>
.pathsPage {
  display: grid;
  gap: var(--s-16);
}

.pathsHero {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: var(--s-16);
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 28px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.12), transparent 36%),
    radial-gradient(circle at 100% 0%, rgba(247, 215, 116, 0.10), transparent 32%),
    rgba(255, 255, 255, 0.035);
}

.pathsHero {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
}

.pathCoach {
  border: 1px solid rgba(110, 229, 255, 0.14);
}

.pathMetrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(92px, 1fr));
  gap: var(--s-8);
}

.pathMetrics span {
  display: grid;
  gap: 4px;
  min-width: 0;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.045);
}

.pathMetrics strong {
  color: rgba(255, 255, 255, 0.96);
  font-size: 1.25rem;
}

.pathMetrics small {
  color: rgba(255, 255, 255, 0.58);
  font-weight: 760;
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.pathsHero h1,
.detailIntro h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.97);
}

.pathsHero h1 {
  font-size: clamp(2rem, 4vw, 4rem);
  line-height: 0.98;
}

.pathsHero p:not(.eyebrow),
.detailIntro p:not(.eyebrow),
.challengeTop p {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.7;
}

.loopPill,
.days {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 8px 12px;
  border-radius: 999px;
  color: rgba(247, 215, 116, 0.92);
  background: rgba(247, 215, 116, 0.08);
  border: 1px solid rgba(247, 215, 116, 0.18);
  font-weight: 850;
}

.pathPicker {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
}

.pathDetail {
  display: grid;
  gap: var(--s-16);
}

.selectedPathCard {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 0.78fr);
  gap: var(--s-20);
  align-items: start;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.11), transparent 34%),
    radial-gradient(circle at 100% 0%, rgba(74, 222, 128, 0.08), transparent 32%),
    rgba(255, 255, 255, 0.035);
}

.detailIntro {
  min-width: 0;
}

.pathStatusRow {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  margin-top: var(--s-16);
}

.pathStatusRow span {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 7px 10px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.74);
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.09);
  font-size: var(--cap);
  font-weight: 820;
}

.pathButton {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px 12px;
  align-content: start;
  min-height: 172px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.86);
  text-align: start;
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: transform 140ms ease, border-color 140ms ease, background 140ms ease;
}

.pathButton:hover {
  transform: translateY(-2px);
  border-color: rgba(110, 229, 255, 0.20);
}

.pathButton.active {
  border-color: rgba(110, 229, 255, 0.30);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.11), rgba(195, 90, 214, 0.08)),
    rgba(255, 255, 255, 0.05);
}

.pathButton.started {
  border-color: rgba(247, 215, 116, 0.22);
}

.pathButton.complete {
  border-color: rgba(74, 222, 128, 0.28);
  background:
    linear-gradient(135deg, rgba(74, 222, 128, 0.12), rgba(110, 229, 255, 0.06)),
    rgba(255, 255, 255, 0.05);
}

.pathIcon {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--path-color) 32%, transparent);
  border: 1px solid color-mix(in srgb, var(--path-color) 42%, rgba(255,255,255,0.12));
  font-weight: 950;
}

.pathButtonCopy {
  display: grid;
  gap: 5px;
  min-width: 0;
}

.pathButtonCopy strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pathButtonCopy small,
.pathButtonHint,
.pathButtonMeta small {
  color: rgba(247, 215, 116, 0.80);
  font-weight: 850;
}

.pathButtonMeta {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.pathButtonMeta > span {
  display: grid;
  gap: 2px;
  min-width: 0;
  padding: 9px 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.pathButtonMeta strong {
  color: rgba(255, 255, 255, 0.94);
  font-size: 0.96rem;
}

.pathButtonMeta small {
  color: rgba(255, 255, 255, 0.56);
  font-size: 0.7rem;
}

.pathButtonHint {
  grid-column: 1 / -1;
  color: rgba(255, 255, 255, 0.60);
  font-size: 0.8rem;
  line-height: 1.45;
}

.detailActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  margin-top: var(--s-16);
}

.detailLink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0 var(--s-16);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--r-10);
  color: rgba(255, 255, 255, 0.90);
  background: rgba(255, 255, 255, 0.06);
  font-weight: 850;
  text-decoration: none;
}

.detailLink.primary {
  color: rgba(255, 255, 255, 0.96);
  border-color: rgba(110, 229, 255, 0.28);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.18), rgba(195, 90, 214, 0.12)),
    rgba(255, 255, 255, 0.07);
}

.progressPanel {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--s-16);
  align-items: center;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 20px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.12), transparent 36%),
    rgba(255, 255, 255, 0.035);
}

.progressPanel.complete {
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.12), transparent 34%),
    rgba(255, 255, 255, 0.035);
}

.progressPanel h3,
.progressPanel p {
  margin: 0;
}

.progressPanel p:not(.eyebrow) {
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.65;
}

.progressPanel .detailActions {
  margin-top: 0;
}

.progressStats {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: var(--s-8);
}

.progressStats span {
  display: grid;
  gap: 4px;
  min-width: 120px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
}

.progressStats strong {
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.25rem;
}

.progressStats small {
  color: rgba(255, 255, 255, 0.62);
  font-weight: 780;
}

.progressEmpty {
  display: grid;
  gap: 5px;
  min-width: 180px;
  padding: 13px;
  border: 1px solid rgba(247, 215, 116, 0.14);
  border-radius: 16px;
  background: rgba(247, 215, 116, 0.055);
}

.progressEmpty strong {
  color: rgba(255, 255, 255, 0.92);
}

.progressEmpty small {
  color: rgba(255, 255, 255, 0.60);
  line-height: 1.5;
}

.challengeStack {
  display: grid;
  gap: var(--s-12);
}

.challengePanel {
  display: grid;
  gap: var(--s-16);
  padding: 18px;
  border-radius: 22px;
}

.challengePanel.joined {
  border-color: rgba(110, 229, 255, 0.20);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.07), transparent 32%),
    rgba(255, 255, 255, 0.035);
}

.challengePanel.current {
  border-color: rgba(247, 215, 116, 0.26);
}

.challengePanel.secured {
  border-color: rgba(74, 222, 128, 0.24);
}

.challengeTop {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(210px, 0.38fr);
  gap: var(--s-16);
  align-items: start;
}

.challengeTop h3 {
  margin: 0;
}

.challengeCopy {
  min-width: 0;
}

.challengeKicker {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-bottom: 10px;
}

.challengeKicker span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 6px 9px;
  border-radius: 999px;
  color: rgba(110, 229, 255, 0.86);
  background: rgba(110, 229, 255, 0.075);
  border: 1px solid rgba(110, 229, 255, 0.16);
  font-size: 0.72rem;
  font-weight: 850;
}

.challengeKicker span:nth-child(2) {
  color: rgba(187, 247, 208, 0.94);
  background: rgba(74, 222, 128, 0.08);
  border-color: rgba(74, 222, 128, 0.18);
}

.challengeSummary {
  display: grid;
  gap: 8px;
}

.summaryItem {
  display: grid;
  gap: 3px;
  padding: 11px 12px;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.045);
}

.summaryItem.primary {
  border-color: rgba(74, 222, 128, 0.18);
  background: rgba(74, 222, 128, 0.06);
}

.summaryItem strong {
  color: rgba(255, 255, 255, 0.94);
  font-size: 0.95rem;
}

.summaryItem small {
  color: rgba(255, 255, 255, 0.56);
  line-height: 1.4;
  font-weight: 720;
}

.challengeProgress {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
}

.challengeProgress span {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 7px 10px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.70);
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: var(--cap);
  font-weight: 820;
}

.challengeActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
}

.missionListBlock {
  display: grid;
  gap: var(--s-12);
}

.missionListHead {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  align-items: baseline;
  justify-content: space-between;
}

.missionListHead strong {
  color: rgba(255, 255, 255, 0.88);
}

.missionListHead small {
  color: rgba(255, 255, 255, 0.56);
  line-height: 1.45;
}

.missionList {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--s-12);
}

.missionPreview {
  display: grid;
  gap: 6px;
  min-height: 142px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.035);
}

.missionPreview.preview {
  opacity: 0.78;
}

.missionPreview.done {
  border-color: rgba(74, 222, 128, 0.22);
  background: rgba(74, 222, 128, 0.055);
}

.missionPreview.remind_later {
  border-color: rgba(247, 215, 116, 0.22);
  background: rgba(247, 215, 116, 0.055);
}

.missionPreview.skipped {
  opacity: 0.66;
}

.missionPreview span {
  color: rgba(110, 229, 255, 0.80);
  font-size: var(--cap);
  font-weight: 850;
}

.missionPreview strong {
  display: block;
  margin-top: 0;
}

.missionPreview p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

@media (max-width: 820px) {
  .pathsHero,
  .challengeTop,
  .selectedPathCard {
    grid-template-columns: 1fr;
  }

  .pathMetrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .challengeSummary {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .pathPicker {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .pathMetrics {
    grid-template-columns: 1fr;
  }

  .pathPicker {
    grid-template-columns: 1fr;
  }

  .pathButton {
    min-height: auto;
  }

  .challengeSummary {
    grid-template-columns: 1fr;
  }

  .detailActions :deep(.btn),
  .challengeActions :deep(.btn),
  .challengeActions .detailLink,
  .detailLink {
    width: 100%;
  }
}
</style>
