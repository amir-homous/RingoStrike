<template>
  <section
    class="ringoCard"
    :class="[card.tone, { collapsed }]"
    :aria-label="t('space.ringoGuide.eyebrow')"
  >
    <div v-if="collapsed" class="collapsedLine">
      <span>{{ card.collapsedText || card.title }}</span>
      <button type="button" class="backButton" @click="$emit('expand')">
        {{ t("space.panel.back") }}
      </button>
    </div>

    <template v-else>
      <div class="ringoCardHead">
        <RingoMoodFigure
          :mood="card.mood"
          :alt="t('space.ringoGuide.eyebrow')"
          size="sm"
          framed
        />
        <div class="ringoCardCopy">
          <span v-if="card.badge" class="stateBadge">{{ card.badge }}</span>
          <span v-else class="stateLabel">{{ card.label }}</span>
          <strong>{{ card.title }}</strong>
          <p v-if="card.body">{{ card.body }}</p>
          <div v-if="card.chips?.length" class="missionMeta">
            <span v-for="chip in card.chips" :key="chip.key" :class="chip.tone">
              {{ chip.text }}
            </span>
          </div>
        </div>
      </div>

      <p v-if="card.note" class="ringoNote">{{ card.note }}</p>

      <button
        v-if="card.primary"
        ref="primaryButton"
        type="button"
        class="primaryAction"
        :disabled="card.primary.disabled"
        @click="$emit('action', card.primary)"
      >
        {{ card.primary.label }}
      </button>

      <div
        v-if="card.support?.length && !choicePanel"
        class="supportGrid"
      >
        <button
          v-for="action in card.support"
          :key="action.key"
          type="button"
          class="supportAction"
          :disabled="action.disabled"
          :aria-label="action.label"
          @click="$emit('action', action)"
        >
          <img
            v-if="actionIcon(action)"
            :src="actionIcon(action)"
            alt=""
            class="supportIcon iconOnDark"
            aria-hidden="true"
          />
          <span>{{ action.label }}</span>
        </button>
      </div>

      <div v-if="card.secondary?.length" class="secondaryActions">
        <button
          v-for="action in card.secondary"
          :key="action.key"
          type="button"
          class="secondaryAction"
          :disabled="action.disabled"
          @click="$emit('action', action)"
        >
          {{ action.label }}
        </button>
      </div>

      <div v-if="choicePanel" class="ringoChoicePanel">
        <p>{{ choicePanel.prompt }}</p>
        <div class="ringoChoiceGrid">
          <button
            v-for="option in choicePanel.options"
            :key="option.key"
            type="button"
            class="choicePill"
            :disabled="choiceDisabled"
            @click="$emit('choice', option)"
          >
            {{ option.label }}
          </button>
        </div>
        <button type="button" class="choiceBack" @click="$emit('close-choice')">
          {{ t("missions.backToMissionActions") }}
        </button>
      </div>
    </template>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";
import { resolveActionIcon } from "@/utils/actionIconUtils";

defineProps({
  card: { type: Object, required: true },
  collapsed: { type: Boolean, default: false },
  choicePanel: { type: Object, default: null },
  choiceDisabled: { type: Boolean, default: false },
});

defineEmits(["action", "choice", "close-choice", "expand"]);

const { t } = useI18n();
const primaryButton = ref(null);

function actionIcon(action) {
  return resolveActionIcon(action?.iconKey || action?.type || "");
}

function focusPrimary() {
  primaryButton.value?.focus();
}

defineExpose({ focusPrimary });
</script>

<style scoped>
.ringoCard {
  display: grid;
  gap: 10px;
  padding: 10px;
  border-radius: 18px;
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.12), transparent 34%),
    rgba(255, 255, 255, 0.038);
  border: 1px solid rgba(110, 229, 255, 0.13);
}

.ringoCard.ready {
  border-color: rgba(110, 229, 255, 0.18);
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 229, 255, 0.16), transparent 36%),
    rgba(110, 229, 255, 0.045);
}

.ringoCard.start,
.ringoCard.bonus,
.ringoCard.safe,
.ringoCard.reminder {
  border-color: rgba(247, 215, 116, 0.16);
  background:
    radial-gradient(circle at 8% 0%, rgba(247, 215, 116, 0.13), transparent 36%),
    rgba(247, 215, 116, 0.045);
}

.ringoCard.done,
.ringoCard.clear {
  border-color: rgba(80, 220, 140, 0.18);
  background:
    radial-gradient(circle at 8% 0%, rgba(80, 220, 140, 0.13), transparent 36%),
    rgba(80, 220, 140, 0.045);
}

