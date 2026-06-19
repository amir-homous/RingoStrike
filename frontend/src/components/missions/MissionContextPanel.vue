<template>
  <div class="missionContextPanel">
    <p class="missionContextKicker">{{ heading }}</p>

    <nav v-if="breadcrumbItems.length" class="missionBreadcrumb" :aria-label="t('missionContext.breadcrumbLabel')">
      <span v-for="(item, index) in breadcrumbItems" :key="`${item}-${index}`">
        {{ item }}
      </span>
    </nav>

    <div v-if="intensityMeta" class="missionIntensity" :class="intensityMeta.intensity">
      <span>{{ intensityMeta.label }}</span>
      <small v-if="intensityMeta.detail">{{ intensityMeta.detail }}</small>
    </div>

    <strong class="missionContextTitle">{{ missionTitle }}</strong>

    <section class="missionContextBlock instruction">
      <span>{{ t("missionContext.instruction.title") }}</span>
      <p>{{ instructionCopy }}</p>
    </section>

    <section class="missionContextBlock why">
      <span>{{ t("missionContext.why.title") }}</span>
      <p>{{ whyCopy }}</p>
    </section>

    <div v-if="isTinyMission" class="missionContextNote tiny">
      <strong>{{ tinyRelationCopy }}</strong>
      <span>{{ t("missionContext.tiny.stillCounts") }}</span>
    </div>

    <div v-if="isBonusMission" class="missionContextNote bonus">
      <strong>{{ t("missionContext.bonus.optionalTitle") }}</strong>
      <span>{{ t("missionContext.bonus.optionalBody") }}</span>
    </div>

    <div v-if="showReminderContext" class="missionContextNote reminder">
      <strong v-if="reminderLabel">{{ t("missionContext.reminder.setFor", { time: reminderLabel }) }}</strong>
      <span>{{ t("missionContext.reminder.returnLater") }}</span>
    </div>

    <small v-if="statusCopy" class="missionStatusCopy">
      {{ statusCopy }}
    </small>

    <small v-if="reminderDeliveryMeta" class="reminderDeliveryChip" :class="reminderDeliveryMeta.state">
      {{ reminderDeliveryMeta.label }}
    </small>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps({
  mission: { type: Object, required: true },
  heading: { type: String, required: true },
  intensityMeta: { type: Object, default: null },
  parentTitle: { type: String, default: "" },
  reminderLabel: { type: String, default: "" },
  statusCopy: { type: String, default: "" },
  reminderDeliveryMeta: { type: Object, default: null },
});

const { t } = useI18n();

const missionTitle = computed(() => props.mission?.title || t("missions.fallbackMission"));

const normalizedIntensity = computed(() => {
  const value = String(props.mission?.mission_intensity || "").toLowerCase();
  return ["main", "tiny", "bonus"].includes(value) ? value : "mission";
});

const isTinyMission = computed(() => normalizedIntensity.value === "tiny");
const isBonusMission = computed(() => normalizedIntensity.value === "bonus");

const breadcrumbItems = computed(() => {
  return [props.mission?.path_title, props.mission?.challenge_name]
    .map((item) => String(item || "").trim())
    .filter(Boolean);
});

const description = computed(() => String(props.mission?.description || "").trim());

const instructionCopy = computed(() => {
  if (description.value.length >= 12) return description.value;
  if (isTinyMission.value) return t("missionContext.instruction.tiny");
  if (isBonusMission.value) return t("missionContext.instruction.bonus");
  if (normalizedIntensity.value === "main") return t("missionContext.instruction.main");
  return t("missionContext.instruction.mission");
});

const whyCopy = computed(() => {
  if (isTinyMission.value) return t("missionContext.why.tiny");
  if (isBonusMission.value) return t("missionContext.why.bonus");
  if (props.mission?.challenge_name) {
    return t("missionContext.why.mainWithChallenge", { challenge: props.mission.challenge_name });
  }
  return t("missionContext.why.main");
});

const tinyRelationCopy = computed(() => {
  const parentTitle = String(props.parentTitle || "").trim();
  if (parentTitle) {
    return t("missionContext.tiny.smallerVersionOf", { mission: parentTitle });
  }
  return t("missionContext.tiny.smallerVersionGeneric");
});

