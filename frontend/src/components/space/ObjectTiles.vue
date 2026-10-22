<template>
  <!-- B32 (D60): five tiles per zone replace the "Objects in this corner" dropdown. -->
  <section class="objectTiles" :aria-labelledby="headingId">
    <div class="objectTilesHead">
      <h4 :id="headingId">{{ t("space.panel.rowObjects") }}</h4>
      <span>{{ t("space.objectGrid.inRoomCount", { count: placedCount }) }}</span>
    </div>
    <div class="objectTilesRow" role="group" :aria-labelledby="headingId">
      <button
        v-for="tile in tiles"
        :key="tile.key"
        type="button"
        class="objectTile"
        :class="[tile.state, { selected: tile.key === selectedKey }]"
        :aria-label="tileLabel(tile)"
        :aria-pressed="tile.key === selectedKey ? 'true' : 'false'"
        :data-reward="tile.key"
        :data-state="tile.state"
        @click="$emit('pick', tile)"
      >
        <img
          v-if="tile.state !== 'later' && art(tile)"
          :src="art(tile)"
          alt=""
          class="objectTileArt"
          :class="{ ghostArt: tile.state === 'next' }"
          :style="artStyle(tile)"
          draggable="false"
          @load="rememberSize(tile, $event)"
        />
        <svg
          v-else
          class="objectTileSilhouette"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <component :is="shape[0]" v-for="(shape, index) in kindSilhouette(tile.kind)" :key="index" v-bind="shape[1]" />
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive } from "vue";
import { useI18n } from "vue-i18n";
import { numberAwareT } from "@/lib/i18nNumbers";
import { TILE_STATE, kindSilhouette } from "@/lib/objectsGrid";
import { objectAssetPath, pixelIconScale } from "@/lib/roomScene";

const props = defineProps({
  tiles: { type: Array, default: () => [] },
  selectedKey: { type: String, default: "" },
});

defineEmits(["pick"]);

const { locale, t: baseT } = useI18n();
const t = numberAwareT(baseT, () => locale.value);
const headingId = `objectTiles-${Math.random().toString(36).slice(2, 8)}`;

const ART = Object.fromEntries(
  Object.entries(import.meta.glob("../../assets/room/objects/*.png", { eager: true, import: "default" }))
    .map(([path, url]) => [`objects/${path.split("/").pop()}`, url]),
);

const placedCount = computed(() => props.tiles.filter((tile) => tile.state === TILE_STATE.PLACED).length);

function art(tile) {
  const key = tile?.reward?.asset_key || "";
  return key ? ART[objectAssetPath(key)] || "" : "";
}

// Pixel art at the largest whole-number scale that fits the 46px box (crisp, never blurred).
const sizes = reactive({});

function rememberSize(tile, event) {
  const img = event?.target;
  if (img?.naturalWidth) sizes[tile.key] = [img.naturalWidth, img.naturalHeight];
}

function artStyle(tile) {
  const size = sizes[tile.key];
  if (!size) return { visibility: "hidden" };
  const k = pixelIconScale(size[0], size[1], 46);
  return { width: `${size[0] * k}px`, height: `${size[1] * k}px` };
}

function tileLabel(tile) {
  const name = tile?.reward?.title || t("space.objectHistory.unknown");
  return t(`space.objectGrid.tileLabel.${tile.state}`, { name });
}
</script>

<style scoped>
.objectTiles {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.objectTilesHead {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.objectTilesHead h4 {
  margin: 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 13px;
  font-weight: 700;
}

.objectTilesHead span {
  color: rgba(255, 255, 255, 0.62);
  font-size: 12px;
}

.objectTilesRow {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.objectTile {
  display: flex;
  flex: none;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  min-width: 60px;
  min-height: 60px;
  padding: 0;
  box-sizing: border-box;
  border-radius: 14px;
  cursor: pointer;
  font: inherit;
}

.objectTile.placed {
  background: rgba(255, 255, 255, 0.09);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.objectTile.next {
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.3);
}

.objectTile.later {
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(255, 255, 255, 0.14);
}

.objectTile.placed.selected {
  border: 2px solid rgba(247, 215, 116, 0.95);
}

.objectTile.next.selected {
  border: 2px dashed rgba(180, 205, 255, 0.9);
}

.objectTile.later.selected {
  border: 2px dashed rgba(255, 255, 255, 0.5);
}

.objectTile:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

.objectTileArt {
  image-rendering: pixelated;
  pointer-events: none;
}

.objectTileArt.ghostArt {
  filter: grayscale(1) brightness(1.5);
  opacity: 0.5;
}

.objectTileSilhouette {
  width: 28px;
  height: 28px;
  fill: none;
  stroke: rgba(255, 255, 255, 0.26);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
