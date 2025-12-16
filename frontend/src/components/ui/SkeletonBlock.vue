<template>
  <div class="sk" :style="{ height: h, width: w }" />
</template>

<script setup>
defineProps({
  h: { type: String, default: '14px' },
  w: { type: String, default: '100%' }
})
</script>

<style scoped>
.sk{
  border-radius: 10px;
  background: linear-gradient(
    90deg,
    rgba(255,255,255,0.06),
    rgba(255,255,255,0.12),
    rgba(255,255,255,0.06)
  );
  background-size: 200% 100%;
  animation: shimmer 1000ms linear infinite;
}
@keyframes shimmer{
  0%{ background-position: 0% 0; }
  100%{ background-position: 200% 0; }
}
</style>
