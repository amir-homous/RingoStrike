<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import api from "@/lib/api";

import BaseCard from "@/components/ui/BaseCard.vue";

import UserAvatar from "@/components/profile/UserAvatar.vue";
import ProfileHeroCard from "@/components/profile/ProfileHeroCard.vue";
import ProfileStatsGrid from "@/components/profile/ProfileStatsGrid.vue";
import ConsistencyHeatmap from "@/components/profile/ConsistencyHeatmap.vue";

const route = useRoute();

const loading = ref(true);
const error = ref("");
const profile = ref(null);

const username = computed(() => route.params.username);

async function loadProfile() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get(
      `/api/public/profile/${username.value}`
    );

    profile.value = response.data.profile;
  } catch (err) {
    error.value =
      err?.response?.data?.error || "failed_to_load_profile";
  } finally {
    loading.value = false;
  }
}

watch(
  () => route.params.username,
  () => {
    loadProfile();
  }
);

onMounted(loadProfile);
</script>

<template>
  <div class="public-profile-page">
    <div class="container">
      <!-- LOADING -->
      <BaseCard
        v-if="loading"
        class="state-card"
      >
        <p>Loading progression identity...</p>
      </BaseCard>

      <!-- ERROR -->
      <BaseCard
        v-else-if="error"
        class="state-card error"
      >
        <p>{{ error }}</p>
      </BaseCard>

      <!-- PROFILE -->
      <template v-else-if="profile">
        <!-- HERO -->
        <ProfileHeroCard :profile="profile">
          <template #avatar>
            <UserAvatar
              :src="profile.avatar_url"
              :name="profile.name"
            />
          </template>
        </ProfileHeroCard>

        <!-- STATS -->
        <div class="section">
          <div class="section-header">
            <h2>Progression Stats</h2>
          </div>

          <ProfileStatsGrid :profile="profile" />
        </div>

        <!-- HEATMAP -->
        <!-- <div class="section">
          <div class="section-header">
            <h2>Consistency Footprint</h2>
          </div>

          <ConsistencyHeatmap />
        </div> -->

        <!-- ACTIVITY -->
        <div class="section">
          <div class="section-header">
            <h2>Momentum Memory</h2>
          </div>

          <div class="activity-list">
            <BaseCard
              v-for="event in profile.recent_activity"
              :key="event.id"
              class="activity-card"
            >
              <div class="activity-top">
                <div>
                  <strong>{{ event.title }}</strong>

                  <p class="subtitle">
                    {{ event.subtitle }}
                  </p>
                </div>

                <span class="event-type">
                  {{ event.type }}
                </span>
              </div>

              <div class="activity-footer">
                <span class="date">
                  {{ event.created_at }}
                </span>

                <span
                  v-if="event.rarity"
                  class="rarity"
                >
                  {{ event.rarity }}
                </span>
              </div>
            </BaseCard>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.public-profile-page {
  min-height: 100vh;
  padding: 32px 20px 80px;
}

.container {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
}

.section {
  margin-top: 28px;
}

.section-header {
  margin-bottom: 14px;
}

.section-header h2 {
  font-size: 1rem;
  font-weight: 700;
  opacity: 0.92;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-card {
  padding: 18px;
}

.activity-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.subtitle {
  margin-top: 8px;
  opacity: 0.72;
}

.activity-footer {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date {
  opacity: 0.5;
  font-size: 0.84rem;
}

.event-type {
  opacity: 0.42;
  text-transform: uppercase;
  font-size: 0.72rem;
}

.rarity {
  text-transform: capitalize;
  font-size: 0.8rem;
  opacity: 0.72;
}

.state-card {
  padding: 40px;
  text-align: center;
}

.error {
  border-color: rgba(255, 100, 100, 0.4);
}
</style>