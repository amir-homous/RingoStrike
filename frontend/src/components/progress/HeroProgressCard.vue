<template>
  <BaseCard class="hero">
    <div class="row">
      <div class="stack-8">
        <p class="caption">{{ t("progress.yourProgress") }}</p>
        <h2 class="h2">{{ greeting }}</h2>
        <p class="mood">{{ t("progress.totalXpLine", { level: stats.level, xp: stats.total_points }) }}</p>
      </div>

      <div class="streak">
        <span aria-hidden="true">🔥</span>
        <div>
          <b>{{ stats.current_streak }}</b>
          <span class="caption">{{ t("progress.dayStreak") }}</span>
        </div>
      </div>
    </div>

    <XPProgressBar :xp="stats.xp" :next-level-xp="stats.next_level_xp" :progress-percent="stats.progress_percent" :animate-pulse="animatePulse" />
  </BaseCard>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import BaseCard from "@/components/ui/BaseCard.vue";
import XPProgressBar from "@/components/progress/XPProgressBar.vue";

const props = defineProps({
  userName: { type: String, default: "Player" },
  stats: { type: Object, required: true },
  animatePulse: { type: Boolean, default: false },
});

const { t } = useI18n();

const greeting = computed(() => t("progress.greeting", { name: props.userName }));
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
