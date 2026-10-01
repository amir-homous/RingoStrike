<template>
  <Teleport to="body">
    <section v-if="open" class="explorePathsPanel" role="dialog" :aria-label="t('missions.explorePathsPanel.label')">
      <div class="panelHead">
        <div>
          <p class="eyebrow compact">{{ t("missions.explorePathsPanel.eyebrow") }}</p>
          <h3>{{ t("missions.explorePathsPanel.title") }}</h3>
          <p>{{ t("missions.explorePathsPanel.body") }}</p>
        </div>

        <button type="button" class="closeButton" :aria-label="t('missions.explorePathsPanel.close')"
          @click="$emit('close')">
          &times;
        </button>
      </div>

      <div v-if="paths.length" class="pathPreviewList">
        <article v-for="path in visiblePaths" :key="pathKey(path)" class="pathPreview">
          <span class="pathIconRing" :style="{ '--path-color': path.color || '#f7d774' }" aria-hidden="true">
            <img v-if="path.iconUrl" :src="path.iconUrl" alt="" />
            <span v-else>{{ initialsFor(path.title) }}</span>
          </span>

          <span class="pathCopy">
            <strong>{{ path.title }}</strong>
            <small v-if="path.description">{{ path.description }}</small>
            <span class="pathMeta">{{ pathMeta(path) }}</span>
            <span v-if="challengePreview(path).length" class="challengePreview">
              <span v-for="challenge in challengePreview(path)" :key="challenge">{{ challenge }}</span>
            </span>
          </span>
        </article>
      </div>

      <div v-else class="emptyState">
        <strong>{{ t("missions.explorePathsPanel.emptyTitle") }}</strong>
        <span>{{ t("missions.explorePathsPanel.emptyBody") }}</span>
      </div>

      <div class="panelActions">
        <BaseButton variant="primary" @click="$emit('open-paths')">
          {{ t("missions.explorePathsPanel.openPaths") }}
        </BaseButton>
        <BaseButton variant="secondary" @click="$emit('close')">
          {{ t("missions.explorePathsPanel.notNow") }}
        </BaseButton>
      </div>
    </section>
  </Teleport>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import BaseButton from "@/components/ui/BaseButton.vue";
import { initialsFor } from "@/utils/missionMomentumUtils";

const props = defineProps({
  open: { type: Boolean, default: false },
  paths: { type: Array, default: () => [] },
});

defineEmits(["close", "open-paths"]);

const { t } = useI18n();

const visiblePaths = computed(() => props.paths.slice(0, 3));

function pathKey(path) {
  return String(path?.path_id || path?.id || path?.key || path?.title || "");
}

function pathMeta(path) {
  const count = Number(path?.challengeCount ?? path?.availableChallengeCount ?? 0);
  if (Number.isFinite(count) && count > 0) {
    return t("missions.explorePathsPanel.challengeCount", { count });
  }

  return t("missions.explorePathsPanel.previewMeta");
}

function challengePreview(path) {
  const values = Array.isArray(path?.challengePreview)
    ? path.challengePreview
    : Array.isArray(path?.challenges)
      ? path.challenges
      : [];

  return values
    .map((challenge) => {
      if (typeof challenge === "string") return challenge;
      return challenge?.name || challenge?.title || "";
    })
    .filter(Boolean)
    .slice(0, 2);
}
</script>

<style scoped>
.explorePathsPanel {
  position: fixed;
  left: 50%;
  bottom: 94px;
  z-index: 76;
  transform: translateX(-50%);
  display: grid;
  gap: 14px;
  box-sizing: border-box;
  width: min(520px, calc(100vw - 28px));
  max-height: min(72vh, 560px);
  padding: 16px;
  border: 1px solid rgba(110, 229, 255, 0.18);
  border-radius: 20px;
  background:
    radial-gradient(circle at 10% 0%, rgba(110, 229, 255, 0.10), transparent 34%),
    radial-gradient(circle at 92% 18%, rgba(247, 215, 116, 0.08), transparent 32%),
    rgba(8, 13, 24, 0.96);
  box-shadow:
    0 22px 70px rgba(0, 0, 0, 0.42),
    inset 0 0 0 1px rgba(255, 255, 255, 0.025);
  color: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(18px);
  overflow: auto;
}

.panelHead {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: flex-start;
}

.panelHead h3,
.panelHead p {
  margin: 0;
}

.panelHead h3 {
  color: rgba(255, 255, 255, 0.96);
  font-size: 1.18rem;
  line-height: 1.2;
}

.panelHead p:not(.eyebrow) {
  margin-top: 6px;
  color: rgba(219, 244, 255, 0.68);
  line-height: 1.55;
}

.eyebrow {
  margin: 0 0 6px;
  color: rgba(110, 229, 255, 0.86);
  font-size: var(--cap);
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.closeButton {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.055);
  cursor: pointer;
  font-size: 1.3rem;
  line-height: 1;
}

.closeButton:hover {
  border-color: rgba(110, 229, 255, 0.24);
  color: rgba(255, 255, 255, 0.92);
  background: rgba(110, 229, 255, 0.08);
}

.pathPreviewList {
  display: grid;
  gap: 8px;
}

.pathPreview {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 11px;
  align-items: center;
  min-width: 0;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.045);
}

.pathIconRing {
  display: inline-grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border: 2px solid color-mix(in srgb, var(--path-color) 50%, rgba(255, 255, 255, 0.10));
  border-radius: 50%;
  background:
    radial-gradient(circle at 35% 20%, color-mix(in srgb, var(--path-color) 18%, transparent), transparent 56%),
    rgba(255, 255, 255, 0.055);
  color: rgba(255, 255, 255, 0.88);
  font-size: 0.78rem;
  font-weight: 950;
}

.pathIconRing img {
  width: 25px;
  height: 25px;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.pathCopy {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.pathCopy strong {
  color: rgba(255, 255, 255, 0.94);
  line-height: 1.2;
}

.pathCopy small,
.pathMeta {
  min-width: 0;
  color: rgba(219, 244, 255, 0.62);
  line-height: 1.4;
}

.challengePreview {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 3px;
}

.challengePreview span {
  min-width: 0;
  padding: 3px 7px;
  border: 1px solid rgba(110, 229, 255, 0.14);
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.74);
  background: rgba(110, 229, 255, 0.055);
  font-size: 0.72rem;
  font-weight: 780;
}

.emptyState {
  display: grid;
  gap: 4px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.035);
}

.emptyState strong {
  color: rgba(255, 255, 255, 0.9);
}

.emptyState span {
  color: rgba(219, 244, 255, 0.62);
}

.panelActions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

@media (max-width: 560px) {
  .explorePathsPanel {
    bottom: 88px;
    padding: 14px;
  }

  .panelActions :deep(.btn) {
    width: 100%;
  }
}
</style>
