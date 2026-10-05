<template>
  <div
    class="spaceObject"
    :class="{ locked: !reward.unlocked, unlocked: reward.unlocked }"
    :aria-label="objectAriaLabel"
    :title="objectAriaLabel"
  >
    <span class="objectMark" aria-hidden="true">
      {{ objectMark }}
    </span>
    <span class="objectText">
      <span class="objectTitle">{{ reward.title }}</span>
      <span class="objectStatus">
        {{ reward.unlocked ? t("space.objectUnlocked") : t("space.objectLockedPreview") }}
      </span>
    </span>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps({
  reward: { type: Object, required: true },
});

const { t } = useI18n();

const objectMark = computed(() => {
  const title = String(props.reward?.title || props.reward?.key || "?").trim();
  return title.slice(0, 1).toUpperCase();
});

const objectAriaLabel = computed(() => {
  const title = props.reward?.title || props.reward?.key || "";
  const state = props.reward?.unlocked
    ? t("space.objectUnlocked")
    : t("space.objectLockedPreview");

  return `${title}: ${state}`;
});
</script>

<style scoped>
.spaceObject {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  min-height: 26px;
  padding: 5px 8px;
  border-radius: 9px;
  color: rgba(255, 255, 255, 0.88);
  background: rgba(110, 229, 255, 0.12);
  border: 1px solid rgba(110, 229, 255, 0.24);
  font-size: 0.72rem;
  font-weight: 800;
}

.spaceObject.unlocked {
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.035),
    0 0 18px rgba(110, 229, 255, 0.08);
}

.spaceObject.locked {
  color: rgba(255, 255, 255, 0.48);
  background: rgba(255, 255, 255, 0.035);
  border-color: rgba(255, 255, 255, 0.09);
  filter: grayscale(0.35);
}

.objectMark {
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  border-radius: 7px;
  color: rgba(6, 11, 20, 0.92);
  background: rgba(255, 255, 255, 0.86);
  font-size: 0.62rem;
  line-height: 1;
}

.locked .objectMark {
  color: rgba(255, 255, 255, 0.50);
  background: rgba(255, 255, 255, 0.12);
}

.objectText {
  display: grid;
  gap: 1px;
  min-width: 0;
}

.objectTitle,
.objectStatus {
  min-width: 0;
  overflow-wrap: anywhere;
}

.objectStatus {
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.58rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

.locked .objectStatus {
  color: rgba(255, 255, 255, 0.42);
}
</style>
