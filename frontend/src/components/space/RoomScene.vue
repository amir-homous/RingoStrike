<template>
  <div ref="frame" class="roomFrame">
    <slot v-if="failed" name="fallback" />

    <div
      v-else
      class="roomScene"
      dir="ltr"
      role="group"
      :aria-label="t('space.roomLabel')"
      :style="{ width: `${baseWidth * scale}px`, height: `${baseHeight * scale}px` }"
    >
      <!-- Pixel layers at base resolution, integer-scaled (addendum §5 order). -->
      <div class="sceneBase" :style="{ transform: `scale(${scale})` }" aria-hidden="true">
        <img :src="asset(layout.stage)" alt="" class="layer" draggable="false" @error="failed = true" />

        <img
          v-for="zone in orderedLayoutZones"
          :key="`prop-${zone.key}`"
          :src="asset(zone.prop.file)"
          alt=""
          class="layer"
          draggable="false"
          :style="at(zone.prop.x, zone.prop.y)"
        />

        <!-- B20: placed objects (unlocked rewards with a PNG), then ghosts (next locked reward with a PNG). -->
        <img
          v-for="item in placedObjects"
          :key="`placed-${item.key}`"
          :src="asset(item.path)"
          alt=""
          class="layer"
          draggable="false"
          :style="at(item.x, item.y)"
        />
        <img
          v-for="item in ghostObjects"
          :key="`ghost-${item.key}`"
          :src="asset(item.path)"
          alt=""
          class="layer ghostLayer"
          draggable="false"
          :style="{ ...at(item.x, item.y), ...ghostStyle }"
        />

        <img
          v-if="ringo"
          :src="asset(ringo.file)"
          alt=""
          class="layer"
          draggable="false"
          :style="at(ringo.x, ringo.y)"
        />

        <img
          v-if="selectedLayout && !rest"
          :src="asset(selectedLayout.dim)"
          alt=""
          class="layer"
          draggable="false"
        />
        <div v-if="rest" class="restOverlay" :style="{ opacity: restOverlayOpacity }" />
        <img
          v-if="selectedLayout && !rest"
          :src="asset(selectedLayout.light.file)"
          alt=""
          class="layer lightLayer"
          draggable="false"
          :style="at(selectedLayout.light.x, selectedLayout.light.y)"
        />

        <img
          v-for="marker in markers"
          :key="`marker-${marker.key}`"
          :src="asset(marker.file)"
          alt=""
          class="layer"
          draggable="false"
          :style="markerStyle(marker)"
          @load="rememberSize(marker.file, $event)"
        />

        <img :src="asset(layout.overlay)" alt="" class="layer" draggable="false" />
      </div>

      <!-- HTML layer: zone hit regions and labels, in screen px. -->
      <div class="sceneHtml">
        <div
          v-for="item in hitZones"
          :key="`hit-${item.key}`"
          class="zoneHitWrap"
          :class="{ selected: item.selected, suggested: item.suggested }"
        >
          <button
            type="button"
            class="zoneHit"
            :style="item.buttonStyle"
            :aria-label="item.ariaLabel"
            :aria-pressed="item.selected ? 'true' : 'false'"
            @click="$emit('select', item.zone)"
          />
          <svg
            class="zoneOutline"
            :style="item.buttonStyle"
            :viewBox="item.viewBox"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            <polygon :points="item.points" vector-effect="non-scaling-stroke" />
          </svg>
          <span class="zoneLabel" :style="item.labelStyle" aria-hidden="true">
            <span v-if="item.suggested" class="suggestedTag">{{ t("space.room.suggestLabel") }}</span>
            <strong>{{ item.title }}</strong>
            <small v-if="item.pathName">{{ item.pathName }}</small>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import layout from "@/assets/room/room_layout.json";
import {
  ROOM_BASE_HEIGHT,
  ROOM_BASE_WIDTH,
  ZONE_ORDER,
  footprintBox,
  footprintClipPath,
  footprintPoints,
  ringoPlacement,
  roomScale,
  zoneMarker,
  zoneObjects,
} from "@/lib/roomScene";

const props = defineProps({
  zones: { type: Array, default: () => [] },
  selectedZoneKey: { type: String, default: "" },
  suggestedZoneKey: { type: String, default: "" },
  rest: { type: Boolean, default: false },
});

defineEmits(["select"]);

const { t } = useI18n();

const assetModules = import.meta.glob("../../assets/room/**/*.png", { eager: true, import: "default" });
const assetUrls = Object.fromEntries(
  Object.entries(assetModules).map(([path, url]) => [path.split("/assets/room/")[1], url]),
);

