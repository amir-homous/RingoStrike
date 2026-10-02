<template>
  <aside class="zonePanel">
    <div class="panelHead">
      <div>
        <p class="panelKicker">{{ zone.path_key }}</p>
        <h3>{{ zone.title }}</h3>
      </div>

      <button type="button" class="closeButton" @click="$emit('close')">
        {{ t("space.close") }}
      </button>
    </div>

    <div class="panelSection">
      <span class="sectionLabel">
        {{ t("space.unlockedCount", { count: unlockedCount }) }}
      </span>
      <div v-if="zone.unlocked_objects.length" class="panelObjects">
        <SpaceObject
          v-for="reward in zone.unlocked_objects"
          :key="reward.key"
          :reward="reward"
        />
      </div>
      <p v-else class="emptyText">{{ t("space.noUnlocked") }}</p>
    </div>

    <div class="panelSection">
      <span class="sectionLabel">
        {{ t("space.lockedPreviewCount", { count: lockedPreviewCount }) }}
      </span>
      <p v-if="zone.locked_preview_objects.length" class="hintText">
        {{ t("space.lockedPreviewHint") }}
      </p>
      <div v-if="zone.locked_preview_objects.length" class="panelObjects">
        <SpaceObject
          v-for="reward in zone.locked_preview_objects.slice(0, 3)"
          :key="reward.key"
          :reward="reward"
        />
      </div>
      <p v-else class="emptyText">{{ t("space.zoneComplete") }}</p>
    </div>

    <p v-if="zone.next_reward" class="nextReward">
      {{ nextRewardText }}
    </p>

    <div v-if="zone.action" class="panelSection zoneAction" :class="zone.action.state">
      <span class="sectionLabel">{{ t("space.zoneAction.label") }}</span>
      <strong>{{ zone.action.title }}</strong>
      <p>{{ zone.action.text }}</p>

      <div class="actionRow">
        <RouterLink class="actionLink primary" :to="zone.action.primaryTo">
          {{ zone.action.primaryLabel }}
        </RouterLink>
        <RouterLink
          v-if="zone.action.secondaryTo"
          class="actionLink secondary"
          :to="zone.action.secondaryTo"
        >
          {{ zone.action.secondaryLabel }}
        </RouterLink>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import SpaceObject from "./SpaceObject.vue";

const props = defineProps({
  zone: { type: Object, required: true },
});

defineEmits(["close"]);

const { t } = useI18n();

const unlockedCount = computed(() => props.zone?.unlocked_objects?.length || 0);
const lockedPreviewCount = computed(() => props.zone?.locked_preview_objects?.length || 0);

const nextRewardText = computed(() => {
  const reward = props.zone?.next_reward;
  if (!reward) return "";

  if (reward.unlock_condition_type === "first_path_mission_done") {
    return t("space.nextRewardFirst", { reward: reward.title });
  }

  return t("space.nextRewardFuture", { reward: reward.title });
});
</script>

<style scoped>
.zonePanel {
  display: grid;
  gap: 14px;
  min-width: 0;
  padding: 15px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.panelHead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.panelKicker,
.sectionLabel {
  display: block;
  margin: 0 0 5px;
  color: rgba(110, 229, 255, 0.72);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.panelHead h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.1rem;
}

.closeButton {
  min-height: 32px;
  padding: 6px 10px;
  border-radius: 9px;
  color: rgba(255, 255, 255, 0.76);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-weight: 800;
}

.panelObjects {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.emptyText,
.hintText,
.nextReward {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.55;
}

.hintText {
  margin-bottom: 8px;
  font-size: 0.82rem;
}

.nextReward {
  padding-top: 2px;
  color: rgba(255, 255, 255, 0.72);
}

.zoneAction {
  display: grid;
  gap: 8px;
  padding-top: 2px;
}

.zoneAction strong {
  color: rgba(255, 255, 255, 0.90);
}

.zoneAction p {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

.actionRow {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.actionLink {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 7px 11px;
  border-radius: 9px;
  text-decoration: none;
  font-size: 0.78rem;
  font-weight: 850;
}

.actionLink.primary {
  color: rgba(5, 10, 18, 0.95);
  background: rgba(110, 229, 255, 0.88);
}

.actionLink.secondary {
  color: rgba(255, 255, 255, 0.76);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
}
</style>
