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
        @scroll="onViewportScroll"
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
              :class="objectGlowClass(item, false)"
              draggable="false"
              :data-reward="item.key"
              :style="at(item.x, item.y)"
            />
            <template v-for="item in ghostObjects" :key="`ghost-${item.key}`">
              <img
                :src="asset(item.path)"
                alt=""
                class="layer ghostLayer"
                :class="[item.phase ? `mat-${item.phase}` : null, objectGlowClass(item, true)]"
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

            <img :src="asset(layout.overlay)" alt="" class="layer" draggable="false" />
          </div>

          <!-- HTML layer: zone hit regions and labels, in screen px. -->
          <div class="sceneHtml">
            <!-- B32 (D62): sparks and the name label of a tapped object, kept inside the frame. -->
            <div v-if="objectEffect" :key="`fx-${objectEffect.nonce}`" class="objectFx" :class="{ ghost: objectEffect.ghost }" aria-hidden="true">
              <svg
                v-for="spark in objectEffect.sparks"
                :key="spark.key"
                class="objectSpark"
                viewBox="0 0 10 10"
                :style="spark.style"
              ><path d="M5 0l1.2 3.8L10 5 6.2 6.2 5 10 3.8 6.2 0 5l3.8-1.2z" /></svg>
              <span v-if="objectEffect.label" class="objectLabel" :style="objectEffect.labelStyle">{{ objectEffect.label }}</span>
            </div>
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
                :tabindex="item.marker ? -1 : null"
                :aria-hidden="item.marker ? 'true' : null"
                :aria-label="item.ariaLabel"
                :aria-pressed="item.selected ? 'true' : 'false'"
                @click="$emit('select', item.zone)"
              />
              <!-- B30: read-only path marker (replaces the bell markers). Tapping it selects the zone. -->
              <button
                v-if="item.marker"
                type="button"
                class="pathMarker"
                :class="{
                  coloured: item.marker.coloured,
                  lit: item.marker.lit,
                  empty: item.marker.empty,
                  offFrame: item.marker.offFrame,
                  otherZone: item.marker.otherZone,
                }"
                :style="item.marker.style"
                :aria-label="item.marker.ariaLabel"
                :aria-pressed="item.selected ? 'true' : 'false'"
                :data-reminder="item.marker.reminder || null"
                :data-done-today="`${item.marker.doneToday}/${item.marker.joined}`"
                @click="$emit('select', item.zone)"
              >
                <svg class="pmRing" viewBox="0 0 40 40" aria-hidden="true">
                  <circle v-if="item.marker.empty" class="pmEmpty" cx="20" cy="20" :r="PM_RING_R" />
                  <circle
                    v-for="(segment, index) in item.marker.ring"
                    :key="index"
                    class="pmSegment"
                    :class="{ done: segment.done }"
                    cx="20"
                    cy="20"
                    :r="PM_RING_R"
                    :stroke-dasharray="segment.dasharray"
                    :stroke-dashoffset="segment.dashoffset"
                  />
                </svg>
                <span class="pmGlyph" :style="{ '--pm-icon': `url(${item.marker.iconUrl})` }" aria-hidden="true" />
                <span v-if="item.marker.allDoneToday" class="pmBadge" aria-hidden="true">
                  <svg viewBox="0 0 12 12"><path d="M2.6 6.3 5 8.6l4.4-5" /></svg>
                </span>
                <span v-if="item.marker.reminder" class="pmChip" :class="`is-${item.marker.reminder}`" aria-hidden="true">
                  <svg v-if="item.marker.reminder === 'telegram_off'" viewBox="0 0 16 16">
                    <path class="pmPlane" d="M14.2 2.3 1.9 7.1c-.5.2-.5.9 0 1.1l3 1 1.2 3.7c.1.4.7.5 1 .2l1.7-1.6 3.1 2.3c.4.3.9.1 1-.4l2.1-10.4c.1-.5-.4-.9-.8-.7ZM6.1 9.1l6.1-4.6-4.9 5.4-.3 2.1-.9-2.9Z" />
                  </svg>
                  <svg v-else viewBox="0 0 16 16">
                    <path class="pmBell" d="M8 1.6c-2.4 0-4.2 1.9-4.2 4.3v2.6L2.6 10.6c-.2.4 0 .8.5.8h9.8c.5 0 .7-.4.5-.8l-1.2-2.1V5.9c0-2.4-1.8-4.3-4.2-4.3ZM6.3 12.4a1.8 1.8 0 0 0 3.4 0Z" />
                  </svg>
                </span>
              </button>
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

            <!-- B30 S2/S3: the open zone's tray (D44, D45, D50). Challenge tray: its challenges. Mission
                 tray (a joined challenge is picked): the challenge icon, its paws, then "+N". Icons
                 only select (D13): the Ringo card answers for the tapped item. -->
            <div
              v-if="tray"
              class="challengeTray"
              :class="[`dir-${tray.dir}`, `mode-${tray.mode}`]"
              :style="tray.style"
              role="group"
              :aria-label="tray.label"
            >
              <span
                v-for="(row, index) in tray.rows"
                :key="`row-${index}`"
                class="trayFrame"
                :style="row"
                aria-hidden="true"
              />
              <span class="trayFlag" :style="tray.flagStyle" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path d="M7 3v18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                  <path d="M7 4.5h10.5l-3 4 3 4H7z" fill="currentColor" fill-opacity=".85" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" />
                </svg>
              </span>
              <button
                v-for="item in tray.items"
                :key="item.key"
                type="button"
                class="trayIcon"
                :class="[`is-${item.state}`, `kind-${item.kind}`, { selected: item.selected, bonus: item.bonus }]"
                :style="item.style"
                :aria-label="item.ariaLabel"
                :aria-pressed="item.kind === 'more' ? null : (item.selected ? 'true' : 'false')"
                :data-challenge="item.kind === 'challenge' ? item.id : null"
                :data-mission="item.kind === 'paw' ? item.id : null"
                :data-state="item.state"
                @click="onTrayItem(item)"
              >
                <template v-if="item.kind === 'more'">
                  <span class="trayMore" aria-hidden="true">{{ item.text }}</span>
                </template>
                <template v-else>
                  <span class="trayRing" aria-hidden="true" />
                  <span class="trayGlyph" :style="{ '--tray-icon': `url(${item.iconUrl})` }" aria-hidden="true" />
                  <span v-if="item.kind === 'challenge' && item.state === 'open'" class="trayPlus" aria-hidden="true">
                    <svg viewBox="0 0 12 12"><path d="M6 2.5v7M2.5 6h7" /></svg>
                  </span>
                  <span v-if="item.kind === 'challenge' && item.state === 'done'" class="trayDay" aria-hidden="true">{{ item.dayText }}</span>
                  <span v-if="item.kind === 'paw' && item.state === 'locked'" class="trayLock" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></svg>
                  </span>
                  <span v-if="item.reminder" class="pawChip" :class="`is-${item.reminder}`" aria-hidden="true">
                    <svg v-if="item.reminder === 'telegram_off'" viewBox="0 0 16 16">
                      <path class="pmPlane" d="M14.2 2.3 1.9 7.1c-.5.2-.5.9 0 1.1l3 1 1.2 3.7c.1.4.7.5 1 .2l1.7-1.6 3.1 2.3c.4.3.9.1 1-.4l2.1-10.4c.1-.5-.4-.9-.8-.7ZM6.1 9.1l6.1-4.6-4.9 5.4-.3 2.1-.9-2.9Z" />
                    </svg>
                    <svg v-else viewBox="0 0 16 16">
                      <path class="pmBell" d="M8 1.6c-2.4 0-4.2 1.9-4.2 4.3v2.6L2.6 10.6c-.2.4 0 .8.5.8h9.8c.5 0 .7-.4.5-.8l-1.2-2.1V5.9c0-2.4-1.8-4.3-4.2-4.3ZM6.3 12.4a1.8 1.8 0 0 0 3.4 0Z" />
                    </svg>
                  </span>
                </template>
              </button>
            </div>

            <!-- B30 S2 placement review only (?trayDebug=1): the selected zone's tray rect. -->
            <div
              v-if="trayDebugBox"
              class="trayDebug"
              :class="{ missing: trayDebugBox.missing }"
              :style="trayDebugBox.style"
              aria-hidden="true"
            >
              <span v-if="!trayDebugBox.missing" class="trayDebugFlag" :style="trayDebugBox.flagStyle" />
              <span class="trayDebugText">{{ trayDebugBox.text }}</span>
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
  TRAY_SCREEN,
  markerSpanPanX,
  placeTray,
  trayRect,
  trayScreenFactor,
  zoneObjects,
} from "@/lib/roomScene";
import { resolveChallengeIcon } from "@/utils/missionMomentumUtils";
import { todayMainDone } from "@/lib/livingSpacePanel";
import { missionPawState, pagePaws, trayMissions, trayRows } from "@/lib/missionTray";
import pawGlyph from "@/assets/missions-icons/paw_glyph.png";
import { REMINDER_CHIP, ringSegments } from "@/lib/pathMarker";

