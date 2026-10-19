<template>
  <div class="challengeList">
    <article
      v-for="item in items"
      :key="item.challenge.id"
      class="challengeRow"
      :class="{ preview: item.preview, expanded: item.expanded, selected: item.selected, done: item.challenge.todayChecked }"
    >
      <button
        type="button"
        class="challengeHead"
        :aria-expanded="item.preview ? undefined : (item.expanded ? 'true' : 'false')"
        @click="$emit('select-challenge', item.challenge)"
      >
        <span class="iconFrame challengeIconFrame" aria-hidden="true">
          <img :src="item.iconUrl" alt="" class="challengeIcon iconOnDark" />
        </span>
        <span class="challengeCopy">
          <span class="challengeStatus">{{ item.statusLabel }}</span>
          <strong>{{ item.challenge.name }}</strong>
          <small v-if="item.challenge.missionCount">
            {{ t("common.countOf", { done: item.challenge.doneCount || 0, total: item.challenge.missionCount }) }}
          </small>
        </span>
      </button>

      <div v-if="item.expanded && item.today" class="todayMissions">
        <span class="todayLabel">{{ t("space.panel.todayList") }}</span>
        <ul>
          <li v-for="row in item.today.rows" :key="row.id">
            <button
              type="button"
              class="missionRow"
              :class="[row.state, row.intensity, { focused: row.focused, dimmed: row.afterMain }]"
              :disabled="!row.selectable"
              :aria-current="row.focused ? 'true' : undefined"
              @click="$emit('select-mission', row.mission)"
            >
              <span class="missionMark" aria-hidden="true">{{ row.state === "done" ? "✓" : "" }}</span>
              <span class="missionCopy">
                <strong>{{ row.mission.title }}</strong>
                <small>
                  {{ intensityLabel(row.intensity) }}
                  <template v-if="row.mission.estimatedMinutes">
                    · {{ t("space.shell.minutes", { count: row.mission.estimatedMinutes }) }}
                  </template>
                </small>
                <small v-if="row.afterMain" class="afterMain">{{ t("space.panel.afterMain") }}</small>
              </span>
              <span v-if="row.dueReminder" class="rowTag due">{{ t("space.panel.reminderBadge") }}</span>
              <span v-else-if="row.focused" class="rowTag">{{ t("space.panel.ringoPick") }}</span>
            </button>
          </li>
        </ul>
        <p v-if="item.today.futureCount" class="futureCount">
          {{ t("space.panel.futureMissions", { count: item.today.futureCount }) }}
        </p>
      </div>
    </article>
  </div>
</template>

<script setup>
import { useI18n } from "vue-i18n";
import { formatNumber, numberAwareT } from "@/lib/i18nNumbers";

defineProps({
  items: { type: Array, default: () => [] },
});

defineEmits(["select-challenge", "select-mission"]);

const { locale, t: baseT } = useI18n();
// B10: numbers in copy use the locale's digits; a numeric count picks the plural form.
const t = numberAwareT(baseT, () => locale.value);
const fmt = (value) => formatNumber(value, locale.value);

function intensityLabel(intensity) {
  return ["tiny", "bonus"].includes(intensity)
    ? t(`space.shell.intensity.${intensity}`)
    : t("space.shell.intensity.main");
}
</script>

<style scoped>
.challengeList {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.challengeRow {
  display: grid;
  min-width: 0;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.challengeRow.preview {
  border-style: dashed;
  border-color: rgba(247, 215, 116, 0.18);
  background: rgba(247, 215, 116, 0.03);
}

.challengeRow.done {
  border-color: rgba(80, 220, 140, 0.18);
}

.challengeRow.selected {
  border-color: rgba(110, 229, 255, 0.28);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.07), rgba(247, 215, 116, 0.03)),
    rgba(255, 255, 255, 0.04);
}

.challengeHead {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px;
  border: 0;
  border-radius: inherit;
  color: inherit;
  background: transparent;
  cursor: pointer;
  text-align: start;
}

.challengeHead:focus-visible,
.missionRow:focus-visible {
  outline: 2px solid rgba(110, 229, 255, 0.6);
  outline-offset: -2px;
}

.iconFrame {
  display: inline-grid;
  place-items: center;
  overflow: hidden;
  border-radius: 50%;
  background:
    radial-gradient(circle at 35% 20%, rgba(255, 255, 255, 0.22), transparent 38%),
    rgba(110, 229, 255, 0.10);
  border: 1px solid rgba(110, 229, 255, 0.18);
}

.challengeIconFrame {
  width: 40px;
  height: 40px;
}

.challengeIcon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  --icon-on-dark-shadow: drop-shadow(0 5px 8px rgba(0, 0, 0, 0.38));
}

.challengeCopy {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.challengeCopy strong {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.88rem;
}

.challengeCopy small {
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.7rem;
  font-weight: 800;
}

.challengeStatus,
.todayLabel {
  color: rgba(110, 229, 255, 0.74);
  font-size: 0.66rem;
  font-weight: 900;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.challengeRow.preview .challengeStatus {
  color: rgba(247, 215, 116, 0.82);
}

.challengeRow.done .challengeStatus {
  color: rgba(80, 220, 140, 0.86);
}

.todayMissions {
  display: grid;
  gap: 7px;
  padding: 0 10px 10px;
}

.todayMissions ul {
  display: grid;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.missionRow {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-height: 46px;
  padding: 8px 10px;
  border-radius: 12px;
  color: inherit;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  text-align: start;
}

.missionRow.focused {
  border-color: rgba(110, 229, 255, 0.3);
  background: rgba(110, 229, 255, 0.07);
}

.missionRow.done {
  border-color: rgba(80, 220, 140, 0.16);
  background: rgba(80, 220, 140, 0.06);
}

.missionRow.due {
  border-color: rgba(247, 215, 116, 0.22);
}

.missionRow.dimmed {
  cursor: default;
  opacity: 0.56;
}

.missionMark {
  display: inline-grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  color: rgba(80, 220, 140, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.14);
  font-size: 0.78rem;
  font-weight: 900;
}

.missionRow.done .missionMark {
  border-color: rgba(80, 220, 140, 0.4);
  background: rgba(80, 220, 140, 0.12);
}

.missionCopy {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.missionCopy strong {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.82rem;
}

.missionCopy small {
  color: rgba(255, 255, 255, 0.54);
  font-size: 0.7rem;
}

.missionCopy .afterMain {
  color: rgba(247, 215, 116, 0.78);
}

.rowTag {
  padding: 3px 7px;
  border-radius: 999px;
  color: rgba(110, 229, 255, 0.92);
  background: rgba(110, 229, 255, 0.10);
  font-size: 0.66rem;
  font-weight: 900;
  white-space: nowrap;
}

.rowTag.due {
  color: rgba(247, 215, 116, 0.98);
  background: rgba(247, 215, 116, 0.10);
}

.futureCount {
  margin: 0;
  padding: 7px 9px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.58);
  border: 1px dashed rgba(255, 255, 255, 0.12);
  font-size: 0.72rem;
}
</style>
