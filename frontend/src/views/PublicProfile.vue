<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import api from "@/lib/api";

import BaseCard from "@/components/ui/BaseCard.vue";

import UserAvatar from "@/components/profile/UserAvatar.vue";
import ProfileHeroCard from "@/components/profile/ProfileHeroCard.vue";
import ProfileStatsGrid from "@/components/profile/ProfileStatsGrid.vue";
import ConsistencyHeatmap from "@/components/profile/ConsistencyHeatmap.vue";

import AchievementPreview from "@/components/achievements/AchievementPreview.vue";

const route = useRoute();

const loading = ref(true);
const error = ref("");

const profile = ref(null);

const achievements = ref([]);
const consistencyDays = ref([]);

const visibleActivities = ref(8);

const username = computed(
  () => route.params.username
);

const iconMap = {
  check: "✓",
  flame: "🔥",
  trophy: "🏆",
  bolt: "⚡",
  star: "✨",
};

async function loadProfile() {
  loading.value = true;
  error.value = "";

  try {
    // MAIN PROFILE
    const response = await api.get(
      `/api/public/profile/${username.value}`
    );

    profile.value = response.data.profile;

    // ACHIEVEMENTS
    try {
      const achievementsResponse = await api.get(
        `/api/public/profile/${username.value}/achievements`
      );

      achievements.value =
        achievementsResponse.data.achievements || [];
    } catch (err) {
      console.error(
        "failed achievements",
        err
      );
    }

    // CONSISTENCY
    try {
      const consistencyResponse = await api.get(
        `/api/public/profile/${username.value}/consistency`
      );

      consistencyDays.value =
        consistencyResponse.data.days || [];
    } catch (err) {
      console.error(
        "failed consistency",
        err
      );
    }

  } catch (err) {
    error.value =
      err?.response?.data?.error ||
      "failed_to_load_profile";
  } finally {
    loading.value = false;
  }
}

function formatRelativeDate(dateString) {
  const date = new Date(dateString);

  const now = new Date();

  const diff =
    Math.floor((now - date) / 1000);

  if (diff < 60) {
    return "Just now";
  }

  if (diff < 3600) {
    return `${Math.floor(diff / 60)}m ago`;
  }

  if (diff < 86400) {
    return `${Math.floor(diff / 3600)}h ago`;
  }

  if (diff < 604800) {
    return `${Math.floor(diff / 86400)}d ago`;
  }

  return date.toLocaleDateString();
}

watch(
  () => route.params.username,
  () => {
    loadProfile();
  }
);

const displayedActivities = computed(
  () =>
    profile.value?.recent_activity?.slice(
      0,
      visibleActivities.value
    ) || []
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
        <ProfileHeroCard :profile="profile" :is-owner="false">
          <template #avatar>
            <UserAvatar
              :src="profile.avatar_url"
              :name="profile.name"
            />
          </template>
        </ProfileHeroCard>


                <div class="section">
                  <div class="section-header">
                    <h2>Consistency Footprint</h2>
                  </div>

                  <ConsistencyHeatmap
                    :days="consistencyDays"
                    :readonly="true"
                  />
                </div>

        <!-- ACHIEVEMENTS -->
        <div
          v-if="achievements.length"
          class="section"
        >
          <div class="section-header">
            <h2>Featured Achievements</h2>
          </div>

          <AchievementPreview
            :achievements="achievements"
          />
        </div>


        <!-- ACTIVITY -->
          <div class="section">
            <div class="section-header">
              <h2>Momentum Memory</h2>
            </div>

            <div class="activity-list">
              <BaseCard
                v-for="event in displayedActivities"
                :key="event.id"
                class="activity-card"
              >
                <div class="activity-top">
                  <div>
                    <div class="activity-icon">
                      {{ iconMap[event.icon] || "•" }}
                    </div>
                    <strong>
                      {{ event.title }}
                    </strong>

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
                    {{ formatRelativeDate(event.created_at) }}
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

            <div
              v-if="
                profile.recent_activity.length >
                visibleActivities
              "
              class="show-more-wrap"
            >
              <button
                class="show-more"
                @click="visibleActivities += 8"
              >
                Show More
              </button>
            </div>
          </div>


        <!-- STATS -->
        <div class="section">
          <div class="section-header">
            <h2>Progression Stats</h2>
          </div>

          <ProfileStatsGrid :profile="profile" />
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

.show-more-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.show-more {
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.04);
  color: white;
  border-radius: 12px;
  padding: 10px 18px;
  cursor: pointer;
  transition: all .18s ease;
}

.show-more:hover {
  background: rgba(255,255,255,.08);
}

.activity-icon{
  width:40px;
  height:40px;
  border-radius:12px;
  display:grid;
  place-items:center;
  background:rgba(255,255,255,.05);
  border:1px solid rgba(255,255,255,.08);
  font-size:18px;
  flex-shrink:0;
}

</style>