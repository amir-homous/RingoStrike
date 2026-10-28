<template>
  <!-- B37 (D86): the whole line holds its space from the start (never looks cut off); a tap, a
       click or Enter finishes it; reduced motion shows it whole. -->
  <span class="typewriterText" :class="{ typing }" :aria-label="text">
    <span class="fullLine" aria-hidden="true">{{ text }}</span>
    <span class="typedLine" aria-hidden="true">{{ visibleText }}<span v-if="typing" class="cursor"></span></span>
  </span>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from "vue";

const props = defineProps({
  text: { type: String, default: "" },
  speed: { type: Number, default: 18 },
  startDelay: { type: Number, default: 120 },
});

const visibleText = ref("");
const typing = ref(false);

let startTimer = null;
let tickTimer = null;

function prefersReducedMotion() {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

// D86: any tap, click or Enter while a line types finishes it.
function finishOnInput(event) {
  if (!typing.value) return;
  if (event.type === "keydown" && event.key !== "Enter") return;
  showFullText(props.text);
}

function listen(on) {
  if (typeof window === "undefined") return;
  const method = on ? "addEventListener" : "removeEventListener";
  window[method]("pointerdown", finishOnInput, true);
  window[method]("keydown", finishOnInput, true);
}

function clearTimers() {
  if (startTimer) {
    globalThis.clearTimeout(startTimer);
    startTimer = null;
  }

  if (tickTimer) {
    globalThis.clearInterval(tickTimer);
    tickTimer = null;
  }
}

function showFullText(value) {
  clearTimers();
  visibleText.value = value;
  typing.value = false;
  listen(false);
}

function play(value) {
  const nextText = String(value || "");

  if (!nextText || typeof window === "undefined" || prefersReducedMotion()) {
    showFullText(nextText);
    return;
  }

  clearTimers();
  visibleText.value = "";
  typing.value = true;
  listen(true);

  const characters = Array.from(nextText);
  let index = 0;

  startTimer = window.setTimeout(() => {
    tickTimer = window.setInterval(() => {
      index += 1;
      visibleText.value = characters.slice(0, index).join("");

      if (index >= characters.length) {
        showFullText(nextText);
      }
    }, Math.max(8, props.speed));
  }, Math.max(0, props.startDelay));
}

watch(
  () => props.text,
  (value) => play(value),
  { immediate: true },
);

onBeforeUnmount(() => {
  clearTimers();
  listen(false);
});
</script>

<style scoped>
/* Both lines sit in one grid cell: the hidden full line sets the size, the typed line draws on it. */
.typewriterText {
  display: inline-grid;
}

.fullLine,
.typedLine {
  grid-area: 1 / 1;
}

.fullLine {
  visibility: hidden;
}

.cursor {
  display: inline-block;
  width: 0.08em;
  height: 1em;
  margin-inline-start: 0.08em;
  vertical-align: -0.12em;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.7;
  animation: cursorBlink 850ms steps(2, end) infinite;
}

@keyframes cursorBlink {
  50% {
    opacity: 0.16;
  }
}

@media (prefers-reduced-motion: reduce) {
  .cursor {
    animation: none;
  }
}
</style>