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
            v-model="selectedPath"
            @continue="continueToSuggestion"
          />

          <ChallengeSuggestion
            v-else
            :path="selectedPath"
            :challenge="suggestedChallenge"
            :joining="joining"
            :error="joinError"
            @start="startSuggestedPath"
            @browse="browseChallenges"
            @skip="skipOnboarding"
          />
        </template>
      </section>
    </main>
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
import StepWelcome from "@/components/onboarding/StepWelcome.vue";
import StepPath from "@/components/onboarding/StepPath.vue";
import ChallengeSuggestion from "@/components/onboarding/ChallengeSuggestion.vue";
import {
  findSuggestedChallenge,
  markOnboardingDone,
  markOnboardingSkipped,
  setIdentityPath,
} from "@/lib/guidedExperience";
import {
  humanizeJoinError,
  submitJoinFlow,
} from "./challengeFlow";

const router = useRouter();
const { t } = useI18n();

const step = ref(1);
const selectedPath = ref("");
const challenges = ref([]);
const loading = ref(false);
const joining = ref(false);
const loadError = ref("");
const joinError = ref("");

const suggestedChallenge = computed(() => {
  return findSuggestedChallenge(challenges.value, selectedPath.value);
});

async function loadChallenges() {
  loading.value = true;
  loadError.value = "";

  try {
    const { data } = await api.get("/challenges");
    challenges.value = data.items || [];
  } catch (error) {
    loadError.value = error?.response?.data?.error || error?.message || String(error);
    challenges.value = [];
  } finally {
    loading.value = false;
  }
}

async function continueToSuggestion() {
  if (!selectedPath.value) return;

  setIdentityPath(selectedPath.value);
  step.value = 3;

  if (!challenges.value.length) {
    await loadChallenges();
  }
}

async function startSuggestedPath() {
  const challenge = suggestedChallenge.value;
  if (!challenge) {
    browseChallenges();
    return;
  }

  if (challenge.is_joined && challenge.enrollment_id) {
    markOnboardingDone(selectedPath.value);
    router.push(`/enrollment/${challenge.enrollment_id}`);
    return;
  }

  joinError.value = "";
  joining.value = true;

  try {
    const result = await submitJoinFlow({
      apiClient: api,
      router,
      challenge,
      reload: loadChallenges,
    });

    markOnboardingDone(selectedPath.value);

    if (!result.navigated) {
      router.push("/dashboard");
    }
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
