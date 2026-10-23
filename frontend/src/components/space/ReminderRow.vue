<template>
  <!-- B33 (D66): challenge icon, mission name, corner name, and "Now" / time / time + Telegram off. -->
  <button
    type="button"
    class="reminderRow"
    :class="`is-${state}`"
    :aria-label="ariaLabel"
    :data-reminder="reminder.id"
    :data-state="state"
    @click="$emit('open', reminder)"
  >
    <span class="reminderRowIcon" aria-hidden="true">
      <span v-if="iconUrl" class="reminderRowGlyph" :style="{ '--row-icon': `url(${iconUrl})` }"></span>
    </span>
    <span class="reminderRowCopy">
      <strong>{{ reminder.title }}</strong>
      <small v-if="reminder.zoneTitle">{{ reminder.zoneTitle }}</small>
    </span>
    <span class="reminderRowWhen" aria-hidden="true">{{ whenText }}</span>
    <svg class="reminderRowChevron" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7" /></svg>
  </button>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { challengeIconKey } from "@/lib/challengeIconKeys";
import { REMINDER_CHIP } from "@/lib/pathMarker";
import { reminderClockTime, reminderRowState } from "@/lib/reminderRows";
import { resolveChallengeIcon } from "@/utils/missionMomentumUtils";

const props = defineProps({
  reminder: { type: Object, required: true },
});

defineEmits(["open"]);

const { t, locale } = useI18n();

const state = computed(() => reminderRowState(props.reminder, { telegram: props.reminder.telegram ?? null }));
const time = computed(() => reminderClockTime(props.reminder.timestamp, locale.value));

const whenText = computed(() => {
  if (state.value === REMINDER_CHIP.DUE) return t("space.reminders.now");
  if (state.value === REMINDER_CHIP.TELEGRAM_OFF) return t("space.reminders.timeTelegramOff", { time: time.value });
  return time.value;
});

const ariaLabel = computed(() => {
  const name = props.reminder.title || t("common.mission");
  const corner = props.reminder.zoneTitle || "";
  if (state.value === REMINDER_CHIP.DUE) return t("space.reminders.rowDue", { name, corner });
  if (state.value === REMINDER_CHIP.TELEGRAM_OFF) return t("space.reminders.rowTelegramOff", { name, corner, time: time.value });
  return t("space.reminders.rowSet", { name, corner, time: time.value });
});

const iconUrl = computed(() => {
  const name = props.reminder.challengeName || "";
  return name ? resolveChallengeIcon({ icon_key: challengeIconKey(name), name }) : "";
});
</script>

<style scoped>
.reminderRow {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  min-height: 60px;
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: #eef0f5;
  text-align: start;
  cursor: pointer;
  font: inherit;
}

.reminderRow:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

.reminderRowIcon {
  display: grid;
  flex: none;
  place-items: center;
  width: 44px;
  height: 44px;
  box-sizing: border-box;
  border-radius: 12px;
  border: 1.5px solid rgba(255, 255, 255, 0.28);
  background: rgba(11, 14, 20, 0.6);
}

.reminderRow.is-due .reminderRowIcon {
  border-color: #ffb759;
}

.reminderRow.is-telegram_off .reminderRowIcon {
  border-color: #ee312a;
}

.reminderRowGlyph {
  width: 24px;
  height: 24px;
  background-color: #eef0f5;
  -webkit-mask: var(--row-icon) center / contain no-repeat;
  mask: var(--row-icon) center / contain no-repeat;
}

.reminderRowCopy {
  display: grid;
  flex: 1;
  min-width: 0;
  gap: 2px;
}

.reminderRowCopy strong {
  overflow: hidden;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.3;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reminderRowCopy small {
  color: rgba(255, 255, 255, 0.66);
  font-size: 12px;
}

.reminderRowWhen {
  flex: none;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  color: #eef0f5;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.reminderRow.is-due .reminderRowWhen {
  border-color: #ffb759;
  background: #ffb759;
  color: #1a0d08;
  font-weight: 700;
}

.reminderRow.is-telegram_off .reminderRowWhen {
  border-color: #ee312a;
  background: rgba(238, 49, 42, 0.15);
  color: #ff8d88;
}

.reminderRowChevron {
  flex: none;
  width: 14px;
  height: 14px;
  fill: none;
  stroke: rgba(255, 255, 255, 0.5);
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

:dir(rtl) .reminderRowChevron {
  transform: scaleX(-1);
}
</style>
