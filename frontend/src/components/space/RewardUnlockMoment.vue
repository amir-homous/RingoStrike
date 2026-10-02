<template>
  <Teleport to="body">
    <Transition name="spaceUnlock">
      <div v-if="open && reward" class="unlockOverlay" role="presentation" @click.self="finish">
        <section class="unlockPanel" role="dialog" aria-modal="true" :aria-label="t('spaceUnlock.title')">
          <div class="unlockAura" aria-hidden="true"></div>

          <div class="unlockHero">
            <div>
              <p class="eyebrow">{{ t("spaceUnlock.eyebrow") }}</p>
              <h2>{{ t("spaceUnlock.title") }}</h2>
              <p>{{ t("spaceUnlock.body", { reward: reward.title, zone: zoneLabel }) }}</p>
            </div>

            <RingoMoodFigure
              class="unlockRingo"
              mood="celebration"
              :alt="t('spaceUnlock.title')"
              size="md"
              floating
            />
          </div>

          <div class="objectCard">
            <span class="objectGlyph" aria-hidden="true">{{ objectGlyph }}</span>
            <div>
              <strong>{{ reward.title }}</strong>
              <p>{{ reward.description || t("spaceUnlock.defaultDescription") }}</p>
            </div>
          </div>

          <p class="savedNote">{{ t("spaceUnlock.savedNote") }}</p>

          <BaseButton class="continueButton" variant="primary" @click="finish">
            {{ t("spaceUnlock.continue") }}
          </BaseButton>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";

const props = defineProps({
  open: { type: Boolean, default: false },
  reward: { type: Object, default: null },
});

const emit = defineEmits(["close"]);

const { t } = useI18n();

const ZONE_LABELS = {
  work_desk: "spaceUnlock.zones.workDesk",
  creative_corner: "spaceUnlock.zones.creativeCorner",
  fitness_corner: "spaceUnlock.zones.fitnessCorner",
  learning_corner: "spaceUnlock.zones.learningCorner",
  sleep_corner: "spaceUnlock.zones.sleepCorner",
};

const zoneLabel = computed(() => {
  const key = ZONE_LABELS[props.reward?.zone_key] || "";
  return key ? t(key) : props.reward?.zone_key || t("spaceUnlock.room");
});

const objectGlyph = computed(() => {
  const title = String(props.reward?.title || props.reward?.key || "?").trim();
  return title.slice(0, 1).toUpperCase();
});

function finish() {
  emit("close", props.reward);
}

function onKeydown(event) {
  if (event.key === "Escape" && props.open) {
    finish();
  }
}

onMounted(() => {
  window.addEventListener("keydown", onKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", onKeydown);
});
</script>

<style scoped>
.unlockOverlay {
  position: fixed;
  inset: 0;
  z-index: 82;
  display: grid;
  place-items: center;
  padding: var(--s-20);
  background: rgba(4, 7, 14, 0.68);
  backdrop-filter: blur(14px);
}

.unlockPanel {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: var(--s-16);
  width: min(520px, 100%);
  padding: 24px;
  border-radius: 12px;
  background:
    radial-gradient(circle at 10% 0%, rgba(110, 229, 255, 0.18), transparent 36%),
    linear-gradient(180deg, rgba(17, 25, 40, 0.96), rgba(8, 12, 22, 0.97));
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.42);
}

.unlockAura {
  position: absolute;
  inset: -40%;
  background: radial-gradient(circle, rgba(110, 229, 255, 0.10), transparent 44%);
  pointer-events: none;
}

.unlockHero,
.objectCard,
.savedNote,
.continueButton {
  position: relative;
  z-index: 1;
}

.unlockHero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: center;
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.unlockHero h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 1.7rem;
  line-height: 1.12;
}

.unlockHero p,
.objectCard p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.6;
}

.objectCard {
  display: flex;
  gap: var(--s-12);
  align-items: center;
  padding: 14px;
  border-radius: 10px;
  background: rgba(110, 229, 255, 0.08);
  border: 1px solid rgba(110, 229, 255, 0.18);
}

.objectGlyph {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  flex: 0 0 auto;
  border-radius: 10px;
  color: rgba(6, 11, 20, 0.92);
  background: rgba(255, 255, 255, 0.88);
  font-size: 1.3rem;
  font-weight: 950;
}

.objectCard strong {
  color: rgba(255, 255, 255, 0.94);
}

.savedNote {
  margin: -6px 0 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

.continueButton {
  justify-self: end;
}

.spaceUnlock-enter-active,
.spaceUnlock-leave-active {
  transition: opacity 180ms ease;
}

.spaceUnlock-enter-active .unlockPanel,
.spaceUnlock-leave-active .unlockPanel {
  transition: transform 180ms ease, opacity 180ms ease;
}

.spaceUnlock-enter-from,
.spaceUnlock-leave-to {
  opacity: 0;
}

.spaceUnlock-enter-from .unlockPanel,
.spaceUnlock-leave-to .unlockPanel {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}

@media (max-width: 620px) {
  .unlockPanel {
    padding: 20px;
  }

  .unlockHero {
    grid-template-columns: 1fr;
  }

  .unlockRingo {
    justify-self: center;
    order: -1;
  }

  .continueButton {
    justify-self: stretch;
  }
}

@media (prefers-reduced-motion: reduce) {
  .spaceUnlock-enter-active,
  .spaceUnlock-leave-active,
  .spaceUnlock-enter-active .unlockPanel,
  .spaceUnlock-leave-active .unlockPanel {
    transition: none;
  }
}
</style>
