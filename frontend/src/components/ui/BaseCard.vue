<template>
  <section class="card" :class="{ padded }">
    <slot />
  </section>
</template>

<script setup>
defineProps({
  padded: { type: Boolean, default: true }
})
</script>

<style scoped>
.card{
  background: linear-gradient(180deg, var(--card2), var(--card));
  border: 1px solid var(--border);
  border-radius: var(--r-12);
  box-shadow: var(--shadow);
}
.card.padded{
  padding: var(--s-16);
}
</style>
