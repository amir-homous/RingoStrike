<template>
  <section class="suggestionStep">
    <div class="stepHeader">
      <p class="eyebrow">{{ t("onboarding.suggestion.eyebrow") }}</p>
      <h1>{{ t("onboarding.suggestion.title") }}</h1>
      <p>
        {{ t("onboarding.suggestion.body", { path: pathLabel }) }}
      </p>
    </div>

    <BaseCard class="suggestionCard">
      <div v-if="challenge" class="challengeCopy">
        <span class="statusPill">
          {{ t("onboarding.suggestion.recommended") }}
        </span>

        <h2>{{ challenge.name || challenge.challenge_name }}</h2>

        <p>
          {{ challenge.description || t("onboarding.suggestion.noDescription") }}
        </p>

        <div class="meta">
          <span v-if="challenge.duration_days">
            {{ t("common.dayChallenge", { count: challenge.duration_days }) }}
          </span>
          <span>{{ t("onboarding.suggestion.dailyMission") }}</span>
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
          v-if="challenge"
          variant="primary"
          :loading="joining"
          @click="$emit('start')"
        >
          {{ t("onboarding.suggestion.start") }}
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
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";

const props = defineProps({
  path: { type: String, default: "" },
  challenge: { type: Object, default: null },
  joining: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

defineEmits(["start", "browse", "skip"]);

const { t } = useI18n();

const pathLabel = computed(() => {
  return props.path ? t(`onboarding.paths.${props.path}.label`) : t("onboarding.path.defaultPath");
});
</script>

<style scoped>
.suggestionStep {
  display: grid;
  gap: var(--s-20);
}

.stepHeader {
  max-width: 760px;
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
  h1 {
    font-size: 1.9rem;
  }

  .actions {
    display: grid;
  }

  .skipButton {
    width: 100%;
  }
}
</style>
