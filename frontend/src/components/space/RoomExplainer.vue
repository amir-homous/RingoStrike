<template>
  <!-- B37 (D83): "What am I looking at?" under Ringo's first card. One line per row; a row opens
       Ringo's explanation. The numbers match the pins in the room. Shown once; "Got it" hides it. -->
  <section class="roomExplainer" :aria-label="t('space.explainer.title')">
    <h3>{{ t("space.explainer.title") }}</h3>
    <ul>
      <li v-for="(row, index) in rows" :key="row.key">
        <button
          type="button"
          class="explainerRow"
          :aria-expanded="openKey === row.key ? 'true' : 'false'"
          :data-row="row.key"
          @click="openKey = openKey === row.key ? '' : row.key"
        >
          <span class="rowPin" aria-hidden="true">{{ fmt(index + 1) }}</span>
          <span class="rowCopy">
            <strong>{{ row.label }}</strong>
            <span>{{ row.line }}</span>
          </span>
        </button>
        <p v-if="openKey === row.key" class="rowMore">{{ row.more }}</p>
      </li>
    </ul>
    <button type="button" class="gotIt" @click="$emit('dismiss')">{{ t("space.explainer.gotIt") }}</button>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import api from "@/lib/api";
import { formatNumber } from "@/lib/i18nNumbers";
import { EXPLAINER_ROWS, challengeLineKey } from "@/lib/roomExplainer";

const props = defineProps({
  // The corner's joined challenge; its members_count decides "with others" (D84).
  challengeId: { type: [Number, String, null], default: null },
});

defineEmits(["dismiss"]);

const { locale, t } = useI18n();
const fmt = (value) => formatNumber(value, locale.value);
const openKey = ref("");
const membersCount = ref(0);

const rows = computed(() => EXPLAINER_ROWS.map((key) => {
  const lineKey = key === "challenges" ? challengeLineKey(membersCount.value) : key;
  return {
    key,
    label: t(`space.explainer.${key}Label`),
    line: t(`space.explainer.${lineKey}Line`),
    more: t(`space.explainer.${key}More`),
  };
}));

// The corner's challenges can load after the box: read the count whenever the id arrives.
watch(() => props.challengeId, async (id) => {
  membersCount.value = 0;
  if (!id) return;
  try {
    const { data } = await api.get(`/challenges/${id}`);
    if (String(id) === String(props.challengeId)) membersCount.value = Number(data?.item?.members_count ?? 0);
  } catch {
    // No count: the plain line ("a small daily habit") stays.
  }
}, { immediate: true });
</script>

<style scoped>
.roomExplainer {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
}

h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.9rem;
}

ul {
  display: grid;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.explainerRow {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  width: 100%;
  min-height: 44px;
  padding: 6px 8px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: start;
  cursor: pointer;
}

.explainerRow:hover,
.explainerRow[aria-expanded="true"] {
  background: rgba(255, 255, 255, 0.05);
}

.explainerRow:focus-visible,
.gotIt:focus-visible {
  outline: 2px solid #6ee5ff;
  outline-offset: 2px;
}

.rowPin {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #f5c84c;
  color: #1a1404;
  font-size: 0.74rem;
  font-weight: 850;
}

.rowCopy {
  display: grid;
  gap: 2px;
  font-size: 0.82rem;
  line-height: 1.4;
}

.rowCopy strong {
  color: rgba(255, 255, 255, 0.92);
}

.rowCopy span {
  color: rgba(255, 255, 255, 0.66);
}

.rowMore {
  margin: 4px 8px 4px 40px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.8rem;
  line-height: 1.5;
}

:dir(rtl) .rowMore {
  margin: 4px 40px 4px 8px;
}

.gotIt {
  justify-self: end;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  border: 1px solid rgba(110, 229, 255, 0.4);
  background: rgba(110, 229, 255, 0.1);
  color: #6ee5ff;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 750;
  cursor: pointer;
}
</style>
