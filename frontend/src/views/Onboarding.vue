<template>

  <main class="onboardingPage">
    <section class="shell">
      <div class="ambient" aria-hidden="true"></div>

      <div class="onboardingTopBar">
        <div class="progressRail" aria-hidden="true">
          <span v-for="n in 3" :key="n" :class="{ active: step >= n }"></span>
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

        <StepPath
          v-else-if="step === 2"
          v-model="selectedPaths"
          :backend-paths="paths"
          :space-state="spaceState"
          @continue="continueToSuggestion"
        />

        <ChallengeSuggestion v-else-if="step === 3" :path="selectedPath" :paths="selectedPaths"
          :challenge="localizedSuggestedChallenge" :challenges="localizedSuggestedChallenges" :joining="joining" :error="joinError"
          @start="startSuggestedPath" @skip="skipOnboarding" />

      </template>
    </section>
  </main>

</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

import api from "@/lib/api";
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
  shouldBypassOnboardingForLegacyProgress,
} from "@/lib/guidedExperience";
import {
  humanizeJoinError,
  isInviteOnlyChallenge,
  submitJoinFlow,
} from "./challengeFlow";
import { localizeChallenge } from "@/lib/ringoContentLocalization";

const router = useRouter();
const route = useRoute();
const { locale, t } = useI18n();

const step = ref(1);
const selectedPaths = ref([]);
const challenges = ref([]);
const paths = ref([]);
const pathChallenges = ref([]);
const pathChallengeGroups = ref([]);
const spaceState = ref(null);
const loading = ref(false);
const joining = ref(false);
const loadError = ref("");
const joinError = ref("");
const onboardingUserKey = ref("");

const IDENTITY_TO_BACKEND_PATH = {
  career: "career",
  creativity: "creativity",
  fitness: "fitness",
  learning: "learning",
  sleep: "sleep",
  focus: "career",
  body: "fitness",
  learning: "learning",
  mind: "sleep",
  consistency: "fitness",
};

function getOnboardingReturnPath() {
  const next = Array.isArray(route.query.next) ? route.query.next[0] : route.query.next;
  return typeof next === "string" && next.startsWith("/") ? next : "/dashboard";
}

const selectedPath = computed(() => selectedPaths.value[0] || "");

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

const localizedSuggestedChallenges = computed(() => {
  return suggestedChallenges.value.map((challenge) => localizeChallenge(challenge, locale.value));
});

const localizedSuggestedChallenge = computed(() => {
  if (!suggestedChallenge.value) return null;

  return localizedSuggestedChallenges.value.find((challenge) => {
    return challenge.challenge_id === suggestedChallenge.value.challenge_id;
  }) || localizeChallenge(suggestedChallenge.value, locale.value);
});

async function loadChallenges() {
  loading.value = true;
  loadError.value = "";

  try {
    const [{ data: challengeData }, { data: pathData }, spaceResponse] = await Promise.all([
      api.get("/challenges"),
      api.get("/paths"),
      api.get("/me/space").catch(() => null),
    ]);
    challenges.value = challengeData.items || [];
    paths.value = pathData.items || [];
    spaceState.value = spaceResponse?.data || null;
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
  const normalizedSavedPath = IDENTITY_TO_BACKEND_PATH[savedPath] || savedPath;

  if (savedPath) {
    selectedPaths.value = [normalizedSavedPath];
    step.value = 3;
  } else {
    step.value = 1;
  }

  await loadChallenges();

  const missionState = await loadTodayMissionState();

  if (shouldBypassOnboardingForLegacyProgress({
    savedPath,
    missionState,
    challenges: challenges.value,
  })) {
    markOnboardingSkipped("", onboardingUserKey.value);
    router.replace(getOnboardingReturnPath());
    return;
  }

  // B37 (D78): a challenge is already joined: straight to the room (no handoff screen).
  if (hasTodayMissionPayload(missionState)) {
    finishOnboarding();
    return;
  }

  if (savedPath) {
    await loadSelectedPathChallenges();

    if (suggestedChallenges.value.some((challenge) => challenge.is_joined)) {
      finishOnboarding();
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
    skipOnboarding();
    return;
  }

  const notJoined = selected.filter((challenge) => !challenge.is_joined);

  if (!notJoined.length) {
    finishOnboarding();
    return;
  }

  joinError.value = "";
  joining.value = true;

  try {
    const selectedBackendPath = selectedBackendPaths.value[0] || null;

    if (selectedBackendPath?.path_id) {
      await api.post(`/paths/${selectedBackendPath.path_id}/start`, {});
    }

    await submitJoinFlow({
      apiClient: api,
      router,
      challenge: notJoined[0],
      reload: loadChallenges,
    });

    // B37 (D78, D82): joined: land in the room on that corner, where Ringo's first card offers
    // "Do it now" (the handoff screen is gone).
    finishOnboarding();
  } catch (error) {
    const message = error?.response?.data?.error || error?.message || String(error);
    joinError.value = humanizeJoinError(message, t);
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

function skipOnboarding() {
  markOnboardingSkipped(selectedPath.value, onboardingUserKey.value);
  router.push("/dashboard");
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
  /* B11: clip (not a scroll container) so the path step's sticky Continue works. */
  overflow: clip;
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

  .onboardingTopBar {
    align-items: flex-start;
  }

  .onboardingLanguageSwitch {
    flex-shrink: 0;
  }
}
</style>