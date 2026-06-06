<template>
  <section class="pathStep">
    <div class="pathHero">
      <div class="stepHeader">
        <p class="eyebrow">{{ t("onboarding.path.eyebrow") }}</p>
        <h1>{{ t("onboarding.path.title") }}</h1>
        <p>{{ t("onboarding.path.body") }}</p>
      </div>

      <RingoMoodFigure
        class="pathRingo"
        :mood="pathMood"
        :alt="t('onboarding.path.title')"
        size="md"
        floating
      />
    </div>

    <div class="pathGrid">
      <button
        v-for="path in paths"
        :key="path"
        type="button"
        class="pathCard"
        :class="{ selected: modelValue === path }"
        @click="$emit('update:modelValue', path)"
      >
        <span class="pathIcon" aria-hidden="true"></span>
        <span class="pathLabel">{{ t(`onboarding.paths.${path}.label`) }}</span>
        <span class="pathSuggestion">
          {{ t("onboarding.path.suggested", { challenge: t(`onboarding.paths.${path}.challenge`) }) }}
        </span>
      </button>
    </div>

    <div class="actions">
      <BaseButton
        variant="primary"
        :disabled="!modelValue"
        @click="$emit('continue')"
      >
        {{ t("onboarding.path.continue") }}
      </BaseButton>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";
import { resolveRingoMood } from "@/constants/ringoSprites";
import { IDENTITY_PATHS } from "@/lib/guidedExperience";

const props = defineProps({
  modelValue: { type: String, default: "" },
});

defineEmits(["update:modelValue", "continue"]);

const { t } = useI18n();
const paths = IDENTITY_PATHS;

const pathMood = computed(() => {
  return props.modelValue
    ? resolveRingoMood("onboardingPathSelected")
    : resolveRingoMood("onboardingPath");
});
</script>

<style scoped>
.pathStep {
  display: grid;
  gap: var(--s-20);
}

.pathHero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-20);
  align-items: center;
}

.stepHeader {
  max-width: 760px;
  min-width: 0;
}

.pathRingo {
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

.stepHeader p:not(.eyebrow) {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.7;
}

.pathGrid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--s-12);
}

.pathCard {
  min-height: 146px;
  display: grid;
  align-content: start;
  gap: 10px;
  padding: 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  color: rgba(255, 255, 255, 0.88);
  text-align: start;
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: transform 140ms ease, background 140ms ease, border-color 140ms ease;
}

.pathCard:hover,
.pathCard.selected {
  transform: translateY(-2px);
  border-color: rgba(110, 229, 255, 0.28);
  background: rgba(110, 229, 255, 0.08);
}

.pathIcon {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: #67e8f9;
  box-shadow: 0 0 20px rgba(103, 232, 249, 0.50);
}

.pathLabel {
  font-weight: 850;
}

.pathSuggestion {
  color: rgba(255, 255, 255, 0.56);
  font-size: 0.88rem;
  line-height: 1.55;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 980px) {
  .pathGrid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .pathHero {
    grid-template-columns: 1fr;
  }

  .pathRingo {
    order: -1;
    justify-self: center;
  }

  h1 {
    font-size: 1.9rem;
  }

  .pathGrid {
    grid-template-columns: 1fr;
  }

  .actions {
    display: grid;
  }
}
</style>
