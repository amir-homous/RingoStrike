<template>
  <TransitionGroup name="toast" tag="div" class="toastStack">
    <div v-for="item in items" :key="item.id" class="toast" :class="item.type">
      {{ item.text }}
    </div>
  </TransitionGroup>
</template>

<script setup>
defineProps({ items: { type: Array, default: () => [] } });
</script>

<style scoped>
.toastStack{position:fixed;right:20px;bottom:20px;display:grid;gap:8px;z-index:30}
.toast{padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.18);background:rgba(13,17,24,.82);backdrop-filter:blur(4px);font-weight:650}
.toast.success{color:rgba(167,243,208,.95);border-color:rgba(16,185,129,.35)}
.toast.level{color:rgba(199,210,254,.95);border-color:rgba(99,102,241,.4)}
.toast-enter-active,.toast-leave-active{transition:all .32s ease}
.toast-enter-from,.toast-leave-to{opacity:0;transform:translateY(10px)}
</style>
