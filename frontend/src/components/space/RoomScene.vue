<template>
  <div ref="frame" class="roomFrame">
    <slot v-if="failed" name="fallback" />

    <!-- The visible room: hugs the scene (or the column when the scene is wider), centered. -->
    <div v-else class="roomViewportWrap" :style="{ width: `${viewportWidth}px` }">
      <div
        ref="viewport"
        class="roomViewport"
        :class="{ panning, phone, zoomed, dragging }"
        :style="{ height: `${viewportHeight}px` }"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointercancel="onPointerUp"
        @click.capture="onClickCapture"
        @focusin="onFocusIn"
      >
        <div
          class="roomScene"
          dir="ltr"
          role="group"
          :aria-label="t('space.roomLabel')"
          :class="{ flipping: Boolean(flip) }"
          :style="{
            width: `${baseWidth * scale}px`,
            height: `${baseHeight * scale}px`,
            transform: sceneTransform,
          }"
        >
          <!-- Pixel layers at base resolution, scaled by the one effective room scale (addendum §5 order). -->
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
            <template v-for="item in ghostObjects" :key="`ghost-${item.key}`">
              <img
                :src="asset(item.path)"
                alt=""
                class="layer ghostLayer"
                :class="item.phase ? `mat-${item.phase}` : null"
                draggable="false"
                :data-reward="item.key"
                :style="{ ...at(item.x, item.y), ...ghostStyle }"
              />
              <!-- B21: the full-colour object fades in over the ghost, settles 1px, then a glint. -->
              <img
                v-if="['resolve', 'settle', 'glint'].includes(item.phase)"
                :src="asset(item.path)"
                alt=""
                class="layer matColor"
                :class="`mat-${item.phase}`"
                draggable="false"
                :data-reward="item.key"
                :style="at(item.x, item.y)"
              />
              <img
                v-if="item.phase === 'glint' && layout.markers?.glint"
                :src="asset(layout.markers.glint)"
                alt=""
                class="layer glintLayer"
                draggable="false"
                :style="markerStyle({ file: layout.markers.glint, point: [item.x + item.w / 2, item.y + 2] })"
                @load="rememberSize(layout.markers.glint, $event)"
              />
            </template>

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
              class="layer dimLayer"
              draggable="false"
            />
            <div v-if="rest" class="restOverlay" :style="{ opacity: restOverlayOpacity }" />
            <img
              v-if="selectedLayout && !rest"
              :src="asset(selectedLayout.light.file)"
              alt=""
              class="layer lightLayer"
              :class="{
                lightHidden: materializing?.phase === 'camera' && materializing.zoneKey === selectedZoneKey,
                lightRise: materializing?.phase === 'light' && materializing.zoneKey === selectedZoneKey,
              }"
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
              :data-zone="item.key"
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
                <polygon :points="item.points" />
              </svg>
              <span class="zoneLabel" :class="{ below: item.labelBelow }" :style="item.labelStyle" aria-hidden="true">
                <span v-if="item.suggested" class="suggestedTag">{{ t("space.room.suggestLabel") }}</span>
                <strong>{{ item.title }}</strong>
                <small v-if="item.pathName">{{ item.pathName }}</small>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Corner overlay at the inline-end top of the visible room (page direction, not mirrored art). -->
      <div v-if="$slots.corner" class="roomCorner">
        <slot name="corner" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, onUpdated, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { formatNumber, numberAwareT } from "@/lib/i18nNumbers";
import layout from "@/assets/room/room_layout.json";
import {
  ROOM_BASE_HEIGHT,
  ROOM_BASE_WIDTH,
  ZONE_ORDER,
  footprintBox,
  footprintClipPath,
  footprintPoints,
  ringoPlacement,
  cameraPan,
  cameraTarget,
  roomScale,
  safeArea,
  safeAreaPanY,
  zoneMarker,
  zoneObjects,
} from "@/lib/roomScene";

