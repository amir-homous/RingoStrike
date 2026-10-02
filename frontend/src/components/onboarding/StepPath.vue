<template>
  <section class="pathStep">
    <div class="pathHero">
      <div class="stepHeader">
        <p class="eyebrow">{{ t("onboarding.path.eyebrow") }}</p>
        <h1>{{ t("onboarding.path.title") }}</h1>
        <p><OnboardingTypewriterText :text="t('onboarding.path.body')" /></p>
      </div>

      <RingoMoodFigure class="pathRingo" :mood="pathMood" :alt="t('onboarding.path.title')" size="md" floating />
    </div>

    <div class="pathExperience">
      <div class="pathGrid">
        <button
          v-for="path in pathOptions"
          :key="path.key"
          type="button"
          class="pathCard"
          :class="{ selected: selectedPaths.includes(path.key), previewed: previewPath === path.key }"
          @mouseenter="previewPath = path.key"
          @focus="previewPath = path.key"
          @click="togglePath(path.key)"
        >
          <span class="pathIcon" :style="{ '--path-color': path.color || '#67e8f9' }" aria-hidden="true">
            {{ path.iconLabel }}
          </span>
          <span class="pathLabel">{{ path.title }}</span>
          <span class="pathZone">{{ t("onboarding.path.roomZone", { zone: path.zoneTitle }) }}</span>
          <span class="pathSuggestion">
            {{ path.outcome }}
          </span>
        </button>
      </div>

      <div class="roomPreview" :aria-label="t('onboarding.path.roomPreviewLabel')">
        <p class="previewTitle">{{ t("onboarding.path.roomPreviewTitle") }}</p>

        <div class="previewRoom">
          <SpaceZone
            v-for="zone in previewZones"
            :key="zone.zone_key"
            :zone="zone"
            :active="activeZoneKey === zone.zone_key"
            @select="selectZone(zone)"
          />
        </div>

        <p v-if="activePreviewOption" class="previewHint">
          <OnboardingTypewriterText
            :text="t('onboarding.path.previewHint', {
              path: activePreviewOption.title,
              reward: activePreviewOption.firstRewardTitle,
            })"
            :speed="12"
            :start-delay="40"
          />
        </p>
      </div>
    </div>

    <div class="actions">
      <BaseButton variant="primary" :disabled="selectedPaths.length === 0" @click="$emit('continue')">
        {{ t("onboarding.path.continueWithCount", { count: selectedPaths.length }) }}
      </BaseButton>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import OnboardingTypewriterText from "@/components/onboarding/OnboardingTypewriterText.vue";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";
import SpaceZone from "@/components/space/SpaceZone.vue";
import { resolveRingoMood } from "@/constants/ringoSprites";
import { localizePath } from "@/lib/ringoContentLocalization";

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  backendPaths: { type: Array, default: () => [] },
  spaceState: { type: Object, default: null },
});

const emit = defineEmits(["update:modelValue", "continue"]);

const { locale, t } = useI18n();
const selectedPaths = computed(() => Array.isArray(props.modelValue) ? props.modelValue : []);
const previewPath = ref("");

const CANONICAL_PATHS = ["career", "creativity", "fitness", "learning", "sleep"];

const PATH_TO_ZONE = {
  career: "work_desk",
  creativity: "creative_corner",
  fitness: "fitness_corner",
  learning: "learning_corner",
  sleep: "sleep_corner",
};

const pathMood = computed(() => {
  return selectedPaths.value.length
    ? resolveRingoMood("onboardingPathSelected")
    : resolveRingoMood("onboardingPath");
});

const pathOptions = computed(() => {
  return CANONICAL_PATHS.map((key) => {
    const backendPath = props.backendPaths.find((path) => path.key === key) || { key };
    const localized = localizePath(backendPath, locale.value) || backendPath;
    const zone = previewZones.value.find((item) => item.path_key === key);
    const firstReward = [
      ...(zone?.unlocked_objects || []),
      ...(zone?.locked_preview_objects || []),
    ][0];

    return {
      ...localized,
      key,
      title: localized.title || t(`onboarding.paths.${key}.label`),
      outcome: t(`onboarding.paths.${key}.outcome`),
      color: localized.color || "#67e8f9",
      iconLabel: String(localized.icon || localized.title || key).slice(0, 1).toUpperCase(),
      zoneTitle: zone?.title || t(`onboarding.paths.${key}.zone`),
      zoneKey: PATH_TO_ZONE[key],
      firstRewardTitle: firstReward?.title || t("onboarding.path.firstRewardFallback"),
    };
  });
});

