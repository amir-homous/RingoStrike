<template>
  <router-view />
  <AppFooter />
</template>

<script setup>
import AppFooter from '@/components/ui/AppFooter.vue'
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
