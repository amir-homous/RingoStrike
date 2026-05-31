<template>
  <AppContainer>
    <AppHeader />

    <div class="publicShell">
      <section class="publicHead">
        <div>
          <p class="eyebrow">
            <span class="pulseDot"></span>
            Public Progression Profile
          </p>

          <h1 class="pageTitle">
            {{ profile?.name || username }}’s journey
          </h1>

          <p class="pageSubtitle">
            A public snapshot of consistency, achievements, and recent progression.
          </p>
        </div>

        <RouterLink class="publicAction" to="/login">
          Start your path
        </RouterLink>
      </section>

      <UiState
        :loading="loading"
        :error="!!error"
        :empty="false"
        loading-title="Loading profile..."
        :error-text="error"
        @retry="load"
      />

      <BaseCard
        v-if="!loading && isPrivate"
        class="stateCard"
      >
        <div class="stateIcon">🔒</div>

        <div>
          <h2>Private Profile</h2>

          <p class="caption">
            This user has chosen to keep their progression journey private.
          </p>
        </div>
      </BaseCard>

      <BaseCard
        v-else-if="!loading && isNotFound"
        class="stateCard"
      >
        <div class="stateIcon">∅</div>

        <div>
          <h2>Profile Not Found</h2>

          <p class="caption">
            The requested profile does not exist or the username is unavailable.
          </p>
        </div>
      </BaseCard>

      <template v-if="!loading && !error && profile">
        <section class="publicSummary">
          <div class="summaryCard">
            <span class="summaryLabel">Consistency days</span>
            <strong>{{ consistency.length }}</strong>
            <small>Public check-in signal</small>
          </div>

          <div class="summaryCard">
            <span class="summaryLabel">Achievements</span>
            <strong>{{ achievements.length }}</strong>
            <small>Unlocked public milestones</small>
          </div>

          <div class="summaryCard">
            <span class="summaryLabel">Identity</span>
            <strong>{{ profileTitleText }}</strong>
            <small>{{ profile.tagline || "Progression in motion" }}</small>
          </div>
        </section>

        <ProfileHeroCard
          :profile="profile"
          :isOwner="false"
        />

        <ProfileStatsGrid :profile="profile" />

        <section class="publicGrid">
          <div class="mainColumn">
            <ConsistencyHeatmap :days="consistency" />

            <AchievementPreview :achievements="achievements" />
          </div>

          <div class="sideColumn">
            <BaseCard class="publicContext">
              <p class="eyebrow compact">Public signal</p>

              <h2 class="cardTitle">
                Consistency without noise
              </h2>

              <p class="cardText">
                RingoStrike public profiles are designed to show identity,
                momentum, and proof of consistency without exposing private app controls.
              </p>
            </BaseCard>

            <BaseCard class="publicContext">
              <p class="eyebrow compact">Recent momentum</p>

              <p class="cardText">
                Recent public activity appears below when the user chooses to share it.
              </p>
            </BaseCard>
          </div>
        </section>

        <ActivityTimeline
          :events="profile.recent_activity || []"
          :loading="false"
        />
      </template>
    </div>
  </AppContainer>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRoute, RouterLink } from "vue-router";

import api from "@/lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import UiState from "@/components/ui/UiState.vue";
import BaseCard from "@/components/ui/BaseCard.vue";

import ProfileHeroCard from "@/components/profile/ProfileHeroCard.vue";
import ProfileStatsGrid from "@/components/profile/ProfileStatsGrid.vue";
import ConsistencyHeatmap from "@/components/profile/ConsistencyHeatmap.vue";

import AchievementPreview from "@/components/achievements/AchievementPreview.vue";
import ActivityTimeline from "@/components/activity/ActivityTimeline.vue";

const route = useRoute();

const isPrivate = ref(false);
const isNotFound = ref(false);

const loading = ref(true);
const error = ref("");

const profile = ref(null);
const consistency = ref([]);
const achievements = ref([]);

const username = computed(() => {
  return String(route.params.username || "profile");
});

