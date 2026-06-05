<template>
  <Teleport to="body">
    <Transition name="joinMoment">
      <div
        v-if="open"
        class="momentOverlay"
        role="presentation"
        @click.self="closeToDashboard"
      >
        <section
          class="momentPanel"
          role="dialog"
          aria-modal="true"
          :aria-label="t('joinSuccess.title')"
        >
          <div class="momentAura" aria-hidden="true"></div>

          <div class="momentMark" aria-hidden="true">
            <span></span>
          </div>

          <p class="eyebrow">{{ t("joinSuccess.eyebrow") }}</p>
          <h2>{{ t("joinSuccess.title") }}</h2>

          <p class="message">
            {{ message }}
          </p>

          <div class="missionCard">
            <span>{{ t("joinSuccess.nextLabel") }}</span>
            <strong>{{ t("joinSuccess.nextMission") }}</strong>
            <p>{{ t("joinSuccess.nextDescription") }}</p>
          </div>

          <div class="actions">
            <BaseButton
              class="primaryAction"
              variant="primary"
              @click="goDashboard"
            >
              {{ primaryLabel }}
            </BaseButton>

            <BaseButton
              v-if="detailsTo"
              variant="secondary"
              @click="goDetails"
            >
              {{ secondaryLabel }}
            </BaseButton>
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";

const props = defineProps({
  open: { type: Boolean, default: false },
  join: { type: Object, default: null },
});

const emit = defineEmits(["close"]);

const router = useRouter();
const { t } = useI18n();

const source = computed(() => props.join?.source || "challenges");

const challengeName = computed(() => {
  return props.join?.challengeName || t("common.challenge");
});

const isExisting = computed(() => props.join?.mode === "existing");

const detailsTo = computed(() => {
  const enrollmentId = props.join?.enrollmentId;
  return enrollmentId ? `/enrollment/${enrollmentId}` : "";
});

const message = computed(() => {
  if (isExisting.value) {
    return t("joinSuccess.existingBody");
  }

  return t("joinSuccess.body", {
    challengeName: challengeName.value,
  });
});

const primaryLabel = computed(() => {
  return source.value === "onboarding"
    ? t("joinSuccess.primary.onboarding")
    : t("joinSuccess.primary.challenges");
});

const secondaryLabel = computed(() => {
  return source.value === "onboarding"
    ? t("joinSuccess.secondary.onboarding")
    : t("joinSuccess.secondary.challenges");
});

function close() {
  emit("close");
}

function goDashboard() {
  close();
  router.push("/dashboard");
}

function goDetails() {
  if (!detailsTo.value) return;
  close();
  router.push(detailsTo.value);
}

function closeToDashboard() {
  goDashboard();
}

function onKeydown(event) {
  if (event.key === "Escape" && props.open) {
    closeToDashboard();
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
.momentOverlay {
  position: fixed;
  inset: 0;
  z-index: 82;
  display: grid;
  place-items: center;
  padding: var(--s-20);
  background: rgba(4, 7, 14, 0.68);
  backdrop-filter: blur(14px);
}

.momentPanel {
  position: relative;
  overflow: hidden;
  width: min(540px, 100%);
  padding: 28px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.13);
  background:
    radial-gradient(circle at 12% 0%, rgba(110, 229, 255, 0.15), transparent 34%),
    radial-gradient(circle at 94% 10%, rgba(253, 230, 138, 0.11), transparent 34%),
    linear-gradient(145deg, rgba(18, 24, 38, 0.96), rgba(10, 14, 25, 0.96));
  box-shadow: 0 34px 110px rgba(0, 0, 0, 0.46);
}

.momentAura {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.04), transparent);
  pointer-events: none;
}

.momentMark,
.eyebrow,
h2,
.message,
.missionCard,
.actions {
  position: relative;
  z-index: 1;
}

.momentMark {
  width: 58px;
  height: 58px;
  display: grid;
  place-items: center;
  margin-bottom: var(--s-16);
  border-radius: 21px;
  background: rgba(110, 229, 255, 0.12);
  border: 1px solid rgba(110, 229, 255, 0.28);
}

.momentMark span {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: #6ee5ff;
  box-shadow: 0 0 28px rgba(110, 229, 255, 0.62);
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.9);
  font-size: 0.74rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 2.35rem;
  line-height: 1.04;
  letter-spacing: 0;
}

.message {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.75;
}

.missionCard {
  display: grid;
  gap: 6px;
  margin-top: var(--s-20);
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(253, 230, 138, 0.22);
  background: rgba(253, 230, 138, 0.075);
}

.missionCard span {
  color: rgba(253, 230, 138, 0.86);
  font-size: 0.76rem;
  font-weight: 800;
}

.missionCard strong {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.06rem;
}

.missionCard p {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: var(--s-12);
  margin-top: var(--s-20);
}

.primaryAction {
  flex: 1 1 auto;
}

.joinMoment-enter-active,
.joinMoment-leave-active {
  transition: opacity 180ms ease;
}

.joinMoment-enter-active .momentPanel,
.joinMoment-leave-active .momentPanel {
  transition: transform 180ms ease, opacity 180ms ease;
}

.joinMoment-enter-from,
.joinMoment-leave-to {
  opacity: 0;
}

.joinMoment-enter-from .momentPanel,
.joinMoment-leave-to .momentPanel {
  opacity: 0;
  transform: translateY(10px) scale(0.985);
}

@media (prefers-reduced-motion: reduce) {
  .joinMoment-enter-active,
  .joinMoment-leave-active,
  .joinMoment-enter-active .momentPanel,
  .joinMoment-leave-active .momentPanel {
    transition: none;
  }
}

@media (max-width: 560px) {
  .momentOverlay {
    place-items: center;
    padding: var(--s-12);
  }

  .momentPanel {
    padding: 22px;
    border-radius: 24px;
  }

  h2 {
    font-size: 1.9rem;
  }

  .actions {
    flex-direction: column;
  }
}
</style>