const props = defineProps({
  zones: { type: Array, default: () => [] },
  selectedZoneKey: { type: String, default: "" },
  suggestedZoneKey: { type: String, default: "" },
  rest: { type: Boolean, default: false },
  // From tablet width the room asks for at least x2; when the x2 room is wider than its column it
  // is clipped and panned to the selected zone (or Ringo A). Phones keep 1 (in-frame scroll, B22).
  minScale: { type: Number, default: 1 },
  // B22 phones (< 600px): overview fitted to the phone room height and centred on Ringo
  // (drag to look around); a selected zone zooms the camera to x2 on its camera rect.
  phone: { type: Boolean, default: false },
  // B21: keys of unlocked rewards still waiting to materialize (drawn as their zone's ghost).
  pendingRewardKeys: { type: Array, default: () => [] },
  // B21: { rewardKey, zoneKey, phase } while a reward materializes (camera, light, resolve, settle, glint).
  materializing: { type: Object, default: null },
});

defineEmits(["select"]);

const { locale, t: baseT } = useI18n();
// B10: numbers in copy use the locale's digits; a numeric count picks the plural form.
const t = numberAwareT(baseT, () => locale.value);
const fmt = (value) => formatNumber(value, locale.value);

const assetModules = import.meta.glob("../../assets/room/**/*.png", { eager: true, import: "default" });
const assetUrls = Object.fromEntries(
  Object.entries(assetModules).map(([path, url]) => [path.split("/assets/room/")[1], url]),
);

const baseWidth = layout.base?.width || ROOM_BASE_WIDTH;
const baseHeight = layout.base?.height || ROOM_BASE_HEIGHT;
const frame = ref(null);
const viewport = ref(null);
const availableWidth = ref(0);
const availableHeight = ref(Number.POSITIVE_INFINITY);
const failed = ref(false);
const naturalSizes = reactive({});
let resizeObserver = null;

// Room bottom margin kept free below the scene when fitting the viewport height.
const BOTTOM_MARGIN = 24;
// Phones: share of the screen height the room frame may take (the rest is the panel or sheet).
const PHONE_ROOM_SHARE = 0.45;
// Phones: camera scale for a selected zone (x2 of the base, spec B22).
const PHONE_ZOOM_SCALE = 2;
// Pointer travel before a press on the phone room becomes a drag instead of a tap.
const DRAG_THRESHOLD = 6;

const safe = safeArea(layout);
const viewportHeightLimit = ref(Number.POSITIVE_INFINITY);
const reducedMotion = ref(false);

// Phone zoom: a zone is selected (not the rest overview).
const zoomed = computed(() => props.phone && Boolean(props.selectedZoneKey) && !props.rest);

// Phone overview scale: the largest (hybrid) scale whose safe-area height fits the phone room height.
const phoneOverviewScale = computed(() => roomScale(Number.POSITIVE_INFINITY, viewportHeightLimit.value, safe.h));

// The one effective scale for every layer: pixel layers (scale transform), hit regions, labels,
// focus polygon and camera pan all multiply base px by it. Integer, or fractional only when the
// fit is close to the next integer (roomScale). The fit uses the safe-area height (B22), so the
// empty strips above and below it may be cropped. x2 minimum from tablet width as before.
const scale = computed(() => {
  if (props.phone) {
    return zoomed.value ? Math.max(PHONE_ZOOM_SCALE, phoneOverviewScale.value) : phoneOverviewScale.value;
  }
  const fit = roomScale(availableWidth.value, availableHeight.value, safe.h);
  const heightLimit = Math.max(1, Math.floor(availableHeight.value / safe.h));
  return Math.max(fit, Math.min(Math.floor(props.minScale) || 1, heightLimit));
});

const viewportWidth = computed(() => Math.min(baseWidth * scale.value, Math.max(0, availableWidth.value)));

