<template>

  <main class="onboardingPage">
    <section class="shell">
      <div class="ambient" aria-hidden="true"></div>

      <div class="onboardingTopBar">
        <div class="progressRail" aria-hidden="true">
          <span v-for="n in 4" :key="n" :class="{ active: step >= n }"></span>
        </div>

        <div class="onboardingLanguageSwitch" :aria-label="t('language.label')">
          <button type="button" :class="{ active: locale === 'en' }" @click="setOnboardingLocale('en')">
            {{ t("language.en") }}
          </button>

          <button type="button" :class="{ active: locale === 'fa' }" @click="setOnboardingLocale('fa')">
            {{ t("language.fa") }}
          </button>
        </div>
      </div>

      <UiState :loading="loading && step === 3" :error="!!loadError" :empty="false"
        :loading-title="t('onboarding.loadingTitle')" :loading-text="t('onboarding.loadingText')"
        :error-title="t('onboarding.errorTitle')" :error-text="loadError || t('common.pleaseTryAgain')"
        @retry="loadChallenges" />

      <template v-if="!loadError">
        <StepWelcome v-if="step === 1" @start="step = 2" />

        <StepPath v-else-if="step === 2" v-model="selectedPaths" @continue="continueToSuggestion" />

        <ChallengeSuggestion v-else-if="step === 3" :path="selectedPath" :paths="selectedPaths"
          :challenge="suggestedChallenge" :challenges="suggestedChallenges" :joining="joining" :error="joinError"
          @start="startSuggestedPath" @browse="browseChallenges" @skip="skipOnboarding" />

        <section v-else class="handoffStep">
          <div class="handoffHero">
            <div class="stepHeader">
              <p class="eyebrow">{{ t("onboarding.handoff.eyebrow") }}</p>
              <h1>{{ t("onboarding.handoff.title") }}</h1>
              <p>{{ t("onboarding.handoff.body") }}</p>
            </div>
          </div>

          <BaseCard class="handoffCard">
            <span class="statusPill">{{ t("onboarding.handoff.readyPill") }}</span>

            <h2>{{ firstMissionTitle || t("onboarding.handoff.fallbackMission") }}</h2>

            <p>{{ t("onboarding.handoff.text") }}</p>

            <div class="handoffHints">
              <div class="handoffHint">
                <strong>{{ t("onboarding.handoff.hints.safe.title") }}</strong>
                <span>{{ t("onboarding.handoff.hints.safe.text") }}</span>
              </div>

              <div class="handoffHint">
                <strong>{{ t("onboarding.handoff.hints.choice.title") }}</strong>
                <span>{{ t("onboarding.handoff.hints.choice.text") }}</span>
              </div>

              <div class="handoffHint">
                <strong>{{ t("onboarding.handoff.hints.reward.title") }}</strong>
                <span>{{ t("onboarding.handoff.hints.reward.text") }}</span>
              </div>
            </div>

            <div class="actions">
              <BaseButton variant="primary" @click="finishOnboarding">
                {{ t("onboarding.handoff.cta") }}
              </BaseButton>
            </div>
          </BaseCard>
        </section>
      </template>
    </section>
  </main>

</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

import api from "@/lib/api";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import StepWelcome from "@/components/onboarding/StepWelcome.vue";
import StepPath from "@/components/onboarding/StepPath.vue";
import ChallengeSuggestion from "@/components/onboarding/ChallengeSuggestion.vue";
import {
  getIdentityPath,
  getOnboardingUserKey,
  hasTodayMissionPayload,
  isOnboardingDone,
  markOnboardingDone,
  markOnboardingSkipped,
  setIdentityPath,
} from "@/lib/guidedExperience";
import {
  humanizeJoinError,
  isInviteOnlyChallenge,
  submitJoinFlow,
} from "./challengeFlow";

const router = useRouter();
const { locale, t } = useI18n();

const step = ref(1);
const selectedPaths = ref([]);
const challenges = ref([]);
const paths = ref([]);
const pathChallenges = ref([]);
const pathChallengeGroups = ref([]);
const loading = ref(false);
const joining = ref(false);
const loadError = ref("");
const joinError = ref("");
const todayMissionState = ref(null);
const onboardingUserKey = ref("");

const IDENTITY_TO_BACKEND_PATH = {
  focus: "career",
  body: "fitness",
  learning: "learning",
  mind: "sleep",
  consistency: "fitness",
};

const selectedPath = computed(() => selectedPaths.value[0] || "");

const firstMissionTitle = computed(() => {
  const missions = todayMissionState.value?.missions;
  const mission = Array.isArray(missions)
    ? missions.find((item) => item?.status === "pending") || missions[0]
    : null;

  return mission?.title || "";
});

