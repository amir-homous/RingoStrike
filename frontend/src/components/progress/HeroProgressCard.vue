<template>
  <BaseCard class="hero">
    <div class="row">
      <div class="stack-8">
        <p class="caption">Your Progress</p>
        <h2 class="h2">{{ greeting }}</h2>
        <p class="mood">Level {{ stats.level }} • {{ stats.total_points }} total XP</p>
      </div>

      <div class="streak">
        <span aria-hidden="true">🔥</span>
        <div>
          <b>{{ stats.current_streak }}</b>
          <span class="caption">Day Streak</span>
        </div>
      </div>
    </div>

    <XPProgressBar :xp="stats.xp" :next-level-xp="stats.next_level_xp" :progress-percent="stats.progress_percent" />
  </BaseCard>
</template>

<script setup>
import { computed } from "vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import XPProgressBar from "@/components/progress/XPProgressBar.vue";

const props = defineProps({
  userName: { type: String, default: "Player" },
  stats: { type: Object, required: true },
});

const greeting = computed(() => `${props.userName}, keep your momentum up!`);
</script>

<style scoped>
.hero{ display:grid; gap: var(--s-16); }
.row{ display:flex; justify-content:space-between; gap:var(--s-16); flex-wrap:wrap; align-items:flex-start; }
.mood{ margin: 0; color: var(--muted); }
.streak{
  display:inline-flex; gap: var(--s-8); align-items:center;
  padding: 10px 12px; border-radius: var(--r-10);
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.09);
}
.streak b{ display:block; font-size: 20px; line-height: 1; }
</style>