const showReminderContext = computed(() => {
  return Boolean(props.mission?.reminder_at || props.mission?.status === "remind_later");
});
</script>

<style scoped>
.missionContextPanel {
  display: grid;
  gap: 10px;
  min-width: 0;
  text-align: start;
}

.missionContextKicker {
  margin: 0;
  color: rgba(110, 229, 255, 0.82);
  font-size: var(--cap);
  font-weight: 900;
}

.missionBreadcrumb {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  min-width: 0;
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.8rem;
  font-weight: 800;
}

.missionBreadcrumb span {
  display: inline-flex;
  min-width: 0;
  align-items: center;
  overflow-wrap: anywhere;
}

.missionBreadcrumb span + span::before {
  content: "/";
  margin-inline-end: 6px;
  color: rgba(255, 255, 255, 0.30);
}

.missionIntensity {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  width: fit-content;
  max-width: 100%;
  padding: 5px 8px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.95);
  background: rgba(110, 229, 255, 0.07);
  font-size: var(--cap);
  font-weight: 850;
  line-height: 1.25;
}

.missionIntensity.tiny {
  border-color: rgba(74, 222, 128, 0.24);
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
}

.missionIntensity.bonus {
  border-color: rgba(247, 215, 116, 0.26);
  color: rgba(253, 230, 138, 0.96);
  background: rgba(247, 215, 116, 0.075);
}

.missionIntensity span,
.missionIntensity small {
  min-width: 0;
  color: inherit;
  font: inherit;
}

.missionIntensity small {
  opacity: 0.78;
}

.missionContextTitle {
  min-width: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1rem;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.missionContextBlock,
.missionContextNote {
  display: grid;
  gap: 4px;
  min-width: 0;
  padding: 10px 11px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.035);
}

.missionContextBlock span,
.missionContextNote strong {
  min-width: 0;
  color: rgba(255, 255, 255, 0.86);
  font-size: var(--cap);
  font-weight: 900;
}

.missionContextBlock p,
.missionContextNote span {
  margin: 0;
  min-width: 0;
  color: rgba(255, 255, 255, 0.66);
  font-size: 0.9rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.missionContextBlock.why {
  border-color: rgba(110, 229, 255, 0.14);
  background: rgba(110, 229, 255, 0.045);
}

.missionContextNote.tiny {
  border-color: rgba(74, 222, 128, 0.18);
  background: rgba(74, 222, 128, 0.055);
}

.missionContextNote.bonus,
.missionContextNote.reminder {
  border-color: rgba(247, 215, 116, 0.18);
  background: rgba(247, 215, 116, 0.055);
}

.missionStatusCopy {
  display: block;
  margin-top: 2px;
  color: rgba(247, 215, 116, 0.82);
  font-size: 0.86rem;
  font-weight: 720;
  line-height: 1.5;
}

.reminderDeliveryChip {
  display: inline-flex;
  width: fit-content;
  margin-top: 2px;
  padding: 5px 8px;
  border: 1px solid rgba(247, 215, 116, 0.22);
  border-radius: 999px;
  color: rgba(253, 230, 138, 0.92);
  background: rgba(247, 215, 116, 0.075);
  font-size: 0.76rem;
  font-weight: 850;
  line-height: 1.2;
}

.reminderDeliveryChip.sent {
  border-color: rgba(74, 222, 128, 0.24);
  color: rgba(187, 247, 208, 0.96);
  background: rgba(74, 222, 128, 0.075);
}

.reminderDeliveryChip.due {
  border-color: rgba(110, 229, 255, 0.24);
  color: rgba(219, 244, 255, 0.96);
  background: rgba(110, 229, 255, 0.075);
}

.reminderDeliveryChip.needsConnection,
.reminderDeliveryChip.disabled {
  border-color: rgba(251, 146, 60, 0.24);
  color: rgba(254, 215, 170, 0.96);
  background: rgba(251, 146, 60, 0.075);
}

@media (max-width: 520px) {
  .missionContextPanel {
    gap: 8px;
  }

  .missionContextBlock,
  .missionContextNote {
    padding: 9px 10px;
  }
}
</style>
