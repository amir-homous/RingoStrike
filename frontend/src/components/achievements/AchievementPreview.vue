<template>
  <BaseCard>
    <div class="head">
      <div>
        <h2 class="h2">Recent Achievements</h2>
        <p class="caption sub">Progress identity milestones</p>
      </div>
      <div class="summary">
        <b>{{ unlockedCount }}</b>
        <span class="caption">Unlocked</span>
      </div>
    </div>

    <p v-if="!achievements.length" class="caption">No achievements available yet.</p>
    <AchievementGrid v-else :items="prioritized" />
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue';
import BaseCard from '@/components/ui/BaseCard.vue';
import AchievementGrid from './AchievementGrid.vue';

const props = defineProps({ achievements: { type: Array, default: () => [] } });

const unlockedCount = computed(() => props.achievements.filter((a) => a.unlocked).length);
const prioritized = computed(() =>
  [...props.achievements]
    .sort((a, b) => {
      if (a.unlocked !== b.unlocked) return a.unlocked ? -1 : 1;
      const ad = a.unlocked_at || '';
      const bd = b.unlocked_at || '';
      return ad < bd ? 1 : -1;
    })
    .slice(0, 6)
);
</script>

<style scoped>
.head{display:flex;justify-content:space-between;align-items:flex-start;gap:var(--s-12);margin-bottom:var(--s-12);flex-wrap:wrap}
.sub{margin-top:4px}
.summary{display:grid;justify-items:end}
.summary b{font-size:22px;line-height:1}
</style>
