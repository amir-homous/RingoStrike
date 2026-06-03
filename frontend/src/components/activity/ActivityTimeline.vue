<template>
  <BaseCard>
    <div class="head"><h2 class="h2">{{ t("activity.title") }}</h2><span class="caption">{{ t("activity.subtitle") }}</span></div>
    <div class="stack-8 body">
      <EmptyTimelineState v-if="!events.length && !loading" />
      <template v-else>
        <TimelineDayGroup v-for="g in grouped" :key="g.key" :label="g.label" :events="g.events" />
      </template>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import BaseCard from "@/components/ui/BaseCard.vue";
import TimelineDayGroup from "@/components/activity/TimelineDayGroup.vue";
import EmptyTimelineState from "@/components/activity/EmptyTimelineState.vue";

const props = defineProps({ events: { type: Array, default: () => [] }, loading: { type: Boolean, default: false } });
const { t } = useI18n();

const grouped = computed(() => {
  const m = new Map();
  const today = new Date();
  today.setHours(0,0,0,0);
  const y = new Date(today); y.setDate(y.getDate()-1);
  for (const ev of props.events) {
    const d = new Date(ev.created_at);
    const day = new Date(d); day.setHours(0,0,0,0);
    const key = day.toISOString().slice(0,10);
    let label = d.toLocaleDateString();
    if (day.getTime() === today.getTime()) label = t("activity.today");
    else if (day.getTime() === y.getTime()) label = t("activity.yesterday");
    if (!m.has(key)) m.set(key, { key, label, events: [] });
    m.get(key).events.push(ev);
  }
  return [...m.values()].sort((a,b)=> (a.key < b.key ? 1 : -1));
});
</script>

<style scoped>
.head{display:flex;justify-content:space-between;gap:var(--s-8);align-items:center;flex-wrap:wrap}
.body{margin-top:var(--s-12)}
</style>
