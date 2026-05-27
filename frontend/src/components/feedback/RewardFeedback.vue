<template>
  <transition-group name="float" tag="div" class="feedbackStack">
    <div v-for="item in items" :key="item.id" class="feedbackItem" :class="item.type">
      {{ item.text }}
    </div>
  </transition-group>
</template>

<script setup>
defineProps({ items: { type: Array, default: () => [] } });
</script>

<style scoped>
.feedbackStack{position:fixed;right:18px;bottom:18px;display:grid;gap:8px;z-index:30}
.feedbackItem{padding:8px 12px;border-radius:10px;border:1px solid var(--border);background:rgba(17,19,26,.8);backdrop-filter: blur(8px);font-weight:650;font-size:13px}
.feedbackItem.xp{border-color:rgba(99,102,241,.45)}
.feedbackItem.streak{border-color:rgba(245,158,11,.4)}
.feedbackItem.level{border-color:rgba(34,197,94,.45)}
.float-enter-active,.float-leave-active{transition: all .35s ease}
.float-enter-from,.float-leave-to{opacity:0;transform: translateY(10px)}
</style>
