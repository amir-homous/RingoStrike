<template>
  <section class="inviteCard">
    <div>
      <p class="inviteKicker">{{ t("challengeInvite.eyebrow") }}</p>
      <h2 v-if="title" class="inviteTitle">{{ title }}</h2>
      <p class="inviteText">{{ text }}</p>
    </div>

    <RouterLink v-if="showAction" class="inviteLink" to="/challenges">
      <span>{{ actionLabel }}</span>
      <span aria-hidden="true">→</span>
    </RouterLink>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps({
  title: { type: String, default: "" },
  text: { type: String, default: "" },
  actionLabel: { type: String, default: "" },
  showAction: { type: Boolean, default: true },
});

const { t } = useI18n();

const text = computed(() => {
  return props.text || t("challengeInvite.text");
});

const actionLabel = computed(() => {
  return props.actionLabel || t("challengeInvite.action");
});
</script>

<style scoped>
.inviteCard {
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--s-16);
  padding: 18px;
  border-radius: 24px;
  border: 1px solid rgba(253, 230, 138, 0.16);
  background:
    radial-gradient(circle at 0% 0%, rgba(253, 230, 138, 0.10), transparent 34%),
    radial-gradient(circle at 100% 0%, rgba(110, 229, 255, 0.07), transparent 35%),
    rgba(255, 255, 255, 0.026);
}

.inviteKicker {
  margin: 0 0 7px;
  color: rgba(253, 230, 138, 0.88);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.inviteTitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.2rem;
}

.inviteText {
  max-width: 760px;
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.65;
}

.inviteTitle + .inviteText {
  margin-top: 7px;
}

.inviteLink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--s-8);
  min-height: 42px;
  padding: 10px 15px;
  border-radius: 15px;
  color: rgba(255, 255, 255, 0.94);
  text-decoration: none;
  font-weight: 850;
  white-space: nowrap;
  background:
    linear-gradient(135deg, rgba(253, 230, 138, 0.18), rgba(110, 229, 255, 0.12)),
    rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(253, 230, 138, 0.22);
}

.inviteLink:hover {
  background: rgba(255, 255, 255, 0.075);
}

@media (max-width: 680px) {
  .inviteCard {
    align-items: stretch;
    flex-direction: column;
  }

  .inviteLink {
    width: 100%;
    white-space: normal;
    text-align: center;
  }
}
</style>