const baseWidth = layout.base?.width || ROOM_BASE_WIDTH;
const baseHeight = layout.base?.height || ROOM_BASE_HEIGHT;
const frame = ref(null);
const availableWidth = ref(0);
const failed = ref(false);
const naturalSizes = reactive({});
let resizeObserver = null;

const scale = computed(() => roomScale(availableWidth.value));

// Rest dims the room to layout.rest.room_dim brightness (addendum §3: overlay opacity 0.26).
const restOverlayOpacity = computed(() => {
  const roomDim = Number(layout.rest?.room_dim);
  return Number.isFinite(roomDim) ? Math.round((1 - roomDim) * 100) / 100 : 0.26;
});

const zonesByKey = computed(() => Object.fromEntries(props.zones.map((zone) => [zone.zone_key, zone])));

const orderedLayoutZones = computed(() => {
  return ZONE_ORDER
    .filter((key) => layout.zones?.[key])
    .map((key) => ({ key, ...layout.zones[key] }));
});

const selectedLayout = computed(() => {
  return props.selectedZoneKey ? layout.zones?.[props.selectedZoneKey] || null : null;
});

const ringo = computed(() => ringoPlacement(layout, { rest: props.rest }));

const sceneObjects = computed(() => {
  const hasAsset = (path) => Boolean(assetUrls[path]);
  return orderedLayoutZones.value.map((zone) => zoneObjects(zone, zonesByKey.value[zone.key], hasAsset));
});

const placedObjects = computed(() => sceneObjects.value.flatMap((objects) => objects.placed));
const ghostObjects = computed(() => sceneObjects.value.map((objects) => objects.ghost).filter(Boolean));

// Ghost treatment from room_layout.json (spec §5); the 2x2 checker dither is a CSS mask.
const ghostStyle = {
  opacity: layout.ghost?.opacity ?? 0.38,
  filter: layout.ghost?.filter || "grayscale(1) brightness(1.5) sepia(.2) hue-rotate(180deg)",
};

const markers = computed(() => {
  return orderedLayoutZones.value
    .map((zone) => {
      const kind = zoneMarker(zonesByKey.value[zone.key]);
      if (!kind || !layout.markers?.[kind]) return null;
      return { key: zone.key, file: layout.markers[kind], point: zone.marker };
    })
    .filter(Boolean);
});

const hitZones = computed(() => {
  const s = scale.value;

  return orderedLayoutZones.value
    .filter((zone) => zonesByKey.value[zone.key])
    .map((zone) => {
      const data = zonesByKey.value[zone.key];
      const box = footprintBox(zone.footprint);
      const placed = (data.unlocked_objects || []).length;
      const states = [t("space.scene.objectsPlaced", { count: placed })];
      if (Number(data.dueReminderCount || 0) > 0) states.push(t("space.scene.reminderDue"));
      else if (Number(data.scheduledReminderCount || 0) > 0) states.push(t("space.scene.reminderScheduled"));

      return {
        key: zone.key,
        zone: data,
        title: data.title,
        pathName: data.pathName || "",
        selected: props.selectedZoneKey === zone.key,
        suggested: props.suggestedZoneKey === zone.key,
        ariaLabel: `${data.title}: ${states.join(", ")}`,
        viewBox: `0 0 ${box.w} ${box.h}`,
        points: footprintPoints(zone.footprint),
        buttonStyle: {
          left: `${box.x * s}px`,
          top: `${box.y * s}px`,
          width: `${box.w * s}px`,
          height: `${box.h * s}px`,
          clipPath: footprintClipPath(zone.footprint, s),
        },
        labelStyle: {
          left: `${(box.x + box.w / 2) * s}px`,
          top: `${box.y * s}px`,
        },
      };
    });
});

function asset(file) {
  return assetUrls[file] || "";
}

function at(x, y) {
  return { left: `${x}px`, top: `${y}px` };
}

function rememberSize(file, event) {
  const img = event?.target;
  if (img?.naturalWidth) naturalSizes[file] = [img.naturalWidth, img.naturalHeight];
}

// Markers anchor at their center; use whole base pixels so integer scaling stays crisp.
function markerStyle(marker) {
  const [w, h] = naturalSizes[marker.file] || [0, 0];
  const [x, y] = marker.point;
  return at(Math.round(x - w / 2), Math.round(y - h / 2));
}

