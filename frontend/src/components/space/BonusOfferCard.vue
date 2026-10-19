<template>
  <section class="bonusOffer" :aria-label="t('space.panel.bonusLabel')">
    <span class="bonusLabel">{{ t("space.panel.bonusLabel") }}</span>
    <strong>{{ title }}</strong>
    <small>{{ meta }}</small>
    <div class="bonusActions">
      <button type="button" class="bonusAccept" @click="$emit('accept')">
        {{ t("space.panel.bonusDoIt") }}
      </button>
      <button v-if="canSwitch" type="button" class="bonusAnother" @click="$emit('another')">
        {{ t("space.panel.bonusAnother") }}
      </button>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from "vue-i18n";
import { formatNumber, numberAwareT } from "@/lib/i18nNumbers";

defineProps({
  title: { type: String, required: true },
  meta: { type: String, default: "" },
  canSwitch: { type: Boolean, default: false },
});

defineEmits(["accept", "another"]);

const { locale, t: baseT } = useI18n();
// B10: numbers in copy use the locale's digits; a numeric count picks the plural form.
const t = numberAwareT(baseT, () => locale.value);
const fmt = (value) => formatNumber(value, locale.value);
</script>

<style scoped>
.bonusOffer {
  display: grid;
  gap: 6px;
  padding: 11px 12px;
  border-radius: 16px;
  background: rgba(247, 215, 116, 0.035);
  border: 1px dashed rgba(247, 215, 116, 0.32);
}

.bonusLabel {
  color: rgba(247, 215, 116, 0.88);
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.06em;
}

.bonusOffer strong {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.88rem;
}

.bonusOffer small {
  color: rgba(255, 255, 255, 0.56);
  font-size: 0.72rem;
  line-height: 1.45;
}

.bonusActions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 2px;
}

.bonusAccept {
  min-height: 40px;
  padding: 8px 14px;
  border-radius: 11px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(247, 215, 116, 0.3);
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 850;
}

.bonusAnother {
  padding: 4px 2px;
  border: 0;
  color: rgba(110, 229, 255, 0.86);
  background: transparent;
  cursor: pointer;
  font-size: 0.74rem;
  font-weight: 850;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.bonusAccept:hover,
.bonusAccept:focus-visible {
  background: rgba(247, 215, 116, 0.1);
  outline: none;
}

.bonusAnother:focus-visible {
  outline: 2px solid rgba(110, 229, 255, 0.6);
  outline-offset: 2px;
}
</style>