const profileTitleText = computed(() => {
  const title = profile.value?.title;

  if (!title) return "Builder";

  if (typeof title === "string") return title;

  if (typeof title === "object") {
    return title.label || title.key || "Builder";
  }

  return "Builder";
});

async function load() {
  loading.value = true;
  error.value = "";
  isPrivate.value = false;
  isNotFound.value = false;

  try {
    const currentUsername = username.value;

    const [p, c, a] = await Promise.all([
      api.get(`/api/public/profile/${currentUsername}`),
      api.get(`/api/public/profile/${currentUsername}/consistency`),
      api.get(`/api/public/profile/${currentUsername}/achievements`),
    ]);

    profile.value = p.data.profile;
    consistency.value = c.data.days || [];
    achievements.value = a.data.achievements || [];
  } catch (err) {
    const code = err?.response?.data?.error;

    profile.value = null;
    consistency.value = [];
    achievements.value = [];

    if (code === "profile_private") {
      isPrivate.value = true;
      return;
    }

    if (code === "profile_not_found") {
      isNotFound.value = true;
      return;
    }

    error.value = code || err?.message || "Failed loading profile";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.publicShell {
  display: grid;
  gap: var(--s-16);
}

.publicHead {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: end;
  padding: 24px;
  border-radius: 28px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.11), transparent 38%),
    radial-gradient(circle at 92% 10%, rgba(195, 90, 214, 0.10), transparent 35%),
    rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.20);
}

.publicHead::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.publicHead > * {
  position: relative;
  z-index: 1;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.eyebrow.compact {
  margin-bottom: 8px;
}

.pulseDot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #4ade80;
  box-shadow: 0 0 16px rgba(74, 222, 128, 0.7);
}

.pageTitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.97);
  font-size: clamp(2rem, 4vw, 4rem);
  line-height: 0.98;
  letter-spacing: -0.065em;
}

.pageSubtitle {
  margin: 14px 0 0;
  max-width: 720px;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.7;
}

.publicAction {
  min-height: 40px;
  padding: 10px 15px;
  border-radius: 15px;
  color: rgba(255, 255, 255, 0.94);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.17), rgba(195, 90, 214, 0.12)),
    rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(110, 229, 255, 0.22);
  text-decoration: none;
  font-weight: 850;
  white-space: nowrap;
}

.stateCard {
  display: flex;
  gap: var(--s-16);
  align-items: flex-start;
  padding: 22px;
}

.stateIcon {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 17px;
  background: rgba(99, 102, 241, 0.14);
}

.stateCard h2 {
  margin: 0 0 8px;
  color: rgba(255, 255, 255, 0.94);
}

.publicSummary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
}

.summaryCard {
  padding: 16px;
  border-radius: 22px;
  background:
    radial-gradient(circle at 100% 0%, rgba(110, 229, 255, 0.07), transparent 36%),
    rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.085);
}

.summaryLabel {
  display: block;
  color: var(--muted2);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.summaryCard strong {
  display: block;
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.2rem;
}

.summaryCard small {
  display: block;
  margin-top: 5px;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.45;
}

.publicGrid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.75fr);
  gap: var(--s-12);
  align-items: start;
}

.mainColumn,
.sideColumn {
  display: grid;
  gap: var(--s-12);
}

.publicContext {
  background:
    radial-gradient(circle at 100% 0%, rgba(195, 90, 214, 0.07), transparent 36%),
    rgba(255, 255, 255, 0.025);
}

.cardTitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  letter-spacing: -0.035em;
}

.cardText {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.65;
}

@media (max-width: 900px) {
  .publicHead,
  .publicGrid {
    grid-template-columns: 1fr;
  }

  .publicSummary {
    grid-template-columns: 1fr;
  }

  .publicAction {
    justify-self: start;
  }
}

@media (max-width: 560px) {
  .publicHead {
    padding: 18px;
    border-radius: 23px;
  }

  .publicAction {
    width: 100%;
    text-align: center;
  }

  .stateCard {
    flex-direction: column;
  }
}
</style>