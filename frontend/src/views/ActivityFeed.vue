<template>
  <AppContainer>
    <AppHeader />

    <main class="activityPage">
      <UiState
        :loading="loading"
        :error="!!error"
        :empty="false"
        :loading-title="t('common.loading')"
        :loading-text="t('common.states.loadingText')"
        :error-title="t('common.states.errorTitle')"
        :error-text="error || t('common.pleaseTryAgain')"
        @retry="loadActivity"
      />

      <ActivityTimeline
        v-if="!loading && !error"
        :events="activityEvents"
        :loading="false"
      />
    </main>
  </AppContainer>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import UiState from "@/components/ui/UiState.vue";
import ActivityTimeline from "@/components/activity/ActivityTimeline.vue";

const { t } = useI18n();

const loading = ref(true);
const error = ref("");
const activityEvents = ref([]);

async function loadActivity() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/me/activity");
    activityEvents.value = response.data?.events || [];
  } catch (e) {
    console.error(e);
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

onMounted(loadActivity);
</script>

<style scoped>
.activityPage {
  display: grid;
  gap: var(--s-16);
  min-width: 0;
}
</style>
