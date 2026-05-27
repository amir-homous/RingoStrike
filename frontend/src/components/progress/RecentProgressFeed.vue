<template>
  <BaseCard class="feed">
    <div class="head">
      <h3 class="h2">Recent Progress</h3>
      <span class="caption">Today</span>
    </div>

    <ul>
      <li v-for="msg in messages" :key="msg">{{ msg }}</li>
    </ul>
  </BaseCard>
</template>

<script setup>
import { computed } from "vue";
import BaseCard from "@/components/ui/BaseCard.vue";

const props = defineProps({ stats: { type: Object, required: true } });

const messages = computed(() => {
  const items = [];
  const estimatedTodayXp = props.stats.current_streak > 0 ? 10 : 0;
  items.push(`+${estimatedTodayXp} XP from completed check-ins`);
  if (props.stats.current_streak > 0) {
    items.push("🔥 Streak maintained today");
  } else {
    items.push("✅ Start a check-in today to begin a streak");
  }
  items.push(`🏁 ${Math.max(0, props.stats.next_level_xp - props.stats.xp)} XP to your next level`);
  return items;
});
</script>

<style scoped>
.head{ display:flex; justify-content:space-between; align-items:center; gap:var(--s-8); }
ul{ margin: var(--s-12) 0 0; padding-left: 18px; color: var(--muted); display:grid; gap:var(--s-8); }
</style>
