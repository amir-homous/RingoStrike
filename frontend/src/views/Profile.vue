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
      v-if="!loading && !error"
      class="stack-16"
    >
      <ProfileHeroCard
  :profile="profile"
  @edit-profile="handleEditProfile"
/>

<ProfileSettingsCard
  v-if="showEditProfile"
  @close="showEditProfile = false"
  @saved="handleProfileSaved"
/>

        <div v-if="showEditProfile">
  TEST WORKS
</div>

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
        :events="activityEvents"
        :loading="false"
      />


      <BaseCard>
        <h2 class="h2">
          Future Extensions
        </h2>

        <p class="caption">
          Public profiles • social layer • seasonal progression • AI insights
        </p>
      </BaseCard>
    </div>
    <RewardFeedback
    :items="rewardToasts"
    />
  </AppContainer>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import UiState from "@/components/ui/UiState.vue";
import BaseCard from "@/components/ui/BaseCard.vue";

import ProfileHeroCard from "@/components/profile/ProfileHeroCard.vue";
import ProfileStatsGrid from "@/components/profile/ProfileStatsGrid.vue";
import ConsistencyHeatmap from "@/components/profile/ConsistencyHeatmap.vue";

import ProfileSettingsCard from "@/components/profile/ProfileSettingsCard.vue";


import AchievementPreview from "@/components/achievements/AchievementPreview.vue";
import ActivityTimeline from "@/components/activity/ActivityTimeline.vue";

import RewardFeedback from "@/components/feedback/RewardFeedback.vue";

import { watch } from "vue";



const loading = ref(true);
const error = ref("");

const profile = ref(null);
const consistency = ref([]);
const achievements = ref([]);
const activityEvents = ref([]);

const showEditProfile = ref(false);

const rewardToasts = ref([]);

function pushToast(text, type = "success") {
  const id = `${Date.now()}-${Math.random()}`;

  rewardToasts.value.push({
    id,
    text,
    type,
  });

  setTimeout(() => {
    rewardToasts.value =
      rewardToasts.value.filter(
        (t) => t.id !== id
      );
  }, 2200);
}

function handleProfileSaved() {

  pushToast(
    "Profile updated successfully",
    "success"
  );

  showEditProfile.value = false;

  load();
}

function handleEditProfile() {

  showEditProfile.value = true
}


watch(showEditProfile, (v) => {

});


async function load() {
  loading.value = true;
  error.value = "";

  try {
    const [p, c, a, t] = await Promise.all([
      api.get("/me/profile"),
      api.get("/me/consistency"),
      api.get("/me/achievements"),
      api.get("/me/activity"),
    ]);

    profile.value = p.data.profile;
    consistency.value = c.data.days || [];
    achievements.value = a.data.achievements || [];
    activityEvents.value = t.data.events || [];
  } catch (e) {
    error.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>