// Visible room height: phones keep the overview frame height while zoomed; elsewhere the whole
// room when it fits, else cropped down to (never below) the safe area.
const viewportHeight = computed(() => {
  if (props.phone) return Math.min(baseHeight, safe.h) * phoneOverviewScale.value;
  const room = baseHeight * scale.value;
  const limit = Number.isFinite(availableHeight.value) ? availableHeight.value : room;
  return Math.min(room, Math.max(safe.h * scale.value, limit));
});

// The camera (a translate on the scene) runs whenever the room is larger than its viewport.
const panning = computed(() => {
  return props.phone
    || baseWidth * scale.value > availableWidth.value
    || viewportHeight.value < baseHeight * scale.value;
});

// Phones: drag offset (screen px) added to the overview camera; keyboard focus re-targets it.
const dragX = ref(0);
const dragging = ref(false);
const focusZoneKey = ref("");
let dragStart = null;
let suppressClick = false;

const pan = computed(() => {
  if (!panning.value) return { x: 0, y: 0 };
  const s = scale.value;
  const view = { viewportWidth: viewportWidth.value, viewportHeight: viewportHeight.value, scale: s };

  if (zoomed.value) {
    return cameraPan({ ...view, target: cameraTarget(layout, props.selectedZoneKey) });
  }

  const zoneKey = props.phone ? focusZoneKey.value : (props.rest ? "" : props.selectedZoneKey);
  const x = cameraPan({ ...view, target: cameraTarget(layout, zoneKey) }).x;
  const minX = Math.min(0, viewportWidth.value - baseWidth * s);
  return {
    x: props.phone ? Math.min(0, Math.max(minX, x + dragX.value)) : x,
    y: safeAreaPanY({ viewportHeight: viewportHeight.value, scale: s, safe }),
  };
});

// Phones: zooming in or out animates the camera (300 ms) with a FLIP: the new layout is first
// drawn with the old camera (translate + relative scale), then eased to the new one.
// The scene's children scale with it, so hit regions and labels stay on the art throughout.
const flip = ref(null);
watch(
  () => ({ zoomed: zoomed.value, s: scale.value, x: pan.value.x, y: pan.value.y }),
  (next, prev) => {
    if (!prev || next.zoomed === prev.zoomed) return;
    dragX.value = 0;
    if (!props.phone || reducedMotion.value || !prev.s || !next.s) return;
    flip.value = { x: prev.x, y: prev.y, k: prev.s / next.s };
    nextTick(() => requestAnimationFrame(() => requestAnimationFrame(() => { flip.value = null; })));
  },
);

const sceneTransform = computed(() => {
  if (flip.value) return `translate(${flip.value.x}px, ${flip.value.y}px) scale(${flip.value.k})`;
  return panning.value ? `translate(${pan.value.x}px, ${pan.value.y}px)` : null;
});

function onPointerDown(event) {
  if (!props.phone || zoomed.value || event.button > 0) return;
  dragStart = { x: event.clientX, offset: dragX.value, base: pan.value.x - dragX.value };
}

function onPointerMove(event) {
  if (!dragStart) return;
  const dx = event.clientX - dragStart.x;
  if (!dragging.value && Math.abs(dx) < DRAG_THRESHOLD) return;
  dragging.value = true;
  const minX = Math.min(0, viewportWidth.value - baseWidth * scale.value);
  const x = Math.min(0, Math.max(minX, dragStart.base + dragStart.offset + dx));
  dragX.value = x - dragStart.base;
}

function onPointerUp() {
  if (dragging.value) {
    // Snap to whole base pixels so the art stays crisp, and swallow the click that ends the drag.
    const s = scale.value;
    const base = pan.value.x - dragX.value;
    dragX.value = Math.round((base + dragX.value) / s) * s - base;
    suppressClick = true;
    setTimeout(() => { suppressClick = false; }, 0);
  }
  dragging.value = false;
  dragStart = null;
}

function onClickCapture(event) {
  if (!suppressClick) return;
  suppressClick = false;
  event.preventDefault();
  event.stopPropagation();
}

