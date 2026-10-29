<template>
  <!-- B37 (D73 to D75): the day moment. Ringo's golden badge ignites, the big count rolls up, the
       last seven days fill to today, then the soft line settles. Reduced motion: the final frame. -->
  <div class="dayMoment" :class="[`case-${moment.case}`, `phase-${phase}`]">
    <p v-if="moment.kicker" class="momentKicker">{{ moment.kicker }}</p>

    <div class="momentBadge" aria-hidden="true">
      <span class="badgeGlow" />
      <span class="badgeCoin"><span class="badgeLetter">R</span></span>
      <span v-for="n in 5" :key="n" class="spark" :class="`spark-${n}`" />
    </div>

    <div v-if="moment.count !== null" class="momentCount">
      <strong>{{ fmt(shownCount) }}</strong>
      <span>{{ moment.countLabel }}</span>
    </div>

    <p class="momentSafe">{{ moment.line }}</p>

    <div v-if="moment.week" class="momentWeek" role="img" :aria-label="weekAria">
      <span class="weekTrack" aria-hidden="true"><span class="weekFill" /></span>
      <span
        v-for="day in moment.week"
        :key="day.date"
        class="weekDay"
        :class="{ lit: day.lit, today: day.today }"
        aria-hidden="true"
      >
        <span class="weekDot" />
        <small>{{ weekday(day.date) }}</small>
      </span>
    </div>

    <span v-if="moment.chip" class="momentChip">{{ moment.chip }}</span>
    <p v-if="moment.softLine" class="momentSoft">{{ moment.softLine }}</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { formatNumber } from "@/lib/i18nNumbers";

const props = defineProps({
  moment: { type: Object, required: true },
});

const { locale, t } = useI18n();
const fmt = (value) => formatNumber(value, locale.value);
// 0 quiet, 1 ignite (300 ms), 2 fill (700 ms), 3 settle (1200 ms).
const phase = ref(0);
const rolled = ref(false);
const timers = [];

const shownCount = computed(() => {
  const count = Number(props.moment.count);
  if (!Number.isFinite(count)) return "";
  return rolled.value || count <= 1 ? count : count - 1;
});

const weekAria = computed(() => {
  const days = (props.moment.week || []).map((day) => t(day.lit ? "ringoRewardSequence.moment.dayLit" : "ringoRewardSequence.moment.dayQuiet", { day: weekday(day.date, "long") }));
  return `${t("ringoRewardSequence.moment.weekLabel")}: ${days.join(", ")}`;
});

function weekday(iso, style = "narrow") {
  try {
    return new Intl.DateTimeFormat(locale.value === "fa" ? "fa-IR" : "en", { weekday: style, timeZone: "UTC" }).format(new Date(`${iso}T00:00:00Z`));
  } catch {
    return "";
  }
}

function reducedMotion() {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}

onMounted(() => {
  if (reducedMotion()) {
    phase.value = 3;
    rolled.value = true;
    return;
  }
  timers.push(setTimeout(() => { phase.value = 1; }, 300));
  timers.push(setTimeout(() => { phase.value = 2; rolled.value = true; }, 700));
  timers.push(setTimeout(() => { phase.value = 3; }, 1200));
});

onBeforeUnmount(() => timers.forEach((id) => clearTimeout(id)));
</script>

<style scoped>
.dayMoment {
  display: grid;
  gap: 8px;
  justify-items: center;
}

.momentKicker {
  margin: 0;
  color: rgba(253, 230, 138, 0.95);
  font-weight: 850;
}

.momentBadge {
  position: relative;
  display: grid;
  place-items: center;
  width: 76px;
  height: 76px;
}

.badgeGlow {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(247, 196, 76, 0.5), transparent 68%);
  opacity: 0;
  transition: opacity 400ms ease;
}

