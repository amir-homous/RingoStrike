<template>
  <section class="suggestionStep">
    <div class="suggestionHero">
      <div class="stepHeader">
        <p class="eyebrow">{{ t("onboarding.suggestion.eyebrow") }}</p>
        <h1>{{ t("onboarding.suggestion.title") }}</h1>
        <p>
          {{ t("onboarding.suggestion.body", { path: pathLabel }) }}
        </p>
        <p class="laterNotice">
          {{ t("onboarding.suggestion.laterNotice") }}
        </p>
      </div>

      <RingoMoodFigure
        class="suggestionRingo"
        :mood="suggestionMood"
        :alt="t('onboarding.suggestion.title')"
        size="md"
        floating
      />
    </div>

    <BaseCard class="suggestionCard">
      <div v-if="challenges.length" class="challengeCopy">
        <span class="statusPill">
          {{ t("onboarding.suggestion.recommended") }}
        </span>

        <h2>{{ t("onboarding.suggestion.chooseTitle") }}</h2>

        <p>
          {{ t("onboarding.suggestion.chooseText") }}
        </p>

        <div class="challengeOptions">
          <button
            v-for="challenge in challenges"
            :key="challenge.challenge_id"
            type="button"
            class="challengeOption"
            :class="{ selected: selectedIds.includes(challenge.challenge_id), joined: challenge.is_joined }"
            @click="toggleChallenge(challenge)"
          >
            <span class="checkMark" aria-hidden="true">
              {{ selectedIds.includes(challenge.challenge_id) ? "✓" : "" }}
            </span>

            <span class="optionCopy">
              <strong>{{ challenge.name || challenge.challenge_name }}</strong>
              <small>{{ challenge.ringo_intro || challenge.description || t("onboarding.suggestion.noDescription") }}</small>
            </span>

            <span class="optionMeta">
              <small v-if="challenge.is_joined">{{ t("onboarding.suggestion.alreadyJoined") }}</small>
              <small v-else>{{ t("common.dayChallenge", { count: challenge.estimated_days || challenge.duration_days || 0 }) }}</small>
            </span>
          </button>
        </div>
      </div>

      <div v-else class="challengeCopy">
        <span class="statusPill fallback">
          {{ t("onboarding.suggestion.fallbackPill") }}
        </span>

        <h2>{{ t("onboarding.suggestion.fallbackTitle") }}</h2>

        <p>
          {{ t("onboarding.suggestion.fallbackText") }}
        </p>
      </div>

      <div v-if="error" class="errorBox">
        {{ error }}
      </div>

      <div class="actions">
        <BaseButton
          v-if="challenges.length"
          variant="primary"
          :loading="joining"
          :disabled="selectedIds.length === 0"
          @click="$emit('start', selectedIds)"
        >
          {{ t("onboarding.suggestion.startSelected", { count: selectedIds.length }) }}
        </BaseButton>

        <BaseButton
          variant="secondary"
          @click="$emit('browse')"
        >
          {{ t("onboarding.suggestion.browse") }}
        </BaseButton>

        <button
          type="button"
          class="skipButton"
          @click="$emit('skip')"
        >
          {{ t("onboarding.suggestion.skip") }}
        </button>
      </div>
    </BaseCard>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";
import { resolveRingoMood } from "@/constants/ringoSprites";

const props = defineProps({
  path: { type: String, default: "" },
  paths: { type: Array, default: () => [] },
  challenge: { type: Object, default: null },
  challenges: { type: Array, default: () => [] },
  joining: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

defineEmits(["start", "browse", "skip"]);

const { t } = useI18n();
const selectedIds = ref([]);

function initialIds(challenges) {
  return challenges
    .filter((challenge) => !challenge.is_joined)
    .slice(0, 1)
    .map((challenge) => challenge.challenge_id);
}

watch(
  () => props.challenges,
  (value) => {
    selectedIds.value = initialIds(value || []);
  },
  { immediate: true },
);

const pathLabel = computed(() => {
  if (props.paths.length) {
    return props.paths
      .map((path) => t(`onboarding.paths.${path}.label`))
      .join(", ");
  }

  return props.path ? t(`onboarding.paths.${props.path}.label`) : t("onboarding.path.defaultPath");
});

const suggestionMood = computed(() => {
  return props.challenges.length
    ? resolveRingoMood("onboardingSuggestion")
    : resolveRingoMood("onboardingFallback");
});

function toggleChallenge(challenge) {
  if (challenge.is_joined) return;

  if (selectedIds.value.includes(challenge.challenge_id)) {
    selectedIds.value = selectedIds.value.filter((id) => id !== challenge.challenge_id);
    return;
  }

  selectedIds.value = [...selectedIds.value, challenge.challenge_id];
}
</script>

<style scoped>
.suggestionStep {
  display: grid;
  gap: var(--s-20);
}

.suggestionHero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-20);
  align-items: center;
}

.stepHeader {
  max-width: 760px;
  min-width: 0;
}

.suggestionRingo {
  justify-self: end;
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
.challengeCopy p {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.7;
}

.laterNotice {
  max-width: 720px;
  margin: 8px 0 0;
  color: rgba(253, 230, 138, 0.82);
  line-height: 1.6;
}

.suggestionCard {
  display: grid;
  gap: var(--s-20);
  padding: 22px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.11), transparent 34%),
    rgba(255, 255, 255, 0.035);
}

.statusPill {
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

.statusPill.fallback {
  color: rgba(253, 224, 71, 0.96);
  background: rgba(250, 204, 21, 0.10);
  border-color: rgba(250, 204, 21, 0.22);
}

h2 {
  margin: 14px 0 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 1.8rem;
  line-height: 1.12;
  letter-spacing: 0;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: var(--s-16);
}

.meta span {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.09);
  font-size: 0.82rem;
}

.challengeOptions {
  display: grid;
  gap: var(--s-12);
  margin-top: var(--s-16);
}

.challengeOption {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: var(--s-12);
  align-items: center;
  padding: 13px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  color: rgba(255, 255, 255, 0.88);
  text-align: start;
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
}

.challengeOption.selected {
  border-color: rgba(110, 229, 255, 0.30);
  background: rgba(110, 229, 255, 0.08);
}

.challengeOption.joined {
  cursor: default;
  opacity: 0.72;
}

.checkMark {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.12);
  font-weight: 900;
}

.optionCopy {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.optionCopy small,
.optionMeta small {
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.45;
}

.optionMeta {
  justify-self: end;
  text-align: end;
}

.errorBox {
  padding: 12px 14px;
  border-radius: 16px;
  color: rgba(254, 202, 202, 0.94);
  background: rgba(239, 68, 68, 0.10);
  border: 1px solid rgba(239, 68, 68, 0.22);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--s-12);
}

.skipButton {
  min-height: 42px;
  padding: 0 8px;
  border: 0;
  color: rgba(255, 255, 255, 0.58);
  background: transparent;
  cursor: pointer;
  font-weight: 720;
}

.skipButton:hover {
  color: rgba(255, 255, 255, 0.82);
}

@media (max-width: 620px) {
  .suggestionHero {
    grid-template-columns: 1fr;
  }

  .suggestionRingo {
    order: -1;
    justify-self: center;
  }

  h1 {
    font-size: 1.9rem;
  }

  .actions {
    display: grid;
  }

  .challengeOption {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .optionMeta {
    grid-column: 2;
    justify-self: start;
    text-align: start;
  }

  .skipButton {
    width: 100%;
  }
}
</style>