// Keyboard on the phone overview: bring the focused zone into the cropped view.
function onFocusIn(event) {
  if (!props.phone || zoomed.value || !event.target?.matches?.(":focus-visible")) return;
  const key = event.target?.closest?.(".zoneHitWrap")?.dataset?.zone;
  if (!key) return;
  dragX.value = 0;
  focusZoneKey.value = key;
}

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
  const pendingKeys = props.pendingRewardKeys;
  return orderedLayoutZones.value.map((zone) => zoneObjects(zone, zonesByKey.value[zone.key], hasAsset, { pendingKeys }));
});

const placedObjects = computed(() => sceneObjects.value.flatMap((objects) => objects.placed));
const ghostObjects = computed(() => {
  const active = props.materializing;
  return sceneObjects.value
    .map((objects) => objects.ghost)
    .filter(Boolean)
    .map((item) => ({ ...item, phase: active?.rewardKey === item.key ? active.phase : "" }));
});

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

// Measured label heights (they differ with the "Ringo suggests" tag and the language).
const labelHeights = reactive({});
const LABEL_GAP = 6;

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
        ariaLabel: `${data.title}${t("common.labelSeparator")}${states.join(t("common.listSeparator"))}`,
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
        // No room above the anchor inside the visible frame (e.g. the phone overview, or a zone at
        // the top of a cropped view): show the label below the anchor instead of clipping it.
        labelBelow: box.y * s + pan.value.y < (labelHeights[zone.key] || 40) + LABEL_GAP,
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

  // Height left for the room in the viewport, below where the room starts (header + title).
  if (el && typeof window !== "undefined") {
    const top = el.getBoundingClientRect().top + window.scrollY;
    availableHeight.value = Math.max(0, window.innerHeight - top - BOTTOM_MARGIN);
    viewportHeightLimit.value = Math.max(0, window.innerHeight * PHONE_ROOM_SHARE);
  }
}

function measureLabels() {
  frame.value?.querySelectorAll(".zoneHitWrap").forEach((wrap) => {
    const height = wrap.querySelector(".zoneLabel")?.offsetHeight || 0;
    if (height && labelHeights[wrap.dataset.zone] !== height) labelHeights[wrap.dataset.zone] = height;
  });
}

let motionQuery = null;
function syncMotion() {
  reducedMotion.value = Boolean(motionQuery?.matches);
}

onUpdated(measureLabels);

onMounted(() => {
  if (typeof window !== "undefined" && window.matchMedia) {
    motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    syncMotion();
    motionQuery.addEventListener?.("change", syncMotion);
  }
  measure();
  nextTick(measureLabels);
  if (typeof ResizeObserver !== "undefined" && frame.value) {
    resizeObserver = new ResizeObserver(measure);
    resizeObserver.observe(frame.value);
  }
  if (typeof window !== "undefined") {
    window.addEventListener("resize", measure);
  }
});

onUnmounted(() => {
  resizeObserver?.disconnect();
  if (typeof window !== "undefined") window.removeEventListener("resize", measure);
  motionQuery?.removeEventListener?.("change", syncMotion);
});
</script>

<style scoped>
.roomFrame {
  display: grid;
  justify-items: center;
  min-width: 0;
  overflow: hidden;
}

.roomViewportWrap {
  position: relative;
  max-width: 100%;
}

/* The viewport only clips/scrolls the (always-LTR) room; in an RTL page a wider block would
   otherwise be anchored to the right edge and add to the pan offset. */
.roomViewport {
  position: relative;
  overflow: hidden;
  direction: ltr;
  border-radius: 6px;
}

/* The room is clipped to its viewport and the camera pans (and on phones zooms) in 300 ms. */
.roomViewport.panning .roomScene {
  transition: transform 300ms ease;
}

/* Phones: horizontal drags look around the overview; vertical swipes still scroll the page. */
.roomViewport.phone:not(.zoomed) {
  touch-action: pan-y;
  cursor: grab;
}

