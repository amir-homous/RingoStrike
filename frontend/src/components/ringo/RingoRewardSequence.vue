<template>
  <Teleport to="body">
    <div v-if="steps.length" class="rewardOverlay" role="dialog" aria-modal="true">
      <section class="rewardPanel">
        <div class="rewardHead">
          <p class="eyebrow">{{ t("ringoRewardSequence.eyebrow") }}</p>
          <button type="button" class="skipButton" @click="finish">
            {{ t("ringoRewardSequence.skipSummary") }}
          </button>
        </div>

        <div class="ringoMark" aria-hidden="true">
          <img v-if="resolvedSprite.src" :src="resolvedSprite.src" :alt="resolvedSprite.key" />
        </div>

        <div class="rewardStep" :class="currentStep.type || 'default'">
          <span class="stepType">{{ stepLabel }}</span>
          <div v-if="isStrikeStep" class="strikeRewardVisual" :class="{ active: animatedStrikeActive }"
            aria-hidden="true">
            <span class="strikeFlame inactive">
              <img :src="strikeInactiveIcon" alt="" />
            </span>
            <span class="strikeArrow">→</span>
            <span class="strikeFlame active">
              <img :src="strikeActiveIcon" alt="" />
            </span>
            <span v-if="strikeStreakLabel" class="strikeStreak">{{ strikeStreakLabel }}</span>
          </div>
          <div v-else-if="stepVisualIcon" class="stepVisualIcon" :class="currentStep.type || 'default'"
            :style="{ '--step-accent': progressColor }" aria-hidden="true">
            <img :src="stepVisualIcon" alt="" />
          </div>
          <h2>{{ stepTitle }}</h2>
          <p v-if="stepText">{{ stepText }}</p>
          <strong v-if="stepValue">{{ stepValue }}</strong>
          <div v-if="currentStep.progressBar" class="stepProgressBar" aria-hidden="true">
            <span class="progressPrevious" :style="{ width: `${displayedProgressOld}%` }"></span>
            <span class="progressCurrent" :class="{ resetting: progressResetting }"
              :style="{ width: `${animatedProgress}%`, '--step-progress-color': progressColor }"></span>
          </div>
          <small v-if="currentStep.meta" class="stepMeta">{{ currentStep.meta }}</small>
        </div>

        <div class="rewardProgress" :aria-label="t('ringoRewardSequence.progress')">
          <span v-for="(_, index) in steps" :key="index"
            :class="{ active: index === currentIndex, complete: index < currentIndex }" />
        </div>

        <div class="rewardActions">
          <template v-if="currentStep.actions?.length">
            <BaseButton v-for="action in currentStep.actions" :key="action.key" :variant="action.variant || 'secondary'"
              @click="chooseAction(action)">
              {{ action.label }}
            </BaseButton>
          </template>
          <BaseButton v-else variant="primary" @click="advance">
            {{ isLastStep ? t("ringoRewardSequence.finish") : t("ringoRewardSequence.continue") }}
          </BaseButton>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import BaseButton from "@/components/ui/BaseButton.vue";
import { resolveRingoSprite } from "@/constants/ringoSprites";
import { missionIconUrl, resolveChallengeIcon, resolvePathIcon } from "@/utils/missionMomentumUtils";
import strikeActiveIcon from "@/assets/strike-active.png";
import strikeInactiveIcon from "@/assets/strike-diactive.png";

const props = defineProps({
  steps: { type: Array, default: () => [] },
  sprite: { type: String, default: "celebration" },
});

