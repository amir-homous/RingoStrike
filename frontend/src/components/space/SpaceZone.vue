<template>
  <button
    type="button"
    class="spaceZone"
    :class="[`zone-${zone.zone_key}`, { active, hasProgress }]"
    @click="$emit('select', zone)"
  >
    <span class="zoneHeader">
      <span class="zoneTitleWrap">
        <img v-if="pathIcon" :src="pathIcon" alt="" class="pathIcon" aria-hidden="true" />
        <span>
        <span class="zoneKicker">{{ zone.path_key }}</span>
        <strong>{{ zone.title }}</strong>
        </span>
      </span>
      <span v-if="zone.has_unseen_rewards" class="unseenDot" aria-hidden="true"></span>
    </span>

    <span class="objectShelf">
      <SpaceObject
        v-for="reward in visibleObjects"
        :key="reward.key"
        :reward="reward"
      />
    </span>
  </button>
</template>

<script setup>
import { computed } from "vue";
import { resolvePathIcon } from "@/utils/missionMomentumUtils";
import SpaceObject from "./SpaceObject.vue";

const props = defineProps({
  zone: { type: Object, required: true },
  active: { type: Boolean, default: false },
});

defineEmits(["select"]);

const hasProgress = computed(() => {
  return (props.zone?.unlocked_objects || []).length > 0;
});

const visibleObjects = computed(() => {
  const unlocked = props.zone?.unlocked_objects || [];
  const locked = props.zone?.locked_preview_objects || [];
  return [...unlocked, ...locked].slice(0, 3);
});

const pathIcon = computed(() => {
  const iconNames = {
    career: "briefcase",
    fitness: "activity",
    learning: "book",
    creativity: "sparkles",
    sleep: "moon",
  };

  return resolvePathIcon(iconNames[props.zone?.path_key] || props.zone?.path_key || "");
});
</script>

<style scoped>
.spaceZone {
  position: relative;
  display: grid;
  gap: 10px;
  align-content: space-between;
  min-width: 0;
  min-height: 132px;
  padding: 13px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 10px;
  color: inherit;
  text-align: start;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.025)),
    rgba(8, 13, 22, 0.58);
  cursor: pointer;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.025);
  transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
}

.spaceZone:hover,
.spaceZone.active {
  transform: translateY(-2px);
  border-color: rgba(110, 229, 255, 0.34);
  background:
    linear-gradient(180deg, rgba(110, 229, 255, 0.075), rgba(255, 255, 255, 0.028)),
    rgba(8, 13, 22, 0.68);
}

.spaceZone.hasProgress {
  border-color: rgba(74, 222, 128, 0.22);
}

.zoneHeader {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  min-width: 0;
}

.zoneTitleWrap {
  display: inline-flex;
  align-items: flex-start;
  gap: 9px;
  min-width: 0;
}

.pathIcon {
  width: 25px;
  height: 25px;
  flex: 0 0 auto;
  object-fit: contain;
  filter: drop-shadow(0 8px 14px rgba(0, 0, 0, 0.32));
}

.zoneHeader strong {
  display: block;
  overflow-wrap: anywhere;
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.98rem;
  line-height: 1.18;
}

.zoneKicker {
  display: block;
  margin-bottom: 4px;
  color: rgba(110, 229, 255, 0.72);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.10em;
  text-transform: uppercase;
}

.unseenDot {
  width: 9px;
  height: 9px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: #4ade80;
  box-shadow: 0 0 18px rgba(74, 222, 128, 0.62);
}

.objectShelf {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-width: 0;
}

@media (max-width: 720px) {
  .spaceZone {
    min-height: 118px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .spaceZone {
    transition: none;
  }

  .spaceZone:hover,
  .spaceZone.active {
    transform: none;
  }
}
</style>
