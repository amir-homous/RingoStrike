<template>
  <section class="coach">
    <div class="spriteFrame" aria-hidden="true">
      <img v-if="resolved.src" :src="resolved.src" :alt="resolved.key" />
    </div>

    <div class="coachCopy">
      <p class="eyebrow">{{ t("ringoCoach.eyebrow") }}</p>
      <p class="message">{{ message || t("ringoCoach.fallbackMessage") }}</p>

      <div v-if="primaryAction || secondaryAction" class="coachActions">
        <RouterLink v-if="primaryAction?.to" class="coachButton primary" :to="primaryAction.to">
          {{ primaryAction.label }}
        </RouterLink>
        <button v-else-if="primaryAction" type="button" class="coachButton primary"
          @click="$emit('action', primaryAction)">
          {{ primaryAction.label }}
        </button>

        <RouterLink v-if="secondaryAction?.to" class="coachButton" :to="secondaryAction.to">
          {{ secondaryAction.label }}
        </RouterLink>
        <button v-else-if="secondaryAction" type="button" class="coachButton" @click="$emit('action', secondaryAction)">
          {{ secondaryAction.label }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { normalizeRingoMood } from "@/constants/ringoMood";
import { resolveRingoSprite } from "@/constants/ringoSprites";

const props = defineProps({
  message: { type: String, default: "" },
  sprite: { type: String, default: "idle" },
  primaryAction: { type: Object, default: null },
  secondaryAction: { type: Object, default: null },
});

defineEmits(["action"]);

const { t } = useI18n();

const resolved = computed(() => resolveRingoSprite(normalizeRingoMood(props.sprite)));
const spriteInitial = computed(() => resolved.value.key.slice(0, 1).toUpperCase());
</script>
<style scoped>
.coach {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 24px;
  align-items: center;
  padding: 16px 20px;
  border-radius: 28px;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
  color: #ffffff;
  font-family: 'Poppins', sans-serif;
}

.spriteFrame {
  width: 120px;
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.spriteFrame img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.coachCopy {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.eyebrow {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6EE5FF;
}

.message {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #ffffff;
}

.coachActions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.coachButton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border-radius: 16px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  transition: all 0.2s ease;
}

.coachButton.primary {
  background: linear-gradient(135deg, #6EE5FF, #C35AD6);
  color: #fff;
}

.coachButton:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

@media (max-width: 620px) {
  .coach {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .spriteFrame {
    margin: 0 auto;
  }

  .coachButton {
    width: 100%;
  }
}
</style>