.roomViewport.dragging {
  cursor: grabbing;
}

.roomViewport.dragging .roomScene,
.roomViewport .roomScene.flipping {
  transition: none;
}

.roomCorner {
  position: absolute;
  z-index: 3;
  top: 8px;
  inset-inline-end: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Phones: the x1 room is too small for an overlay (it would cover the zone labels),
   so the chips sit in their own row above the room. */
@media (max-width: 599px) {
  .roomViewportWrap {
    display: flex;
    flex-direction: column;
  }

  /* 44px tall so the info button's 44px touch area is not clipped by the frame. */
  .roomCorner {
    position: static;
    order: -1;
    justify-content: flex-end;
    min-height: 44px;
    margin-bottom: 2px;
    padding-inline-end: 9px;
  }
}

.roomScene {
  position: relative;
  transform-origin: 0 0;
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

/* B21 materialize (spec §6): light rises 300 ms; ghost fades out while colour fades in 600 ms;
   1px settle drop 200 ms (base px: the layers are inside the scaled base); glint 500 ms. */
.lightLayer.lightHidden {
  opacity: 0;
}

.lightLayer.lightRise {
  animation: matLightRise 300ms ease-out both;
}

.ghostLayer.mat-resolve {
  animation: matGhostOut 600ms ease-in-out forwards;
}

.ghostLayer.mat-settle,
.ghostLayer.mat-glint {
  visibility: hidden;
}

.matColor.mat-resolve {
  animation: matColorIn 600ms ease-in-out both;
}

.matColor.mat-settle {
  animation: matSettle 200ms ease-in both;
}

.glintLayer {
  animation: matGlint 500ms ease-out both;
}

@keyframes matLightRise {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes matGhostOut {
  to { opacity: 0; }
}

@keyframes matColorIn {
  from { opacity: 0; transform: translateY(-1px); }
  to { opacity: 1; transform: translateY(-1px); }
}

@keyframes matSettle {
  from { transform: translateY(-1px); }
  to { transform: translateY(0); }
}

@keyframes matGlint {
  0% { opacity: 0; }
  30% { opacity: 1; }
  100% { opacity: 0; }
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

/* Keyboard focus only: a soft outline that follows the footprint polygon, stroked in base px
   (the SVG viewBox is in base px, so 1 unit = 1 room pixel at any scale, fractional too). */
.zoneOutline {
  position: absolute;
  overflow: visible;
  opacity: 0;
  pointer-events: none;
  transition: opacity 140ms ease;
}

.zoneOutline polygon {
  fill: none;
  stroke: rgba(150, 236, 255, 0.78);
  stroke-width: 1;
  stroke-linejoin: round;
  filter: drop-shadow(0 0 2px rgba(110, 229, 255, 0.55));
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

/* Flipped below the anchor when there is no room above it in the visible frame. */
.zoneLabel.below {
  transform: translate(-50%, 0) translateY(4px);
}

.zoneLabel small {
  color: rgba(110, 229, 255, 0.82);
  font-size: 0.66rem;
  font-weight: 800;
}

/* Zone label on hover, keyboard focus, selection and suggestion. No boxes: selection is the
   dim + light layers, a suggestion is its label only. */
.zoneHit:hover ~ .zoneLabel,
.zoneHit:focus-visible ~ .zoneLabel,
.zoneHitWrap.selected .zoneLabel,
.zoneHitWrap.suggested .zoneLabel {
  opacity: 1;
}

/* The footprint outline appears only for keyboard focus (never on a mouse click). */
.zoneHit:focus-visible ~ .zoneOutline {
  opacity: 1;
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
  .lightLayer.lightRise,
  .ghostLayer.mat-resolve,
  .matColor,
  .glintLayer {
    animation: none;
  }

  .zoneOutline,
  .zoneLabel,
  .roomViewport.panning .roomScene {
    transition: none;
  }
}
</style>
