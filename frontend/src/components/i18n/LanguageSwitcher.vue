<template>
  <div class="languageSwitcher" :aria-label="t('language.label')">
    <button
      v-for="option in options"
      :key="option"
      type="button"
      class="languageButton"
      :class="{ active: locale === option }"
      :aria-pressed="locale === option"
      @click="setLocale(option)"
    >
      {{ t(`language.${option}`) }}
    </button>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { setLocale, SUPPORTED_LOCALES } from "@/i18n";

const { locale, t } = useI18n();

const options = computed(() => SUPPORTED_LOCALES);
</script>

<style scoped>
.languageSwitcher {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(255, 255, 255, 0.04);
}

.languageButton {
  min-width: 34px;
  min-height: 30px;
  padding: 5px 8px;
  border: 0;
  border-radius: 999px;
  color: var(--muted);
  background: transparent;
  cursor: pointer;
  font-weight: 850;
  font-size: 0.75rem;
}

.languageButton.active {
  color: rgba(255, 255, 255, 0.94);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.16), rgba(195, 90, 214, 0.12)),
    rgba(255, 255, 255, 0.055);
}
</style>
