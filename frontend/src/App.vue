<template>
  <router-view />
  <AppFooter v-if="!route.meta?.hideFooter" />
</template>

<script setup>
import { useRoute } from "vue-router";
import AppFooter from "@/components/ui/AppFooter.vue";

const route = useRoute();
</script>

<style>
.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content-area {
  flex: 1;
}
</style>