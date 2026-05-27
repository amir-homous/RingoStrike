<template>
  <BaseCard class="goal">
    <p class="caption">Next Goal</p>
    <h3 class="h2">{{ remainingXp }} XP until Level {{ nextLevel }}</h3>
  </BaseCard>
</template>

<script setup>
import { computed } from "vue";
import BaseCard from "@/components/ui/BaseCard.vue";

const props = defineProps({ stats: { type: Object, required: true } });
const remainingXp = computed(() => Math.max(0, (props.stats.next_level_xp || 0) - (props.stats.xp || 0)));
const nextLevel = computed(() => (props.stats.level || 0) + 1);
</script>

<style scoped>
.goal{ background: linear-gradient(180deg, rgba(99,102,241,0.16), rgba(255,255,255,0.04)); }
.goal h3{ margin-top: var(--s-8); }
</style>
