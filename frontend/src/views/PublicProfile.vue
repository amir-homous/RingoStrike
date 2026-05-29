<script setup>
import { onMounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import api from "../lib/api";

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

onMounted(loadProfile);
</script>

<template>
  <div class="public-profile-page">
    <div class="container">
      <div v-if="loading" class="state-card">
        <p>Loading profile...</p>
      </div>

      <div v-else-if="error" class="state-card error">
        <p>{{ error }}</p>
      </div>

      <template v-else-if="profile">
        <!-- HERO -->
        <section class="hero-card">
          <div class="hero-top">
            <img
              :src="`/${profile.avatar_url || 'player.png'}`"
              class="avatar"
              alt="avatar"
            />

            <div class="identity">
              <h1>{{ profile.name }}</h1>

              <p class="username">
                @{{ profile.username }}
              </p>

              <div class="title-pill">
                {{ profile.title?.label }}
              </div>
            </div>
          </div>

          <p class="tagline">
            {{ profile.tagline }}
          </p>

          <p
            v-if="profile.bio"
            class="bio"
          >
            {{ profile.bio }}
          </p>
        </section>

        <!-- STATS -->
        <section class="stats-grid">
          <div class="stat-card">
            <span class="label">Level</span>
            <strong>{{ profile.stats.level }}</strong>
          </div>

          <div class="stat-card">
            <span class="label">XP</span>
            <strong>{{ profile.stats.total_xp }}</strong>
          </div>

          <div class="stat-card">
            <span class="label">Current Streak</span>
            <strong>{{ profile.stats.current_streak }}</strong>
          </div>

          <div class="stat-card">
            <span class="label">Longest Streak</span>
            <strong>{{ profile.stats.longest_streak }}</strong>
          </div>
        </section>

        <!-- ACTIVITY -->
        <section class="activity-section">
          <div class="section-header">
            <h2>Momentum Memory</h2>
          </div>

          <div class="activity-list">
            <div
              v-for="event in profile.recent_activity"
              :key="event.id"
              class="activity-card"
            >
              <div class="activity-top">
                <strong>{{ event.title }}</strong>

                <span class="activity-type">
                  {{ event.type }}
                </span>
              </div>

              <p class="subtitle">
                {{ event.subtitle }}
              </p>

              <span class="date">
                {{ event.created_at }}
              </span>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<style scoped>
.public-profile-page {
  min-height: 100vh;
  padding: 40px 20px 80px;
  background:
    radial-gradient(circle at top, rgba(255,255,255,0.06), transparent 30%),
    #0b1020;
  color: white;
}

.container {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}

.hero-card,
.stat-card,
.activity-card,
.state-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 24px;
  backdrop-filter: blur(12px);
}

.hero-card {
  padding: 32px;
  margin-bottom: 24px;
}

.hero-top {
  display: flex;
  gap: 20px;
  align-items: center;
}

.avatar {
  width: 96px;
  height: 96px;
  border-radius: 24px;
  object-fit: cover;
}

.identity h1 {
  margin: 0;
  font-size: 2rem;
}

.username {
  opacity: 0.7;
  margin-top: 6px;
}

.title-pill {
  margin-top: 12px;
  display: inline-flex;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  font-size: 0.9rem;
}

.tagline {
  margin-top: 24px;
  font-size: 1.05rem;
  opacity: 0.9;
}

.bio {
  margin-top: 14px;
  opacity: 0.7;
  line-height: 1.6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 24px;
}

.label {
  display: block;
  opacity: 0.6;
  margin-bottom: 10px;
}

.activity-section {
  margin-top: 10px;
}

.section-header {
  margin-bottom: 16px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-card {
  padding: 20px;
}

.activity-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.activity-type {
  opacity: 0.5;
  text-transform: uppercase;
  font-size: 0.8rem;
}

.subtitle {
  margin-top: 10px;
  opacity: 0.8;
}

.date {
  margin-top: 14px;
  display: block;
  opacity: 0.45;
  font-size: 0.85rem;
}

.state-card {
  padding: 40px;
  text-align: center;
}

.error {
  border-color: rgba(255,80,80,0.4);
}

@media (max-width: 768px) {
  .hero-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>