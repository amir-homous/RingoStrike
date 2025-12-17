<template>
  <div v-if="loading" class="box">
    <div class="row">
      <Spinner />
      <div class="txt">
        <div class="title">{{ loadingTitle }}</div>
        <div class="caption">{{ loadingText }}</div>
      </div>
    </div>
    <div class="skwrap">
      <SkeletonBlock h="14px" w="40%" />
      <SkeletonBlock h="14px" w="70%" />
      <SkeletonBlock h="14px" w="55%" />
    </div>
  </div>

  <div v-else-if="error" class="box">
    <div class="title">{{ errorTitle }}</div>
    <div class="caption">{{ errorText }}</div>
    <div class="actions">
      <BaseButton variant="secondary" @click="$emit('retry')">Retry</BaseButton>
    </div>
  </div>

  <div v-else-if="empty" class="box">
    <div class="title">{{ emptyTitle }}</div>
    <div class="caption">{{ emptyText }}</div>
    <div v-if="$slots.action" class="actions">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
import BaseButton from './BaseButton.vue'
import Spinner from './Spinner.vue'
import SkeletonBlock from './SkeletonBlock.vue'

defineProps({
  loading: { type: Boolean, default: false },
  empty: { type: Boolean, default: false },
  error: { type: Boolean, default: false },

  loadingTitle: { type: String, default: 'Loading…' },
  loadingText: { type: String, default: 'Please wait a moment.' },

  emptyTitle: { type: String, default: 'Nothing here yet' },
  emptyText: { type: String, default: 'Try again later or take an action.' },

  errorTitle: { type: String, default: 'Something went wrong' },
  errorText: { type: String, default: 'We couldn’t load this data. Please try again.' }
})

defineEmits(['retry'])
</script>

<style scoped>
.box{
  border: 1px dashed rgba(255,255,255,0.18);
  border-radius: var(--r-12);
  padding: var(--s-16);
  background: rgba(255,255,255,0.03);
}
.row{ display:flex; gap: var(--s-12); align-items:flex-start; }
.txt{ display:grid; gap: var(--s-4); }
.title{ font-weight: 700; }
.actions{ margin-top: var(--s-12); display:flex; gap: var(--s-8); }
.skwrap{ margin-top: var(--s-12); display:grid; gap: var(--s-8); }
.caption{ font-size: var(--cap); color: var(--muted2); }
</style>
