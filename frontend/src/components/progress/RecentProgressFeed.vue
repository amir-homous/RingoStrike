<template>
  <BaseCard class="feed">
    <div class="head">
      <h3 class="h2">{{ t("progress.recent") }}</h3>
      <span class="caption">{{ t("progress.today") }}</span>
    </div>

    <ul>
      <li v-for="msg in messages" :key="msg">{{ msg }}</li>
    </ul>
  </BaseCard>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import BaseCard from "@/components/ui/BaseCard.vue";

const props = defineProps({ stats: { type: Object, required: true } });
const { t } = useI18n();

const messages = computed(() => {
  const items = [];
  const estimatedTodayXp = props.stats.current_streak > 0 ? 10 : 0;
  items.push(t("progress.xpFromCheckins", { xp: estimatedTodayXp }));
  if (props.stats.current_streak > 0) {
    items.push(`🔥 ${t("progress.streakToday")}`);
  } else {
    items.push(`✅ ${t("progress.startStreak")}`);
  }
  items.push(`🏁 ${t("progress.xpToNext", { xp: Math.max(0, props.stats.next_level_xp - props.stats.xp) })}`);
  return items;
});
</script>

<style scoped>
.head{ display:flex; justify-content:space-between; align-items:center; gap:var(--s-8); }
ul{ margin: var(--s-12) 0 0; padding-left: 18px; color: var(--muted); display:grid; gap:var(--s-8); }
</style>
