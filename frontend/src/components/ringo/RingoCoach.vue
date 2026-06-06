<template>
  <section class="coach" :class="`sprite-${resolved.key}`">
    <div class="spriteFrame" aria-hidden="true">
      <img v-if="resolved.src" :src="resolved.src" :alt="resolved.key" />
      <div v-else class="spriteFallback">
        <span>{{ spriteInitial }}</span>
      </div>
    </div>

    <div class="coachCopy">
      <p class="eyebrow">{{ t("ringoCoach.eyebrow") }}</p>
      <p class="message">{{ message || t("ringoCoach.fallbackMessage") }}</p>

      <div v-if="primaryAction || secondaryAction" class="coachActions">
        <RouterLink
          v-if="primaryAction?.to"
          class="coachButton primary"
          :to="primaryAction.to"
        >
          {{ primaryAction.label }}
        </RouterLink>
        <button
          v-else-if="primaryAction"
          type="button"
          class="coachButton primary"
          @click="$emit('action', primaryAction)"
        >
          {{ primaryAction.label }}
        </button>

        <RouterLink
          v-if="secondaryAction?.to"
          class="coachButton"
          :to="secondaryAction.to"
        >
          {{ secondaryAction.label }}
        </RouterLink>
        <button
          v-else-if="secondaryAction"
          type="button"
          class="coachButton"
          @click="$emit('action', secondaryAction)"
        >
          {{ secondaryAction.label }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { resolveRingoSprite } from "@/constants/ringoSprites";

const props = defineProps({
  message: { type: String, default: "" },
  sprite: { type: String, default: "idle" },
  primaryAction: { type: Object, default: null },
  secondaryAction: { type: Object, default: null },
});

defineEmits(["action"]);

const { t } = useI18n();

const resolved = computed(() => resolveRingoSprite(props.sprite));
const spriteInitial = computed(() => resolved.value.key.slice(0, 1).toUpperCase());
</script>

<style scoped>
.coach {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: var(--s-16);
  align-items: center;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 24px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.13), transparent 36%),
    radial-gradient(circle at 100% 12%, rgba(247, 215, 116, 0.10), transparent 32%),
    rgba(255, 255, 255, 0.045);
  box-shadow: 0 22px 60px rgba(0, 0, 0, 0.24);
}

.spriteFrame {
  display: grid;
  place-items: center;
  width: 74px;
  height: 74px;
  border-radius: 24px;
  border: 1px solid rgba(110, 229, 255, 0.22);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.16), rgba(195, 90, 214, 0.12)),
    rgba(255, 255, 255, 0.06);
}

.spriteFrame img {
  display: block;
  width: 64px;
  height: 64px;
  object-fit: contain;
}

.spriteFallback {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 18px;
  color: rgba(255, 255, 255, 0.96);
  background:
    radial-gradient(circle at 34% 28%, rgba(255, 255, 255, 0.42), transparent 18%),
    linear-gradient(135deg, rgba(110, 229, 255, 0.34), rgba(247, 215, 116, 0.24));
  font-weight: 950;
}

.coachCopy {
  min-width: 0;
}

.eyebrow {
  margin: 0 0 6px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.message {
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.65;
}

.coachActions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  margin-top: var(--s-12);
}

.coachButton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  color: rgba(255, 255, 255, 0.86);
  background: rgba(255, 255, 255, 0.055);
  cursor: pointer;
  font-weight: 850;
  text-decoration: none;
}

.coachButton.primary {
  color: rgba(255, 255, 255, 0.95);
  border-color: rgba(110, 229, 255, 0.28);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.18), rgba(195, 90, 214, 0.13)),
    rgba(255, 255, 255, 0.06);
}

.coachButton:hover {
  text-decoration: none;
  background: rgba(255, 255, 255, 0.085);
}

.coachButton:focus-visible {
  outline: none;
  box-shadow: var(--focus);
}

@media (max-width: 620px) {
  .coach {
    grid-template-columns: 1fr;
  }

  .spriteFrame {
    width: 64px;
    height: 64px;
  }

  .coachButton {
    width: 100%;
  }
}
</style>
