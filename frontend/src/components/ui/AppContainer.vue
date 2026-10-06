<template>
  <div class="app" :class="{ appWide: isWideLayout }">
    <div class="container" :class="{ containerWide: isWideLayout }">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const isWideLayout = computed(() => route.meta.layout === "wide");
</script>

<style scoped>
.app{
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: var(--s-24) var(--px);
  background: var(--bg);
  overflow-x: clip;
}
.appWide{
  padding-inline: clamp(16px, 2vw, 32px);
}
.container{
  width: 100%;
  min-width: 0;
  max-width: var(--container);
  margin: 0 auto;
}
.containerWide{
  max-width: none;
}
</style>