.ringoCard.locked {
  border-color: rgba(255, 255, 255, 0.11);
  background:
    radial-gradient(circle at 8% 0%, rgba(255, 255, 255, 0.09), transparent 36%),
    rgba(255, 255, 255, 0.035);
}

.ringoCard.collapsed {
  padding: 8px 10px;
  border-radius: 14px;
}

.collapsedLine {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-width: 0;
}

.collapsedLine span {
  overflow: hidden;
  min-width: 0;
  color: rgba(255, 255, 255, 0.86);
  font-size: 0.82rem;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.backButton,
.choicePill,
.choiceBack,
.secondaryAction {
  min-height: 30px;
  padding: 6px 9px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-size: 0.72rem;
  font-weight: 850;
}

.backButton {
  flex: 0 0 auto;
}

.ringoCardHead {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  align-items: center;
}

.ringoCardHead :deep(.ringoMood.size-sm) {
  width: 72px;
  height: 72px;
  border-radius: 18px;
}

.ringoCardCopy {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.stateLabel {
  display: block;
  color: rgba(110, 229, 255, 0.72);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.ringoCard.safe .stateLabel {
  color: rgba(247, 215, 116, 0.92);
}

.stateBadge {
  justify-self: start;
  padding: 3px 8px;
  border-radius: 999px;
  color: rgba(247, 215, 116, 0.98);
  background: rgba(247, 215, 116, 0.10);
  border: 1px solid rgba(247, 215, 116, 0.22);
  font-size: 0.7rem;
  font-weight: 900;
}

.ringoCardCopy strong {
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.92rem;
}

.ringoCardCopy p,
.ringoNote {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
  font-size: 0.82rem;
}

.ringoNote {
  font-size: 0.76rem;
}

.missionMeta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 2px;
}

.missionMeta span {
  padding: 4px 7px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.68);
  background: rgba(255, 255, 255, 0.055);
  font-size: 0.7rem;
  font-weight: 800;
}

.missionMeta .due {
  color: rgba(247, 215, 116, 0.98);
  background: rgba(247, 215, 116, 0.10);
}

.primaryAction {
  width: 100%;
  min-height: 50px;
  padding: 8px 14px;
  border: 0;
  border-radius: 12px;
  color: rgba(5, 10, 18, 0.95);
  background: rgba(110, 229, 255, 0.88);
  cursor: pointer;
  font-size: 0.86rem;
  font-weight: 900;
}

.ringoCard.safe .primaryAction {
  background: rgba(247, 215, 116, 0.9);
}

.supportGrid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.supportAction {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 5px;
  min-width: 0;
  min-height: 66px;
  padding: 8px 6px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-size: 0.72rem;
  font-weight: 850;
  line-height: 1.3;
  text-align: center;
  overflow-wrap: anywhere;
}

.supportIcon {
  width: 22px;
  height: 22px;
  object-fit: contain;
  --icon-on-dark-shadow: drop-shadow(0 4px 7px rgba(0, 0, 0, 0.36));
}

.secondaryActions {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.backButton:hover,
.backButton:focus-visible,
.supportAction:hover,
.supportAction:focus-visible,
.secondaryAction:hover,
.secondaryAction:focus-visible,
.choicePill:hover,
.choicePill:focus-visible,
.choiceBack:hover,
.choiceBack:focus-visible {
  color: rgba(255, 255, 255, 0.92);
  background: rgba(110, 229, 255, 0.08);
  border-color: rgba(110, 229, 255, 0.18);
  outline: none;
}

.primaryAction:focus-visible {
  outline: 2px solid rgba(255, 255, 255, 0.86);
  outline-offset: 2px;
}

.primaryAction:disabled,
.supportAction:disabled,
.secondaryAction:disabled,
.choicePill:disabled {
  cursor: default;
  opacity: 0.62;
}

.ringoChoicePanel {
  display: grid;
  gap: 8px;
  padding: 9px;
  border-radius: 13px;
  background: rgba(5, 10, 18, 0.28);
  border: 1px solid rgba(110, 229, 255, 0.12);
}

.ringoChoicePanel p {
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.76rem;
}

.ringoChoiceGrid {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.choiceBack {
  width: fit-content;
  color: rgba(255, 255, 255, 0.58);
  background: transparent;
}

@media (max-width: 720px) {
  .ringoCardHead :deep(.ringoMood.size-sm) {
    width: 64px;
    height: 64px;
  }
}
</style>
