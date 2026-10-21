<template>
  <section class="missionFlow" :aria-labelledby="headingId">
    <!-- Flow A, step 1: focus with a count-up timer (never a countdown). -->
    <template v-if="step === 'focus'">
      <div class="flowBody">
      <header class="flowHead">
        <span class="flowKicker">{{ t("space.missionAction.focusKicker") }}</span>
        <h3 :id="headingId" ref="heading" tabindex="-1">{{ zoneTitle }}</h3>
      </header>

      <div class="flowTimer" role="timer" :aria-label="t('space.missionAction.timerLabel')">
        <strong><bdi dir="ltr">{{ clock }}</bdi></strong>
        <small>{{ t("space.missionAction.timerCaption") }}</small>
      </div>

      <p class="flowRingo">{{ t("space.missionAction.focusRingo") }}</p>

      <div class="flowMission">
        <span class="flowLabel">{{ t("space.missionAction.mainMission") }}</span>
        <strong>{{ mission?.title }}</strong>
        <ul v-if="microActions.length" class="flowMicro">
          <li v-for="(item, index) in microActions" :key="index">
            <label>
              <input v-model="checked[index]" type="checkbox" />
              <span>{{ item }}</span>
            </label>
          </li>
        </ul>
      </div>

      <label class="flowField">
        <span>{{ t("space.missionAction.noteLabel") }}</span>
        <textarea v-model="note" :maxlength="NOTE_MAX" rows="2"></textarea>
      </label>
      </div>

      <div class="flowActions">
      <button type="button" class="flowPrimary" @click="finishFocus">{{ t("space.missionAction.done") }}</button>
      <button type="button" class="flowQuiet" @click="cancelFocus">{{ t("space.missionAction.cancel") }}</button>
      <p class="flowFooter">{{ t("space.missionAction.cancelCaption") }}</p>
      </div>
    </template>

    <!-- Flow A, step 2 (check-out) and Flow B (already did it): optional questions, Save always on. -->
    <template v-else>
      <div class="flowBody">
      <header class="flowHead">
        <span class="flowKicker">{{ step === "earlier" ? t("space.missionAction.earlierKicker") : t("space.missionAction.focusKicker") }}</span>
        <h3 :id="headingId" ref="heading" tabindex="-1">
          {{ step === "earlier" ? t("space.missionAction.earlierRingo") : t("space.missionAction.checkoutRingo") }}
        </h3>
        <button v-if="step === 'earlier'" type="button" class="flowClose" :disabled="submitting" @click="$emit('close')">
          {{ t("space.missionAction.close") }}
        </button>
      </header>

      <p v-if="step === 'checkout'" class="flowPill">
        <span>{{ t("space.missionAction.durationLabel") }}</span>
        <strong><bdi dir="ltr">{{ durationClock }}</bdi></strong>
      </p>
      <p v-else class="flowMissionLine">
        <span class="flowLabel">{{ t("space.missionAction.mainMission") }}</span>
        <strong>{{ mission?.title }}</strong>
      </p>

      <fieldset v-if="step === 'earlier'" class="flowGroup">
        <legend>{{ t("space.missionAction.whenQuestion") }}</legend>
        <div class="flowChips">
          <button
            v-for="slot in SLOTS"
            :key="slot"
            type="button"
            class="flowChip"
            :class="{ selected: when === slot }"
            :aria-pressed="when === slot ? 'true' : 'false'"
            :disabled="!slotIsEnabled(slot)"
            @click="when = when === slot ? '' : slot"
          >
            <svg v-if="when === slot" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.2 8.4l3 3 6.6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg>
            {{ t(`space.missionAction.slots.${slot}`) }}
          </button>
        </div>
        <label v-if="when === 'exact'" class="flowField flowTime">
          <span>{{ t("space.missionAction.exactTimeLabel") }}</span>
          <input v-model="exactTime" type="time" dir="ltr" />
        </label>
      </fieldset>

      <fieldset class="flowGroup">
        <legend>{{ t("space.missionAction.whereQuestion") }}</legend>
        <div class="flowChips">
          <button
            v-for="key in PLACE_KEYS"
            :key="key"
            type="button"
            class="flowChip"
            :class="{ selected: place === key }"
            :aria-pressed="place === key ? 'true' : 'false'"
            @click="place = place === key ? '' : key"
          >
            <svg v-if="place === key" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.2 8.4l3 3 6.6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg>
            {{ t(`space.missionAction.places.${key}`) }}
          </button>
        </div>
        <p v-if="remembered && place === remembered.key" class="flowRemember">
          {{ t("space.missionAction.rememberedPlace", { place: placeName(remembered) }) }}
        </p>
        <label v-if="place === 'other'" class="flowField">
          <span>{{ t("space.missionAction.placeOtherLabel") }}</span>
          <input v-model="placeLabel" type="text" :maxlength="PLACE_LABEL_MAX" />
        </label>
      </fieldset>

      <fieldset class="flowGroup">
        <legend>{{ t("space.missionAction.feelQuestion") }}</legend>
        <div class="flowChips">
          <button
            v-for="key in FEELING_KEYS"
            :key="key"
            type="button"
            class="flowChip"
            :class="{ selected: feeling === key }"
            :aria-pressed="feeling === key ? 'true' : 'false'"
            @click="feeling = feeling === key ? '' : key"
          >
            <svg v-if="feeling === key" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.2 8.4l3 3 6.6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg>
            {{ t(`space.missionAction.feelings.${key}`) }}
          </button>
        </div>
      </fieldset>

      <label class="flowField">
        <span>{{ t("space.missionAction.noteLabel") }}</span>
        <textarea v-model="note" :maxlength="NOTE_MAX" rows="2"></textarea>
      </label>
      </div>

      <!-- The save area stays at the bottom of the panel or sheet; the body above scrolls. -->
      <div class="flowActions">
      <p v-if="error" class="flowError" role="alert">{{ t("space.missionAction.saveError") }}</p>

      <button type="button" class="flowPrimary" :disabled="submitting" :aria-busy="submitting ? 'true' : null" @click="save(false)">
        <span v-if="submitting" class="flowSpinner" aria-hidden="true"></span>
        {{ submitting ? t("space.missionAction.saving") : t("space.missionAction.save") }}
      </button>
      <button v-if="step === 'checkout'" type="button" class="flowQuiet" :disabled="submitting" @click="save(true)">
        {{ t("space.missionAction.saveWithoutAnswers") }}
      </button>
      <p class="flowFooter">
        {{ step === "earlier" ? t("space.missionAction.optionalFooter") : t("space.missionAction.privateFooter") }}
      </p>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import { formatClock } from "@/lib/i18nNumbers";
