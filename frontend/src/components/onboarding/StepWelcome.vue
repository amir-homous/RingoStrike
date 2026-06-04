<template>
  <section class="welcomeStep">
    <div class="marker" aria-hidden="true">
      <span></span>
    </div>

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
  </section>
</template>

<script setup>
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";

defineEmits(["start"]);

const { t } = useI18n();
</script>

<style scoped>
.welcomeStep {
  display: grid;
  justify-items: start;
  gap: var(--s-16);
}

.marker {
  width: 62px;
  height: 62px;
  display: grid;
  place-items: center;
  border-radius: 22px;
  background: rgba(110, 229, 255, 0.12);
  border: 1px solid rgba(110, 229, 255, 0.24);
}

.marker span {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #67e8f9;
  box-shadow: 0 0 26px rgba(103, 232, 249, 0.62);
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
  h1 {
    font-size: 2.1rem;
    line-height: 1.08;
  }

  .startButton {
    width: 100%;
  }
}
</style>
