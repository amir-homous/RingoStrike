<template>
  <BaseCard>
    <div class="head"><h2 class="h2">Recent Achievements</h2><span class="caption">Identity milestones</span></div>
    <p v-if="!recent.length" class="caption">Unlock achievements to build your consistency identity.</p>
    <AchievementGrid v-else :items="recent" />
  </BaseCard>
</template>
<script setup>
import { computed } from 'vue';
import BaseCard from '@/components/ui/BaseCard.vue';
import AchievementGrid from './AchievementGrid.vue';
const props = defineProps({achievements:{type:Array,default:()=>[]}})
const recent = computed(()=> props.achievements.filter(a=>a.unlocked).sort((a,b)=>(a.unlocked_at<b.unlocked_at?1:-1)).slice(0,3))
</script>
<style scoped>.head{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px}</style>
