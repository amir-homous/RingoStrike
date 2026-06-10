<template>
  <BaseCard class="pathSelection">
    <div class="pathHead">
      <div>
        <p class="eyebrow compact">{{ t("paths.eyebrow") }}</p>
        <h2>{{ t("paths.title") }}</h2>
        <p>{{ t("paths.subtitle") }}</p>
      </div>

      <BaseButton variant="secondary" :loading="loading" @click="loadPaths">
        {{ t("common.retry") }}
      </BaseButton>
    </div>

    <UiState
      :loading="loading"
      :error="!!error"
      :empty="!loading && !error && localizedPaths.length === 0"
      :loading-title="t('paths.loadingTitle')"
      :loading-text="t('paths.loadingText')"
      :error-title="t('paths.errorTitle')"
      :error-text="error || t('common.pleaseTryAgain')"
      :empty-title="t('paths.emptyTitle')"
      :empty-text="t('paths.emptyText')"
      @retry="loadPaths"
    />

    <div v-if="!loading && !error && localizedPaths.length" class="pathGrid">
      <button
        v-for="path in localizedPaths"
        :key="path.path_id"
        type="button"
        class="pathCard"
        :class="{
          active: path.user_status === 'Active',
          selected: selectedPath?.path_id === path.path_id,
        }"
        @click="selectPathById(path.path_id)"
      >
        <span class="pathIcon" :style="{ '--path-color': path.color || '#6ee5ff' }">
          {{ path.icon?.slice(0, 1)?.toUpperCase() || "P" }}
        </span>

        <span class="pathCopy">
          <strong>{{ path.title }}</strong>
          <small>{{ path.description }}</small>
        </span>

        <span class="pathCta">
          {{ path.user_status === "Active" ? t("paths.active") : selectedPath?.path_id === path.path_id ? t("paths.selected") : t("paths.select") }}
        </span>
      </button>
    </div>

    <div v-if="selectedPathDisplay" class="pathChallenges">
      <div class="challengeHead">
        <div>
          <p class="eyebrow compact">{{ t("paths.relatedEyebrow") }}</p>
          <h3>{{ t("paths.relatedTitle", { path: selectedPathDisplay.title }) }}</h3>
        </div>

        <div class="challengeActions">
          <BaseButton
            v-if="selectedPath.user_status !== 'Active' || allowActiveStart"
            variant="primary"
            :loading="startingId === selectedPath.path_id"
            @click="startPath(selectedPath)"
          >
            {{ t("paths.startFirstMission", { path: selectedPathDisplay.title }) }}
          </BaseButton>

          <RouterLink class="challengeRoute" to="/challenges">
            {{ t("paths.browseChallenges") }}
          </RouterLink>
        </div>
      </div>

      <UiState
        :loading="challengesLoading"
        :error="!!challengesError"
        :empty="!challengesLoading && !challengesError && localizedPathChallenges.length === 0"
        :loading-title="t('paths.challengesLoadingTitle')"
        :loading-text="t('paths.challengesLoadingText')"
        :error-title="t('paths.challengesErrorTitle')"
        :error-text="challengesError || t('common.pleaseTryAgain')"
        :empty-title="t('paths.challengesEmptyTitle')"
        :empty-text="t('paths.challengesEmptyText')"
        @retry="loadPathChallenges(selectedPath)"
      />

      <div v-if="!challengesLoading && !challengesError && localizedPathChallenges.length" class="challengePreviewGrid">
        <article
          v-for="challenge in localizedPathChallenges.slice(0, 3)"
          :key="challenge.challenge_id"
          class="challengePreview"
        >
          <span>{{ t("paths.stage", { stage: challenge.stage || 1 }) }}</span>
          <h4>{{ challenge.name }}</h4>
          <p>{{ challenge.ringo_intro || challenge.description }}</p>
          <small>{{ t("paths.estimatedDays", { count: challenge.estimated_days || challenge.duration_days || 0 }) }}</small>
        </article>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";
import {
  localizeChallenge,
  localizePath,
} from "@/lib/ringoContentLocalization";

defineProps({
  allowActiveStart: { type: Boolean, default: false },
});

const emit = defineEmits(["started"]);
const { locale, t } = useI18n();

const paths = ref([]);
const loading = ref(true);
const error = ref("");
const startingId = ref(null);
const selectedPath = ref(null);
const pathChallenges = ref([]);
const challengesLoading = ref(false);
const challengesError = ref("");

const localizedPaths = computed(() => {
  return paths.value.map((path) => localizePath(path, locale.value));
});

const selectedPathDisplay = computed(() => {
  return localizePath(selectedPath.value, locale.value);
});