const emit = defineEmits(["finish", "action"]);
const { t } = useI18n();
const currentIndex = ref(0);
const animatedProgress = ref(0);
const displayedProgressOld = ref(0);
const progressResetting = ref(false);
const animatedStrikeActive = ref(false);
const reducedMotion = ref(false);
let progressFrame = 0;
let strikeFrame = 0;
let progressTimer = 0;
let reducedMotionQuery = null;

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
const progressOld = computed(() => boundedPercent(currentStep.value?.progressBar?.old));
const progressNew = computed(() => boundedPercent(currentStep.value?.progressBar?.new));
const progressColor = computed(() => {
  const color = String(currentStep.value?.progressBar?.color || currentStep.value?.color || "").trim();
  return /^#[0-9a-f]{3}([0-9a-f]{3})?$/i.test(color) ? color : "rgba(110, 229, 255, 0.92)";
});
const isStrikeStep = computed(() => currentStep.value?.type === "strike_secured");
const strikeStreakLabel = computed(() => {
  const oldValue = currentStep.value?.oldStreak;
  const newValue = currentStep.value?.newStreak;
  const newNumber = Number(newValue);
  const oldNumber = Number(oldValue);

  if (Number.isFinite(newNumber) && Number.isFinite(oldNumber) && oldNumber !== newNumber) {
    return `${oldNumber} → ${newNumber}`;
  }

  if (Number.isFinite(newNumber)) return String(newNumber);
  return "";
});
const stepVisualIcon = computed(() => {
  if (currentStep.value?.type === "mission_complete") {
    return missionIconUrl({
      key: currentStep.value.missionKey || currentStep.value.mission_key || currentStep.value.key || "",
    });
  }
  if (currentStep.value?.icon) return currentStep.value.icon;
  if (currentStep.value?.type === "path_strengthened") {
    return resolvePathIcon(currentStep.value.pathIcon || currentStep.value.pathId || "");
  }
  if (currentStep.value?.type === "challenge_strengthened" || currentStep.value?.type === "challenge_secured") {
    return resolveChallengeIcon(currentStep.value.challengeId || "");
  }
  return "";
});

watch(
  () => props.steps,
  () => {
    currentIndex.value = 0;
  },
);

watch(
  currentStep,
  () => {
    runStepAnimation();
  },
  { immediate: true },
);

onMounted(() => {
  if (typeof window === "undefined" || !window.matchMedia) return;

  reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  reducedMotion.value = Boolean(reducedMotionQuery.matches);
  const updateReducedMotion = () => {
    reducedMotion.value = Boolean(reducedMotionQuery.matches);
    runStepAnimation();
  };

  reducedMotionQuery.addEventListener?.("change", updateReducedMotion);
  reducedMotionQuery.addListener?.(updateReducedMotion);
  reducedMotionQuery._rewardSequenceListener = updateReducedMotion;
});

onBeforeUnmount(() => {
  cancelAnimationFrame(progressFrame);
  cancelAnimationFrame(strikeFrame);
  window.clearTimeout(progressTimer);

  const listener = reducedMotionQuery?._rewardSequenceListener;
  if (listener) {
    reducedMotionQuery.removeEventListener?.("change", listener);
    reducedMotionQuery.removeListener?.(listener);
  }
});

function advance() {
  if (isLastStep.value) {
    finish();
    return;
  }

  currentIndex.value += 1;
}

function chooseAction(action) {
  emit("action", action);
  finish();
}

function finish() {
  emit("finish");
}

async function runStepAnimation() {
  cancelAnimationFrame(progressFrame);
  cancelAnimationFrame(strikeFrame);
  window.clearTimeout(progressTimer);

  displayedProgressOld.value = reducedMotion.value ? 0 : progressOld.value;
  animatedProgress.value = reducedMotion.value ? progressNew.value : progressOld.value;
  progressResetting.value = false;
  animatedStrikeActive.value = reducedMotion.value ? isStrikeStep.value : false;

  await nextTick();

  if (reducedMotion.value) {
    animatedProgress.value = progressNew.value;
    animatedStrikeActive.value = isStrikeStep.value;
    return;
  }

  progressFrame = requestAnimationFrame(() => {
    runProgressSegments(progressSegments());
  });

  if (isStrikeStep.value) {
    strikeFrame = requestAnimationFrame(() => {
      animatedStrikeActive.value = true;
    });
  }
}

function progressSegments() {
  const progressBar = currentStep.value?.progressBar;
  if (!progressBar || !hasUsableProgress(progressBar.old) || !hasUsableProgress(progressBar.new)) {
    return [];
  }

  const oldLevel = Number(progressBar.oldLevel);
  const newLevel = Number(progressBar.newLevel);
  const levelIncreased = Number.isFinite(oldLevel) && Number.isFinite(newLevel) && newLevel > oldLevel;

  if (levelIncreased && progressNew.value < progressOld.value) {
    return [
      { old: progressOld.value, new: 100 },
      { old: 0, new: progressNew.value },
    ];
  }

  return [{ old: progressOld.value, new: progressNew.value }];
}

