<template>
  <section class="todayStrip" :class="{ complete: mainDone }">
    <div class="todayHead">
      <span class="stripLabel">{{ t("space.panel.todayStrip") }}</span>
      <strong v-if="total > 0">
        {{ t("space.shell.todayMissions") }} · {{ done }}/{{ total }}
      </strong>
    </div>
    <p v-if="firstRewardText" class="firstRewardLine" :class="{ complete: firstRewardUnlocked }">
      {{ firstRewardText }}
    </p>
  </section>
</template>

<script setup>
import { useI18n } from "vue-i18n";

defineProps({
  done: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  mainDone: { type: Boolean, default: false },
  firstRewardText: { type: String, default: "" },
  firstRewardUnlocked: { type: Boolean, default: false },
});

const { t } = useI18n();
</script>

<style scoped>
.todayStrip {
  display: grid;
  gap: 6px;
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.032);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.todayStrip.complete {
  border-color: rgba(80, 220, 140, 0.16);
  background: rgba(80, 220, 140, 0.05);
}

.todayHead {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 6px 10px;
}

.stripLabel {
  color: rgba(110, 229, 255, 0.72);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.todayHead strong {
  color: rgba(255, 255, 255, 0.86);
  font-size: 0.78rem;
}

.firstRewardLine {
  margin: 0;
  color: rgba(247, 215, 116, 0.82);
  font-size: 0.76rem;
  line-height: 1.5;
}

.firstRewardLine.complete {
  color: rgba(120, 230, 160, 0.86);
}
</style>