import {
  FEELING_KEYS,
  NOTE_MAX,
  PLACE_KEYS,
  PLACE_LABEL_MAX,
  buildContext,
  performedAtWindow,
  readFocusStart,
  readLastPlace,
  slotEnabled,
  slotPerformedAt,
  writeFocusStart,
  writeLastPlace,
} from "@/lib/missionActionFlow";

const SLOTS = ["morning", "noon", "afternoon", "evening", "exact"];

const props = defineProps({
  // "focus" (Do it now) or "earlier" (Already did it).
  mode: { type: String, default: "focus" },
  mission: { type: Object, required: true },
  zoneTitle: { type: String, default: "" },
  pathKey: { type: String, default: "" },
  userKey: { type: String, default: "" },
  submitting: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

const emit = defineEmits(["save", "cancel", "close"]);

const { t, locale } = useI18n();
const headingId = `missionFlowHeading-${Math.random().toString(36).slice(2, 8)}`;
const heading = ref(null);

const step = ref(props.mode === "earlier" ? "earlier" : "focus");
const startedAt = ref(null);
const now = ref(Date.now());
const durationSeconds = ref(0);
const note = ref("");
const checked = ref([]);
const place = ref("");
const placeLabel = ref("");
const feeling = ref("");
const when = ref("");
const exactTime = ref("");
const remembered = ref(null);
const ringoDay = ref(null);
const ringoDayFetchedAt = ref(Date.now());
let ticker = null;

// The mission's micro-actions, when the mission has any (local only, never sent).
const microActions = computed(() => {
  const items = props.mission?.microActions || props.mission?.micro_actions || [];
  return Array.isArray(items) ? items.filter((item) => typeof item === "string" && item.trim()) : [];
});

const elapsedSeconds = computed(() => (startedAt.value ? Math.max(0, Math.floor((now.value - startedAt.value) / 1000)) : 0));
const clock = computed(() => formatClock(elapsedSeconds.value, locale.value));
const durationClock = computed(() => formatClock(durationSeconds.value, locale.value));

const window_ = computed(() => performedAtWindow(ringoDay.value, { fetchedAt: ringoDayFetchedAt.value, clientNow: now.value }));

function slotIsEnabled(slot) {
  return slotEnabled(slot, { window: window_.value });
}

function placeName(value) {
  if (!value) return "";
  return value.key === "other" && value.label ? value.label : t(`space.missionAction.places.${value.key}`);
}

function focusHeading() {
  nextTick(() => heading.value?.focus({ preventScroll: true }));
}

function startTicker() {
  stopTicker();
  ticker = setInterval(() => { now.value = Date.now(); }, 1000);
}

function stopTicker() {
  if (ticker) clearInterval(ticker);
  ticker = null;
}

function finishFocus() {
  durationSeconds.value = Math.max(1, elapsedSeconds.value);
  step.value = "checkout";
  focusHeading();
}

function cancelFocus() {
  writeFocusStart(props.userKey, props.mission?.id, null);
  stopTicker();
  emit("cancel");
}

function save(withoutAnswers) {
  if (props.submitting) return;
  const earlier = step.value === "earlier";
  const answers = withoutAnswers ? {} : {
    place: place.value,
    placeLabel: placeLabel.value,
    feeling: feeling.value,
    note: note.value,
  };
  const body = buildContext({
    mode: earlier ? "earlier" : "now",
    durationSeconds: earlier ? null : durationSeconds.value,
    performedAt: earlier && when.value ? slotPerformedAt(when.value, { exactTime: exactTime.value, window: window_.value }) : null,
    ...answers,
  });
  if (!withoutAnswers && place.value) writeLastPlace(props.userKey, props.pathKey, place.value, placeLabel.value);
  emit("save", body);
}

async function loadRingoDay() {
  try {
    const { data } = await api.get("/me/ringo/today");
    ringoDay.value = data?.ringo_day || null;
    ringoDayFetchedAt.value = Date.now();
  } catch {
    ringoDay.value = null;
  }
}

watch(when, (value) => {
  if (value === "exact" && !exactTime.value) {
    const current = new Date();
    exactTime.value = `${String(current.getHours()).padStart(2, "0")}:${String(current.getMinutes()).padStart(2, "0")}`;
  }
});

onMounted(() => {
  remembered.value = readLastPlace(props.userKey, props.pathKey);
  if (remembered.value) {
    place.value = remembered.value.key;
    placeLabel.value = remembered.value.label || "";
  }
  if (step.value === "focus") {
    // The start time is a convenience: a reload resumes the same timer.
    const saved = readFocusStart(props.userKey, props.mission?.id);
    startedAt.value = saved || Date.now();
    if (!saved) writeFocusStart(props.userKey, props.mission?.id, startedAt.value);
    now.value = Date.now();
  } else {
    loadRingoDay();
  }
  startTicker();
  focusHeading();
});

onUnmounted(stopTicker);

defineExpose({ clearTimer: () => writeFocusStart(props.userKey, props.mission?.id, null) });
</script>

<style scoped>
/* The flow fills the panel (or sheet): the body scrolls, the save area stays at the bottom. */
.missionFlow {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  min-width: 0;
  min-height: 0;
  height: 100%;
}

.flowBody {
  display: grid;
  align-content: start;
  gap: 12px;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 2px 3px 12px 2px;
  scrollbar-width: thin;
}

.flowActions {
  display: grid;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 -12px 16px -12px rgba(0, 0, 0, 0.45);
}

.flowHead {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 4px 10px;
  align-items: start;
}

.flowKicker,
.flowLabel {
  color: rgba(110, 229, 255, 0.72);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.flowHead h3 {
  grid-column: 1;
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.02rem;
  line-height: 1.45;
}

.flowHead h3:focus {
  outline: none;
}

.flowClose {
  grid-column: 2;
  grid-row: 1 / span 2;
  min-height: 44px;
  padding: 6px 12px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  font: inherit;
  font-size: 0.8rem;
  font-weight: 800;
}

.flowTimer {
  display: grid;
  justify-items: center;
  gap: 4px;
  padding: 16px 10px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.038);
  border: 1px solid rgba(110, 229, 255, 0.13);
}

.flowTimer strong {
  color: #f7e3a1;
  font-size: 2.6rem;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}

.flowTimer small,
.flowFooter,
.flowRemember {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.74rem;
  line-height: 1.5;
}

.flowRingo {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.84rem;
  line-height: 1.55;
}

.flowMission,
.flowMissionLine {
  display: grid;
  gap: 4px;
  margin: 0;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.flowMission strong,
.flowMissionLine strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.9rem;
}

.flowMicro {
  display: grid;
  gap: 6px;
  margin: 6px 0 0;
  padding: 0;
  list-style: none;
}

.flowMicro label {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.82rem;
}

.flowField {
  display: grid;
  gap: 6px;
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.78rem;
  font-weight: 800;
}

.flowField textarea,
.flowField input {
  width: 100%;
  min-height: 44px;
  padding: 9px 11px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.92);
  background: rgba(5, 10, 18, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.12);
  font: inherit;
  font-size: 0.86rem;
  resize: vertical;
}

.flowTime input {
  max-width: 160px;
}

.flowGroup {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  border: 0;
}

.flowGroup legend {
  margin-bottom: 8px;
  padding: 0;
  color: rgba(255, 255, 255, 0.86);
  font-size: 0.86rem;
  font-weight: 800;
}

.flowChips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.flowChip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 44px;
  padding: 6px 12px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  cursor: pointer;
  font: inherit;
  font-size: 0.8rem;
  font-weight: 800;
}

