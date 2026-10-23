<template>
  <!-- B35 (D69): an hour and a minute field with Latin digits (EN and FA), checked against the reset. -->
  <div class="timePicker" dir="ltr">
    <div class="timeFields" role="group" :aria-label="t('space.reminderTime.groupLabel')">
      <div v-for="part in PARTS" :key="part" class="timePart">
        <button
          type="button"
          class="timeStep"
          :aria-label="t(`space.reminderTime.${part}Later`)"
          @click="step(part, 1)"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 15l7-7 7 7" /></svg>
        </button>
        <input
          :ref="(el) => (inputs[part] = el)"
          v-model="values[part]"
          class="timeInput"
          :class="{ refused: Boolean(error) }"
          type="text"
          inputmode="numeric"
          maxlength="2"
          autocomplete="off"
          :aria-label="t(`space.reminderTime.${part}Label`)"
          :aria-invalid="error ? 'true' : 'false'"
          :aria-describedby="hintId"
          @input="onInput(part)"
          @blur="values[part] = tidy(part)"
          @keydown.enter.prevent="submit"
          @keydown.up.prevent="step(part, 1)"
          @keydown.down.prevent="step(part, -1)"
        />
        <button
          type="button"
          class="timeStep"
          :aria-label="t(`space.reminderTime.${part}Earlier`)"
          @click="step(part, -1)"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 9l7 7 7-7" /></svg>
        </button>
      </div>
      <span class="timeColon" aria-hidden="true">:</span>
    </div>

    <p :id="hintId" class="timeHint" :class="{ refused: Boolean(error) }" :role="error ? 'alert' : null">
      {{ error ? t(`space.reminderTime.${error === 'invalid' ? 'invalid' : 'afterReset'}`) : t("space.reminderTime.hint") }}
    </p>

    <button type="button" class="timeSet" :disabled="disabled" @click="submit">{{ t("space.reminderTime.set") }}</button>
    <button type="button" class="timeBack" @click="$emit('back')">{{ t("space.reminderTime.backQuick") }}</button>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { latinDigits, pad2, parseTimePart, stepTimePart } from "@/lib/reminderTime";

const props = defineProps({
  hour: { type: String, default: "" },
  minute: { type: String, default: "" },
  // "" | "invalid" | "after_reset", set by the panel after a refused submit.
  error: { type: String, default: "" },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(["set", "back", "edit"]);

const PARTS = ["hour", "minute"];
const { t } = useI18n();
const hintId = `timeHint-${Math.random().toString(36).slice(2, 8)}`;
const values = reactive({ hour: props.hour, minute: props.minute });
const inputs = reactive({});
const error = ref(props.error);
watch(() => props.error, (value) => { error.value = value; });

function tidy(part) {
  const value = parseTimePart(values[part], part === "hour" ? 23 : 59);
  return value === null ? latinDigits(values[part]).replace(/\D/g, "").slice(0, 2) : pad2(value);
}

function onInput(part) {
  values[part] = latinDigits(values[part]).replace(/\D/g, "").slice(0, 2);
  error.value = "";
  emit("edit");
}

function step(part, delta) {
  values[part] = stepTimePart(values[part], part, delta);
  error.value = "";
  emit("edit");
}

function submit() {
  if (props.disabled) return;
  emit("set", { hour: values.hour, minute: values.minute });
}

onMounted(() => inputs.hour?.focus());
</script>

<style scoped>
.timePicker {
  display: grid;
  gap: 10px;
}

.timeFields {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.timePart {
  display: grid;
  justify-items: center;
  gap: 2px;
}

.timePart:nth-of-type(2) {
  order: 3;
}

.timeColon {
  order: 2;
  color: #eef0f5;
  font-size: 30px;
  font-weight: 700;
}

.timeStep {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.timeStep svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.timeInput {
  width: 72px;
  min-height: 48px;
  box-sizing: border-box;
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  background: rgba(11, 14, 20, 0.6);
  color: #eef0f5;
  font: inherit;
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  font-size: 30px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  text-align: center;
}

.timeInput.refused {
  border-color: #ee312a;
}

.timeStep:focus-visible,
.timeInput:focus-visible,
.timeSet:focus-visible,
.timeBack:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

.timeHint {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: 12px;
  line-height: 1.45;
  text-align: center;
}

.timeHint.refused {
  color: #ff8d88;
}

.timeSet {
  min-height: 48px;
  border: 0;
  border-radius: 12px;
  background: #f4d36b;
  color: #1a1608;
  cursor: pointer;
  font: inherit;
  font-size: 15px;
  font-weight: 700;
}

.timeSet:disabled {
  cursor: default;
  opacity: 0.62;
}

.timeBack {
  min-height: 44px;
  border: 0;
  background: transparent;
  color: rgba(255, 255, 255, 0.78);
  cursor: pointer;
  font: inherit;
  font-size: 13px;
}
</style>