const activePreviewKey = computed(() => {
  return previewPath.value || selectedPaths.value[0] || "career";
});

const activePreviewOption = computed(() => {
  return pathOptions.value.find((path) => path.key === activePreviewKey.value) || pathOptions.value[0];
});

const activeZoneKey = computed(() => {
  return PATH_TO_ZONE[activePreviewKey.value] || "";
});

const previewZones = computed(() => {
  const apiZones = Array.isArray(props.spaceState?.zones) ? props.spaceState.zones : [];

  return CANONICAL_PATHS.map((key) => {
    const zoneKey = PATH_TO_ZONE[key];
    const apiZone = apiZones.find((zone) => zone.zone_key === zoneKey);

    if (apiZone) return apiZone;

    return {
      path_key: key,
      zone_key: zoneKey,
      title: t(`onboarding.paths.${key}.zone`),
      has_unseen_rewards: false,
      unlocked_objects: [],
      locked_preview_objects: [
        {
          id: `${key}-preview`,
          key: `${key}-preview`,
          title: t(`onboarding.paths.${key}.firstReward`),
          unlocked: false,
        },
      ],
    };
  });
});

function togglePath(path) {
  if (selectedPaths.value.includes(path)) {
    emit("update:modelValue", selectedPaths.value.filter((item) => item !== path));
    return;
  }

  emit("update:modelValue", [path]);
  previewPath.value = path;
}

function selectZone(zone) {
  const option = pathOptions.value.find((path) => path.zoneKey === zone.zone_key);
  if (!option) return;

  previewPath.value = option.key;
  emit("update:modelValue", [option.key]);
}
</script>

<style scoped>
.pathStep {
  display: grid;
  gap: var(--s-20);
}

.pathHero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-20);
  align-items: center;
}

.stepHeader {
  max-width: 760px;
  min-width: 0;
}

.pathRingo {
  justify-self: end;
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
  font-size: 2.55rem;
  line-height: 1.04;
  letter-spacing: 0;
}

.stepHeader p:not(.eyebrow) {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.7;
}

.pathGrid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--s-12);
}

.pathExperience {
  display: grid;
  gap: var(--s-16);
}

.pathCard {
  min-height: 146px;
  display: grid;
  align-content: start;
  gap: 10px;
  padding: 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  color: rgba(255, 255, 255, 0.88);
  text-align: start;
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: transform 140ms ease, background 140ms ease, border-color 140ms ease;
}

.pathCard:hover,
.pathCard.previewed,
.pathCard.selected {
  transform: translateY(-2px);
  border-color: rgba(110, 229, 255, 0.28);
  background: rgba(110, 229, 255, 0.08);
}

.pathIcon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  color: rgba(6, 11, 20, 0.88);
  background: var(--path-color, #67e8f9);
  box-shadow: 0 0 20px color-mix(in srgb, var(--path-color, #67e8f9) 40%, transparent);
  font-weight: 950;
}

.pathLabel {
  font-weight: 850;
}

.pathZone {
  color: rgba(110, 229, 255, 0.74);
  font-size: 0.76rem;
  font-weight: 800;
}

.pathSuggestion {
  color: rgba(255, 255, 255, 0.56);
  font-size: 0.88rem;
  line-height: 1.55;
}

.roomPreview {
  display: grid;
  gap: var(--s-12);
  padding: 14px;
  border-radius: 20px;
  background:
    radial-gradient(circle at 12% 0%, rgba(110, 229, 255, 0.08), transparent 34%),
    rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.09);
}

.previewTitle,
.previewHint {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.previewTitle {
  color: rgba(255, 255, 255, 0.86);
  font-size: 0.84rem;
  font-weight: 850;
}

.previewRoom {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.previewRoom :deep(.spaceZone) {
  min-height: 112px;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 980px) {
  .pathGrid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .previewRoom {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .pathHero {
    grid-template-columns: 1fr;
  }

  .pathRingo {
    order: -1;
    justify-self: center;
  }

  h1 {
    font-size: 1.9rem;
  }

  .pathGrid {
    grid-template-columns: 1fr;
  }

  .previewRoom {
    grid-template-columns: 1fr;
  }

  .actions {
    display: grid;
  }
}
</style>