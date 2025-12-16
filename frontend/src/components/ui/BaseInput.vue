<template>
  <div class="wrap">
    <label v-if="label" class="label">{{ label }}</label>
    <input
      class="input"
      :class="{ error: !!error }"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <div v-if="error" class="err">{{ error }}</div>
    <div v-else-if="hint" class="hint">{{ hint }}</div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false }
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.wrap{ display: grid; gap: var(--s-8); }
.label{ font-size: var(--cap); color: var(--muted); }
.input{
  height: 42px;
  padding: 0 var(--s-12);
  border-radius: var(--r-10);
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.92);
}
.input:focus{ outline: none; box-shadow: var(--focus); border-color: rgba(99,102,241,0.55); }
.input:disabled{ opacity: 0.6; cursor: not-allowed; }
.input.error{ border-color: rgba(239,68,68,0.55); box-shadow: 0 0 0 3px rgba(239,68,68,0.20); }
.err{ font-size: var(--cap); color: rgba(239,68,68,0.9); }
.hint{ font-size: var(--cap); color: var(--muted2); }
</style>