const selectedBackendPaths = computed(() => {
  const keys = selectedPaths.value.map((path) => IDENTITY_TO_BACKEND_PATH[path] || path);
  return paths.value.filter((path) => keys.includes(path.key));
});

const suggestedChallenges = computed(() => {
  if (pathChallengeGroups.value.length) {
    return pathChallengeGroups.value.flatMap((group) => {
      return group.items
        .filter((challenge) => !isInviteOnlyChallenge(challenge) && !challenge.needs_code)
        .slice(0, 3);
    });
  }

  return (pathChallenges.value.length ? pathChallenges.value : challenges.value)
    .filter((challenge) => !isInviteOnlyChallenge(challenge) && !challenge.needs_code)
    .slice(0, 3);
});

const suggestedChallenge = computed(() => {
  return suggestedChallenges.value.find((challenge) => !challenge.is_joined)
    || suggestedChallenges.value[0]
    || null;
});

async function loadChallenges() {
  loading.value = true;
  loadError.value = "";

  try {
    const [{ data: challengeData }, { data: pathData }] = await Promise.all([
      api.get("/challenges"),
      api.get("/paths"),
    ]);
    challenges.value = challengeData.items || [];
    paths.value = pathData.items || [];
  } catch (error) {
    loadError.value = error?.response?.data?.error || error?.message || String(error);
    challenges.value = [];
  } finally {
    loading.value = false;
  }
}

async function loadTodayMissionState() {
  try {
    const { data } = await api.get("/me/today-missions");
    return data;
  } catch {
    return null;
  }
}

async function loadCurrentUserKey() {
  const { data } = await api.get("/me");
  onboardingUserKey.value = getOnboardingUserKey(data);
}

async function resumeOnboarding() {
  try {
    await loadCurrentUserKey();
  } catch {
    router.replace({ path: "/login", query: { next: "/onboarding" } });
    return;
  }

  if (isOnboardingDone(onboardingUserKey.value)) {
    router.replace("/dashboard");
    return;
  }

  const savedPath = getIdentityPath(onboardingUserKey.value);

  if (savedPath) {
    selectedPaths.value = [savedPath];
    step.value = 3;
  } else {
    step.value = 1;
  }

  await loadChallenges();

  const missionState = await loadTodayMissionState();
  todayMissionState.value = missionState;

  if (hasTodayMissionPayload(missionState)) {
    step.value = 4;
    return;
  }

  if (!savedPath && challenges.value.some((challenge) => challenge.is_joined)) {
    step.value = 4;
    return;
  }

  if (savedPath) {
    await loadSelectedPathChallenges();

    if (suggestedChallenges.value.some((challenge) => challenge.is_joined)) {
      step.value = 4;
    }
  }
}

async function loadSelectedPathChallenges() {
  pathChallenges.value = [];
  pathChallengeGroups.value = [];

  if (!selectedBackendPaths.value.length) return;

  const responses = await Promise.all(
    selectedBackendPaths.value.map((path) => api.get(`/paths/${path.path_id}/challenges`)),
  );

  const byId = new Map();
  const groups = [];

  responses.forEach((response, index) => {
    const items = response.data?.items || [];
    groups.push({
      path_id: selectedBackendPaths.value[index]?.path_id || null,
      key: selectedBackendPaths.value[index]?.key || "",
      items,
    });

    for (const challenge of items) {
      byId.set(challenge.challenge_id, challenge);
    }
  });

  pathChallengeGroups.value = groups;
  pathChallenges.value = [...byId.values()];
}

async function continueToSuggestion() {
  if (!selectedPaths.value.length) return;

  setIdentityPath(selectedPath.value, onboardingUserKey.value);
  step.value = 3;

  if (!challenges.value.length) {
    await loadChallenges();
  }

  await loadSelectedPathChallenges();
}

async function startSuggestedPath(selectedIds = []) {
  const selectedId = selectedIds[0];
  const selected = suggestedChallenges.value.filter((challenge) =>
    challenge.challenge_id === selectedId,
  );

  if (!selected.length) {
    browseChallenges();
    return;
  }

  const notJoined = selected.filter((challenge) => !challenge.is_joined);

  if (!notJoined.length) {
    await prepareFinalHandoff();
    return;
  }

  joinError.value = "";
  joining.value = true;

  try {
    await submitJoinFlow({
      apiClient: api,
      router,
      challenge: notJoined[0],
      reload: loadChallenges,
    });

    await loadChallenges();
    await loadSelectedPathChallenges();

    todayMissionState.value = await loadTodayMissionState();
    step.value = 4;
  } catch (error) {
    const message = error?.response?.data?.error || error?.message || String(error);
    joinError.value = humanizeJoinError(message);
  } finally {
    joining.value = false;
  }
}

