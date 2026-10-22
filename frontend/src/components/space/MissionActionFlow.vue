<template>
  <section class="missionFlow" :aria-labelledby="headingId">
    <!-- Flow A, step 1: focus with a count-up timer (never a countdown). -->
    <template v-if="step === 'focus'">
      <div class="flowBody">
      <header class="flowHead">
        <span class="flowKicker">{{ t("space.missionAction.focusKicker") }}</span>
        <h3 :id="headingId" ref="heading" tabindex="-1">{{ zoneTitle }}</h3>
      </header>

      <!-- B31: the timer card. Background image (or the plain card), scrim, Pause/Resume and music. -->
      <div class="flowTimer" :class="{ paused, plain: !background }">
        <img v-if="background" class="flowTimerImage" :src="background" alt="" @error="background = null" />
        <span class="flowTimerScrim" aria-hidden="true"></span>
        <span v-if="paused" class="flowPausedChip">
          <svg viewBox="0 0 16 16" aria-hidden="true"><rect x="4" y="3" width="3" height="10" rx="1" fill="currentColor" /><rect x="9" y="3" width="3" height="10" rx="1" fill="currentColor" /></svg>
          {{ t("space.missionAction.pausedChip") }}
        </span>
        <strong class="flowClock" role="timer" :aria-label="t('space.missionAction.timerLabel')"><bdi dir="ltr">{{ clock }}</bdi></strong>
        <small class="flowTimerCaption" aria-live="polite">
          {{ paused ? t("space.missionAction.pausedCaption") : t("space.missionAction.timerCaption") }}
        </small>
        <div class="flowTimerControls">
          <button type="button" class="flowPause" :class="{ resume: paused }" @click="togglePause">
            <svg v-if="paused" viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.2v9.6L12.6 8z" fill="currentColor" /></svg>
            <svg v-else viewBox="0 0 16 16" aria-hidden="true"><rect x="4" y="3" width="3" height="10" rx="1" fill="currentColor" /><rect x="9" y="3" width="3" height="10" rx="1" fill="currentColor" /></svg>
            {{ paused ? t("space.missionAction.resume") : t("space.missionAction.pause") }}
          </button>
          <button
            v-if="musicAvailable"
            type="button"
            class="flowMute"
            :class="{ muted }"
            :aria-pressed="muted ? 'true' : 'false'"
            :aria-label="muted ? t('space.missionAction.unmuteMusic') : t('space.missionAction.muteMusic')"
            :title="muted ? t('space.missionAction.unmuteMusic') : t('space.missionAction.muteMusic')"
            @click="toggleMute"
          >
            <svg v-if="muted" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 7.5h3l4-3.5v12l-4-3.5H3z" fill="currentColor" /><path d="M13 7.5l4.5 5M17.5 7.5l-4.5 5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" /></svg>
            <svg v-else viewBox="0 0 20 20" aria-hidden="true"><path d="M3 7.5h3l4-3.5v12l-4-3.5H3z" fill="currentColor" /><path d="M13 7.2a3.6 3.6 0 0 1 0 5.6M15.2 5a6.6 6.6 0 0 1 0 10" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" /></svg>
          </button>
        </div>
      </div>

      <!-- Both lines share one grid cell, so pausing never changes the height (no layout shift). -->
      <p class="flowRingo flowRingoSwap" aria-live="polite">
        <span :class="{ hidden: paused }" :aria-hidden="paused ? 'true' : null">{{ t("space.missionAction.focusRingo") }}</span>
        <span :class="{ hidden: !paused }" :aria-hidden="paused ? null : 'true'">{{ t("space.missionAction.pausedRingo") }}</span>
      </p>

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
import musicFiles from "virtual:focus-music";
import {
  focusElapsedMs,
  globToRelative,
  pauseFocus,
  readMusicMuted,
  resolveBackground,
  resolveMusic,
  resumeFocus,
  writeMusicMuted,
} from "@/lib/focusMedia";
import {
  FEELING_KEYS,
  NOTE_MAX,
  PLACE_KEYS,
  PLACE_LABEL_MAX,
  buildContext,
  performedAtWindow,
  readFocusState,
  readLastPlace,
  slotEnabled,
  slotPerformedAt,
  writeFocusStart,
  writeFocusState,
  writeLastPlace,
} from "@/lib/missionActionFlow";

const SLOTS = ["morning", "noon", "afternoon", "evening", "exact"];

// B31: focus backgrounds are bundled assets; a new image needs no code change (see docs/FOCUS_MEDIA.md).
const BACKGROUNDS = globToRelative(
  import.meta.glob("../../assets/focus-backgrounds/**/*.{webp,png,jpg,jpeg,WEBP,PNG,JPG,JPEG}", { eager: true, import: "default" }),
);
const MUSIC_VOLUME = 0.35;

