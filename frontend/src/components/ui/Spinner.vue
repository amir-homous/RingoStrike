<template>
  <span class="spinner" />
</template>

<style scoped>
.spinner{
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 2px solid rgba(255,255,255,0.25);
  border-top-color: rgba(255,255,255,0.85);
  animation: spin 800ms linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
