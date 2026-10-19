<template>
  <aside class="roomPanel" :aria-label="t('space.title')">
    <div class="roomHead">
      <p class="roomKicker">{{ t("space.eyebrow") }}</p>
      <h3>{{ t("space.title") }}</h3>
    </div>

    <section class="roomRingo" :class="tone">
      <RingoMoodFigure :mood="mood" :alt="t('space.ringoGuide.eyebrow')" size="sm" framed />
      <div class="roomRingoCopy">
        <span class="roomLabel">{{ t("space.ringoGuide.eyebrow") }}</span>
        <strong>{{ title }}</strong>
        <p v-if="text">{{ text }}</p>
      </div>
    </section>

    <section class="daySummary" :aria-label="t('space.room.summaryLabel')">
      <span class="roomLabel">{{ t("space.room.summaryLabel") }}</span>
      <div class="summaryGrid">
        <article>
          <strong><bdi dir="ltr">{{ completed }}/{{ total }}</bdi></strong>
          <small>{{ t("space.room.missionsDone") }}</small>
        </article>
        <article :class="{ safe: todaySafe }">
          <strong>
            {{ todaySafe ? t("space.shell.restSummarySafeValue") : t("space.shell.restSummaryOpenValue") }}
          </strong>
          <small>{{ t("space.shell.restSummarySafeLabel") }}</small>
        </article>
        <article :class="{ due: dueCount > 0 }">
          <strong>{{ t("space.room.remindersValue", { due: dueCount, scheduled: scheduledCount }) }}</strong>
          <small>{{ t("space.room.remindersLabel") }}</small>
        </article>
        <article>
          <strong>{{ objectsToday }}</strong>
          <small>{{ t("space.room.objectsToday") }}</small>
        </article>
      </div>
    </section>

    <section v-if="suggestedZone" class="suggestion">
      <span class="roomLabel">{{ t("space.room.suggestLabel") }}</span>
      <strong>{{ suggestedZone.title }}</strong>
      <button ref="suggestButton" type="button" class="openZone" @click="$emit('select-zone', suggestedZone)">
        {{ t("space.room.openZone", { zone: suggestedZone.title }) }}
      </button>
    </section>

    <p class="invite">{{ t("space.room.invite") }}</p>
  </aside>
</template>

<script setup>
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";

defineProps({
  title: { type: String, default: "" },
  text: { type: String, default: "" },
  mood: { type: String, default: "welcome" },
  tone: { type: String, default: "neutral" },
  todaySafe: { type: Boolean, default: false },
  completed: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  dueCount: { type: Number, default: 0 },
  scheduledCount: { type: Number, default: 0 },
  objectsToday: { type: Number, default: 0 },
  suggestedZone: { type: Object, default: null },
});

defineEmits(["select-zone"]);

const { t } = useI18n();
const suggestButton = ref(null);

function focusSuggestion() {
  suggestButton.value?.focus();
}

defineExpose({ focusSuggestion });
</script>

<style scoped>
.roomPanel {
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

.roomKicker,
.roomLabel {
  display: block;
  margin: 0 0 5px;
  color: rgba(110, 229, 255, 0.72);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.roomHead h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.1rem;
}

.roomRingo {
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

.roomRingo.safe {
  border-color: rgba(247, 215, 116, 0.16);
  background:
    radial-gradient(circle at 8% 0%, rgba(247, 215, 116, 0.13), transparent 36%),
    rgba(247, 215, 116, 0.045);
}

.roomRingo :deep(.ringoMood.size-sm) {
  width: 72px;
  height: 72px;
  border-radius: 18px;
}

.roomRingoCopy {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.roomRingoCopy strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.92rem;
}

.roomRingoCopy p,
.invite {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
  font-size: 0.82rem;
}

.daySummary,
.suggestion {
  display: grid;
  gap: 8px;
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.summaryGrid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.summaryGrid article {
  display: grid;
  gap: 3px;
  min-width: 0;
  padding: 9px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.summaryGrid article.safe {
  border-color: rgba(80, 220, 140, 0.18);
}

.summaryGrid article.due {
  border-color: rgba(247, 215, 116, 0.22);
}

.summaryGrid strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.86rem;
}

.summaryGrid small {
  color: rgba(255, 255, 255, 0.54);
  font-size: 0.7rem;
  line-height: 1.35;
}

.suggestion {
  border-color: rgba(247, 215, 116, 0.2);
  background: rgba(247, 215, 116, 0.04);
}

.suggestion strong {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.openZone {
  width: 100%;
  min-height: 46px;
  padding: 8px 14px;
  border: 0;
  border-radius: 12px;
  color: rgba(5, 10, 18, 0.95);
  background: rgba(110, 229, 255, 0.88);
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 900;
}

.openZone:focus-visible {
  outline: 2px solid rgba(255, 255, 255, 0.86);
  outline-offset: 2px;
}

@media (max-width: 720px) {
  .roomPanel {
    height: auto;
    overflow: visible;
    padding: 12px;
  }

  .roomRingo :deep(.ringoMood.size-sm) {
    width: 64px;
    height: 64px;
  }
}
</style>