const props = defineProps({
  zones: { type: Array, default: () => [] },
  selectedZoneKey: { type: String, default: "" },
  // B30 S2: the challenge the Ringo card answers for (highlighted in the tray).
  selectedChallengeId: { type: [Number, String, null], default: null },
  // B30 S3: a challenge was tapped (its missions show) and the paw tapped.
  challengePicked: { type: Boolean, default: false },
  pickedMissionId: { type: [Number, String, null], default: null },
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
  // B32 (D62): { key, ghost, label, nonce } when an object tile is tapped: that object lifts and glows.
  objectHighlight: { type: Object, default: null },
});

const emit = defineEmits(["select", "select-challenge", "select-mission"]);

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
    const camera = cameraPan({ ...view, target: cameraTarget(layout, props.selectedZoneKey) });
    return props.phone ? nudgeToObject(camera, s) : camera;
  }

  const zoneKey = props.phone ? focusZoneKey.value : (props.rest ? "" : props.selectedZoneKey);
  // D46: the phone overview opens with the span of the five path markers centred.
  const x = props.phone && !zoneKey
    ? markerSpanPanX(layout, viewportWidth.value, s)
    : cameraPan({ ...view, target: cameraTarget(layout, zoneKey) }).x;
  const minX = Math.min(0, viewportWidth.value - baseWidth * s);
  return {
    x: props.phone ? Math.min(0, Math.max(minX, x + dragX.value)) : x,
    y: safeAreaPanY({ viewportHeight: viewportHeight.value, scale: s, safe }),
  };
});

// B32: on a phone a tapped object can sit at the edge of its zone's camera (Fitness at 360 px);
// while it is highlighted the camera moves just enough to show it whole (inset 12px).
function nudgeToObject(camera, s) {
  const item = objectFxItem.value;
  if (!item) return camera;
  const inset = 12;
  const lift = props.objectHighlight?.ghost ? 0 : 4;
  const vw = viewportWidth.value;
  const vh = viewportHeight.value;
  let { x, y } = camera;
  const x0 = item.x * s + x;
  const x1 = (item.x + item.w) * s + x;
  if (x1 > vw - inset) x -= x1 - (vw - inset);
  if (x0 + (x - camera.x) < inset) x += inset - (x0 + (x - camera.x));
  const y0 = (item.y - lift) * s + y;
  const y1 = (item.y + item.h) * s + y;
  if (y1 > vh - inset) y -= y1 - (vh - inset);
  if (y0 + (y - camera.y) < inset) y += inset - (y0 + (y - camera.y));
  return {
    x: Math.min(0, Math.max(vw - baseWidth * s, x)),
    y: Math.min(0, Math.max(vh - baseHeight * s, y)),
  };
}

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

