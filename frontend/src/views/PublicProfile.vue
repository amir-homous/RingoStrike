<template>
  <AppContainer>
    <AppHeader />

    <UiState
      :loading="loading"
      :error="!!error"
      :empty="false"
      loading-title="Loading profile..."
      :error-text="error"
      @retry="load"
    />

    <div
      v-if="!loading && !error && profile"
      class="stack-16"
    >
      <ProfileHeroCard
        :profile="profile"
        :isOwner="false"
      />

      <ProfileStatsGrid
        :profile="profile"
      />

      <ConsistencyHeatmap
        :days="consistency"
      />

      <AchievementPreview
        :achievements="achievements"
      />

      <ActivityTimeline
        :events="profile.recent_activity || []"
        :loading="false"
      />
    </div>
  </AppContainer>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";

import api from "@/lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import UiState from "@/components/ui/UiState.vue";

import ProfileHeroCard from "@/components/profile/ProfileHeroCard.vue";
import ProfileStatsGrid from "@/components/profile/ProfileStatsGrid.vue";
import ConsistencyHeatmap from "@/components/profile/ConsistencyHeatmap.vue";

import AchievementPreview from "@/components/achievements/AchievementPreview.vue";
import ActivityTimeline from "@/components/activity/ActivityTimeline.vue";

const route = useRoute();

const loading = ref(true);
const error = ref("");

const profile = ref(null);
const consistency = ref([]);
const achievements = ref([]);

async function load() {
  loading.value = true;
  error.value = "";

  try {
    const username = route.params.username;

    const [p, c, a] = await Promise.all([
      api.get(`/api/public/profile/${username}`),
      api.get(`/api/public/profile/${username}/consistency`),
      api.get(`/api/public/profile/${username}/achievements`),
    ]);

    profile.value = p.data.profile;

    consistency.value =
      c.data.days || [];

    achievements.value =
      a.data.achievements || [];
  }
  catch (err) {
    error.value =
      err?.response?.data?.error ||
      err?.message ||
      "Failed loading profile";
  }
  finally {
    loading.value = false;
  }
}

onMounted(load);
</script>