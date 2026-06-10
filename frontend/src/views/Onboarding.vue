<template>
  <AppContainer>
    <AppHeader />

    <main class="onboardingPage">
      <section class="shell">
        <div class="ambient" aria-hidden="true"></div>

        <div class="progressRail" aria-hidden="true">
          <span
            v-for="n in 3"
            :key="n"
            :class="{ active: step >= n }"
          ></span>
        </div>

        <UiState
          :loading="loading && step === 3"
          :error="!!loadError"
          :empty="false"
          :loading-title="t('onboarding.loadingTitle')"
          :loading-text="t('onboarding.loadingText')"
          :error-title="t('onboarding.errorTitle')"
          :error-text="loadError || t('common.pleaseTryAgain')"
          @retry="loadChallenges"
        />

        <template v-if="!loadError">
          <StepWelcome
            v-if="step === 1"
            @start="step = 2"
          />

          <StepPath
            v-else-if="step === 2"
            v-model="selectedPaths"
            @continue="continueToSuggestion"
          />

          <ChallengeSuggestion
            v-else
            :path="selectedPath"
            :paths="selectedPaths"
            :challenge="suggestedChallenge"
            :challenges="suggestedChallenges"
            :joining="joining"
            :error="joinError"
            @start="startSuggestedPath"
            @browse="browseChallenges"
            @skip="skipOnboarding"
          />
        </template>
      </section>
    </main>

    <JoinSuccessMoment
      :open="!!joinSuccess"
      :join="joinSuccess"
      @close="joinSuccess = null"
    />
  </AppContainer>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

import api from "@/lib/api";
import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import UiState from "@/components/ui/UiState.vue";
import JoinSuccessMoment from "@/components/feedback/JoinSuccessMoment.vue";
import StepWelcome from "@/components/onboarding/StepWelcome.vue";
import StepPath from "@/components/onboarding/StepPath.vue";
import ChallengeSuggestion from "@/components/onboarding/ChallengeSuggestion.vue";
import {
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
const { t } = useI18n();

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
const joinSuccess = ref(null);

const IDENTITY_TO_BACKEND_PATH = {
  focus: "career",
  body: "fitness",
  learning: "learning",
  mind: "sleep",
  consistency: "fitness",
};

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

  setIdentityPath(selectedPath.value);
  step.value = 3;

  if (!challenges.value.length) {
    await loadChallenges();
  }

  await loadSelectedPathChallenges();
}

async function startSuggestedPath(selectedIds = []) {
  const selected = suggestedChallenges.value.filter((challenge) =>
    selectedIds.includes(challenge.challenge_id),
  );

  if (!selected.length) {
    browseChallenges();
    return;
  }

  const notJoined = selected.filter((challenge) => !challenge.is_joined);

  if (!notJoined.length) {
    markOnboardingDone(selectedPath.value);
    router.push("/dashboard");
    return;
  }

  joinError.value = "";
  joining.value = true;

  try {
    const results = [];

    for (const challenge of notJoined) {
      const result = await submitJoinFlow({
        apiClient: api,
        router,
        challenge,
        reload: loadChallenges,
      });
      results.push(result);
    }

    await loadChallenges();
    await loadSelectedPathChallenges();

    markOnboardingDone(selectedPath.value);

    if (results.length === 1) {
      joinSuccess.value = {
        ...results[0],
        source: "onboarding",
      };
      return;
    }

    router.push("/dashboard");
  } catch (error) {
    const message = error?.response?.data?.error || error?.message || String(error);
    joinError.value = humanizeJoinError(message);
  } finally {
    joining.value = false;
  }
}

function browseChallenges() {
  markOnboardingSkipped(selectedPath.value);
  router.push("/challenges");
}

function skipOnboarding() {
  markOnboardingSkipped(selectedPath.value);
  router.push("/dashboard");
}
</script>

<style scoped>
.onboardingPage {
  display: grid;
  min-height: calc(100vh - 160px);
  align-items: center;
  padding: var(--s-20) 0;
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
}

.ambient {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.shell > * {
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

@media (max-width: 620px) {
  .onboardingPage {
    align-items: start;
    min-height: auto;
  }

  .shell {
    padding: 20px;
    border-radius: 24px;
  }
}
</style>
