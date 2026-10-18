<template>
  <section class="detailsRow" :class="{ open }">
    <button
      :id="`${rowId}-toggle`"
      type="button"
      class="detailsToggle"
      :aria-expanded="open ? 'true' : 'false'"
      :aria-controls="`${rowId}-region`"
      @click="$emit('toggle')"
    >
      <span class="detailsTitle">{{ title }}</span>
      <small v-if="meta" class="detailsMeta">{{ meta }}</small>
      <span class="chevron" aria-hidden="true"></span>
    </button>
    <div
      v-if="open"
      :id="`${rowId}-region`"
      class="detailsRegion"
      role="region"
      :aria-labelledby="`${rowId}-toggle`"
    >
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  rowId: { type: String, required: true },
  title: { type: String, required: true },
  meta: { type: String, default: "" },
  open: { type: Boolean, default: false },
});

defineEmits(["toggle"]);
</script>

<style scoped>
.detailsRow {
  display: grid;
  min-width: 0;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.detailsRow.open {
  border-color: rgba(110, 229, 255, 0.16);
}

.detailsToggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-height: 46px;
  padding: 10px 12px;
  border: 0;
  border-radius: inherit;
  color: rgba(255, 255, 255, 0.88);
  background: transparent;
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 850;
  text-align: start;
}

.detailsToggle:focus-visible {
  outline: 2px solid rgba(110, 229, 255, 0.6);
  outline-offset: -2px;
}

.detailsTitle {
  flex: 1 1 auto;
  min-width: 0;
}

.detailsMeta {
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.72rem;
  font-weight: 750;
}

.chevron {
  width: 8px;
  height: 8px;
  /* Physical borders so the chevron points down in both LTR and RTL. */
  border-right: 2px solid rgba(255, 255, 255, 0.6);
  border-bottom: 2px solid rgba(255, 255, 255, 0.6);
  transform: rotate(45deg);
  transition: transform 160ms ease;
}

.detailsRow.open .chevron {
  transform: rotate(225deg);
}

.detailsRegion {
  display: grid;
  gap: 10px;
  min-width: 0;
  padding: 0 10px 10px;
}

@media (prefers-reduced-motion: reduce) {
  .chevron {
    transition: none;
  }
}
</style>
