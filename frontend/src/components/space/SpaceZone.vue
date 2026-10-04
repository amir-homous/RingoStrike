<template>
  <button
    type="button"
    class="spaceZone"
    :class="[`zone-${zone.zone_key}`, { active, hasProgress }]"
    @click="$emit('select', zone)"
  >
    <span class="zoneHeader">
      <span class="zoneTitleWrap">
        <span v-if="pathIcon" class="iconFrame pathIconFrame" aria-hidden="true">
          <img :src="pathIcon" alt="" class="pathIcon" />
        </span>
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

    <span v-if="pathProgress" class="zoneProgress">
      <span class="zoneProgressHead">
        <strong>{{ pathProgress.percent }}%</strong>
        <small>{{ pathProgress.done }}/{{ pathProgress.total }}</small>
      </span>
      <span class="zoneProgressTrack" aria-hidden="true">
        <span :style="{ width: `${pathProgress.percent}%` }"></span>
      </span>
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

const pathProgress = computed(() => {
  const detail = props.zone?.pathDetail;
  if (!detail) return null;

  const total = Number(detail.pathProgressTotal || 0);
  const done = Math.min(total, Math.max(0, Number(detail.pathProgressDone || 0)));
  const percent = total > 0 ? Math.round((done / total) * 100) : 0;

  return { done, total, percent };
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

.iconFrame {
  display: inline-grid;
  place-items: center;
  overflow: hidden;
  flex: 0 0 auto;
  border-radius: 9px;
  background:
    radial-gradient(circle at 35% 20%, rgba(255, 255, 255, 0.20), transparent 38%),
    rgba(110, 229, 255, 0.10);
  border: 1px solid rgba(110, 229, 255, 0.18);
}

.pathIconFrame {
  width: 31px;
  height: 31px;
}

.pathIcon {
  display: block;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  object-fit: contain;
  filter: invert(1) brightness(1.45) drop-shadow(0 5px 8px rgba(0, 0, 0, 0.38));
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

.zoneProgress {
  display: grid;
  gap: 5px;
  min-width: 0;
}

.zoneProgressHead {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.zoneProgressHead strong {
  color: rgba(247, 215, 116, 0.94);
  font-size: 0.86rem;
  line-height: 1;
}

.zoneProgressHead small {
  color: rgba(255, 255, 255, 0.48);
  font-size: 0.66rem;
  font-weight: 850;
}

.zoneProgressTrack {
  overflow: hidden;
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
}

.zoneProgressTrack span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(110, 229, 255, 0.88), rgba(247, 215, 116, 0.94));
  box-shadow: 0 0 14px rgba(110, 229, 255, 0.18);
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