const props = defineProps({
  // "focus" (Do it now) or "earlier" (Already did it).
  mode: { type: String, default: "focus" },
  mission: { type: Object, required: true },
  zoneTitle: { type: String, default: "" },
  pathKey: { type: String, default: "" },
  userKey: { type: String, default: "" },
  // B31: the challenge's icon key, for a challenge-specific background or music folder.
  challengeKey: { type: String, default: "" },
  submitting: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

const emit = defineEmits(["save", "cancel", "close"]);

const { t, locale } = useI18n();
const headingId = `missionFlowHeading-${Math.random().toString(36).slice(2, 8)}`;
const heading = ref(null);

const step = ref(props.mode === "earlier" ? "earlier" : "focus");
// The focus record: { startedAt, pausedAt, pausedMs } (timestamps, so paused time never counts).
const focus = ref(null);
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

const media = { pathKey: props.pathKey, challengeKey: props.challengeKey };
const background = ref(resolveBackground(BACKGROUNDS, media));
const tracks = resolveMusic(musicFiles, media);
const muted = ref(readMusicMuted());
// Music that could not start without a tap (a restored timer, or the browser's autoplay rule).
const musicBlocked = ref(false);
const musicFailed = ref(false);
let audio = null;
let trackIndex = tracks.length > 1 ? Math.floor(Math.random() * tracks.length) : 0;

// The mission's micro-actions, when the mission has any (local only, never sent).
const microActions = computed(() => {
  const items = props.mission?.microActions || props.mission?.micro_actions || [];
  return Array.isArray(items) ? items.filter((item) => typeof item === "string" && item.trim()) : [];
});

const paused = computed(() => Boolean(focus.value?.pausedAt));
const elapsedSeconds = computed(() => Math.floor(focusElapsedMs(focus.value, now.value) / 1000));
const musicAvailable = computed(() => tracks.length > 0 && !musicFailed.value);
const musicOn = computed(() => !muted.value && !musicBlocked.value);
// B31: the timer digits are always Latin (0 to 9, tabular), also in FA: the Persian zero reads as a
// dot next to the other digits. Every other number in FA keeps Persian digits.
const clock = computed(() => formatClock(elapsedSeconds.value, "en"));
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

function trackUrl(file) {
  return `${import.meta.env.BASE_URL}Musics/${file.split("/").map(encodeURIComponent).join("/")}`;
}

function playMusic() {
  if (!musicAvailable.value || !musicOn.value || paused.value || step.value !== "focus") return;
  if (!audio) {
    audio = new Audio();
    audio.volume = MUSIC_VOLUME;
    audio.loop = tracks.length === 1;
    audio.preload = "auto";
    audio.addEventListener("ended", () => {
      trackIndex = (trackIndex + 1) % tracks.length;
      audio.src = trackUrl(tracks[trackIndex]);
      playMusic();
    });
    // A missing or broken file: try the next track once each, then hide the button (quietly).
    let failures = 0;
    audio.addEventListener("error", () => {
      failures += 1;
      if (failures >= tracks.length) {
        musicFailed.value = true;
        stopMusic();
        return;
      }
      trackIndex = (trackIndex + 1) % tracks.length;
      audio.src = trackUrl(tracks[trackIndex]);
      playMusic();
    });
    audio.addEventListener("playing", () => { failures = 0; });
    audio.src = trackUrl(tracks[trackIndex]);
  }
  const attempt = audio.play();
  if (attempt?.catch) {
    attempt.catch((error) => {
      // The browser wants a tap first: show the button as off, a tap on it starts the music.
      if (error?.name === "NotAllowedError") musicBlocked.value = true;
    });
  }
}

function pauseMusic() {
  try {
    audio?.pause();
  } catch {
    // ignore
  }
}

function stopMusic() {
  if (!audio) return;
  pauseMusic();
  try {
    audio.removeAttribute("src");
    audio.load();
  } catch {
    // ignore
  }
  audio = null;
}

function toggleMute() {
  if (musicOn.value) {
    muted.value = true;
    writeMusicMuted(true);
    pauseMusic();
    return;
  }
  muted.value = false;
  musicBlocked.value = false;
  writeMusicMuted(false);
  playMusic();
}

function togglePause() {
  if (!focus.value) return;
  const current = Date.now();
  focus.value = paused.value ? resumeFocus(focus.value, current) : pauseFocus(focus.value, current);
  now.value = current;
  writeFocusState(props.userKey, props.mission?.id, focus.value);
  if (paused.value) pauseMusic();
  else playMusic();
}

function finishFocus() {
  // Done works while paused: the paused time is already left out.
  durationSeconds.value = Math.max(1, elapsedSeconds.value);
  stopMusic();
  step.value = "checkout";
  focusHeading();
}

function cancelFocus() {
  stopMusic();
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
    // The start time is a convenience: a reload resumes the same timer (and its pause).
    const saved = readFocusState(props.userKey, props.mission?.id);
    focus.value = saved || { startedAt: Date.now(), pausedAt: null, pausedMs: 0 };
    if (!saved) writeFocusState(props.userKey, props.mission?.id, focus.value);
    now.value = Date.now();
    // Music starts only right after the "Do it now" tap; a restored timer waits for a tap on the button.
    if (saved) musicBlocked.value = true;
    else playMusic();
  } else {
    loadRingoDay();
  }
  startTicker();
  focusHeading();
});

