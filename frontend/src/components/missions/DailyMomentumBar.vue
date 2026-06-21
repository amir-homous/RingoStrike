<template>
  <section class="dailyMomentumBar" :class="stateKey" :aria-label="t('missions.dailyMomentum.label')">
    <button type="button" class="strikeBlock" :title="strikeTitle" :aria-label="strikeTitle"
      @click="$emit('explain-strike')">
      <span class="strikeOrb" :class="{ active: todaySafe }" aria-hidden="true">
        <img :src="todaySafe ? strikeActiveIcon : strikeInactiveIcon" alt="" />
      </span>
      <span class="strikeCopy">
        <strong>{{ streakValue }}</strong>
        <!-- <span>{{ stateTitle }}</span> -->
      </span>
    </button>

    <div class="pathMomentum" :aria-label="t('missions.dailyMomentum.pathsLabel')">
      <button v-for="path in visiblePathGroups" :key="path.key" type="button" class="pathRingButton"
        :class="{ complete: path.stats.percent === 100 }"
        :style="{ color: pathRingColor(path) }"
        :title="pathLabel(path)" :aria-label="pathLabel(path)" @click="$emit('select-path', path)">
        <span class="pathRing" aria-hidden="true">
          <svg class="pathRingSvg" viewBox="0 0 80 80" focusable="false">
            <circle class="ringTrack" cx="40" cy="40" r="35" :stroke="ringTrackColor(path)"
              :stroke-width="ringStrokeWidth" pathLength="100" />
            <circle class="ringValue" :class="{ empty: ringPercent(path) <= 0 }" cx="40" cy="40" r="35"
              :stroke="pathRingColor(path)" :stroke-width="ringStrokeWidth" pathLength="100"
              :stroke-dasharray="ringDashArray(path)" />
          </svg>
          <span class="pathIcon">
            <img v-if="path.iconUrl" :src="path.iconUrl" alt="" />
            <span v-else>{{ initialsFor(path.title) }}</span>
          </span>
        </span>
      </button>

      <button v-if="showExplorePaths" type="button" class="pathRingButton explorePathButton"
        :title="t('missions.dailyMomentum.explorePaths')" :aria-label="t('missions.dailyMomentum.explorePaths')"
        @click="$emit('explore-paths')">
        <span class="pathIcon exploreIcon" aria-hidden="true">
          <img v-if="exploreIcon" :src="exploreIcon" alt="" />
          <span v-else>+</span>
        </span>
      </button>

      <div v-if="!visiblePathGroups.length" class="pathEmpty">
        <span>{{ t("missions.dailyMomentum.noPathsShort") }}</span>
      </div>
    </div>

    <div class="momentumActions" :aria-label="t('missions.dailyMomentum.actions.label')">
      <button v-for="action in actions" :key="action.key" type="button" class="momentumAction"
        :class="action.variant || 'secondary'" :disabled="action.disabled" @click="$emit('action', action)">
        <img v-if="actionIcon(action)" class="actionIcon" :src="actionIcon(action)" alt="" aria-hidden="true" />
        {{ action.label }}
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import {
  initialsFor,
  safeColor,
} from "@/utils/missionMomentumUtils";
import { resolveActionIcon } from "@/utils/actionIconUtils";
import strikeActiveIcon from "@/assets/strike-active.png";
import strikeInactiveIcon from "@/assets/strike-diactive.png";

const props = defineProps({
  todaySafe: { type: Boolean, default: false },
  streakCount: { type: [Number, null], default: null },
  pathGroups: { type: Array, default: () => [] },
  actions: { type: Array, default: () => [] },
  showExplorePaths: { type: Boolean, default: false },
});

defineEmits(["select-path", "action", "explain-strike", "explore-paths"]);
const { t } = useI18n();

const ringStrokeWidth = 4;
const exploreIcon = resolveActionIcon("explorePaths");

const visiblePathGroups = computed(() => {
  return props.pathGroups
    .filter((path) => Number(path?.stats?.total || 0) > 0);
});

const progressedPathCount = computed(() => {
  return visiblePathGroups.value.filter((path) => Number(path?.stats?.done || 0) > 0).length;
});

const allVisiblePathsComplete = computed(() => {
  return visiblePathGroups.value.length > 0
    && visiblePathGroups.value.every((path) => Number(path?.stats?.percent || 0) >= 100);
});

const stateKey = computed(() => {
  if (!props.todaySafe) return "notSafe";
  if (allVisiblePathsComplete.value) return "complete";
  if (progressedPathCount.value > 1) return "building";
  return "safe";
});