async function runProgressSegments(segments) {
  if (!segments.length) return;

  const [first, second] = segments;
  displayedProgressOld.value = first.old;
  animatedProgress.value = first.old;
  await nextTick();

  progressFrame = requestAnimationFrame(() => {
    animatedProgress.value = first.new;

    if (!second) return;

    progressTimer = window.setTimeout(async () => {
      progressResetting.value = true;
      displayedProgressOld.value = second.old;
      animatedProgress.value = second.old;
      await nextTick();

      progressFrame = requestAnimationFrame(() => {
        progressResetting.value = false;
        animatedProgress.value = second.new;
      });
    }, 760);
  });
}

function hasUsableProgress(value) {
  const number = Number(value);
  return Number.isFinite(number);
}

function boundedPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return 0;
  return Math.max(0, Math.min(100, Math.round(number)));
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
  position: relative;
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

.stepVisualIcon {
  justify-self: center;
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  margin-block-end: 2px;
  border: 3px solid color-mix(in srgb, var(--step-accent) 42%, rgba(255, 255, 255, 0.10));
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 30%, color-mix(in srgb, var(--step-accent) 18%, transparent), transparent 62%),
    rgba(255, 255, 255, 0.055);
  box-shadow:
    0 0 22px color-mix(in srgb, var(--step-accent) 16%, transparent),
    inset 0 0 0 1px rgba(255, 255, 255, 0.035);
}

.stepVisualIcon img {
  width: 34px;
  height: 34px;
  object-fit: contain;
  filter: invert(1) drop-shadow(0 0 10px rgba(0, 0, 0, 0.24));
}

.stepVisualIcon.mission_complete img,
.stepVisualIcon.challenge_strengthened img,
.stepVisualIcon.final_choice img {
  filter: brightness(0) invert(1) drop-shadow(0 0 10px rgba(110, 229, 255, 0.18));
}

.stepVisualIcon.path_strengthened img {
  width: 36px;
  height: 36px;
}

.stepVisualIcon.challenge_strengthened {
  background:
    radial-gradient(circle at 50% 30%, rgba(255, 255, 255, 0.16), transparent 62%),
    rgba(255, 255, 255, 0.09);
}

.strikeRewardVisual {
  justify-self: center;
  display: inline-grid;
  grid-template-columns: auto auto auto;
  gap: 10px;
  align-items: center;
  margin-block-end: 2px;
}

.strikeFlame {
  display: grid;
  place-items: center;
  width: 54px;
  height: 54px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.045);
}

.strikeFlame img {
  width: 34px;
  height: 34px;
  object-fit: contain;
}

.strikeFlame.inactive {
  filter: grayscale(1);
  opacity: 0.46;
}

.strikeFlame.inactive img {
  filter: brightness(0) invert(1);
}

.strikeFlame.active {
  border-color: rgba(247, 215, 116, 0.30);
  background: rgba(247, 215, 116, 0.10);
  opacity: 0.32;
  transform: scale(0.92);
  transition:
    opacity 360ms ease,
    transform 360ms ease,
    box-shadow 360ms ease;
}

.strikeRewardVisual.active .strikeFlame.active {
  opacity: 1;
  transform: scale(1);
  box-shadow: 0 0 24px rgba(247, 215, 116, 0.18);
}

.strikeArrow {
  color: rgba(255, 255, 255, 0.42);
  font-weight: 900;
}

.strikeStreak {
  grid-column: 1 / -1;
  justify-self: center;
  min-height: 22px;
  padding: 3px 9px;
  border: 1px solid rgba(247, 215, 116, 0.20);
  border-radius: 999px;
  color: rgba(253, 230, 138, 0.95);
  background: rgba(247, 215, 116, 0.08);
  font-size: 0.78rem;
  font-weight: 850;
}

.stepProgressBar {
  position: relative;
  overflow: hidden;
  width: min(300px, 100%);
  height: 10px;
  margin: 6px auto 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
}

.stepProgressBar span {
  position: absolute;
  inset-block: 0;
  inset-inline-start: 0;
  border-radius: inherit;
}

.progressPrevious {
  background: rgba(255, 255, 255, 0.16);
}

.progressCurrent {
  background: linear-gradient(90deg, rgba(110, 229, 255, 0.92), var(--step-progress-color));
  box-shadow: 0 0 18px color-mix(in srgb, var(--step-progress-color) 34%, transparent);
  transition: width 720ms cubic-bezier(0.22, 0.9, 0.32, 1);
}

.progressCurrent.resetting {
  transition: none;
}

.stepMeta {
  color: rgba(255, 255, 255, 0.54);
  font-weight: 760;
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
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

@media (prefers-reduced-motion: reduce) {

  .progressCurrent,
  .strikeFlame.active {
    transition: none;
  }
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
