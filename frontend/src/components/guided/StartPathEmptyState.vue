<template>
  <BaseCard class="startPath">
    <div class="ambient" aria-hidden="true"></div>

    <div class="content">
      <div class="marker" aria-hidden="true">
        <span></span>
      </div>

      <div class="copy">
        <p class="eyebrow">{{ t("guidedStart.eyebrow") }}</p>

        <h2>{{ t("guidedStart.title") }}</h2>

        <p>
          {{ t("guidedStart.body") }}
        </p>
      </div>

      <div class="actions">
        <RouterLink
          v-slot="{ navigate }"
          :to="primaryTo"
          custom
        >
          <BaseButton
            variant="primary"
            @click="navigate"
          >
            {{ t("guidedStart.primaryCta") }}
          </BaseButton>
        </RouterLink>

        <RouterLink
          v-slot="{ navigate }"
          :to="secondaryTo"
          custom
        >
          <BaseButton
            variant="secondary"
            @click="navigate"
          >
            {{ t("guidedStart.secondaryCta") }}
          </BaseButton>
        </RouterLink>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";

defineProps({
  primaryTo: { type: String, default: "/onboarding" },
  secondaryTo: { type: String, default: "/challenges" },
});

const { t } = useI18n();
</script>

<style scoped>
.startPath {
  position: relative;
  overflow: hidden;
  padding: 26px;
  border-radius: 30px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.14), transparent 34%),
    radial-gradient(circle at 92% 12%, rgba(195, 90, 214, 0.12), transparent 32%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.065), rgba(255, 255, 255, 0.024));
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.24);
}

.ambient {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.content {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: center;
}

.marker {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  border-radius: 20px;
  background: rgba(99, 102, 241, 0.16);
  border: 1px solid rgba(99, 102, 241, 0.28);
}

.marker span {
  width: 13px;
  height: 13px;
  border-radius: 999px;
  background: #67e8f9;
  box-shadow: 0 0 24px rgba(103, 232, 249, 0.74);
}

.copy {
  min-width: 0;
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.88);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 2.65rem;
  line-height: 1;
  letter-spacing: 0;
}

.copy p:not(.eyebrow) {
  max-width: 720px;
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.7;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--s-12);
}

@media (max-width: 860px) {
  .content {
    grid-template-columns: 1fr;
  }

  .actions {
    justify-content: flex-start;
  }

  h2 {
    font-size: 2.2rem;
  }
}

@media (max-width: 560px) {
  .startPath {
    padding: 18px;
    border-radius: 24px;
  }

  .actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  h2 {
    font-size: 1.75rem;
    line-height: 1.08;
  }
}
</style>
