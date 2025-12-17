<template>
    <button class="btn" :class="[`v-${variant}`, { loading: props.loading }]" :disabled="disabled || props.loading"
        type="button" @click="onClick">
        <span v-if="props.loading" class="spin" aria-hidden="true">
            <Spinner />
        </span>
        <span class="label">
            <slot />
        </span>
    </button>
</template>

<script setup>
import Spinner from './Spinner.vue'

const props = defineProps({
    variant: { type: String, default: 'primary' }, // primary | secondary | danger
    loading: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['click'])

function onClick(e) {
    if (props.disabled || props.loading) return
    emit('click', e)
}
</script>

<style scoped>
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--s-8);
    min-height: 42px;
    padding: 0 var(--s-16);
    border-radius: var(--r-10);
    border: 1px solid var(--border);
    color: rgba(255, 255, 255, 0.92);
    cursor: pointer;
    user-select: none;
    font-weight: 650;
    letter-spacing: 0.01em;
    transition: transform 120ms ease, background 120ms ease, border-color 120ms ease, opacity 120ms ease;
}

.btn:focus-visible {
    outline: none;
    box-shadow: var(--focus);
}

.btn:active {
    transform: translateY(1px);
}

.btn:disabled {
    opacity: 0.55;
    cursor: not-allowed;
    transform: none;
}

.v-primary {
    background: rgba(99, 102, 241, 0.26);
    border-color: rgba(99, 102, 241, 0.45);
}

.v-primary:hover {
    background: rgba(99, 102, 241, 0.34);
}

.v-secondary {
    background: rgba(255, 255, 255, 0.07);
}

.v-secondary:hover {
    background: rgba(255, 255, 255, 0.10);
}

.v-danger {
    background: rgba(239, 68, 68, 0.18);
    border-color: rgba(239, 68, 68, 0.35);
}

.v-danger:hover {
    background: rgba(239, 68, 68, 0.26);
}

.spin {
    display: inline-flex;
    align-items: center;
}

.label {
    display: inline-flex;
    align-items: center;
}
</style>
