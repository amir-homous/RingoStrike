<template>
  <section class="nextActionCard" :class="{ allDone }">
    <div class="cardGlow" aria-hidden="true"></div>

    <div class="content">
      <p class="kicker">{{ t("postCheckin.eyebrow") }}</p>
      <h2>{{ title }}</h2>
      <p>{{ body }}</p>
      <p class="discoverHint">{{ t("challengeInvite.text") }}</p>
    </div>

    <div class="actions">
      <RouterLink class="primaryAction" to="/challenges">
        <span>{{ primaryLabel }}</span>
        <span aria-hidden="true">→</span>
      </RouterLink>

      <RouterLink
        v-if="currentPathTo"
        class="secondaryAction"
        :to="currentPathTo"
      >
        {{ t("postCheckin.viewCurrent") }}
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps({
  enrollmentId: { type: [Number, String], default: null },
  allDone: { type: Boolean, default: false },
});

const { t } = useI18n();

const currentPathTo = computed(() => {
  return props.enrollmentId ? `/enrollment/${props.enrollmentId}` : "";
});

const title = computed(() => {
  return props.allDone
    ? t("postCheckin.allTitle")
    : t("postCheckin.title");
});

const body = computed(() => {
  return props.allDone
    ? t("postCheckin.allBody")
    : t("postCheckin.body");
});

const primaryLabel = computed(() => {
  return props.allDone
    ? t("postCheckin.explore")
    : t("postCheckin.discover");
});
</script>

<style scoped>
.nextActionCard {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: center;
  padding: 22px;
  border-radius: 26px;
  border: 1px solid rgba(74, 222, 128, 0.18);
  background:
    radial-gradient(circle at 0% 0%, rgba(74, 222, 128, 0.13), transparent 34%),
    radial-gradient(circle at 96% 8%, rgba(253, 230, 138, 0.10), transparent 34%),
    rgba(255, 255, 255, 0.028);
  box-shadow: 0 22px 70px rgba(0, 0, 0, 0.22);
}

.nextActionCard.allDone {
  border-color: rgba(110, 229, 255, 0.20);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.12), transparent 34%),
    radial-gradient(circle at 96% 8%, rgba(74, 222, 128, 0.10), transparent 34%),
    rgba(255, 255, 255, 0.028);
}

.cardGlow {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.content,
.actions {
  position: relative;
  z-index: 1;
}

.kicker {
  margin: 0 0 7px;
  color: rgba(134, 239, 172, 0.88);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.95);
  font-size: clamp(1.45rem, 3vw, 2.1rem);
  line-height: 1.08;
}

p {
  max-width: 760px;
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.65;
}

.discoverHint {
  padding-top: 10px;
  color: rgba(255, 255, 255, 0.56);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--s-10);
}

.primaryAction,
.secondaryAction {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--s-8);
  min-height: 42px;
  padding: 10px 15px;
  border-radius: 15px;
  text-decoration: none;
  font-weight: 850;
  white-space: nowrap;
}

.primaryAction {
  color: rgba(255, 255, 255, 0.94);
  background:
    linear-gradient(135deg, rgba(253, 230, 138, 0.19), rgba(110, 229, 255, 0.13)),
    rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(253, 230, 138, 0.24);
}

.secondaryAction {
  color: rgba(255, 255, 255, 0.86);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.10);
}

.primaryAction:hover,
.secondaryAction:hover {
  background: rgba(255, 255, 255, 0.075);
}

@media (max-width: 760px) {
  .nextActionCard {
    grid-template-columns: 1fr;
  }

  .actions {
    justify-content: stretch;
  }

  .primaryAction,
  .secondaryAction {
    width: 100%;
    white-space: normal;
    text-align: center;
  }
}
</style>