const stateTitle = computed(() => t(`missions.dailyMomentum.states.${stateKey.value}`));

const streakValue = computed(() => {
  const count = Number(props.streakCount);
  if (Number.isFinite(count) && count > 0) return String(count);
  return "0";
});

const strikeTitle = computed(() => {
  const count = Number(props.streakCount);
  const streak = Number.isFinite(count) && count > 0
    ? t("missions.dailyMomentum.streakDays", { count })
    : t("missions.dailyMomentum.streakFresh");

  return `${stateTitle.value}. ${streak}`;
});

function pathLabel(path) {
  return t("missions.dailyMomentum.pathA11y", {
    path: path?.title || t("missions.fallbackPath"),
    percent: Number(path?.stats?.percent || 0),
  });
}

function actionIcon(action) {
  return resolveActionIcon(action?.icon || action?.key);
}

function pathRingColor(path) {
  return safeColor(path?.color);
}

function ringTrackColor(path) {
  return Number(path?.stats?.percent || 0) >= 100
    ? "rgba(247, 215, 116, 0.16)"
    : "rgba(255, 255, 255, 0.105)";
}

function ringPercent(path) {
  const percent = Math.min(100, Math.max(0, Number(path?.stats?.percent || 0)));
  return Number.isFinite(percent) ? percent : 0;
}

function ringDashArray(path) {
  return `${ringPercent(path)} 100`;
}
</script>

<style scoped>
.dailyMomentumBar {
  position: fixed;
  left: 50%;
  right: auto;
  bottom: 18px;
  z-index: 27;
  transform: translateX(-50%);
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  box-sizing: border-box;
  width: min(var(--container, 1120px), calc(100vw - 32px));
  max-width: calc(100vw - 32px);
  min-width: 0;
  padding: 9px;
  border: 1px solid rgba(110, 229, 255, 0.12);
  border-radius: 20px;
  background:
    radial-gradient(circle at 10% 0%, rgba(110, 229, 255, 0.08), transparent 32%),
    radial-gradient(circle at 88% 20%, rgba(247, 215, 116, 0.07), transparent 30%),
    linear-gradient(135deg, rgba(11, 17, 29, 0.88), rgba(5, 10, 18, 0.76));
  box-shadow:
    0 18px 50px rgba(0, 0, 0, 0.30),
    inset 0 0 0 1px rgba(255, 255, 255, 0.025);
  backdrop-filter: blur(18px);
  overflow: hidden;
}

.strikeBlock,
.pathRingButton,
.momentumAction {
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: inherit;
  background: rgba(255, 255, 255, 0.035);
  cursor: pointer;
  text-align: start;
}

.strikeBlock {
  display: flex;
  gap: 8px;
  align-items: center;
  min-height: 54px;
  padding: 7px 9px;
  border-radius: 14px;
}

.strikeBlock:hover,
.pathRingButton:hover,
.momentumAction:hover:not(:disabled) {
  border-color: rgba(110, 229, 255, 0.22);
  background: rgba(110, 229, 255, 0.055);
}

.strikeOrb {
  display: inline-grid;
  place-items: center;
  width: 38px;
  height: 38px;
  flex: 0 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.045);
  filter: grayscale(1);
  opacity: 0.64;
}

.strikeOrb.active {
  border-color: rgba(247, 215, 116, 0.26);
  background: rgba(247, 215, 116, 0.10);
  filter: none;
  opacity: 1;
  box-shadow: 0 0 22px rgba(247, 215, 116, 0.10);
}

.strikeOrb img {
  width: 25px;
  height: 25px;
  object-fit: contain;
  filter: invert(1);
  opacity: 0.74;
}

.strikeOrb.active img {
  width: 29px;
  height: 29px;
  filter: drop-shadow(0 0 9px rgba(247, 215, 116, 0.34));
  opacity: 1;
}

.strikeCopy {
  display: grid;
  grid-template-columns: auto;
  gap: 1px;
}

.strikeCopy strong {
  min-width: 0;
  color: rgba(255, 255, 255, 0.93);
  font-size: 1.15rem;
  font-weight: 950;
  line-height: 1;
}

