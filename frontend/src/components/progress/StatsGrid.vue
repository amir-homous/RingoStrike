<template>
  <div class="grid">
    <BaseCard v-for="item in items" :key="item.label" class="stat" :padded="true">
      <p class="caption">{{ item.label }}</p>
      <p class="value">{{ item.value }}</p>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import BaseCard from "@/components/ui/BaseCard.vue";

const props = defineProps({ stats: { type: Object, required: true } });
const { t } = useI18n();

const items = computed(() => [
  { label: t("progress.totalXp"), value: props.stats.total_points },
  { label: t("progress.totalCheckins"), value: props.stats.total_checkins },
  { label: t("progress.currentStreak"), value: props.stats.current_streak },
  { label: t("progress.longestStreak"), value: props.stats.longest_streak },
  { label: t("progress.currentLevel"), value: props.stats.level },
]);
</script>

<style scoped>
.grid{ display:grid; gap:var(--s-12); grid-template-columns: repeat(auto-fit,minmax(150px,1fr)); }
.value{ margin: 4px 0 0; font-size: 22px; font-weight: 700; line-height: 1.2; }
.stat{ background: rgba(255,255,255,0.02); box-shadow:none; }
</style>
