<template>
  <section class="group stack-8">
    <p class="caption head">{{ label }}</p>
    <ActivityTimelineItem v-for="ev in events" :key="ev.id" :event="ev" />
  </section>
</template>

<script setup>
import ActivityTimelineItem from "@/components/activity/ActivityTimelineItem.vue";
defineProps({ label: { type: String, required: true }, events: { type: Array, default: () => [] } });
</script>

<style scoped>
.group + .group{margin-top:var(--s-16);padding-top:var(--s-12);border-top:1px solid rgba(255,255,255,.08)}
.head{text-transform:uppercase;letter-spacing:.04em}
</style>
