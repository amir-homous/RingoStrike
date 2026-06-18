<template>
  <BaseCard class="compactProgressStrip" :class="{ safe: todaySafe }">
    <div class="progressIdentity">
      <span v-if="todaySafe" class="safeDot" aria-hidden="true"></span>
      <span>{{ todaySafe ? t("progress.compactTodaySafe") : t("progress.compactTodayOpen") }}</span>
    </div>

    <div class="progressMeta" :aria-label="t('progress.compactLabel')">
      <span>{{ t("progress.compactStreak", { count: streak }) }}</span>
      <span>{{ t("common.level", { level }) }}</span>
      <span>{{ t("progress.compactToNext", { percent: progressPercent, level: nextLevel }) }}</span>
    </div>

    <div class="miniXpBar" aria-hidden="true">
      <span :style="{ width: `${progressPercent}%` }"></span>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import BaseCard from "@/components/ui/BaseCard.vue";

const props = defineProps({
  stats: { type: Object, required: true },
  todaySafe: { type: Boolean, default: false },
});

const { t } = useI18n();

const level = computed(() => Number(props.stats?.level || 1));
const nextLevel = computed(() => level.value + 1);
const streak = computed(() => Number(props.stats?.current_streak || 0));
const progressPercent = computed(() => {
  const value = Number(props.stats?.progress_percent || 0);
  if (!Number.isFinite(value)) return 0;

  return Math.max(0, Math.min(100, Math.round(value)));
});
</script>

<style scoped>
.compactProgressStrip {
  display: grid;
  gap: 10px;
  padding: 14px 16px;
  border-color: rgba(110, 229, 255, 0.15);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.08), transparent 34%),
    rgba(255, 255, 255, 0.026);
}

.compactProgressStrip.safe {
  border-color: rgba(74, 222, 128, 0.17);
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.07), transparent 34%),
    rgba(255, 255, 255, 0.026);
}

.progressIdentity,
.progressMeta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.progressIdentity {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.78rem;
  font-weight: 850;
}

.safeDot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #4ade80;
  box-shadow: 0 0 14px rgba(74, 222, 128, 0.55);
}

.progressMeta {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.76rem;
  font-weight: 760;
}

.progressMeta span:not(:last-child)::after {
  content: "·";
  margin-inline-start: 8px;
  color: rgba(255, 255, 255, 0.32);
}

.miniXpBar {
  overflow: hidden;
  height: 5px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.07);
}

.miniXpBar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(110, 229, 255, 0.9), rgba(247, 215, 116, 0.82));
}
</style>
