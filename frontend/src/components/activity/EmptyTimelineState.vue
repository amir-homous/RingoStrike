<template>
  <div class="empty stack-8">
    <p class="h2">{{ t("activity.emptyTitle") }}</p>
    <p class="caption">{{ t("activity.emptyText") }}</p>
  </div>
</template>
<script setup>
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>
<style scoped>
.empty{padding:var(--s-12);border:1px dashed rgba(255,255,255,.16);border-radius:var(--r-10);background:rgba(255,255,255,.02)}
</style>