const localizedPathChallenges = computed(() => {
  return pathChallenges.value.map((challenge) => localizeChallenge(challenge, locale.value));
});

async function loadPaths() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await api.get("/paths");
    paths.value = data?.items || [];
    selectedPath.value = paths.value.find((path) => path.user_status === "Active") || paths.value[0] || null;

    if (selectedPath.value) {
      await loadPathChallenges(selectedPath.value);
    }
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function selectPath(path) {
  selectedPath.value = path;
  await loadPathChallenges(path);
}

async function selectPathById(pathId) {
  const path = paths.value.find((item) => item.path_id === pathId);
  if (path) await selectPath(path);
}

async function loadPathChallenges(path) {
  if (!path?.path_id) return;

  selectedPath.value = path;
  challengesLoading.value = true;
  challengesError.value = "";

  try {
    const { data } = await api.get(`/paths/${path.path_id}/challenges`);
    pathChallenges.value = data?.items || [];
  } catch (e) {
    challengesError.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    challengesLoading.value = false;
  }
}

async function startPath(path) {
  startingId.value = path.path_id;
  error.value = "";

  try {
    const { data } = await api.post(`/paths/${path.path_id}/start`, {});
    selectedPath.value = {
      ...path,
      user_status: "Active",
    };
    await loadPathChallenges(selectedPath.value);

    const firstChallenge = pathChallenges.value[0];
    let joinResult = null;

    if (firstChallenge?.challenge_id) {
      const joinResponse = await api.post(`/challenges/${firstChallenge.challenge_id}/join`, {});
      joinResult = {
        ...joinResponse.data,
        challenge_name: firstChallenge.name,
      };
    }

    emit("started", {
      ...data,
      joined_challenge: joinResult,
    });
    await loadPaths();
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    startingId.value = null;
  }
}

onMounted(loadPaths);
</script>

<style scoped>
.pathSelection {
  display: grid;
  gap: var(--s-16);
}

.pathHead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--s-16);
}

.pathHead h2,
.pathHead p {
  margin: 0;
}

.pathHead p:last-child {
  margin-top: 6px;
  color: var(--muted);
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.pathGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--s-12);
}

.pathChallenges {
  display: grid;
  gap: var(--s-12);
  padding-top: var(--s-4);
}

.challengeHead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--s-16);
}

.challengeHead h3,
.challengeHead p {
  margin: 0;
}

.challengeRoute {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 8px 12px;
  border: 1px solid rgba(110, 229, 255, 0.22);
  border-radius: 14px;
  color: rgba(255, 255, 255, 0.92);
  background: rgba(255, 255, 255, 0.055);
  font-weight: 850;
  text-decoration: none;
}

.challengeActions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--s-8);
}

.challengeRoute:hover {
  text-decoration: none;
  background: rgba(255, 255, 255, 0.085);
}

.challengePreviewGrid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
}

.challengePreview {
  min-width: 0;
  padding: 13px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.035);
}

.challengePreview span,
.challengePreview small {
  color: rgba(110, 229, 255, 0.76);
  font-size: var(--cap);
  font-weight: 850;
}

.challengePreview h4 {
  margin: 6px 0 0;
}

.challengePreview p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

.pathCard {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: var(--s-12);
  align-items: start;
  min-height: 146px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.90);
  text-align: start;
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
}

.pathCard.active {
  border-color: rgba(110, 229, 255, 0.28);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.10), rgba(195, 90, 214, 0.08)),
    rgba(255, 255, 255, 0.05);
}

.pathCard.selected {
  border-color: rgba(247, 215, 116, 0.30);
}

.pathCard:disabled {
  opacity: 0.7;
  cursor: wait;
}

.pathIcon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 15px;
  color: rgba(255, 255, 255, 0.95);
  background: color-mix(in srgb, var(--path-color) 34%, transparent);
  border: 1px solid color-mix(in srgb, var(--path-color) 44%, rgba(255, 255, 255, 0.10));
  font-weight: 950;
}

.pathCopy {
  display: grid;
  gap: 5px;
  min-width: 0;
}

.pathCopy small {
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.5;
}

.pathCta {
  grid-column: 1 / -1;
  align-self: end;
  color: rgba(247, 215, 116, 0.92);
  font-weight: 850;
}

@media (max-width: 620px) {
  .pathHead {
    display: grid;
  }

  .challengeHead {
    display: grid;
  }

  .challengeActions {
    justify-content: stretch;
  }

  .challengeActions :deep(.btn),
  .challengeRoute {
    width: 100%;
  }

  .challengePreviewGrid {
    grid-template-columns: 1fr;
  }
}
</style>
