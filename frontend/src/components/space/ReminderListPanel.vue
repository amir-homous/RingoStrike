<template>
  <!-- B34 (D68): tapping the clock opens Ringo's panel with every reminder (board 24). -->
  <aside class="reminderListPanel" :aria-labelledby="headingId">
    <div class="listHead">
      <p class="listKicker">{{ t("space.reminderClock.kicker") }}</p>
      <h3 :id="headingId" ref="heading" tabindex="-1">{{ t("space.reminderClock.title") }}</h3>
    </div>

    <section class="listRingo">
      <RingoMoodFigure :mood="reminders.some((item) => item.due) ? 'thinking' : 'welcome'" :alt="t('space.ringoGuide.eyebrow')" size="sm" framed />
      <div class="listRingoCopy">
        <span class="listLabel">{{ t("space.ringoGuide.eyebrow") }}</span>
        <strong>{{ reminders.length ? t("space.reminderClock.ringoTitle") : t("space.reminderClock.emptyTitle") }}</strong>
        <p>{{ reminders.length ? t("space.reminderClock.ringoBody") : t("space.reminderClock.emptyBody") }}</p>
      </div>
    </section>

    <div v-if="reminders.length" class="listRows">
      <ReminderRow
        v-for="reminder in reminders"
        :key="reminder.id"
        :reminder="reminder"
        @open="$emit('open', $event)"
      />
    </div>

    <button type="button" class="listBack" @click="$emit('close')">{{ t("space.reminderClock.back") }}</button>
  </aside>
</template>

<script setup>
import { nextTick, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";
import ReminderRow from "./ReminderRow.vue";

defineProps({
  // Due first, then later today (LivingSpace's reminderItems).
  reminders: { type: Array, default: () => [] },
});

defineEmits(["open", "close"]);

const { t } = useI18n();
const headingId = `reminderList-${Math.random().toString(36).slice(2, 8)}`;
const heading = ref(null);

onMounted(() => nextTick(() => heading.value?.focus({ preventScroll: false })));
</script>

<style scoped>
.reminderListPanel {
  display: grid;
  align-content: start;
  gap: 12px;
  min-width: 0;
  height: 100%;
  padding: 14px;
  border-radius: 20px;
  overflow-y: auto;
  background:
    radial-gradient(circle at 10% 0%, rgba(110, 229, 255, 0.08), transparent 32%),
    radial-gradient(circle at 88% 18%, rgba(247, 215, 116, 0.07), transparent 30%),
    linear-gradient(135deg, rgba(11, 17, 29, 0.88), rgba(5, 10, 18, 0.76));
  border: 1px solid rgba(110, 229, 255, 0.13);
  box-shadow:
    0 18px 50px rgba(0, 0, 0, 0.24),
    inset 0 0 0 1px rgba(255, 255, 255, 0.025);
  backdrop-filter: blur(18px);
}

.listKicker,
.listLabel {
  display: block;
  margin: 0 0 5px;
  color: rgba(110, 229, 255, 0.72);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.listHead h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.1rem;
}

.listHead h3:focus {
  outline: none;
}

.listRingo {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  padding: 10px;
  border-radius: 18px;
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.12), transparent 34%),
    rgba(255, 255, 255, 0.038);
  border: 1px solid rgba(110, 229, 255, 0.13);
}

.listRingo :deep(.ringoMood.size-sm) {
  width: 72px;
  height: 72px;
  border-radius: 18px;
}

.listRingoCopy {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.listRingoCopy strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.92rem;
}

.listRingoCopy p {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  font-size: 0.82rem;
  line-height: 1.55;
}

.listRows {
  display: grid;
  gap: 8px;
}

.listBack {
  min-height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.06);
  color: #eef0f5;
  cursor: pointer;
  font: inherit;
  font-size: 13px;
}

.listBack:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}
</style>