.flowChip svg {
  width: 14px;
  height: 14px;
}

.flowChip.selected {
  color: rgba(255, 255, 255, 0.96);
  background: rgba(110, 229, 255, 0.16);
  border-color: rgba(110, 229, 255, 0.6);
}

.flowChip:disabled {
  cursor: default;
  opacity: 0.45;
}

.flowPrimary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 52px;
  border: 0;
  border-radius: 14px;
  color: #1a1406;
  background: #f7d774;
  cursor: pointer;
  font: inherit;
  font-size: 16px;
  font-weight: 800;
}

.flowQuiet {
  width: 100%;
  min-height: 44px;
  border: 0;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.72);
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 0.86rem;
  font-weight: 800;
}

.flowPrimary:disabled,
.flowQuiet:disabled,
.flowClose:disabled {
  cursor: default;
  opacity: 0.6;
}

.flowChip:focus-visible,
.flowPrimary:focus-visible,
.flowQuiet:focus-visible,
.flowClose:focus-visible,
.flowField textarea:focus-visible,
.flowField input:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

.flowPill {
  display: inline-flex;
  justify-self: start;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 6px 12px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(247, 215, 116, 0.1);
  border: 1px solid rgba(247, 215, 116, 0.24);
  font-size: 0.78rem;
  font-weight: 800;
}

.flowPill strong {
  color: #f7e3a1;
  font-variant-numeric: tabular-nums;
}

.flowError {
  margin: 0;
  padding: 8px 10px;
  border-radius: 12px;
  color: rgba(255, 233, 196, 0.92);
  background: rgba(247, 215, 116, 0.08);
  border: 1px solid rgba(247, 215, 116, 0.22);
  font-size: 0.8rem;
}

.flowSpinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(26, 20, 6, 0.3);
  border-top-color: #1a1406;
  border-radius: 50%;
  animation: flowSpin 0.8s linear infinite;
}

@keyframes flowSpin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .flowSpinner {
    animation: none;
  }
}
</style>
