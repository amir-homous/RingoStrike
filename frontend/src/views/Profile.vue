<template>
  <AppContainer>
    <AppHeader />

    <div class="profileShell">
      <section class="profileHead">
        <div>
          <p class="eyebrow">
            <span class="pulseDot"></span>
            {{ t("profile.privateEyebrow") }}
          </p>

          <h1 class="pageTitle">
            {{ t("profile.title") }}
          </h1>

          <p class="pageSubtitle">
            {{ t("profile.subtitle") }}
          </p>
        </div>

        <div class="headActions">
          <button
            type="button"
            class="profileAction"
            @click="handleEditProfile"
          >
            {{ t("profile.edit") }}
          </button>

          <RouterLink
            v-if="profile?.username"
            class="profileAction ghost"
            :to="`/u/${profile.username}`"
          >
            {{ t("profile.publicProfile") }}
          </RouterLink>
        </div>
      </section>

      <UiState
        :loading="loading"
        :error="!!error"
        :empty="false"
        :loading-title="t('profile.loadingTitle')"
        :error-text="error"
        @retry="load"
      />

      <template v-if="!loading && !error && profile">
        <section class="identitySummary">
          <div class="summaryCard">
            <span class="summaryLabel">{{ t("profile.visibility") }}</span>
            <strong>{{ visibilityLabel }}</strong>
            <small>{{ visibilityHint }}</small>
          </div>

          <div class="summaryCard">
            <span class="summaryLabel">{{ t("profile.consistencyDays") }}</span>
            <strong>{{ consistency.length }}</strong>
            <small>{{ t("profile.recordedDays") }}</small>
          </div>

          <div class="summaryCard">
            <span class="summaryLabel">{{ t("profile.achievements") }}</span>
            <strong>{{ unlockedAchievementCount }}</strong>
            <small>{{ t("profile.unlockedMilestones") }}</small>
          </div>
        </section>

        <ProfileHeroCard
          :profile="profile"
          @edit-profile="handleEditProfile"
        />

        <ProfileSettingsCard
          v-if="showEditProfile"
          id="settings"
          class="settingsPanel"
          @close="showEditProfile = false"
          @saved="handleProfileSaved"
        />

        <ProfileStatsGrid :profile="profile" />

        <section class="profileGrid">
          <div class="mainColumn">
            <ConsistencyHeatmap :days="consistency" />

            <AchievementPreview :achievements="achievements" />
          </div>

          <div class="sideColumn">
            <BaseCard class="identityCard">
              <p class="eyebrow compact">{{ t("profile.identityStatus") }}</p>

              <h2 class="cardTitle">
                {{ identityStatusTitle }}
              </h2>

              <p class="cardText">
                {{ identityStatusText }}
              </p>

              <div class="identitySignals">
                <span>{{ profileTitleText }}</span>
                <span>{{ profile?.tagline || t("profile.consistencyMotion") }}</span>
              </div>
            </BaseCard>

            <BaseCard class="nextCard">
              <p class="eyebrow compact">{{ t("profile.comingNext") }}</p>

              <h2 class="cardTitle">
                {{ t("profile.futureTitle") }}
              </h2>

              <p class="cardText">
                {{ t("profile.futureText") }}
              </p>
            </BaseCard>
          </div>
        </section>

        <ActivityTimeline
          :events="activityEvents"
          :loading="false"
        />
      </template>
    </div>

    <RewardFeedback :items="rewardToasts" />
  </AppContainer>
</template>

<script setup>
import { computed, ref, onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
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
import {
  countUnlockedAchievements,
  getProfileTitleText,
  getProfileVisibilityLabel,
  loadPrivateProfileData,
} from "./profileFlow";

const loading = ref(true);
const error = ref("");

const profile = ref(null);

const consistency = ref([]);
const achievements = ref([]);
const activityEvents = ref([]);

const showEditProfile = ref(false);
const rewardToasts = ref([]);
const { t } = useI18n();
const route = useRoute();

const visibilityLabel = computed(() => {
  return getProfileVisibilityLabel(profile.value) === "Private"
    ? t("profile.privateLabel")
    : t("profile.publicLabel");
});

const visibilityHint = computed(() => {
  return getProfileVisibilityLabel(profile.value) === "Private"
    ? t("profile.privateHint")
    : t("profile.publicHint");
});

const unlockedAchievementCount = computed(() => {
  return countUnlockedAchievements(achievements.value);
});

const identityStatusTitle = computed(() => {
  return getProfileVisibilityLabel(profile.value) === "Private"
    ? t("profile.privateMode")
    : t("profile.publicMode");
});

const identityStatusText = computed(() => {
  return getProfileVisibilityLabel(profile.value) === "Private"
    ? t("profile.privateText")
    : t("profile.publicText");
});

const profileTitleText = computed(() => {
  const value = getProfileTitleText(profile.value);
  return value === "Progression Builder" ? t("profile.builder") : value;
});

function pushToast(text, type = "success") {
  const id = `${Date.now()}-${Math.random()}`;

  rewardToasts.value.push({
    id,
    text,
    type,
  });

  setTimeout(() => {
    rewardToasts.value = rewardToasts.value.filter((t) => t.id !== id);
  }, 2200);
}

function handleProfileSaved() {
  pushToast(t("profile.updated"), "success");
  showEditProfile.value = false;
  load();
}

function handleEditProfile() {
  showEditProfile.value = true;
}

function syncSettingsHash() {
  if (route.hash === "#settings") {
    showEditProfile.value = true;
  }
}

async function load() {
  loading.value = true;
  error.value = "";

  try {
    const data = await loadPrivateProfileData(api);

    profile.value = data.profile;
    consistency.value = data.consistency;
    achievements.value = data.achievements;
    activityEvents.value = data.activityEvents;
  } catch (e) {
    error.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

watch(
  () => route.hash,
  () => syncSettingsHash(),
);

onMounted(() => {
  syncSettingsHash();
  load();
});
</script>

<style scoped>
.profileShell {
  display: grid;
  gap: var(--s-16);
}

.settingsPanel {
  scroll-margin-top: 110px;
}

.profileHead {
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

.profileHead::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.profileHead > * {
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

.headActions {
  display: flex;
  gap: var(--s-12);
  flex-wrap: wrap;
  justify-content: flex-end;
}

.profileAction {
  min-height: 40px;
  padding: 10px 15px;
  border-radius: 15px;
  color: rgba(255, 255, 255, 0.94);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.17), rgba(195, 90, 214, 0.12)),
    rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(110, 229, 255, 0.22);
  text-decoration: none;
  cursor: pointer;
  font-weight: 850;
}

.profileAction.ghost {
  background: rgba(255, 255, 255, 0.035);
  border-color: rgba(255, 255, 255, 0.10);
}

.identitySummary {
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
  font-size: 1.35rem;
}

.summaryCard small {
  display: block;
  margin-top: 5px;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.45;
}

.settingsPanel {
  border-color: rgba(110, 229, 255, 0.18);
}

.profileGrid {
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

.identityCard,
.nextCard {
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

.identitySignals {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.identitySignals span {
  padding: 7px 10px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.76);
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.78rem;
  font-weight: 750;
}

@media (max-width: 900px) {
  .profileHead,
  .profileGrid {
    grid-template-columns: 1fr;
  }

  .headActions {
    justify-content: flex-start;
  }

  .identitySummary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .profileHead {
    padding: 18px;
    border-radius: 23px;
  }

  .headActions {
    flex-direction: column;
    align-items: stretch;
  }

  .profileAction {
    width: 100%;
    text-align: center;
  }
}
</style>