.badgeCoin {
  position: relative;
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  border: 3px solid #b9822a;
  background: radial-gradient(circle at 35% 30%, #fff1b8, #f5c84c 45%, #c8901f);
  box-shadow: inset 0 -3px 0 rgba(120, 72, 10, 0.35);
  filter: saturate(0.35) brightness(0.8);
  transition: filter 300ms ease, transform 300ms ease;
}

.badgeLetter {
  color: #5a3a06;
  font-size: 1.5rem;
  font-weight: 900;
  line-height: 1;
}

.spark {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffd36b;
  opacity: 0;
}

.spark-1 { top: 2px; left: 50%; }
.spark-2 { top: 18px; right: 0; }
.spark-3 { bottom: 10px; right: 6px; }
.spark-4 { bottom: 10px; left: 6px; }
.spark-5 { top: 18px; left: 0; }

/* Ignite: the badge lights like a small flame, sparks fly once, then a steady glow. */
.phase-1 .badgeCoin,
.phase-2 .badgeCoin,
.phase-3 .badgeCoin {
  filter: none;
  transform: scale(1.06);
}

.phase-1 .badgeGlow,
.phase-2 .badgeGlow,
.phase-3 .badgeGlow {
  opacity: 1;
}

.phase-1 .spark {
  animation: spark 600ms ease-out forwards;
}

.phase-3 .badgeCoin {
  transform: scale(1);
}

.phase-3 .badgeGlow {
  animation: glow 2400ms ease-in-out infinite;
}

@keyframes spark {
  0% { opacity: 1; transform: translate(0, 0) scale(1); }
  100% { opacity: 0; transform: translate(var(--dx, 0), -14px) scale(0.4); }
}

@keyframes glow {
  50% { opacity: 0.7; }
}

.momentCount {
  display: grid;
  justify-items: center;
  gap: 2px;
}

.momentCount strong {
  color: rgba(253, 230, 138, 0.98);
  font-size: 2.6rem;
  line-height: 1;
  transition: transform 300ms ease;
}

.phase-2 .momentCount strong {
  transform: scale(1.08);
}

.momentCount span {
  color: rgba(255, 255, 255, 0.72);
  font-weight: 750;
}

.momentSafe {
  margin: 0;
  color: rgba(255, 255, 255, 0.86);
}

.momentWeek {
  position: relative;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  width: min(300px, 100%);
  margin-block: 4px;
}

.weekTrack {
  position: absolute;
  inset-inline: 7%;
  top: 9px;
  height: 2px;
  background: rgba(255, 255, 255, 0.12);
}

.weekFill {
  position: absolute;
  inset-block: 0;
  inset-inline-start: 0;
  width: 0;
  background: rgba(247, 196, 76, 0.7);
  transition: width 400ms ease;
}

.phase-2 .weekFill,
.phase-3 .weekFill {
  width: 100%;
}

.weekDay {
  position: relative;
  display: grid;
  justify-items: center;
  gap: 4px;
}

.weekDot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px dashed rgba(255, 255, 255, 0.32);
  background: rgba(8, 13, 24, 1);
  transition: background 240ms ease, border-color 240ms ease, transform 240ms ease;
}

.weekDay.lit .weekDot {
  border: 2px solid #f5c84c;
  background: #f5c84c;
}

/* Today's circle waits, then fills and pops with the bar. */
.phase-0 .weekDay.today .weekDot,
.phase-1 .weekDay.today .weekDot {
  border: 2px dashed rgba(247, 196, 76, 0.7);
  background: rgba(8, 13, 24, 1);
}

.phase-2 .weekDay.today.lit .weekDot {
  transform: scale(1.25);
}

.weekDay small {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.68rem;
}

.weekDay.today small {
  color: rgba(253, 230, 138, 0.9);
  font-weight: 800;
}

.momentChip {
  padding: 3px 10px;
  border: 1px solid rgba(247, 215, 116, 0.24);
  border-radius: 999px;
  color: rgba(253, 230, 138, 0.95);
  background: rgba(247, 215, 116, 0.08);
  font-size: 0.8rem;
  font-weight: 800;
}

.momentSoft {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  opacity: 0;
  transition: opacity 400ms ease;
}

.phase-3 .momentSoft {
  opacity: 1;
}

@media (prefers-reduced-motion: reduce) {
  .badgeGlow,
  .badgeCoin,
  .weekFill,
  .weekDot,
  .momentCount strong,
  .momentSoft {
    transition: none;
  }

  .spark,
  .phase-3 .badgeGlow {
    animation: none;
  }
}
</style>
