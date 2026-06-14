<template>
  <Teleport to="body">
    <div v-if="steps.length" class="rewardOverlay" role="dialog" aria-modal="true">
      <section class="rewardPanel">
        <div class="rewardHead">
          <p class="eyebrow">{{ t("ringoRewardSequence.eyebrow") }}</p>
          <button type="button" class="skipButton" @click="finish">
            {{ t("ringoRewardSequence.skip") }}
          </button>
        </div>

        <div class="ringoMark" aria-hidden="true">
          <img v-if="resolvedSprite.src" :src="resolvedSprite.src" :alt="resolvedSprite.key" />
        </div>

        <div class="rewardStep" :class="currentStep.type || 'default'">
          <span class="stepType">{{ stepLabel }}</span>
          <h2>{{ stepTitle }}</h2>
          <p v-if="stepText">{{ stepText }}</p>
          <strong v-if="stepValue">{{ stepValue }}</strong>
        </div>

        <div class="rewardProgress" :aria-label="t('ringoRewardSequence.progress')">
          <span
            v-for="(_, index) in steps"
            :key="index"
            :class="{ active: index === currentIndex, complete: index < currentIndex }"
          />
        </div>

        <div class="rewardActions">
          <BaseButton variant="primary" @click="advance">
            {{ isLastStep ? t("ringoRewardSequence.finish") : t("ringoRewardSequence.continue") }}
          </BaseButton>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import BaseButton from "@/components/ui/BaseButton.vue";
import { resolveRingoSprite } from "@/constants/ringoSprites";

const props = defineProps({
  steps: { type: Array, default: () => [] },
  sprite: { type: String, default: "celebration" },
});

const emit = defineEmits(["finish"]);
const { t } = useI18n();
const currentIndex = ref(0);

const currentStep = computed(() => props.steps[currentIndex.value] || {});
const isLastStep = computed(() => currentIndex.value >= props.steps.length - 1);
const resolvedSprite = computed(() => resolveRingoSprite(currentStep.value.sprite || props.sprite));

const stepLabel = computed(() => {
  return currentStep.value.label || t(`ringoRewardSequence.types.${currentStep.value.type || "default"}`);
});

const stepTitle = computed(() => {
  return currentStep.value.title || t("ringoRewardSequence.fallbackTitle");
});

const stepText = computed(() => currentStep.value.text || "");
const stepValue = computed(() => currentStep.value.value || "");

watch(
  () => props.steps,
  () => {
    currentIndex.value = 0;
  },
);

function advance() {
  if (isLastStep.value) {
    finish();
    return;
  }

  currentIndex.value += 1;
}

function finish() {
  emit("finish");
}
</script>

<style scoped>
.rewardOverlay {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: 18px;
  background: rgba(2, 6, 12, 0.72);
  backdrop-filter: blur(10px);
}

.rewardPanel {
  display: grid;
  gap: 14px;
  width: min(480px, 100%);
  padding: 18px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 22px;
  color: rgba(255, 255, 255, 0.94);
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.10), transparent 36%),
    rgba(8, 13, 24, 0.96);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
}

.rewardHead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.eyebrow,
.stepType {
  margin: 0;
  color: rgba(110, 229, 255, 0.86);
  font-size: var(--cap);
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.skipButton {
  min-height: 34px;
  padding: 7px 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.06);
  cursor: pointer;
  font-weight: 780;
}

.ringoMark {
  justify-self: center;
  width: 104px;
  height: 104px;
}

.ringoMark img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.rewardStep {
  display: grid;
  gap: 8px;
  min-height: 154px;
  align-content: center;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.045);
  text-align: center;
}

.rewardStep h2,
.rewardStep p {
  margin: 0;
}

.rewardStep h2 {
  color: rgba(255, 255, 255, 0.96);
  font-size: clamp(1.25rem, 4vw, 1.75rem);
  line-height: 1.2;
}

.rewardStep p {
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.65;
}

.rewardStep strong {
  color: rgba(187, 247, 208, 0.98);
  font-size: 1.4rem;
}

.rewardProgress {
  display: flex;
  justify-content: center;
  gap: 7px;
}

.rewardProgress span {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
}

.rewardProgress span.active,
.rewardProgress span.complete {
  background: rgba(110, 229, 255, 0.92);
}

.rewardActions {
  display: flex;
  justify-content: center;
}

@media (max-width: 560px) {
  .rewardPanel {
    padding: 14px;
  }

  .rewardHead {
    display: grid;
  }

  .skipButton,
  .rewardActions :deep(.btn) {
    width: 100%;
  }
}
</style>
