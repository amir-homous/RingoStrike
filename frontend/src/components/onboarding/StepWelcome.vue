<template>
  <section class="welcomeStep">
    <div class="welcomeCopy">
      <p class="eyebrow">{{ t("onboarding.welcome.eyebrow") }}</p>

      <h1>{{ t("onboarding.welcome.title") }}</h1>

      <p class="body">
        {{ t("onboarding.welcome.body") }}
      </p>

      <BaseButton
        class="startButton"
        variant="primary"
        @click="$emit('start')"
      >
        {{ t("onboarding.welcome.cta") }}
      </BaseButton>
    </div>

    <RingoMoodFigure
      class="welcomeRingo"
      :mood="welcomeMood"
      :alt="t('onboarding.welcome.title')"
      size="lg"
      floating
    />
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";
import { resolveRingoMood } from "@/constants/ringoSprites";

defineEmits(["start"]);

const { t } = useI18n();
const welcomeMood = computed(() => resolveRingoMood("welcome"));
</script>

<style scoped>
.welcomeStep {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-24);
  align-items: center;
}

.welcomeCopy {
  display: grid;
  justify-items: start;
  gap: var(--s-16);
  min-width: 0;
}

.welcomeRingo {
  justify-self: end;
}

.eyebrow {
  margin: 0;
  color: rgba(110, 229, 255, 0.88);
  font-size: 0.74rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1 {
  max-width: 780px;
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 3rem;
  line-height: 1;
  letter-spacing: 0;
}

.body {
  max-width: 720px;
  margin: 0;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.75;
}

.startButton {
  min-width: 140px;
}

@media (max-width: 620px) {
  .welcomeStep {
    grid-template-columns: 1fr;
  }

  .welcomeRingo {
    order: -1;
    justify-self: center;
  }

  h1 {
    font-size: 2.1rem;
    line-height: 1.08;
  }

  .startButton {
    width: 100%;
  }
}
</style>
