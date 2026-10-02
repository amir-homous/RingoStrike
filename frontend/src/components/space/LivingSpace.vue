<template>
  <BaseCard class="livingSpace">
    <div class="spaceHead">
      <div>
        <p class="spaceKicker">{{ t("space.eyebrow") }}</p>
        <h2>{{ t("space.title") }}</h2>
        <p>{{ t("space.subtitle") }}</p>
        <p v-if="spaceState" class="spaceStatus">{{ spaceStatus }}</p>
      </div>

      <div v-if="spaceState" class="spaceMeta">
        <span>{{ t("space.objects", { count: unlockedCount }) }}</span>
        <span v-if="spaceState.has_unseen_rewards">{{ t("space.newReward") }}</span>
      </div>
    </div>

    <UiState
      :loading="loading"
      :error="!!error"
      :empty="false"
      :loading-title="t('space.loadingTitle')"
      :loading-text="t('space.loadingText')"
      :error-title="t('space.errorTitle')"
      :error-text="error || t('common.pleaseTryAgain')"
      @retry="loadSpace"
    />

    <div v-if="spaceState && !loading && !error" class="spaceLayout">
      <div class="roomStage" :aria-label="t('space.roomLabel')">
        <SpaceZone
          v-for="zone in spaceState.zones"
          :key="zone.zone_key"
          :zone="zone"
          :active="activeZone?.zone_key === zone.zone_key"
          @select="selectZone"
        />
      </div>

      <SpaceZonePanel
        v-if="activeZone"
        :zone="activeZone"
        @close="activeZone = null"
      />
    </div>
  </BaseCard>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import SpaceZone from "./SpaceZone.vue";
import SpaceZonePanel from "./SpaceZonePanel.vue";

const props = defineProps({
  refreshKey: { type: Number, default: 0 },
});

const { t } = useI18n();

const loading = ref(false);
const error = ref("");
const spaceState = ref(null);
const activeZone = ref(null);

const unlockedCount = computed(() => {
  return spaceState.value?.unlocked_objects?.length || 0;
});

const spaceStatus = computed(() => {
  if (!unlockedCount.value) {
    return t("space.emptyStatus");
  }

  return t("space.progressStatus", { count: unlockedCount.value });
});

async function loadSpace() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await api.get("/me/space");
    spaceState.value = data;

    if (activeZone.value) {
      activeZone.value = data.zones.find(
        (zone) => zone.zone_key === activeZone.value.zone_key,
      ) || null;
    }
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

function selectZone(zone) {
  activeZone.value = zone;
}

onMounted(loadSpace);

watch(
  () => props.refreshKey,
  () => {
    loadSpace();
  },
);
</script>

<style scoped>
.livingSpace {
  display: grid;
  gap: var(--s-16);
  padding: 18px;
  overflow: hidden;
  background:
    radial-gradient(circle at 15% 0%, rgba(110, 229, 255, 0.08), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.018));
}

.spaceHead {
  display: flex;
  justify-content: space-between;
  gap: var(--s-16);
  align-items: flex-start;
}

.spaceKicker {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.82);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}

.spaceHead h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.42rem;
  line-height: 1.14;
}

.spaceHead p {
  margin: 8px 0 0;
  max-width: 680px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.6;
}

.spaceHead .spaceStatus {
  color: rgba(255, 255, 255, 0.72);
  font-weight: 750;
}

.spaceMeta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.spaceMeta span {
  display: inline-flex;
  align-items: center;
  min-height: 31px;
  padding: 7px 10px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.09);
  font-size: 0.76rem;
  font-weight: 850;
}

.spaceLayout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 0.38fr);
  gap: var(--s-12);
  align-items: stretch;
}

.roomStage {
  position: relative;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  grid-auto-rows: minmax(120px, auto);
  gap: 10px;
  min-height: 430px;
  padding: 12px;
  border-radius: 10px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.02)),
    linear-gradient(145deg, rgba(10, 18, 30, 0.96), rgba(8, 12, 20, 0.95));
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.roomStage :deep(.zone-work_desk) {
  grid-column: 1 / span 3;
  grid-row: 1;
}

.roomStage :deep(.zone-learning_corner) {
  grid-column: 4 / span 3;
  grid-row: 1;
}

.roomStage :deep(.zone-creative_corner) {
  grid-column: 1 / span 2;
  grid-row: 2;
}

.roomStage :deep(.zone-fitness_corner) {
  grid-column: 3 / span 2;
  grid-row: 2;
}

.roomStage :deep(.zone-sleep_corner) {
  grid-column: 5 / span 2;
  grid-row: 2;
}

@media (max-width: 920px) {
  .spaceLayout,
  .spaceHead {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .spaceMeta {
    justify-content: flex-start;
  }
}

@media (max-width: 720px) {
  .roomStage {
    grid-template-columns: 1fr;
    grid-auto-rows: auto;
    min-height: 0;
  }

  .roomStage :deep(.spaceZone) {
    grid-column: auto;
    grid-row: auto;
  }
}
</style>
