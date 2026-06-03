<template><BaseCard><div class="head"><h2 class="h2">{{ t("profileComponents.consistency") }}</h2><span class="caption">{{ t("profileComponents.lastMonths") }}</span></div><div class="grid"><button v-for="d in cells" :key="d.date" class="cell" :class="`i-${d.i}`" :title="t('profileComponents.cellTitle', { date: d.date, count: d.count })"/></div></BaseCard></template>
<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import BaseCard from "@/components/ui/BaseCard.vue";

const props = defineProps({
  days: {
    type: Array,
    default: () => [],
  },
});

const { t } = useI18n();

const by = computed(() => {
  const map = {};

  for (const item of props.days) {
    // PUBLIC PROFILE FORMAT
    if (typeof item === "string") {
      map[item] = (map[item] || 0) + 1;
      continue;
    }

    // DASHBOARD FORMAT
    if (item?.date) {
      map[item.date] = item.count || 0;
    }
  }

  return map;
});

const cells = computed(() => {
  const out = [];

  const now = new Date();

  for (let i = 139; i >= 0; i--) {
    const d = new Date(now);

    d.setDate(now.getDate() - i);

    const key = d.toISOString().slice(0, 10);

    const c = by.value[key] || 0;

    const ii =
      c >= 4
        ? 4
        : c >= 3
        ? 3
        : c >= 2
        ? 2
        : c >= 1
        ? 1
        : 0;

    out.push({
      date: key,
      count: c,
      i: ii,
    });
  }

  return out;
});
</script>
<style scoped>.head{display:flex;justify-content:space-between;gap:10px;margin-bottom:10px}.grid{display:grid;grid-template-columns:repeat(28,1fr);gap:4px}.cell{aspect-ratio:1;border:0;border-radius:4px;background:rgba(255,255,255,.05)}.i-1{background:rgba(99,102,241,.32)}.i-2{background:rgba(99,102,241,.48)}.i-3{background:rgba(56,189,248,.56)}.i-4{background:rgba(56,189,248,.75)}@media(max-width:640px){.head{align-items:flex-start;flex-direction:column}.grid{grid-template-columns:repeat(14,1fr);gap:5px}.cell{border-radius:5px}}@media(max-width:380px){.grid{gap:4px}}</style>
