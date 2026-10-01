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
      <span class="sectionLabel">{{ t("space.unlocked") }}</span>
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
      <span class="sectionLabel">{{ t("space.preview") }}</span>
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
      {{ t("space.nextReward", { reward: zone.next_reward.title }) }}
    </p>
  </aside>
</template>

<script setup>
import { useI18n } from "vue-i18n";
import SpaceObject from "./SpaceObject.vue";

defineProps({
  zone: { type: Object, required: true },
});

defineEmits(["close"]);

const { t } = useI18n();
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
.nextReward {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.55;
}

.nextReward {
  padding-top: 2px;
  color: rgba(255, 255, 255, 0.72);
}
</style>