function setOnboardingLocale(value) {
  if (!["en", "fa"].includes(value)) return;

  locale.value = value;

  if (typeof window !== "undefined") {
    window.localStorage.setItem("ringostrike_locale", value);
  }

  if (typeof document !== "undefined") {
    document.documentElement.lang = value;
    document.documentElement.dir = value === "fa" ? "rtl" : "ltr";
  }
}

function browseChallenges() {
  markOnboardingSkipped(selectedPath.value, onboardingUserKey.value);
  router.push("/challenges");
}

function skipOnboarding() {
  markOnboardingSkipped(selectedPath.value, onboardingUserKey.value);
  router.push("/dashboard");
}

async function prepareFinalHandoff() {
  todayMissionState.value = await loadTodayMissionState();
  step.value = 4;
}

function finishOnboarding() {
  markOnboardingDone(selectedPath.value, onboardingUserKey.value);
  router.push({ path: "/dashboard", query: { firstRun: "1" } });
}

onMounted(resumeOnboarding);
</script>

<style scoped>
.onboardingPage {
  display: grid;
  width: 100%;
  min-height: 100dvh;
  place-items: center;
  padding: clamp(20px, 4vh, 48px) var(--s-20);
  box-sizing: border-box;
}

.shell {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: var(--s-20);
  padding: 30px;
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.14), transparent 34%),
    radial-gradient(circle at 94% 10%, rgba(195, 90, 214, 0.12), transparent 34%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.066), rgba(255, 255, 255, 0.024));
  box-shadow: 0 32px 100px rgba(0, 0, 0, 0.32);
  width: min(100%, 1080px);
}

.ambient {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.shell>* {
  position: relative;
  z-index: 1;
}

.progressRail {
  display: flex;
  gap: 8px;
}

.progressRail span {
  width: 42px;
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
}

.progressRail span.active {
  background: rgba(110, 229, 255, 0.78);
  box-shadow: 0 0 18px rgba(110, 229, 255, 0.32);
}

.handoffStep {
  display: grid;
  gap: var(--s-20);
}

.handoffHero,
.stepHeader {
  max-width: 760px;
  min-width: 0;
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.88);
  font-size: 0.74rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 2.55rem;
  line-height: 1.04;
  letter-spacing: 0;
}

.stepHeader p:not(.eyebrow),
.handoffCard p {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.7;
}

.handoffCard {
  display: grid;
  gap: var(--s-16);
  padding: 22px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.11), transparent 34%),
    rgba(255, 255, 255, 0.035);
}

.statusPill {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  color: rgba(167, 243, 208, 0.96);
  font-size: 0.76rem;
  font-weight: 780;
  background: rgba(74, 222, 128, 0.12);
  border: 1px solid rgba(74, 222, 128, 0.24);
}

.handoffCard h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 1.8rem;
  line-height: 1.12;
  letter-spacing: 0;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-12);
  margin-top: 4px;
}

.handoffHints {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
}

.handoffHint {
  display: grid;
  gap: 6px;
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.handoffHint strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.88rem;
}

.handoffHint span {
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.84rem;
  line-height: 1.55;
}

.onboardingTopBar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s-16);
}

.onboardingLanguageSwitch {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.onboardingLanguageSwitch button {
  min-width: 38px;
  min-height: 28px;
  padding: 0 10px;
  border: 0;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.76rem;
  font-weight: 780;
  background: transparent;
  cursor: pointer;
}

.onboardingLanguageSwitch button.active {
  color: rgba(255, 255, 255, 0.94);
  background: rgba(110, 229, 255, 0.13);
  box-shadow: inset 0 0 0 1px rgba(110, 229, 255, 0.18);
}

.onboardingLanguageSwitch button:hover {
  color: rgba(255, 255, 255, 0.86);
}



@media (max-width: 620px) {
  .onboardingPage {
    display: grid;
    width: 100%;
    min-height: 100dvh;
    place-items: center;
    padding: 20px;
  }

  .shell {
    width: 100%;
    padding: 20px;
    border-radius: 24px;
  }

  h1 {
    font-size: 1.9rem;
  }

  .actions {
    display: grid;
  }

  .handoffHints {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--s-12);
  }

  .handoffHint {
    display: grid;
    gap: 6px;
    padding: 14px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .handoffHint strong {
    color: rgba(255, 255, 255, 0.92);
    font-size: 0.88rem;
  }

  .handoffHint span {
    color: rgba(255, 255, 255, 0.58);
    font-size: 0.84rem;
    line-height: 1.55;
  }

  .onboardingTopBar {
    align-items: flex-start;
  }

  .onboardingLanguageSwitch {
    flex-shrink: 0;
  }
}
</style>
