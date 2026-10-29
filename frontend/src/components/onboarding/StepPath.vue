<template>
  <!-- B37 (D79, D80): pick a corner on the real room. One line for the chosen corner, and a Now /
       After a few steps switch that only changes the picture and one line. -->
  <section class="pathStep cornerStep">
    <div class="stepHeader">
      <p class="eyebrow">{{ t("onboarding.corner.eyebrow") }}</p>
      <h1>{{ t("onboarding.corner.title") }}</h1>
    </div>

    <div class="cornerLayout">
      <RoomPicture
        class="cornerPicture"
        :model-value="chosenZone"
        :after="after"
        :markers="markers"
        @update:model-value="chooseZone"
      />

      <div class="cornerSide">
        <div class="cornerChips" role="group" :aria-label="t('onboarding.corner.chipsLabel')">
          <button
            v-for="option in pathOptions"
            :key="option.key"
            type="button"
            class="cornerChip"
            :class="{ chosen: chosenPath === option.key }"
            :style="{ '--chip-color': option.color }"
            :aria-pressed="chosenPath === option.key ? 'true' : 'false'"
            :data-path="option.key"
            @click="choosePath(option.key)"
          >
            {{ option.zoneTitle }}
          </button>
        </div>

        <div class="cornerSwitch" role="group" :aria-label="t('onboarding.corner.switchLabel')">
          <button
            type="button"
            class="switchButton"
            :class="{ active: !after }"
            :aria-pressed="after ? 'false' : 'true'"
            data-switch="now"
            @click="after = false"
          >
            {{ t("onboarding.corner.now") }}
          </button>
          <button
            type="button"
            class="switchButton"
            :class="{ active: after }"
            :aria-pressed="after ? 'true' : 'false'"
            data-switch="after"
            @click="after = true"
          >
            {{ t("onboarding.corner.after") }}
          </button>
        </div>

        <p class="cornerLine" aria-live="polite">
          <template v-if="chosenOption">
            <strong>{{ chosenOption.zoneTitle }}.</strong>
            {{ chosenOption.outcome }}
            <span class="stateLine">{{ after ? t("onboarding.corner.afterLine") : t("onboarding.corner.nowLine") }}</span>
          </template>
          <template v-else>{{ t("onboarding.corner.hint") }}</template>
        </p>

        <div class="actions">
          <BaseButton variant="primary" :disabled="!chosenPath" @click="$emit('continue')">
            {{ t("onboarding.corner.continue") }}
          </BaseButton>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import RoomPicture from "@/components/onboarding/RoomPicture.vue";
import { spaceZoneTitle } from "@/lib/livingSpaceCopy";
import { localizePath } from "@/lib/ringoContentLocalization";
import { resolvePathIcon } from "@/utils/missionMomentumUtils";

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  backendPaths: { type: Array, default: () => [] },
  spaceState: { type: Object, default: null },
});

const emit = defineEmits(["update:modelValue", "continue"]);

const { locale, t, te } = useI18n();
const after = ref(false);

// The room's order on screen: the back wall from left to right, then the floor.
const CANONICAL_PATHS = ["career", "learning", "creativity", "sleep", "fitness"];

const PATH_ICONS = {
  career: "briefcase",
  creativity: "sparkles",
  fitness: "activity",
  learning: "book",
  sleep: "moon",
};

const PATH_TO_ZONE = {
  career: "work_desk",
  creativity: "creative_corner",
  fitness: "fitness_corner",
  learning: "learning_corner",
  sleep: "sleep_corner",
};

const ZONE_TO_PATH = Object.fromEntries(Object.entries(PATH_TO_ZONE).map(([path, zone]) => [zone, path]));

const chosenPath = computed(() => (Array.isArray(props.modelValue) ? props.modelValue[0] : "") || "");
const chosenZone = computed(() => PATH_TO_ZONE[chosenPath.value] || "");

const pathOptions = computed(() => {
  return CANONICAL_PATHS.map((key) => {
    const backendPath = props.backendPaths.find((path) => path.key === key) || { key };
    const localized = localizePath(backendPath, locale.value) || backendPath;
    const zoneKey = PATH_TO_ZONE[key];
    return {
      key,
      zoneKey,
      color: localized.color || backendPath.color || "#67e8f9",
      iconUrl: resolvePathIcon(backendPath.icon || PATH_ICONS[key]),
      zoneTitle: spaceZoneTitle(zoneKey, t, te, t(`onboarding.paths.${key}.zone`)),
      // The corner's one line is the existing path outcome copy (B10).
      outcome: t(`onboarding.paths.${key}.outcome`),
    };
  });
});

const chosenOption = computed(() => pathOptions.value.find((option) => option.key === chosenPath.value) || null);

const markers = computed(() => Object.fromEntries(pathOptions.value.map((option) => [option.zoneKey, {
  label: option.zoneTitle,
  iconUrl: option.iconUrl,
  color: option.color,
}])));

function choosePath(path) {
  emit("update:modelValue", [path]);
}

function chooseZone(zoneKey) {
  const path = ZONE_TO_PATH[zoneKey];
  if (path) choosePath(path);
}
</script>

<style scoped>
.pathStep {
  display: grid;
  gap: var(--s-16);
}

.stepHeader {
  max-width: 760px;
  min-width: 0;
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.88);
  font-size: 0.74rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 2rem;
  line-height: 1.1;
  letter-spacing: 0;
}

/* Wide screens: the room on the start side, the choice on the end side, so Continue stays above the
   fold at 1366x768. Narrow screens stack them. */
.cornerLayout {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(240px, 1fr);
  gap: var(--s-20);
  align-items: start;
}

.cornerPicture {
  max-width: 600px;
}

.cornerSide {
  display: grid;
  gap: var(--s-12);
  align-content: start;
}

.cornerChips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cornerChip {
  min-height: 44px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: rgba(255, 255, 255, 0.78);
  cursor: pointer;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 700;
}

.cornerChip.chosen {
  border-color: var(--chip-color);
  background: color-mix(in srgb, var(--chip-color) 18%, transparent);
  color: #fff;
}

.cornerSwitch {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.switchButton {
  min-height: 44px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 700;
}

.switchButton.active {
  border-color: #6ee5ff;
  background: rgba(110, 229, 255, 0.14);
  color: #6ee5ff;
}

.cornerChip:focus-visible,
.switchButton:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

.cornerLine {
  min-height: 3em;
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.92rem;
  line-height: 1.55;
}

.cornerLine strong {
  color: #fff;
}

.stateLine {
  display: block;
  color: rgba(255, 255, 255, 0.64);
}

.actions {
  display: grid;
}

@media (max-width: 860px) {
  .cornerLayout {
    grid-template-columns: 1fr;
  }

  .cornerPicture {
    max-width: none;
  }

  h1 {
    font-size: 1.6rem;
  }

  /* Phones: Continue stays in view at the bottom of the screen. */
  .actions {
    position: sticky;
    bottom: 0;
    z-index: 2;
    padding: 10px 0 calc(10px + env(safe-area-inset-bottom));
    background: linear-gradient(to top, rgba(8, 12, 22, 0.96) 60%, rgba(8, 12, 22, 0));
  }
}
</style>
