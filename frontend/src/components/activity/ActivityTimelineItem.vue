<template>
  <article class="item">
    <span class="dot" :class="`t-${event.type}`" aria-hidden="true">{{ icon }}</span>
    <div class="content">
      <p class="title">{{ event.title }}</p>
      <p v-if="event.subtitle" class="subtitle">{{ event.subtitle }}</p>
    </div>
  </article>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({ event: { type: Object, required: true } });

const icon = computed(() => {
  const map = { checkin: "✓", streak: "🔥", level_up: "🏁" };
  return map[props.event.type] || "•";
});
</script>

<style scoped>
.item{display:grid;grid-template-columns:26px 1fr;gap:var(--s-12);align-items:flex-start;padding:10px 0}
.dot{width:26px;height:26px;border-radius:999px;border:1px solid rgba(255,255,255,.16);display:grid;place-items:center;background:rgba(255,255,255,.04);font-size:12px}
.dot.t-checkin{border-color:rgba(56,189,248,.35)}
.dot.t-streak{border-color:rgba(245,158,11,.4)}
.dot.t-level_up{border-color:rgba(99,102,241,.45)}
.title{margin:0;font-weight:620}
.subtitle{margin:2px 0 0;color:var(--muted2);font-size:var(--cap)}
</style>
