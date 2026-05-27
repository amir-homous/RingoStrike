<template>
  <div class="stack-8">
    <div class="labels">
      <span class="caption">XP Progress</span>
      <span class="caption">{{ safePercent }}%</span>
    </div>

    <div class="track" :class="{ pulse: animatePulse }" role="progressbar" :aria-valuenow="safePercent" aria-valuemin="0" aria-valuemax="100">
      <div class="fill" :style="{ width: `${safePercent}%` }" />
    </div>

    <div class="meta">
      <span>{{ xp }} XP</span>
      <span>{{ nextLevelXp }} XP</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  xp: { type: Number, default: 0 },
  nextLevelXp: { type: Number, default: 100 },
  progressPercent: { type: Number, default: 0 },
  animatePulse: { type: Boolean, default: false },
});

const safePercent = computed(() => {
  const v = Number.isFinite(props.progressPercent) ? props.progressPercent : 0;
  return Math.max(0, Math.min(100, Math.round(v)));
});
</script>

<style scoped>
.labels, .meta{display:flex;justify-content:space-between;gap: var(--s-8)}
.track{height: 12px;border-radius: 999px;background: rgba(255,255,255,0.08);border: 1px solid rgba(255,255,255,0.1);overflow: hidden;transition:box-shadow 240ms ease,border-color 240ms ease}
.track.pulse{box-shadow:0 0 0 3px rgba(99,102,241,.16);border-color:rgba(99,102,241,.45)}
.fill{height: 100%;border-radius: inherit;background: linear-gradient(90deg, rgba(99,102,241,0.88), rgba(56,189,248,0.88));transition: width 500ms ease}
.meta{font-size: var(--cap);color: var(--muted)}
</style>