onUnmounted(() => {
  stopTicker();
  stopMusic();
});

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

/* B31 (boards 12 to 15): 348x196 in the panel, 362x204 on a phone. Every piece is placed
   absolutely, so pausing, the chip or a missing image never shifts the layout. */
.flowTimer {
  position: relative;
  justify-self: center;
  width: 100%;
  max-width: 348px;
  /* clip-path, not overflow: hidden, so the card keeps its height in a short, scrolling sheet. */
  clip-path: inset(0 round 14px);
  border-radius: 14px;
  background: linear-gradient(160deg, #222a36, #141a23);
  isolation: isolate;
}

/* The 1px edge is drawn on top, so it never adds to the 348x196 (362x204) size. */
.flowTimer::after {
  content: "";
  position: absolute;
  inset: 0;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: inherit;
  pointer-events: none;
}

/* The 348:196 (phone 362:204) ratio as real content height. */
.flowTimer::before {
  content: "";
  display: block;
  padding-top: 56.32%;
}

.flowTimerImage {
  position: absolute;
  inset: 0;
  z-index: -2;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.flowTimerScrim {
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(180deg, rgba(11, 14, 20, 0.35) 0%, rgba(11, 14, 20, 0.55) 45%, rgba(11, 14, 20, 0.86) 100%);
}

.flowPausedChip {
  position: absolute;
  top: 12px;
  left: 50%;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 999px;
  color: #6ee5ff;
  background: rgba(11, 14, 20, 0.55);
  border: 1px solid rgba(110, 229, 255, 0.6);
  font-size: 11px;
  font-weight: 700;
  transform: translateX(-50%);
  white-space: nowrap;
}

.flowPausedChip svg {
  width: 11px;
  height: 11px;
}

.flowClock {
  position: absolute;
  top: 36px;
  inset-inline: 0;
  color: #fff;
  /* Latin digits with real tabular widths in EN and FA (Vazirmatn's Latin 8 is wider). */
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  font-size: 44px;
  font-weight: 700;
  line-height: 1.15;
  text-align: center;
  font-variant-numeric: tabular-nums lining-nums;
  font-feature-settings: "tnum" 1, "lnum" 1;
  letter-spacing: 0.02em;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.65);
  transition: opacity 0.2s ease;
}

.flowTimer.paused .flowClock {
  opacity: 0.62;
}

.flowTimerCaption {
  position: absolute;
  top: 92px;
  inset-inline: 12px;
  margin: 0;
  color: rgba(255, 255, 255, 0.86);
  font-size: 12px;
  line-height: 1.4;
  text-align: center;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.7);
}

.flowTimerControls {
  position: absolute;
  bottom: 16px;
  inset-inline: 0;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.flowPause,
.flowMute {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  color: #fff;
  background: rgba(11, 14, 20, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(4px);
  cursor: pointer;
  font: inherit;
}

.flowPause {
  gap: 7px;
  min-width: 104px;
  padding: 0 20px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.flowPause svg {
  width: 14px;
  height: 14px;
}

.flowPause.resume {
  color: #6ee5ff;
  border-color: #6ee5ff;
}

.flowMute {
  width: 40px;
  padding: 0;
  border-radius: 50%;
}

.flowMute svg {
  width: 18px;
  height: 18px;
}

.flowMute.muted {
  color: rgba(255, 255, 255, 0.7);
  border-style: dashed;
  border-color: rgba(255, 255, 255, 0.45);
}

/* 40 px pills get a 44 px hit area without changing their look. */
.flowPause::after,
.flowMute::after {
  content: "";
  position: absolute;
  inset: -2px;
}

.flowPause,
.flowMute {
  position: relative;
}

.flowPause:focus-visible,
.flowMute:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

@media (max-width: 599px) {
  .flowTimer {
    max-width: 362px;
  }

  .flowTimer::before {
    padding-top: 56.35%;
  }

  .flowClock {
    top: 34px;
    font-size: 42px;
  }

  .flowTimerCaption {
    top: 90px;
  }
}

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

.flowRingoSwap {
  display: grid;
}

.flowRingoSwap > span {
  grid-area: 1 / 1;
}

.flowRingoSwap > .hidden {
  visibility: hidden;
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

  .flowClock {
    transition: none;
  }
}
</style>
