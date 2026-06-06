<template>
  <AppContainer>
    <AppHeader />

    <main class="pathsPage">
      <section class="pathsHero">
        <div>
          <p class="eyebrow">{{ t("pathsPage.eyebrow") }}</p>
          <h1>{{ t("pathsPage.title") }}</h1>
          <p>{{ t("pathsPage.subtitle") }}</p>
        </div>

        <div class="loopPill">
          {{ t("pathsPage.loop") }}
        </div>
      </section>

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
        <section class="pathPicker" :aria-label="t('pathsPage.pickPath')">
          <button
            v-for="path in paths"
            :key="path.path_id"
            type="button"
            class="pathButton"
            :class="{ active: selectedPath?.path_id === path.path_id }"
            @click="selectPath(path)"
          >
            <span :style="{ '--path-color': path.color || '#6ee5ff' }">{{ path.icon?.slice(0, 1)?.toUpperCase() || "P" }}</span>
            <strong>{{ path.title }}</strong>
            <small>{{ path.user_status === "Active" ? t("paths.active") : t("paths.select") }}</small>
          </button>
        </section>

        <section v-if="selectedPath" class="pathDetail">
          <div class="detailIntro">
            <p class="eyebrow compact">{{ t("pathsPage.selectedEyebrow") }}</p>
            <h2>{{ selectedPath.title }}</h2>
            <p>{{ selectedPath.description }}</p>

            <div class="detailActions">
              <BaseButton
                v-if="challenges.length && selectedPath.user_status !== 'Active'"
                variant="primary"
                :loading="starting"
                @click="startSelectedPath"
              >
                {{ t("paths.startFirstMission", { path: selectedPath.title }) }}
              </BaseButton>

              <RouterLink class="detailLink" to="/challenges">
                {{ t("paths.browseChallenges") }}
              </RouterLink>
            </div>
          </div>

          <BaseCard v-if="pathProgress" class="progressPanel" :class="{ complete: pathProgress.todayComplete }">
            <div>
              <p class="eyebrow compact">{{ t("pathsPage.todaySummary") }}</p>
              <h3>{{ pathProgress.title }}</h3>
              <p>{{ pathProgress.body }}</p>
            </div>

            <div class="progressStats">
              <span>
                <strong>{{ pathSummary.today_missions_done }}/{{ pathSummary.today_missions_total }}</strong>
                <small>{{ t("pathsPage.missionsDone") }}</small>
              </span>
              <span>
                <strong>{{ pathSummary.today_checked_challenges }}/{{ pathSummary.joined_challenges }}</strong>
                <small>{{ t("pathsPage.challengesSecured") }}</small>
              </span>
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

              <RouterLink
                v-if="pathProgress.action === 'dashboard'"
                class="detailLink primary"
                to="/dashboard"
              >
                {{ pathProgress.primaryCta }}
              </RouterLink>

              <RouterLink
                v-if="pathProgress.action === 'library'"
                class="detailLink primary"
                to="/challenges"
              >
                {{ pathProgress.primaryCta }}
              </RouterLink>

              <RouterLink
                v-if="pathProgress.action === 'preview'"
                class="detailLink"
                to="/challenges"
              >
                {{ t("pathsPage.browseLibrary") }}
              </RouterLink>

              <RouterLink
                v-if="currentChallenge?.enrollment_id && pathProgress.action !== 'preview'"
                class="detailLink"
                :to="`/enrollment/${currentChallenge.enrollment_id}`"
              >
                {{ t("pathsPage.viewDetails") }}
              </RouterLink>
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
                <div>
                  <p class="eyebrow compact">
                    {{ t("paths.stage", { stage: challenge.stage || 1 }) }}
                  </p>
                  <h3>{{ challenge.name }}</h3>
                  <p>{{ challenge.ringo_intro || challenge.description }}</p>
                </div>

                <div class="challengeBadges">
                  <span v-if="challenge.is_joined" class="statusBadge">
                    {{ challenge.today_checked ? t("pathsPage.securedToday") : t("pathsPage.activeNow") }}
                  </span>
                  <span class="days">
                    {{ t("paths.estimatedDays", { count: challenge.estimated_days || challenge.duration_days || 0 }) }}
                  </span>
                </div>
              </div>

              <div v-if="challenge.is_joined" class="challengeProgress">
                <span>
                  {{ t("pathsPage.challengeMissionProgress", {
                    done: challenge.today_missions_done || 0,
                    total: challenge.today_missions_total || 0,
                  }) }}
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

              <div class="missionList">
                <article
                  v-for="mission in challenge.missions"
                  :key="mission.mission_id"
                  class="missionPreview"
                  :class="mission.today_status"
                >
                  <span>{{ missionStatusLabel(mission) }} · {{ mission.xp_reward }} XP</span>
                  <strong>{{ mission.title }}</strong>
                  <p>{{ mission.description }}</p>
                  <small v-if="mission.today_status === 'locked'">
                    {{ missionUnlockLabel(mission) }}
                  </small>
                </article>
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

