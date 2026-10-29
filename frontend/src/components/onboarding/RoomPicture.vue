<template>
  <!-- B37 (D79, D80): the real room as a picture, built only from the existing room layers. The five
       path markers pick a corner; "after" shows that corner's first objects and a warmer light. -->
  <div ref="frame" class="roomPicture" :style="{ height: `${height}px` }">
    <div class="pictureScene" dir="ltr" :style="{ transform: `scale(${scale})` }" aria-hidden="true">
      <img :src="asset(layout.stage)" alt="" class="layer" draggable="false" />
      <img
        v-for="zone in zones"
        :key="`prop-${zone.key}`"
        :src="asset(zone.prop.file)"
        alt=""
        class="layer"
        draggable="false"
        :style="at(zone.prop.x, zone.prop.y)"
      />
      <img
        v-for="item in afterObjects"
        :key="`obj-${item.key}`"
        :src="asset(item.file)"
        alt=""
        class="layer"
        draggable="false"
        :style="at(item.x, item.y)"
      />
      <img v-if="ringo" :src="asset(ringo.file)" alt="" class="layer" draggable="false" :style="at(ringo.x, ringo.y)" />
      <img v-if="selected" :src="asset(selected.dim)" alt="" class="layer dim" draggable="false" />
      <img
        v-if="selected"
        :src="asset(selected.light.file)"
        alt=""
        class="layer light"
        draggable="false"
        :style="at(selected.light.x, selected.light.y)"
      />
      <span v-if="selected && after" class="warm" :style="warmStyle" />
      <img :src="asset(layout.overlay)" alt="" class="layer" draggable="false" />
    </div>

    <button
      v-for="zone in zones"
      :key="`marker-${zone.key}`"
      type="button"
      class="cornerMarker"
      :class="{ chosen: zone.key === modelValue }"
      :style="markerStyle(zone)"
      :aria-label="zone.label"
      :aria-pressed="zone.key === modelValue ? 'true' : 'false'"
      :data-zone="zone.key"
      @click="$emit('update:modelValue', zone.key)"
    >
      <span class="markerGlyph" :style="{ '--marker-icon': `url(${zone.iconUrl})` }" aria-hidden="true" />
    </button>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import layout from "@/assets/room/room_layout.json";
import { ZONE_ORDER, objectAssetPath, ringoPlacement } from "@/lib/roomScene";

const props = defineProps({
  // The chosen zone key ("" = none yet).
  modelValue: { type: String, default: "" },
  // false: the corner as it is now (no objects); true: after a few steps (its first objects, warm light).
  after: { type: Boolean, default: false },
  // { zoneKey: { label, iconUrl, color } }
  markers: { type: Object, default: () => ({}) },
});

defineEmits(["update:modelValue"]);

const assetModules = import.meta.glob("../../assets/room/**/*.png", { eager: true, import: "default" });
const assetUrls = Object.fromEntries(Object.entries(assetModules).map(([path, url]) => [path.split("/assets/room/")[1], url]));
const asset = (file) => assetUrls[file] || "";

const BASE_W = layout.base?.width || 480;
const BASE_H = layout.base?.height || 270;
const frame = ref(null);
const width = ref(BASE_W);
let observer = null;

const scale = computed(() => Math.max(0.4, width.value / BASE_W));
const height = computed(() => Math.round(BASE_H * scale.value));
const ringo = ringoPlacement(layout, { rest: false });

const zones = computed(() => ZONE_ORDER.filter((key) => layout.zones?.[key]).map((key) => ({
  key,
  ...layout.zones[key],
  label: props.markers[key]?.label || key,
  iconUrl: props.markers[key]?.iconUrl || "",
  color: props.markers[key]?.color || "#6ee5ff",
})));

const selected = computed(() => (props.modelValue ? layout.zones?.[props.modelValue] || null : null));

// "After a few steps": the chosen corner's first objects, the ones that have art (its layout slots).
const afterObjects = computed(() => {
  if (!props.after || !selected.value) return [];
  return Object.entries(selected.value.slots || {})
    .map(([key, slot]) => ({ key, file: objectAssetPath(slot.asset_key), x: slot.x, y: slot.y }))
    .filter((item) => asset(item.file));
});

// A soft warm light over the corner's light pool (no new art).
const warmStyle = computed(() => {
  const [x, y, w, h] = selected.value?.light?.pool || [BASE_W / 2, BASE_H / 2, 80, 60];
  return {
    left: `${x - w}px`,
    top: `${y - h}px`,
    width: `${w * 2}px`,
    height: `${h * 2}px`,
  };
});

function at(x, y) {
  return { left: `${x}px`, top: `${y}px` };
}

function markerStyle(zone) {
  const [x, y] = zone.path_marker || [0, 0];
  const s = scale.value;
  return {
    left: `${Math.round(x * s - 22)}px`,
    top: `${Math.round(y * s - 22)}px`,
    "--marker-color": zone.color,
  };
}

onMounted(() => {
  const measure = () => { width.value = frame.value?.clientWidth || BASE_W; };
  measure();
  if (typeof ResizeObserver !== "undefined") {
    observer = new ResizeObserver(measure);
    observer.observe(frame.value);
  }
});

onBeforeUnmount(() => observer?.disconnect());
</script>

<style scoped>
.roomPicture {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: #05070d;
}

.pictureScene {
  position: absolute;
  left: 0;
  top: 0;
  width: 480px;
  height: 270px;
  transform-origin: 0 0;
}

.layer {
  position: absolute;
  left: 0;
  top: 0;
  max-width: none;
  image-rendering: pixelated;
  user-select: none;
  pointer-events: none;
}

.light {
  mix-blend-mode: screen;
}

.warm {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(255, 196, 110, 0.42), rgba(255, 170, 80, 0.16) 60%, transparent);
  mix-blend-mode: screen;
  pointer-events: none;
  transition: opacity 300ms ease;
}

.cornerMarker {
  position: absolute;
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin: 0;
  padding: 0;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.28);
  background: rgba(11, 14, 20, 0.86);
  color: #aeb4c0;
  cursor: pointer;
  transition: border-color 160ms ease, box-shadow 160ms ease, color 160ms ease;
}

.cornerMarker.chosen {
  border-color: var(--marker-color);
  color: var(--marker-color);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.9), 0 0 12px var(--marker-color);
}

.cornerMarker:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

.markerGlyph {
  width: 22px;
  height: 22px;
  background-color: currentColor;
  -webkit-mask: var(--marker-icon) center / contain no-repeat;
  mask: var(--marker-icon) center / contain no-repeat;
}

@media (prefers-reduced-motion: reduce) {
  .cornerMarker,
  .warm {
    transition: none;
  }
}
</style>