// The camera (translate) is the only pan. Focusing an element outside the clipped frame makes the
// browser scroll the overflow-hidden viewport as well, which would double the offset: undo it.
function onViewportScroll(event) {
  const el = event.currentTarget;
  if (el.scrollLeft || el.scrollTop) {
    el.scrollLeft = 0;
    el.scrollTop = 0;
  }
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

// B30 S2 placement review: `?trayDebug=1` outlines the selected zone's challenge tray rect
// (room_layout.json `tray`, checked by test:room-trays). Not the real tray.
const trayDebug = typeof window !== "undefined" && new URLSearchParams(window.location.search).has("trayDebug");
const trayDebugBox = computed(() => {
  const key = props.selectedZoneKey;
  if (!trayDebug || !key || props.rest || !layout.zones?.[key]) return null;
  const s = scale.value;
  const zone = layout.zones[key];
  const rect = trayRect(zone.tray, s, { phone: props.phone });
  if (!rect) {
    const [x, y] = zone.path_marker || [0, 0];
    return {
      missing: true,
      text: `${key}: no tray placement`,
      style: { left: `${Math.round(x * s + 30)}px`, top: `${Math.round(y * s - 12)}px` },
    };
  }
  const [fx, fy] = zone.tray.flag;
  return {
    missing: false,
    text: `tray ${zone.tray.dir} · ${Math.round(rect.w * s)}x${Math.round(rect.h * s)}px`,
    style: {
      left: `${rect.x * s}px`,
      top: `${rect.y * s}px`,
      width: `${rect.w * s}px`,
      height: `${rect.h * s}px`,
    },
    flagStyle: { left: `${(fx - rect.x) * s}px`, top: `${(fy - rect.y) * s}px` },
  };
});

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

// B32 (D62): the tapped object's own layer lifts and glows (no copy, no outline, no redraw).
// Placed: ~4 base px up and a warm gold glow, settling by ~1.2 s, with a few sparks. Ghost: a pale
// blue glow. Reduced motion: no lift and no sparks, only a short soft glow.
const OBJECT_FX_MS = 1300;
const OBJECT_LABEL_MS = 2400;
const objectFxActive = ref(null);
let objectFxTimer = null;
let objectLabelTimer = null;
const objectLabelOn = ref(false);
// The label sits above the object unless that covers the zone's marker, tray or name: then below.
const objectLabelBelow = ref(false);
// Covered both above and below (a small phone frame): the label is left out; the card names it.
const objectLabelHidden = ref(false);

watch(() => props.objectHighlight?.nonce, () => {
  const fx = props.objectHighlight;
  clearTimeout(objectFxTimer);
  clearTimeout(objectLabelTimer);
  objectFxActive.value = null;
  objectLabelOn.value = false;
  objectLabelBelow.value = false;
  objectLabelHidden.value = false;
  if (!fx?.key) return;
  // Restart the animation on a repeated tap of the same object.
  nextTick(() => {
    objectFxActive.value = { ...fx };
    objectLabelOn.value = true;
    objectFxTimer = setTimeout(() => { objectFxActive.value = null; }, OBJECT_FX_MS);
    objectLabelTimer = setTimeout(() => { objectLabelOn.value = false; }, OBJECT_LABEL_MS);
    nextTick(placeObjectLabel);
  });
});

function placeObjectLabel() {
  const label = frame.value?.querySelector(".objectLabel");
  if (!label) return;
  const box = label.getBoundingClientRect();
  const overlaps = [...frame.value.querySelectorAll(".pathMarker, .trayFrame, .zoneLabel")].some((el) => {
    const style = getComputedStyle(el);
    if (!el.offsetParent || style.visibility === "hidden" || Number(style.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && box.left < r.right && box.right > r.left && box.top < r.bottom && box.bottom > r.top;
  });
  if (!overlaps) return;
  if (objectLabelBelow.value) {
    objectLabelHidden.value = true;
    return;
  }
  objectLabelBelow.value = true;
  nextTick(placeObjectLabel);
}

function objectGlowClass(item, ghost) {
  const fx = objectFxActive.value;
  if (!fx || fx.key !== item.key || Boolean(fx.ghost) !== ghost) return null;
  if (reducedMotion.value) return ghost ? "objGlowGhostSoft" : "objGlowSoft";
  return ghost ? "objGlowGhost" : "objLift";
}

const objectFxItem = computed(() => {
  const fx = props.objectHighlight;
  if (!fx?.key) return null;
  const list = fx.ghost ? ghostObjects.value : placedObjects.value;
  return list.find((item) => item.key === fx.key) || null;
});

const objectEffect = computed(() => {
  const fx = props.objectHighlight;
  const item = objectFxItem.value;
  if (!fx || !item || (!objectFxActive.value && !objectLabelOn.value)) return null;
  const s = scale.value;
  const frame = frameRect.value;
  const inset = 4;
  const clampX = (x, w) => Math.min(Math.max(x, frame.x0 + inset), frame.x1 - inset - w);
  const clampY = (y, h) => Math.min(Math.max(y, frame.y0 + inset), frame.y1 - inset - h);
  const size = 10;
  const sparks = objectFxActive.value && !fx.ghost && !reducedMotion.value
    ? [
      [item.x - 5, item.y - 3, 0],
      [item.x + item.w + 1, item.y - 5, 120],
      [item.x + item.w / 2, item.y - 10, 240],
      [item.x + item.w + 3, item.y + item.h - 6, 360],
    ].map(([bx, by, delay], index) => ({
      key: index,
      style: {
        left: `${clampX(bx * s - size / 2, size)}px`,
        top: `${clampY(by * s - size / 2, size)}px`,
        width: `${size}px`,
        height: `${size}px`,
        animationDelay: `${delay}ms`,
      },
    }))
    : [];
  const label = objectLabelOn.value && !objectLabelHidden.value ? fx.label || "" : "";
  // The label sits above the object, centred; its width is estimated for the clamp (12px text).
  const labelW = Math.min(240, 22 + String(label).length * 7);
  const labelH = 26;
  const lift = reducedMotion.value || fx.ghost ? 0 : 4;
  return {
    nonce: fx.nonce,
    ghost: Boolean(fx.ghost),
    sparks,
    label,
    labelStyle: {
      left: `${clampX((item.x + item.w / 2) * s - labelW / 2, labelW)}px`,
      top: `${clampY(objectLabelBelow.value ? (item.y + item.h) * s + 8 : (item.y - lift) * s - labelH - 8, labelH)}px`,
      maxWidth: `${labelW}px`,
    },
  };
});

onUnmounted(() => {
  clearTimeout(objectFxTimer);
  clearTimeout(objectLabelTimer);
});

// Ghost treatment from room_layout.json (spec §5); the 2x2 checker dither is a CSS mask.
const ghostStyle = {
  opacity: layout.ghost?.opacity ?? 0.38,
  filter: layout.ghost?.filter || "grayscale(1) brightness(1.5) sepia(.2) hue-rotate(180deg)",
};

// B30: path marker size in screen px. The ring grows with the room but stays readable at x1;
// the button (hit target) is never below 44px and the glyph never below 20px.
const PM_RING_R = 17;
const PM_REMINDER_KEYS = {
  [REMINDER_CHIP.DUE]: "space.scene.pathMarker.reminderDue",
  [REMINDER_CHIP.TELEGRAM_OFF]: "space.scene.pathMarker.reminderTelegramOff",
  [REMINDER_CHIP.SET]: "space.scene.pathMarker.reminderSet",
};

// Phones keep the x1 size (ring 34, glyph 20, hit 44) also while zoomed; desktop grows with the
// room scale up to ring 56, glyph 24, hit 56 at x3.
function pathMarkerSizes(s, phone = false) {
  const grow = phone ? 0 : Math.min(2, Math.max(0, s - 1));
  const ring = Math.round(34 + grow * 11);
  return { ring, hit: Math.max(44, ring), glyph: Math.round(20 + grow * 2) };
}

// Visual extents of the marker from its centre (screen px): ring, check badge (bottom right),
// reminder chip (top right). Must match the .pmBadge and .pmChip CSS below.
function pathMarkerExtents(state, ring) {
  const radius = ring / 2;
  const chip = state.reminder ? ring * 0.3 + 18 : 0;
  const badge = state.allDoneToday ? ring * 0.22 + 16 : 0;
  return {
    left: radius,
    right: Math.max(radius, chip, badge),
    up: Math.max(radius, chip),
    down: Math.max(radius, badge),
  };
}

const PM_CLAMP_INSET = 4;

function pathMarkerView(zone, data, s, clampTo = null) {
  const state = data?.pathMarker;
  const point = zone.path_marker;
  if (!state || !Array.isArray(point) || point.length !== 2) return null;

  const { ring, hit, glyph } = pathMarkerSizes(s, props.phone);
  const geometry = ringSegments(state.segments.length, PM_RING_R);
  const placed = (data.unlocked_objects || []).length;
  const parts = [data.title, t("space.scene.pathMarker.path", { path: state.title })];
  parts.push(state.empty
    ? t("space.scene.pathMarker.noneJoined")
    : t("space.scene.pathMarker.doneToday", { done: state.doneToday, joined: state.joined }));
  if (PM_REMINDER_KEYS[state.reminder]) parts.push(t(PM_REMINDER_KEYS[state.reminder]));
  parts.push(t("space.scene.objectsPlaced", { count: placed }));

  const extent = pathMarkerExtents(state, ring);
  let cx = point[0] * s;
  let cy = point[1] * s;
  // Phone zoom: keep the selected zone's marker (and its chip and badge) inside the visible
  // camera rect, inset by 4px. The anchors in room_layout.json do not move.
  if (clampTo) {
    cx = Math.min(Math.max(cx, clampTo.x0 + extent.left + PM_CLAMP_INSET), clampTo.x1 - extent.right - PM_CLAMP_INSET);
    cy = Math.min(Math.max(cy, clampTo.y0 + extent.up + PM_CLAMP_INSET), clampTo.y1 - extent.down - PM_CLAMP_INSET);
  }

  return {
    ...state,
    ring: state.segments.map((segment, index) => ({ ...segment, ...geometry[index] })),
    ariaLabel: parts.filter(Boolean).join(t("common.listSeparator")),
    top: cy - extent.up,
    bottom: cy + extent.down,
    // For the tray: the marker's visual extents, but never less than its hit area.
    geometry: {
      cx,
      cy,
      ax: point[0] * s,
      ay: point[1] * s,
      left: Math.max(extent.left, hit / 2),
      right: Math.max(extent.right, hit / 2),
      up: Math.max(extent.up, hit / 2),
      down: Math.max(extent.down, hit / 2),
    },
    style: {
      left: `${Math.round(cx - hit / 2)}px`,
      top: `${Math.round(cy - hit / 2)}px`,
      "--pm-hit": `${hit}px`,
      "--pm-ring": `${ring}px`,
      "--pm-glyph": `${glyph}px`,
      ...(state.coloured ? { "--pm-color": state.color } : {}),
    },
  };
}

// Measured label sizes (they differ with the "Ringo suggests" tag and the language).
const labelHeights = reactive({});
const labelWidths = reactive({});
const LABEL_GAP = 6;
const LABEL_FRAME_INSET = 4;

// Visible camera rect in scene px.
const frameRect = computed(() => ({
  x0: -pan.value.x,
  y0: -pan.value.y,
  x1: -pan.value.x + viewportWidth.value,
  y1: -pan.value.y + viewportHeight.value,
}));

// A zone is open (its panel or sheet shows): the room is not at rest and a zone is selected.
const openZoneKey = computed(() => (!props.rest && props.selectedZoneKey) || "");

// Phone zoom: the selected zone's marker is clamped inside the frame. Phone overview: a marker
// whose anchor is in view is clamped inside it; one whose anchor is out of view is hidden (it stays
// focusable, and focus pans the room to its zone). While a zone is open the other zones' markers
// are hidden too (D23); they stay in the Tab order and show again on keyboard focus.
function markerFor(zone, data, s) {
  const frame = frameRect.value;
  const anchor = zone.path_marker || [];
  const anchorInFrame = anchor.length === 2
    && anchor[0] * s >= frame.x0 && anchor[0] * s <= frame.x1
    && anchor[1] * s >= frame.y0 && anchor[1] * s <= frame.y1;
  const overview = props.phone && !zoomed.value;
  const clampTo = (zoomed.value && props.selectedZoneKey === zone.key) || (overview && anchorInFrame)
    ? frame
    : null;
  const marker = pathMarkerView(zone, data, s, clampTo);
  if (marker) {
    marker.offFrame = overview && !anchorInFrame;
    marker.otherZone = Boolean(openZoneKey.value) && openZoneKey.value !== zone.key;
  }
  return marker;
}

// B30 S2: the open zone's challenge tray (D44, D45), screen px in scene coordinates.
const TRAY_DAY_STATES = { open: "open", joined: "joined", done: "done" };
const PM_REMINDER_ARIA = {
  [REMINDER_CHIP.DUE]: "space.scene.pathMarker.reminderDue",
  [REMINDER_CHIP.TELEGRAM_OFF]: "space.scene.pathMarker.reminderTelegramOff",
  [REMINDER_CHIP.SET]: "space.scene.pathMarker.reminderSet",
};

function trayChallengeState(challenge) {
  if (!challenge?.isJoined) return TRAY_DAY_STATES.open;
  return challenge.todayChecked ? TRAY_DAY_STATES.done : TRAY_DAY_STATES.joined;
}

function challengeEntry(challenge, selected) {
  const state = trayChallengeState(challenge);
  const name = challenge.name || t("common.challenge");
  const day = Number(challenge.totalCheckins || 0);
  return {
    kind: "challenge",
    key: `challenge-${challenge.id}`,
    id: challenge.id,
    challenge,
    state,
    selected,
    iconUrl: resolveChallengeIcon({ icon_key: challenge.iconKey, name: challenge.name }),
    dayText: t("space.scene.tray.day", { n: day }),
    ariaLabel: t(`space.scene.tray.${state}`, { name, n: day }),
  };
}

// D19, D20, D32: open (white paw, ring), locked (grey, lock, dim ring), done (large lime paw, no
// ring); Bonus: dashed ring, done = large gold paw. Reminder chip in its own slot (D21, D51).
function pawEntry(mission, mainDone) {
  const { state, bonus } = missionPawState(mission, { mainDone });
  const name = mission.title || t("common.mission");
  const parts = [t(`space.scene.missionTray.${bonus ? "bonus" : "mission"}${state[0].toUpperCase()}${state.slice(1)}`, { name })];
  if (PM_REMINDER_ARIA[mission.reminder]) parts.push(t(PM_REMINDER_ARIA[mission.reminder]));
  return {
    kind: "paw",
    key: `paw-${mission.id}`,
    id: mission.id,
    mission,
    state,
    bonus,
    reminder: mission.reminder || "",
    selected: String(props.pickedMissionId ?? "") === String(mission.id ?? ""),
    iconUrl: pawGlyph,
    ariaLabel: parts.join(t("common.listSeparator")),
  };
}

// B30 S3: which page of paws the mission tray shows (reset when the picked challenge changes).
const missionPage = ref({ challengeId: null, page: 0 });
watch(
  () => [openZoneKey.value, props.selectedChallengeId, props.challengePicked],
  () => {
    missionPage.value = { challengeId: null, page: 0 };
  },
);

const tray = computed(() => {
  const key = openZoneKey.value;
  const zone = key ? orderedLayoutZones.value.find((item) => item.key === key) : null;
  const data = key ? zonesByKey.value[key] : null;
  const challenges = data?.pathDetail?.challenges || [];
  if (!zone?.tray || !data || !challenges.length) return null;

  const s = scale.value;
  const k = trayScreenFactor(s, { phone: props.phone });
  const flag = TRAY_SCREEN.flag * k;
  const icon = TRAY_SCREEN.icon * k;
  const pad = TRAY_SCREEN.pad * k;
  const rowH = TRAY_SCREEN.height * k;
  const fixed = flag / 2 + pad * 2;

  // Mission tray once a joined challenge is picked (D50); otherwise the challenge tray.
  const picked = props.challengePicked
    ? challenges.find((challenge) => String(challenge.id ?? "") === String(props.selectedChallengeId ?? ""))
    : null;
  const mode = picked?.isJoined ? "missions" : "challenges";

  let entries;
  let pitch = TRAY_SCREEN.pitch * k;
  let rowCounts;
  if (mode === "missions") {
    const missions = trayMissions(picked.missions || []);
    const mainDone = todayMainDone(picked.missions || []);
    // Room for icons per row (screen px): the zone's clear run on desktop (plus its second row, if
    // any), the visible frame on phones (the tray is clamped into it, with a row below).
    // A desktop row ends where the x2 row ends (flag edge at x2 + run), so the room for icons is
    // (run - 7) base px minus the padding, at any scale.
    const rowRoom = props.phone
      ? [viewportWidth.value - 8 - fixed, viewportWidth.value - 8 - fixed]
      : [(zone.tray.run - 7) * s - pad * 2, ...(zone.tray.wrap ? [(zone.tray.wrap.run - 7) * s - pad * 2] : [])];
    const sizing = trayRows({ pawCount: missions.length, rows: rowRoom, pitches: [48 * k, 44 * k] });
    const page = missionPage.value.challengeId === picked.id ? missionPage.value.page : 0;
    const paged = pagePaws(missions, { slots: sizing.slots, page });
    const control = paged.control;
    entries = [
      challengeEntry(picked, true),
      ...paged.visible.map((mission) => pawEntry(mission, mainDone)),
      // Pager in the same row (no extra space, no list): "+N" shows the next paws, the last page
      // gets a back control to the first. The label is Ringo's one line, "N more steps".
      ...(control
        ? [{
          kind: "more",
          key: `pager-${control.kind}`,
          state: control.kind,
          pager: control,
          challengeId: picked.id,
          text: control.kind === "next" ? t("space.scene.missionTray.moreChip", { count: control.count }) : "‹",
          ariaLabel: control.kind === "next"
            ? t("space.scene.missionTray.moreAria", { count: control.count })
            : t("space.scene.missionTray.backAria"),
          selected: false,
        }]
        : []),
    ];
    pitch = sizing.pitch;
    const first = Math.min(entries.length, sizing.perRow[0] || entries.length);
    rowCounts = first < entries.length ? [first, entries.length - first] : [entries.length];
  } else {
    entries = challenges.slice(0, 3).map((challenge) => {
      return challengeEntry(challenge, String(props.selectedChallengeId ?? "") === String(challenge.id ?? ""));
    });
    rowCounts = [entries.length];
  }

  // Rows inside one block: row 1 on the anchor row, row 2 at the layout's wrap offset (desktop) or
  // just below (phone). Widths in screen px; the flag sits on row 1's start edge.
  const rowGap = 4 * k;
  const secondDy = props.phone || !zone.tray.wrap ? rowH + rowGap : zone.tray.wrap.dy * s;
  const rowWidth = (count) => fixed + count * pitch;
  const blockW = Math.max(...rowCounts.map(rowWidth));
  const rowTops = rowCounts.map((_, index) => (index === 0 ? 0 : secondDy));
  const minTop = Math.min(...rowTops);
  const blockH = Math.max(...rowTops) - minTop + rowH;
  const [fx, fy] = zone.tray.flag;
  const dir0 = zone.tray.dir;
  const anchorRect = {
    x: dir0 === "left" ? fx * s + flag / 2 - blockW : fx * s - flag / 2,
    y: fy * s - rowH / 2 + minTop,
    w: blockW,
    h: blockH,
  };
  const marker = markerFor(zone, data, s);
  const rect = placeTray({
    rect: anchorRect,
    dir: dir0,
    marker: marker?.geometry || null,
    frame: props.phone ? frameRect.value : null,
  });
  if (!rect) return null;

  const left = rect.dir === "left";
  const rowStyles = rowCounts.map((count, index) => {
    const width = rowWidth(count) - flag / 2;
    return {
      top: `${rowTops[index] - minTop}px`,
      height: `${rowH}px`,
      left: `${left ? blockW - flag / 2 - width : flag / 2}px`,
      width: `${width}px`,
    };
  });
  let cursor = 0;
  const items = entries.map((entry) => {
    const row = rowCounts[0] > cursor ? 0 : 1;
    const indexInRow = row === 0 ? cursor : cursor - rowCounts[0];
    cursor += 1;
    const offset = flag / 2 + pad + indexInRow * pitch + (pitch - icon) / 2;
    return {
      ...entry,
      style: {
        left: `${left ? blockW - offset - icon : offset}px`,
        top: `${rowTops[row] - minTop + (rowH - icon) / 2}px`,
        width: `${icon}px`,
        height: `${icon}px`,
      },
    };
  });

  return {
    mode,
    dir: rect.dir,
    rect,
    items,
    rows: rowStyles,
    label: mode === "missions"
      ? t("space.scene.missionTray.label", { challenge: picked.name || t("common.challenge") })
      : t("space.scene.tray.label", { path: data.pathMarker?.title || data.title }),
    style: {
      left: `${rect.x}px`,
      top: `${rect.y}px`,
      width: `${rect.w}px`,
      height: `${rect.h}px`,
      "--tray-k": k,
    },
    flagStyle: { left: `${left ? blockW - flag / 2 : flag / 2}px`, top: `${-minTop + rowH / 2}px` },
  };
});

// A tray icon: a challenge selects it (in the mission tray the challenge icon goes back to the
// challenge tray), a paw selects the mission, "+N" asks Ringo to explain the rest.
function onTrayItem(item) {
  if (item.kind === "challenge") {
    emit("select-challenge", tray.value?.mode === "missions" ? null : item.challenge);
  } else if (item.kind === "paw") {
    emit("select-mission", item.mission);
  } else if (item.kind === "more" && item.pager) {
    missionPage.value = { challengeId: item.challengeId, page: item.pager.page };
    // Keep keyboard focus on the pager slot after the paws swap.
    nextTick(() => frame.value?.querySelector(".challengeTray .trayIcon.kind-more")?.focus());
  }
}

function boxesOverlap(a, b) {
  return a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
}

const hitZones = computed(() => {
  const s = scale.value;
  const frame = frameRect.value;
  const trayBox = tray.value
    ? { x0: tray.value.rect.x, y0: tray.value.rect.y, x1: tray.value.rect.x + tray.value.rect.w, y1: tray.value.rect.y + tray.value.rect.h }
    : null;

  return orderedLayoutZones.value
    .filter((zone) => zonesByKey.value[zone.key])
    .map((zone) => {
      const data = zonesByKey.value[zone.key];
      const box = footprintBox(zone.footprint);
      const marker = markerFor(zone, data, s);
      // The label stays centred on the footprint (clamped inside the visible frame) and never
      // covers the path marker: above the marker (and its chip), or below it when there is no room
      // above in the visible frame. It never touches the open zone's tray either: it flips to the
      // other side of the marker, or goes below the tray.
      const labelH = labelHeights[zone.key] || 40;
      const labelW = labelWidths[zone.key] || 0;
      let labelX = (box.x + box.w / 2) * s;
      if (labelW && frame.x1 - frame.x0 > labelW + LABEL_FRAME_INSET * 2) {
        labelX = Math.min(Math.max(labelX, frame.x0 + labelW / 2 + LABEL_FRAME_INSET), frame.x1 - labelW / 2 - LABEL_FRAME_INSET);
      }
      const labelAbove = marker ? Math.min(box.y * s, marker.top) : box.y * s;
      const labelBelowTop = marker ? Math.max(box.y * s, marker.bottom) : box.y * s;
      let labelBelow = labelAbove + pan.value.y < labelH + LABEL_GAP;
      let labelTop = labelBelow ? labelBelowTop : labelAbove;
      if (trayBox && zone.key === openZoneKey.value) {
        const spanX = { x0: labelX - labelW / 2, x1: labelX + labelW / 2 };
        const boxAt = (below, top) => (below
          ? { ...spanX, y0: top + 4, y1: top + 4 + labelH }
          : { ...spanX, y0: top - 4 - labelH, y1: top - 4 });
        if (boxesOverlap(boxAt(labelBelow, labelTop), trayBox)) {
          const flipped = labelBelow ? labelAbove : labelBelowTop;
          // Flipping up needs room above inside the visible frame; flipping down always fits.
          const roomToFlip = labelBelow ? flipped + pan.value.y >= labelH + LABEL_GAP : true;
          if (roomToFlip && !boxesOverlap(boxAt(!labelBelow, flipped), trayBox)) {
            labelBelow = !labelBelow;
            labelTop = flipped;
          } else {
            labelBelow = true;
            labelTop = trayBox.y1;
          }
        }
      }
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
        marker,
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
          left: `${labelX}px`,
          top: `${labelTop}px`,
        },
        // No room above the anchor inside the visible frame (e.g. the phone overview, or a zone at
        // the top of a cropped view): show the label below the anchor instead of clipping it.
        labelBelow,
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
    const label = wrap.querySelector(".zoneLabel");
    const height = label?.offsetHeight || 0;
    const width = label?.offsetWidth || 0;
    if (height && labelHeights[wrap.dataset.zone] !== height) labelHeights[wrap.dataset.zone] = height;
    if (width && labelWidths[wrap.dataset.zone] !== width) labelWidths[wrap.dataset.zone] = width;
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

/* B32 (D62): lift ~4 base px in 250 ms, hold, settle over ~700 ms; the warm glow fades by ~1.2 s.
   Translate is in base px (the layer is inside the scaled base). No outline anywhere. */
.layer.objLift {
  animation: objLift 1200ms ease-out both;
}

.ghostLayer.objGlowGhost {
  -webkit-mask-image: none;
  mask-image: none;
  animation: objGhostGlow 1200ms ease-out both;
}

.layer.objGlowSoft {
  animation: objGlowSoft 600ms ease-out both;
}

.ghostLayer.objGlowGhostSoft {
  -webkit-mask-image: none;
  mask-image: none;
  animation: objGhostGlowSoft 600ms ease-out both;
}

@keyframes objLift {
  0% { transform: translateY(0); filter: none; }
  21% { transform: translateY(-4px); filter: brightness(1.15) sepia(.3) drop-shadow(0 0 3px rgba(247, 215, 116, .95)) drop-shadow(0 0 8px rgba(247, 215, 116, .5)); }
  42% { transform: translateY(-4px); filter: brightness(1.15) sepia(.3) drop-shadow(0 0 3px rgba(247, 215, 116, .9)) drop-shadow(0 0 8px rgba(247, 215, 116, .45)); }
  100% { transform: translateY(0); filter: none; }
}

@keyframes objGhostGlow {
  0% { opacity: .38; filter: grayscale(1) brightness(1.5); }
  25%, 55% { opacity: .85; filter: grayscale(1) brightness(1.7) drop-shadow(0 0 4px rgba(170, 205, 255, .9)) drop-shadow(0 0 9px rgba(170, 205, 255, .45)); }
  100% { opacity: .38; filter: grayscale(1) brightness(1.5); }
}

@keyframes objGlowSoft {
  0%, 100% { filter: none; }
  40% { filter: brightness(1.1) drop-shadow(0 0 3px rgba(247, 215, 116, .7)); }
}

@keyframes objGhostGlowSoft {
  0%, 100% { opacity: .38; filter: grayscale(1) brightness(1.5); }
  40% { opacity: .7; filter: grayscale(1) brightness(1.6) drop-shadow(0 0 3px rgba(170, 205, 255, .7)); }
}

.objectFx {
  position: absolute;
  inset: 0;
  z-index: 4;
  pointer-events: none;
}

.objectSpark {
  position: absolute;
  fill: #f7d774;
  opacity: 0;
  animation: objSpark 900ms ease-out both;
}

@keyframes objSpark {
  0% { opacity: 0; transform: scale(.4); }
  30% { opacity: 1; transform: scale(1); }
  100% { opacity: 0; transform: scale(.6) translateY(-3px); }
}

.objectLabel {
  position: absolute;
  overflow: hidden;
  padding: 4px 10px;
  border-radius: 999px;
  color: #fff;
  background: rgba(11, 14, 20, .94);
  border: 1px solid rgba(255, 255, 255, .18);
  font-size: 12px;
  line-height: 16px;
  white-space: nowrap;
  text-overflow: ellipsis;
  animation: objLabelIn 200ms ease-out both;
}

@keyframes objLabelIn {
  from { opacity: 0; }
  to { opacity: 1; }
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
  z-index: 2;
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
.pathMarker:hover ~ .zoneLabel,
.pathMarker:focus-visible ~ .zoneLabel,
.zoneHitWrap.selected .zoneLabel,
.zoneHitWrap.suggested .zoneLabel {
  opacity: 1;
}

/* The footprint outline appears only for keyboard focus (never on a mouse click). */
.zoneHit:focus-visible ~ .zoneOutline,
.pathMarker:focus-visible ~ .zoneOutline {
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

/* B30: read-only path marker, daily (D44). Neutral grey until a challenge in the path is done
   today, then the path's own colour (--pm-color). The glyph is the path icon tinted through a CSS mask
   (currentColor), not .iconOnDark (that filter can only make white). Physical corners: the room
   never mirrors. */
.pathMarker {
  --pm-neutral: #a3abb8;
  position: absolute;
  z-index: 1;
  display: grid;
  place-items: center;
  width: var(--pm-hit);
  height: var(--pm-hit);
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 50%;
  color: var(--pm-neutral);
  background: transparent;
  cursor: pointer;
  pointer-events: auto;
  -webkit-tap-highlight-color: transparent;
}

.pathMarker.offFrame,
.pathMarker.otherZone {
  opacity: 0;
  pointer-events: none;
}

/* Hidden markers stay in the Tab order and show again on keyboard focus. */
.pathMarker.otherZone:focus-visible {
  opacity: 1;
}

/* B30 S2: challenge tray (D44, D45). Sizes scale with --tray-k (1 at x2 and on phones). */
.challengeTray {
  position: absolute;
  z-index: 1;
}

.trayFrame {
  position: absolute;
  border-radius: 999px;
  background: rgba(10, 12, 18, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.trayFlag {
  position: absolute;
  z-index: 1;
  display: grid;
  place-items: center;
  width: calc(28px * var(--tray-k));
  height: calc(28px * var(--tray-k));
  box-sizing: border-box;
  border-radius: 50%;
  color: #b4bac6;
  background: #090d17;
  border: 1px solid rgba(127, 125, 125, 0.78);
  transform: translate(-50%, -50%);
}

.trayFlag svg {
  width: 55%;
  height: 55%;
}

.trayIcon {
  position: absolute;
  z-index: 1;
  display: grid;
  place-items: center;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 50%;
  color: #aeb4c0;
  background: transparent;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.trayIcon:focus-visible {
  outline: 2px solid rgba(150, 236, 255, 0.92);
  outline-offset: 1px;
}

.trayRing {
  position: absolute;
  inset: calc(4px * var(--tray-k));
  box-sizing: border-box;
  border-radius: 50%;
  background: rgba(11, 14, 20, 0.86);
  border: 3px solid rgba(255, 255, 255, 0.26);
}

.trayGlyph {
  position: relative;
  width: calc(20px * var(--tray-k));
  height: calc(20px * var(--tray-k));
  background-color: currentColor;
  -webkit-mask: var(--tray-icon) center / contain no-repeat;
  mask: var(--tray-icon) center / contain no-repeat;
}

/* Needs joining: white dashed ring and a plus badge. */
.trayIcon.is-open {
  color: #eef0f5;
}

.trayIcon.is-open .trayRing {
  border: 2px dashed rgba(238, 240, 245, 0.9);
}

.trayPlus {
  position: absolute;
  right: 0;
  bottom: 0;
  display: grid;
  place-items: center;
  width: 16px;
  height: 16px;
  box-sizing: border-box;
  border-radius: 50%;
  background: #0b0e14;
  border: 1.5px solid #eef0f5;
}

.trayPlus svg {
  width: 10px;
  height: 10px;
  fill: none;
  stroke: #eef0f5;
  stroke-width: 2;
  stroke-linecap: round;
}

/* Done today: lime ring with a glow and the Day N pill (Day N = counted check-ins). */
.trayIcon.is-done {
  color: #a3e635;
}

.trayIcon.is-done .trayRing {
  border-color: #a3e635;
  box-shadow: 0 0 8px 1px rgba(163, 230, 53, 0.45);
}

.trayDay {
  position: absolute;
  left: 50%;
  bottom: calc(-6px * var(--tray-k));
  padding: 0 5px;
  border-radius: 999px;
  color: #10160a;
  background: #a3e635;
  font-size: 10px;
  font-weight: 800;
  line-height: 14px;
  white-space: nowrap;
  transform: translateX(-50%);
}

/* B30 S3: paws (S0 canvas). Open: white paw, plain ring. */
.trayIcon.kind-paw {
  color: #e6e9ef;
}

/* Locked: grey paw, dim ring, a lock badge. Tapping it only opens Ringo's explanation (D20). */
.trayIcon.kind-paw.is-locked {
  color: rgba(139, 147, 163, 0.75);
}

.trayIcon.kind-paw.is-locked .trayRing {
  border-color: rgba(255, 255, 255, 0.14);
}

.trayLock {
  position: absolute;
  right: 0;
  bottom: 0;
  display: grid;
  place-items: center;
  width: 16px;
  height: 16px;
  box-sizing: border-box;
  border-radius: 50%;
  background: #0b0e14;
  border: 1.5px solid #8b93a3;
}

.trayLock svg {
  width: 10px;
  height: 10px;
  fill: none;
  stroke: #8b93a3;
  stroke-width: 2.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* Bonus: dashed ring (white when open, grey when locked). */
.trayIcon.kind-paw.bonus .trayRing {
  border: 2px dashed rgba(238, 240, 245, 0.85);
}

.trayIcon.kind-paw.bonus.is-locked .trayRing {
  border-color: rgba(139, 147, 163, 0.7);
}

/* Done today: no ring, a larger paw (44px at x2, D32); lime, or gold for a Bonus. */
.trayIcon.kind-paw.is-done {
  color: #a3e635;
}

.trayIcon.kind-paw.is-done.bonus {
  color: #f7d774;
}

.trayIcon.kind-paw.is-done .trayRing {
  border: 0;
  background: transparent;
}

.trayIcon.kind-paw.is-done .trayGlyph {
  width: calc(44px * var(--tray-k));
  height: calc(44px * var(--tray-k));
}

/* Reminder chip in its own slot, top right, outside the ring (D21): set, due, Telegram off. */
.pawChip {
  position: absolute;
  right: -4px;
  top: -4px;
  display: grid;
  place-items: center;
  width: 16px;
  height: 16px;
  box-sizing: border-box;
  border-radius: 50%;
}

.pawChip svg {
  width: 10px;
  height: 10px;
}

.pawChip.is-due {
  background: #ffb759;
  box-shadow: 0 0 0 1.5px rgba(6, 10, 18, 0.9);
}

.pawChip.is-due .pmBell {
  fill: #05090f;
}

.pawChip.is-telegram_off {
  background: #05090f;
  border: 1.5px solid #ee312a;
}

.pawChip.is-telegram_off .pmPlane {
  fill: #ee312a;
}

.pawChip.is-set {
  background: #05090f;
  border: 1.5px solid #ffffff;
}

.pawChip.is-set .pmBell {
  fill: #ffb759;
}

/* "+N": more missions than paws; Ringo explains them (D50). */
.trayIcon.kind-more {
  color: #eef0f5;
}

.trayMore {
  display: grid;
  place-items: center;
  width: calc(36px * var(--tray-k));
  height: calc(36px * var(--tray-k));
  box-sizing: border-box;
  border-radius: 50%;
  background: rgba(11, 14, 20, 0.86);
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  font-size: 12px;
  font-weight: 800;
}

.trayIcon.kind-more.selected .trayMore {
  border-color: #ffffff;
}

/* The challenge the Ringo card answers for. */
.trayIcon.selected .trayRing {
  outline: 1.5px solid #ffffff;
  outline-offset: 2px;
}

.pathMarker.coloured {
  color: var(--pm-color, var(--pm-neutral));
}

.pathMarker::before {
  content: "";
  position: absolute;
  width: var(--pm-ring);
  height: var(--pm-ring);
  border-radius: 50%;
  background: rgba(6, 10, 18, 0.78);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.45);
  transition: box-shadow 200ms ease;
}

.pathMarker.lit::before {
  box-shadow:
    0 0 0 1px color-mix(in srgb, currentColor 45%, transparent),
    0 0 10px 2px color-mix(in srgb, currentColor 55%, transparent);
}

.pathMarker:focus-visible {
  outline: 2px solid rgba(150, 236, 255, 0.92);
  outline-offset: 1px;
}

.pmRing {
  position: absolute;
  width: var(--pm-ring);
  height: var(--pm-ring);
  overflow: visible;
}

.pmRing circle {
  fill: none;
  stroke-width: 3;
}

.pmEmpty {
  stroke: var(--pm-neutral);
  stroke-dasharray: 3 3.2;
  opacity: 0.7;
}

.pmSegment {
  stroke: rgba(163, 171, 184, 0.34);
  transition: stroke 200ms ease;
}

.pmSegment.done {
  stroke: currentColor;
}

.pmGlyph {
  position: relative;
  width: var(--pm-glyph);
  height: var(--pm-glyph);
  background-color: currentColor;
  -webkit-mask: var(--pm-icon) center / contain no-repeat;
  mask: var(--pm-icon) center / contain no-repeat;
}

.pathMarker.lit .pmGlyph {
  filter: drop-shadow(0 0 3px currentColor);
}

/* Every joined challenge done today: check badge on the ring, bottom right. */
.pmBadge {
  position: absolute;
  left: calc(50% + var(--pm-ring) * 0.22);
  top: calc(50% + var(--pm-ring) * 0.22);
  display: grid;
  place-items: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 0 2px rgba(6, 10, 18, 0.9);
}

.pmBadge svg {
  width: 11px;
  height: 11px;
  fill: none;
  stroke: #05090f;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* Reminder chip: its own slot top right, outside the ring and apart from the badge. */
.pmChip {
  position: absolute;
  left: calc(50% + var(--pm-ring) * 0.3);
  top: calc(50% - var(--pm-ring) * 0.3 - 18px);
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  box-sizing: border-box;
}

.pmChip svg {
  width: 12px;
  height: 12px;
}

.pmChip.is-due {
  background: #ffb759;
  box-shadow: 0 0 0 1.5px rgba(6, 10, 18, 0.9);
}

.pmChip.is-due .pmBell {
  fill: #05090f;
}

.pmChip.is-telegram_off {
  background: #05090f;
  border: 1.5px solid #ee312a;
}

.pmChip.is-telegram_off .pmPlane {
  fill: #ee312a;
}

.pmChip.is-set {
  background: #05090f;
  border: 1.5px solid #ffffff;
}

.pmChip.is-set .pmBell {
  fill: #ffb759;
}

.trayDebug {
  position: absolute;
  z-index: 3;
  box-sizing: border-box;
  border: 2px dashed #ff4fd8;
  border-radius: 999px;
  background: rgba(255, 79, 216, 0.16);
  pointer-events: none;
}

.trayDebug.missing {
  border-radius: 6px;
  padding: 2px 6px;
  background: rgba(40, 0, 30, 0.85);
}

.trayDebugFlag {
  position: absolute;
  width: 8px;
  height: 8px;
  margin: -4px 0 0 -4px;
  border-radius: 50%;
  background: #ff4fd8;
}

.trayDebugText {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 2px);
  transform: translateX(-50%);
  padding: 1px 6px;
  border-radius: 4px;
  color: #fff;
  background: rgba(40, 0, 30, 0.85);
  font: 600 10px/1.4 ui-monospace, monospace;
  white-space: nowrap;
}

.trayDebug.missing .trayDebugText {
  position: static;
  transform: none;
  padding: 0;
  background: none;
}

@media (prefers-reduced-motion: reduce) {
  .pathMarker::before,
  .pmSegment {
    transition: none;
  }

  .lightLayer.lightRise,
  .ghostLayer.mat-resolve,
  .matColor,
  .glintLayer {
    animation: none;
  }

  /* B32: no lift and no sparks, only a short soft glow (also before the JS media check runs). */
  .layer.objLift {
    animation: objGlowSoft 600ms ease-out both;
  }

  .ghostLayer.objGlowGhost {
    animation: objGhostGlowSoft 600ms ease-out both;
  }

  .objectSpark {
    display: none;
  }

  .zoneOutline,
  .zoneLabel,
  .roomViewport.panning .roomScene {
    transition: none;
  }
}
</style>