.strikeCopy span {
  max-width: 86px;
  color: rgba(219, 244, 255, 0.68);
  font-size: 0.68rem;
  font-weight: 820;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pathMomentum {
  display: flex;
  gap: 7px;
  align-items: center;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.pathMomentum::-webkit-scrollbar {
  display: none;
}

.pathRingButton {
  display: inline-grid;
  place-items: center;
  width: 50px;
  height: 50px;
  flex: 0 0 auto;
  padding: 0;
  border-color: transparent;
  border-radius: 50%;
  background: transparent;
}

.pathRingButton:hover {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.045);
}

.pathRing {
  position: relative;
  display: inline-grid;
  place-items: center;
  width: 48px;
  height: 48px;
  flex: 0 0 auto;
}

.pathRingSvg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: visible;
  pointer-events: none;
  transform: rotate(-90deg);
}

.ringTrack,
.ringValue {
  fill: none;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}

.ringValue {
  filter: drop-shadow(0 0 8px color-mix(in srgb, currentColor 30%, transparent));
  transition: stroke-dasharray 220ms ease, opacity 180ms ease;
}

.ringValue.empty {
  opacity: 0;
}

.pathRingButton.complete .ringValue {
  opacity: 1;
  filter: drop-shadow(0 0 12px color-mix(in srgb, currentColor 42%, transparent));
}

.pathIcon {
  position: relative;
  z-index: 2;
  display: inline-grid;
  place-items: center;
  width: 36px;
  height: 36px;
  padding: 8px;
  border-radius: 50%;
  overflow: hidden;
  background:
    radial-gradient(circle at 34% 20%, rgba(255, 255, 255, 0.10), transparent 54%),
    rgba(255, 255, 255, 0.045);
  color: rgba(255, 255, 255, 0.86);
  font-size: 0.68rem;
  font-weight: 950;
}

.pathIcon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0) invert(1);
}

.explorePathButton {
  border-color: rgba(255, 255, 255, 0.14);
  border-style: dashed;
  background: rgba(255, 255, 255, 0.028);
}

.explorePathButton:hover {
  border-color: rgba(110, 229, 255, 0.24);
  background: rgba(110, 229, 255, 0.05);
}

.exploreIcon {
  border: 0;
  background:
    radial-gradient(circle at 34% 20%, rgba(255, 255, 255, 0.08), transparent 54%),
    rgba(255, 255, 255, 0.035);
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.15rem;
  line-height: 1;
}

.exploreIcon img {
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.86;
}

.pathEmpty {
  display: inline-flex;
  align-items: center;
  min-height: 42px;
  padding: 0 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.62);
  font-size: var(--cap);
  font-weight: 850;
}

.momentumActions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
  min-width: 0;
}

.momentumAction {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 40px;
  padding: 8px 11px;
  border-radius: 13px;
  font-size: 0.78rem;
  font-weight: 900;
  line-height: 1.1;
  white-space: nowrap;
}

.momentumAction img {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  object-fit: contain;
}

.actionIcon {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.86;
}

.momentumAction.primary {
  color: rgba(219, 244, 255, 0.96);
  border-color: rgba(110, 229, 255, 0.22);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.14), rgba(247, 215, 116, 0.08)),
    rgba(255, 255, 255, 0.06);
  box-shadow: inset 0 0 0 1px rgba(110, 229, 255, 0.035);
}

.momentumAction.secondary {
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.055);
}

.dailyMomentumBar.notSafe .strikeBlock {
  border-color: rgba(247, 215, 116, 0.15);
  background: rgba(247, 215, 116, 0.04);
}

.dailyMomentumBar.safe .strikeBlock,
.dailyMomentumBar.building .strikeBlock,
.dailyMomentumBar.complete .strikeBlock {
  border-color: rgba(110, 229, 255, 0.16);
  background: rgba(110, 229, 255, 0.045);
}

.dailyMomentumBar.complete {
  border-color: rgba(247, 215, 116, 0.16);
}

@media (max-width: 880px) {
  .dailyMomentumBar {
    bottom: calc(88px + env(safe-area-inset-bottom));
    grid-template-columns: auto minmax(0, 1fr);
    align-items: center;
  }

  .momentumActions {
    grid-column: 1 / -1;
    justify-content: stretch;
  }

  .momentumAction {
    flex: 1 1 0;
  }
}

@media (max-width: 520px) {
  .dailyMomentumBar {
    gap: 7px;
    padding: 7px;
  }

  .strikeBlock {
    min-height: 48px;
    padding: 6px 8px;
  }

  .strikeCopy span {
    max-width: 64px;
  }

  .pathRingButton {
    width: 44px;
    height: 44px;
  }

  .pathRing {
    width: 42px;
    height: 42px;
  }

  .pathIcon {
    width: 32px;
    height: 32px;
    padding: 7px;
  }
}
</style>