function measure() {
  const el = frame.value;
  availableWidth.value = el?.clientWidth || 0;

  // When the room is wider than its frame (narrow screens), start centered on Ringo.
  // The real mobile crop and zoom is B22.
  const roomWidth = baseWidth * scale.value;
  if (el && roomWidth > el.clientWidth && ringo.value) {
    const ringoCenter = (ringo.value.x + ringo.value.w / 2) * scale.value;
    el.scrollLeft = Math.max(0, Math.min(roomWidth - el.clientWidth, ringoCenter - el.clientWidth / 2));
  }
}

onMounted(() => {
  measure();
  if (typeof ResizeObserver !== "undefined" && frame.value) {
    resizeObserver = new ResizeObserver(measure);
    resizeObserver.observe(frame.value);
  }
});

onUnmounted(() => {
  resizeObserver?.disconnect();
});
</script>

<style scoped>
.roomFrame {
  display: grid;
  justify-items: safe center;
  min-width: 0;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: thin;
}

.roomScene {
  position: relative;
  flex: 0 0 auto;
  overflow: hidden;
  border-radius: 6px;
  background: #05070d;
}

.sceneBase {
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

.ghostLayer {
  /* 2x2 base-px checker: a 1px cell pattern, integer-scaled with the room. */
  -webkit-mask-image: conic-gradient(#000 0 25%, transparent 0 50%, #000 0 75%, transparent 0);
  mask-image: conic-gradient(#000 0 25%, transparent 0 50%, #000 0 75%, transparent 0);
  -webkit-mask-size: 2px 2px;
  mask-size: 2px 2px;
}

.lightLayer {
  mix-blend-mode: screen;
}

.restOverlay {
  position: absolute;
  inset: 0;
  background: #000;
  pointer-events: none;
}

.sceneHtml {
  position: absolute;
  inset: 0;
}

.zoneHitWrap {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.zoneHit {
  position: absolute;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  pointer-events: auto;
}

.zoneHit:focus-visible {
  outline: none;
}

.zoneOutline {
  position: absolute;
  overflow: visible;
  opacity: 0;
  pointer-events: none;
  transition: opacity 140ms ease;
}

.zoneOutline polygon {
  fill: rgba(255, 255, 255, 0.04);
  stroke: rgba(214, 240, 255, 0.85);
  stroke-width: 1.5;
}

.zoneLabel {
  position: absolute;
  display: grid;
  justify-items: center;
  gap: 2px;
  max-width: 180px;
  padding: 4px 8px;
  border-radius: 9px;
  color: rgba(255, 255, 255, 0.94);
  background: rgba(5, 9, 16, 0.82);
  border: 1px solid rgba(110, 229, 255, 0.22);
  font-size: 0.74rem;
  line-height: 1.25;
  text-align: center;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transform: translate(-50%, -100%) translateY(-4px);
  transition: opacity 140ms ease;
}

.zoneLabel small {
  color: rgba(110, 229, 255, 0.82);
  font-size: 0.66rem;
  font-weight: 800;
}

/* Labels and outline only on hover, keyboard focus, or selection (spec §4). */
.zoneHit:hover ~ .zoneOutline,
.zoneHit:focus-visible ~ .zoneOutline,
.zoneHitWrap.selected .zoneOutline,
.zoneHit:hover ~ .zoneLabel,
.zoneHit:focus-visible ~ .zoneLabel,
.zoneHitWrap.selected .zoneLabel {
  opacity: 1;
}

.zoneHit:focus-visible ~ .zoneOutline polygon {
  stroke: rgba(110, 229, 255, 1);
  stroke-width: 2;
}

/* B23 temporary suggestion (until the visual suggestion is designed): gold outline + tag, always shown. */
.zoneHitWrap.suggested .zoneOutline,
.zoneHitWrap.suggested .zoneLabel {
  opacity: 1;
}

.zoneHitWrap.suggested .zoneOutline polygon {
  stroke: rgba(247, 215, 116, 0.92);
  fill: rgba(247, 215, 116, 0.05);
}

.zoneHitWrap.suggested .zoneLabel {
  border-color: rgba(247, 215, 116, 0.4);
}

.suggestedTag {
  padding: 1px 6px;
  border-radius: 999px;
  color: rgba(247, 215, 116, 0.96);
  background: rgba(247, 215, 116, 0.12);
  font-size: 0.62rem;
  font-weight: 900;
}

@media (prefers-reduced-motion: reduce) {
  .zoneOutline,
  .zoneLabel {
    transition: none;
  }
}
</style>