const { t } = useI18n();
const router = useRouter();

const paths = ref([]);
const selectedPath = ref(null);
const challenges = ref([]);
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

async function loadPaths() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await api.get("/paths");
    paths.value = data?.items || [];
    selectedPath.value = paths.value.find((path) => path.user_status === "Active") || paths.value[0] || null;

    if (selectedPath.value) {
      await loadPathChallenges(selectedPath.value);
    }
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function selectPath(path) {
  selectedPath.value = path;
  await loadPathChallenges(path);
}

async function loadPathChallenges(path) {
  if (!path?.path_id) return;

  challengesLoading.value = true;
  challengesError.value = "";

  try {
    const { data } = await api.get(`/paths/${path.path_id}/challenges`);
    challenges.value = data?.items || [];
    pathSummary.value = data?.summary || {
      joined_challenges: 0,
      today_checked_challenges: 0,
      today_missions_done: 0,
      today_missions_total: 0,
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

  const todayTotal = Number(pathSummary.value.today_missions_total || 0);
  const todayDone = Number(pathSummary.value.today_missions_done || 0);
  const todayComplete = todayTotal > 0 && todayDone >= todayTotal;

  if (todayComplete) {
    return {
      todayComplete: true,
      title: t("pathsPage.todayCompleteTitle", { path: selectedPath.value.title }),
      body: nextChallenge.value
        ? t("pathsPage.todayCompleteBodyWithNext", { challenge: nextChallenge.value.name })
        : t("pathsPage.todayCompleteBody"),
      primaryCta: nextChallenge.value
        ? t("pathsPage.previewNextChallenge")
        : t("pathsPage.browseLibrary"),
      action: nextChallenge.value ? "preview" : "library",
    };
  }

  return {
    todayComplete: false,
    title: currentChallenge.value
      ? t("pathsPage.currentChallengeTitle", { challenge: currentChallenge.value.name })
      : t("pathsPage.pathActiveTitle", { path: selectedPath.value.title }),
    body: t("pathsPage.currentChallengeBody", {
      done: todayDone,
      total: todayTotal,
    }),
    primaryCta: t("paths.openTodayMission"),
    action: "dashboard",
  };
});

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
    await startChallenge(firstChallenge);
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

.pathsHero,
.pathDetail {
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
  align-items: end;
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
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--s-12);
}

.pathButton {
  display: grid;
  gap: 8px;
  min-height: 118px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.86);
  text-align: start;
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
}

.pathButton.active {
  border-color: rgba(110, 229, 255, 0.30);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.11), rgba(195, 90, 214, 0.08)),
    rgba(255, 255, 255, 0.05);
}

.pathButton span {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--path-color) 32%, transparent);
  border: 1px solid color-mix(in srgb, var(--path-color) 42%, rgba(255,255,255,0.12));
  font-weight: 950;
}

.pathButton small {
  color: rgba(247, 215, 116, 0.80);
  font-weight: 850;
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
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: center;
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
  grid-column: 1 / -1;
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

.challengeStack {
  display: grid;
  gap: var(--s-12);
}

.challengePanel {
  display: grid;
  gap: var(--s-16);
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
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-12);
}

.challengeTop h3 {
  margin: 0;
}

.challengeBadges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  justify-content: flex-end;
}

.statusBadge {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 8px 12px;
  border-radius: 999px;
  color: rgba(187, 247, 208, 0.94);
  background: rgba(74, 222, 128, 0.08);
  border: 1px solid rgba(74, 222, 128, 0.20);
  font-weight: 850;
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

.missionList {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: var(--s-12);
}

.missionPreview {
  padding: 12px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.035);
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
  margin-top: 5px;
}

.missionPreview p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

@media (max-width: 820px) {
  .pathsHero,
  .challengeTop,
  .progressPanel {
    grid-template-columns: 1fr;
  }

  .challengeBadges {
    justify-content: flex-start;
  }

  .pathPicker {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .pathPicker {
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
