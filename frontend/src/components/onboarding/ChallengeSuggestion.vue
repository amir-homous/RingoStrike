<template>
  <!-- B37 (D81): pick a first challenge. Three cards (icon, name, one short line); "Start this
       challenge" and "Choose later" stay above the fold. -->
  <section class="suggestionStep">
    <div class="stepHeader">
      <p class="eyebrow">{{ t("onboarding.suggestion.firstEyebrow") }}</p>
      <h1>{{ t("onboarding.suggestion.pickTitle") }}</h1>
    </div>

    <BaseCard class="suggestionCard">
      <div v-if="challenges.length" class="challengeOptions" role="radiogroup" :aria-label="t('onboarding.suggestion.pickTitle')">
        <button
          v-for="challenge in orderedChallenges"
          :key="challenge.challenge_id"
          type="button"
          role="radio"
          class="challengeOption"
          :class="{ selected: selectedIds.includes(challenge.challenge_id), joined: challenge.is_joined }"
          :aria-checked="selectedIds.includes(challenge.challenge_id) ? 'true' : 'false'"
          :data-challenge="challenge.challenge_id"
          @click="toggleChallenge(challenge)"
        >
          <span class="challengeIcon" aria-hidden="true">
            <img :src="challengeIcon(challenge)" alt="" class="iconOnDark" />
          </span>
          <span class="optionCopy">
            <strong>{{ challengeTitle(challenge) }}</strong>
            <small>
              <template v-if="challenge.is_joined">{{ t("onboarding.suggestion.alreadyJoined") }}</template>
              <template v-else>{{ t("onboarding.suggestion.cardLine", { days: fmt(challengeDuration(challenge)), line: challengeDescription(challenge) }) }}</template>
            </small>
          </span>
        </button>
      </div>

      <div v-else class="challengeCopy">
        <span class="statusPill fallback">
          {{ t("onboarding.suggestion.fallbackPill") }}
        </span>
        <h2>{{ t("onboarding.suggestion.fallbackTitle") }}</h2>
        <p>{{ t("onboarding.suggestion.fallbackLater") }}</p>
      </div>

      <div v-if="error" class="errorBox">
        {{ error }}
      </div>

      <div class="actions">
        <BaseButton v-if="challenges.length" variant="primary" :loading="joining" :disabled="selectedIds.length === 0"
          @click="$emit('start', selectedIds)">
          {{ t("onboarding.suggestion.startThis") }}
        </BaseButton>
        <button type="button" class="skipButton" @click="$emit('skip')">
          {{ t("onboarding.suggestion.chooseLater") }}
        </button>
      </div>
    </BaseCard>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { formatNumber, numberAwareT } from "@/lib/i18nNumbers";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { challengeIconKey } from "@/lib/challengeIconKeys";
import { localizeChallenge } from "@/lib/ringoContentLocalization";
import { resolveChallengeIcon } from "@/utils/missionMomentumUtils";

const props = defineProps({
  path: { type: String, default: "" },
  paths: { type: Array, default: () => [] },
  challenge: { type: Object, default: null },
  challenges: { type: Array, default: () => [] },
  joining: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

defineEmits(["start", "skip"]);

const { locale, t: baseT } = useI18n();
// B10: numbers in copy use the locale's digits; a numeric count picks the plural form.
const t = numberAwareT(baseT, () => locale.value);
const fmt = (value) => formatNumber(value, locale.value);
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

const primaryChallenge = computed(() => {
  return props.challenge
    || props.challenges.find((challenge) => !challenge.is_joined)
    || props.challenges[0]
    || null;
});

// The recommended challenge first, then the others (three cards at most).
const orderedChallenges = computed(() => {
  const primaryId = primaryChallenge.value?.challenge_id;
  const rest = props.challenges.filter((challenge) => challenge.challenge_id !== primaryId);
  return [primaryChallenge.value, ...rest].filter(Boolean).slice(0, 3);
});

// The icon from the stable English key, never the translated name (B33 fix).
function challengeIcon(challenge) {
  return resolveChallengeIcon({ icon_key: challengeIconKey(challenge?.name || challenge?.challenge_name), challenge_id: challenge?.challenge_id });
}

function challengeTitle(challenge) {
  const displayChallenge = localizeChallenge(challenge, locale.value);
  return displayChallenge?.name || displayChallenge?.challenge_name || t("common.challenge");
}

function challengeDescription(challenge) {
  const displayChallenge = localizeChallenge(challenge, locale.value);

  return displayChallenge?.ringo_intro
    || displayChallenge?.description
    || t("onboarding.suggestion.noDescription");
}

function challengeDuration(challenge) {
  return challenge?.estimated_days || challenge?.duration_days || 0;
}

function toggleChallenge(challenge) {
  if (challenge.is_joined) return;

  if (selectedIds.value.includes(challenge.challenge_id)) {
    selectedIds.value = selectedIds.value.filter((id) => id !== challenge.challenge_id);
    return;
  }

  selectedIds.value = [challenge.challenge_id];
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

.recommendedChallenge {
  display: grid;
  gap: var(--s-12);
}

.primaryChallenge {
  padding: 18px;
  border-color: rgba(110, 229, 255, 0.36);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.12), transparent 34%),
    rgba(110, 229, 255, 0.07);
}

.recommendedLabel {
  color: rgba(167, 243, 208, 0.92);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.alternativeChoices {
  display: grid;
  gap: 10px;
}

.alternativeTitle {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.82rem;
}

.secondaryChallenge {
  opacity: 0.84;
}

.secondaryChallenge:hover,
.secondaryChallenge.selected {
  opacity: 1;
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

/* B37 (D81): three compact cards with the challenge icon; the actions stay above the fold. */
.suggestionStep h1 {
  font-size: 2rem;
  line-height: 1.1;
}

.suggestionCard {
  gap: var(--s-16);
  padding: 18px;
}

.challengeOptions {
  margin-top: 0;
  gap: 10px;
}

.challengeOption {
  grid-template-columns: auto minmax(0, 1fr);
  min-height: 64px;
  padding: 10px 12px;
}

.challengeOption.selected {
  border-color: rgba(110, 229, 255, 0.85);
  box-shadow: inset 0 0 0 1px rgba(110, 229, 255, 0.5);
}

.challengeOption:focus-visible,
.skipButton:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

.challengeIcon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(11, 14, 20, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.challengeIcon img {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.optionCopy strong {
  font-size: 0.98rem;
}

.suggestionCard .actions {
  display: grid;
  gap: 4px;
}

.suggestionCard .skipButton {
  min-height: 44px;
}

@media (max-width: 620px) {
  .suggestionStep h1 {
    font-size: 1.6rem;
  }

  .suggestionCard .actions {
    position: sticky;
    bottom: 0;
    z-index: 2;
    padding: 10px 0 calc(10px + env(safe-area-inset-bottom));
    background: linear-gradient(to top, rgba(8, 12, 22, 0.96) 60%, rgba(8, 12, 22, 0));
  }
}
</style>