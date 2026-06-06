<template>
  <AppContainer>
    <AppHeader />

    <div class="challengesPage">
      <RingoCoach
        v-if="challengeCoach"
        class="challengeCoach"
        :message="challengeCoach.message"
        :sprite="challengeCoach.sprite_key"
        :primary-action="challengeCoach.primary_action"
        :secondary-action="challengeCoach.secondary_action"
        @action="handleCoachAction"
      />

      <section class="heroCard">
        <div class="heroGlow"></div>

        <div class="heroContent">
          <div class="heroMain">
            <div class="eyebrow">
              <span class="pulseDot"></span>
              {{ t("challenges.eyebrow") }}
            </div>

            <h1 class="heroTitle">
              {{ t("challenges.title") }}
            </h1>

            <p class="heroText">
              {{ t("challenges.subtitle") }}
            </p>

            <div class="heroPills">
              <span class="heroPill">{{ t("challenges.pills.consistency") }}</span>
              <span class="heroPill">{{ t("challenges.pills.momentum") }}</span>
              <span class="heroPill">{{ t("challenges.pills.xp") }}</span>
              <span class="heroPill">{{ t("challenges.pills.social") }}</span>
            </div>

            <div class="journeySteps" :aria-label="t('challenges.journeyLabel')">
              <span>{{ t("challenges.journey.choose") }}</span>
              <span aria-hidden="true">→</span>
              <span>{{ t("challenges.journey.mission") }}</span>
              <span aria-hidden="true">→</span>
              <span>{{ t("challenges.journey.reward") }}</span>
            </div>
          </div>

          <div class="heroStats">
            <div class="heroStat">
              <span class="statValue">{{ items.length }}</span>
              <span class="statLabel">{{ t("challenges.availableStat") }}</span>
            </div>

            <div class="heroStat joined">
              <span class="statValue">{{ joinedCount }}</span>
              <span class="statLabel">{{ t("challenges.joinedStat") }}</span>
            </div>

            <div class="heroStat invite">
              <span class="statValue">{{ inviteOnlyCount }}</span>
              <span class="statLabel">{{ t("challenges.inviteStat") }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="pathGuide" aria-labelledby="path-guide-title">
        <div>
          <p class="eyebrow compact">{{ t("challenges.pathGuide.eyebrow") }}</p>
          <h2 id="path-guide-title" class="sectionTitle">{{ t("challenges.pathGuide.title") }}</h2>
          <p class="sectionText">{{ t("challenges.pathGuide.text") }}</p>
        </div>

        <div class="pathGrid">
          <button
            v-for="path in pathOptions"
            :key="path.key"
            type="button"
            class="pathOption"
            :class="{ active: selectedPath === path.key }"
            @click="selectPath(path)"
          >
            <span
              class="pathDot"
              :style="{ '--path-color': path.color || '#fde68a' }"
              aria-hidden="true"
            ></span>
            <span>{{ path.title }}</span>
            <small>{{ path.description }}</small>
          </button>
        </div>
      </section>

      <section
        v-if="selectedPath"
        class="selectedPathPanel"
        :class="{ missing: !selectedPathChallenge }"
      >
        <div class="selectedPathCopy">
          <p class="selectedLabel">{{ selectedPathTitle }}</p>
          <h2>{{ selectedPathHeading }}</h2>
          <p class="selectedText">{{ selectedPathDescription }}</p>

          <div class="missionPreview">
            <span>{{ t("challenges.selectedPath.missionLabel") }}</span>
            <strong>{{ selectedMissionTitle }}</strong>
          </div>
        </div>

        <div class="selectedPathAction">
          <span class="recommendedLabel">
            {{ t("challenges.selectedPath.recommended", { challenge: selectedChallengeName }) }}
          </span>

          <BaseButton
            class="pathStartButton"
            variant="primary"
            :loading="selectedPathChallenge && joiningId === selectedPathChallenge.challenge_id"
            :disabled="!selectedPathChallenge"
            @click="startSelectedPath"
          >
            {{ selectedPathCta }}
          </BaseButton>

          <p class="selectedHint">
            {{ selectedPathChallenge ? t("challenges.selectedPath.helper") : t("challenges.selectedPath.missing") }}
          </p>
        </div>
      </section>

      <section class="discoveryPanel">
        <ChallengeDiscoveryInvite
          :title="t('challengeInvite.title')"
          :show-action="false"
        />

        <div class="toolbar">
          <div>
            <div class="eyebrow compact">{{ t("challenges.launchDefaults") }}</div>
            <h2 class="sectionTitle">{{ t("challenges.availableTitle") }}</h2>
            <p class="sectionText">
              {{ t("challenges.helper") }}
            </p>
          </div>

          <div class="actions">
            <BaseButton variant="secondary" :loading="loading" @click="load">
              {{ t("challenges.refresh") }}
            </BaseButton>
          </div>
        </div>

        <div class="controls">
          <div class="searchBox">
            <span aria-hidden="true">⌕</span>
            <input v-model="search" type="search" :placeholder="t('challenges.search')" />
          </div>

          <div class="segmentedControl" :aria-label="t('challenges.filterLabel')">
            <button type="button" :class="{ active: filter === 'all' }" @click="setFilter('all')">
              {{ t("challenges.filters.all") }}
            </button>

            <button type="button" :class="{ active: filter === 'available' }" @click="setFilter('available')">
              {{ t("challenges.filters.available") }}
            </button>

            <button type="button" :class="{ active: filter === 'joined' }" @click="setFilter('joined')">
              {{ t("challenges.filters.joined") }}
            </button>

            <button type="button" :class="{ active: filter === 'invite' }" @click="setFilter('invite')">
              {{ t("challenges.filters.invite") }}
            </button>
          </div>
        </div>

        <BaseCard class="listCard">
          <UiState :loading="loading" :error="!!loadError" :empty="!loading && !loadError && filteredItems.length === 0"
            :loading-title="t('challenges.loadingTitle')" :loading-text="t('challenges.loadingText')"
            :empty-title="t('challenges.emptyTitle')" :empty-text="t('challenges.emptyText')"
            :error-title="t('challenges.errorTitle')" :error-text="loadError || t('common.pleaseTryAgain')"
            @retry="load" />

          <div v-if="!loading && !loadError && filteredItems.length" class="list">
            <div v-for="ch in visibleItems" :key="ch.challenge_id" class="challengeShell">
              <ChallengeCard :challenge="ch" :loading="joiningId === ch.challenge_id" :show-join="!ch.is_joined"
                :show-checkin="false" @join="join(ch)" />

              <div v-if="(isInviteOnly(ch) || ch.needs_code) && !ch.is_joined" class="inviteBox">
                <div class="inviteCopy">
                  <label class="capLabel" :for="`code-${ch.challenge_id}`">
                    {{ t("challenges.inviteRequired") }}
                  </label>

                  <div class="caption">
                    {{ t("challenges.inviteHelp") }}
                  </div>
                </div>

                <div class="inviteControls">
                  <input :id="`code-${ch.challenge_id}`" v-model="codes[ch.challenge_id]" class="input"
                    :placeholder="t('challenges.enterCode')" @keyup.enter="join(ch)" />

                  <BaseButton variant="secondary" :loading="joiningId === ch.challenge_id" @click="join(ch)">
                    {{ t("challenges.unlock") }}
                  </BaseButton>
                </div>
              </div>

              <div v-if="errors[ch.challenge_id]" class="err">
                {{ humanizeError(errors[ch.challenge_id]) }}
              </div>
            </div>

            <button v-if="hasHiddenItems" type="button" class="showMoreButton" @click="showAll = !showAll">
              <span>
                {{ showAll ? t("common.showFewer") : t("common.showMore", { count: filteredItems.length - itemLimit })
                }}
              </span>

              <span aria-hidden="true">
                {{ showAll ? "↑" : "↓" }}
              </span>
            </button>
          </div>
        </BaseCard>
      </section>
    </div>

    <JoinSuccessMoment
      :open="!!joinSuccess"
      :join="joinSuccess"
      @close="joinSuccess = null"
    />
  </AppContainer>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "@/lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";
import ChallengeCard from "@/components/challenges/ChallengeCard.vue";
import JoinSuccessMoment from "@/components/feedback/JoinSuccessMoment.vue";
import ChallengeDiscoveryInvite from "@/components/guided/ChallengeDiscoveryInvite.vue";
import RingoCoach from "@/components/ringo/RingoCoach.vue";
import { getSuggestedChallengeName } from "@/lib/guidedExperience";
import {
  humanizeJoinError,
  isInviteOnlyChallenge,
  submitJoinFlow,
} from "./challengeFlow";

const router = useRouter();
const { t } = useI18n();

const loading = ref(true);
const loadError = ref("");

const items = ref([]);
const joiningId = ref(null);
const joinSuccess = ref(null);

const codes = ref({});
const errors = ref({});

const search = ref("");
const filter = ref("available");
const showAll = ref(false);
const selectedPath = ref("");
const pathItems = ref([]);
const pathChallenges = ref([]);
const pathLoadError = ref("");

const itemLimit = 6;
const fallbackPathOptions = ["focus", "body", "learning", "mind", "consistency"];

const pathOptions = computed(() => {
  if (pathItems.value.length) {
    return pathItems.value.map((path) => ({
      key: path.key || String(path.path_id),
      path_id: path.path_id,
      title: path.title,
      description: path.description,
      color: path.color,
      user_status: path.user_status,
    }));
  }

  return fallbackPathOptions.map((key) => ({
    key,
    title: t(`challengeCard.paths.${key}`),
    description: t(`challenges.selectedPath.${key}.description`),
    color: "",
    user_status: null,
  }));
});

const joinedCount = computed(() => {
  return items.value.filter((item) => item.is_joined).length;
});

const inviteOnlyCount = computed(() => {
  return items.value.filter((item) => isInviteOnly(item) || item.needs_code).length;
});

const selectedPathChallenge = computed(() => {
  if (!selectedPath.value) return null;

  const pathChallenge = pathChallenges.value.find((item) => !item.is_joined)
    || pathChallenges.value.find((item) => item.is_joined && !item.today_checked)
    || pathChallenges.value[0]
    || null;

  if (pathChallenge) return pathChallenge;

  const suggestedName = getSuggestedChallengeName(selectedPath.value).toLowerCase();
  return items.value.find((item) => {
    const name = String(item.name || item.challenge_name || item.enrollment_name || "").trim().toLowerCase();
    return name === suggestedName;
  }) || null;
});

const selectedPathItem = computed(() => {
  return pathOptions.value.find((path) => path.key === selectedPath.value) || null;
});

const selectedPathTitle = computed(() => {
  return selectedPathItem.value?.title || t(`challengeCard.paths.${selectedPath.value}`);
});

const selectedPathHeading = computed(() => {
  if (selectedPathItem.value?.path_id) {
    return t("challenges.selectedPath.backendTitle", { path: selectedPathTitle.value });
  }

  return selectedPath.value ? t(`challenges.selectedPath.${selectedPath.value}.title`) : "";
});

const selectedPathDescription = computed(() => {
  return selectedPathItem.value?.description ||
    (selectedPath.value ? t(`challenges.selectedPath.${selectedPath.value}.description`) : "");
});

const selectedMissionTitle = computed(() => {
  const mission = selectedPathChallenge.value?.missions?.find((item) => item.available_today)
    || selectedPathChallenge.value?.missions?.[0]
    || null;

  if (mission?.title) return mission.title;
  if (selectedPath.value && !selectedPathItem.value?.path_id) {
    return t(`challenges.selectedPath.${selectedPath.value}.mission`);
  }
  return t("challenges.selectedPath.backendMissionFallback");
});

const selectedChallengeName = computed(() => {
  return selectedPathChallenge.value?.name ||
    selectedPathChallenge.value?.challenge_name ||
    getSuggestedChallengeName(selectedPath.value);
});

const challengeCoach = computed(() => {
  if (selectedPath.value && selectedPathChallenge.value) {
    const joined = selectedPathChallenge.value.is_joined;
    const checkedToday = Boolean(selectedPathChallenge.value.today_checked);

    return {
      sprite_key: joined ? checkedToday ? "proud" : "thinking" : "focus",
      message: joined
        ? checkedToday
          ? t("challenges.coach.pathDone", { challenge: selectedChallengeName.value })
          : t("challenges.coach.pathJoined", { challenge: selectedChallengeName.value })
        : t("challenges.coach.pathReady", {
          path: selectedPathTitle.value,
          challenge: selectedChallengeName.value,
        }),
      primary_action: {
        label: selectedPathCta.value,
        type: "start_selected_path",
      },
      secondary_action: {
        label: t("challenges.coach.clearPath"),
        type: "clear_path",
      },
    };
  }

  if (selectedPath.value && !selectedPathChallenge.value) {
    return {
      sprite_key: "explaining",
      message: t("challenges.coach.pathMissing", { path: selectedPathTitle.value }),
      primary_action: {
        label: t("challenges.filters.available"),
        type: "clear_path",
      },
      secondary_action: {
        label: t("challenges.refresh"),
        type: "refresh",
      },
    };
  }

  if (joinedCount.value > 0) {
    return {
      sprite_key: "encouraging",
      message: t("challenges.coach.hasJoined", { count: joinedCount.value }),
      primary_action: {
        label: t("challenges.coach.pickPath"),
        type: "focus_paths",
      },
      secondary_action: {
        label: t("paths.openTodayMission"),
        type: "route",
        to: "/dashboard",
      },
    };
  }

  return {
    sprite_key: "welcome",
    message: t("challenges.coach.firstPath"),
    primary_action: {
      label: t("challenges.coach.pickPath"),
      type: "focus_paths",
    },
    secondary_action: {
      label: t("challenges.filters.available"),
      type: "clear_path",
    },
  };
});

const selectedPathCta = computed(() => {
  if (!selectedPathChallenge.value) return t("challenges.selectedPath.unavailableCta");
  if (selectedPathChallenge.value.is_joined && selectedPathChallenge.value.enrollment_id) {
    if (selectedPathChallenge.value.today_checked) {
      return t("challenges.selectedPath.doneCta");
    }
    return t("challenges.selectedPath.continueCta");
  }
  if (isInviteOnly(selectedPathChallenge.value) || selectedPathChallenge.value.needs_code) {
    return t("challenges.selectedPath.unlockCta");
  }
  if (selectedPathItem.value?.path_id) {
    return t("challenges.selectedPath.backendCta", { path: selectedPathTitle.value });
  }
  return t(`challenges.selectedPath.${selectedPath.value}.cta`);
});

function isInviteOnly(challenge) {
  return isInviteOnlyChallenge(challenge);
}

const filteredItems = computed(() => {
  const query = search.value.trim().toLowerCase();
  const selectedPathChallengeIds = new Set(pathChallenges.value.map((item) => item.challenge_id));
  const sourceItems = selectedPath.value && selectedPathChallengeIds.size
    ? items.value.filter((item) => selectedPathChallengeIds.has(item.challenge_id))
    : items.value;

  return sourceItems.filter((item) => {
    const title = String(item.name || item.enrollment_name || item.challenge_name || "").toLowerCase();
    const description = String(item.description || "").toLowerCase();
    const visibility = String(item.visibility || "").toLowerCase();

    const matchesSearch =
      !query ||
      title.includes(query) ||
      description.includes(query) ||
      visibility.includes(query);

    if (!matchesSearch) return false;

    if (filter.value === "available") return !item.is_joined;
    if (filter.value === "joined") return Boolean(item.is_joined);
    if (filter.value === "invite") return isInviteOnly(item) || item.needs_code;

    return true;
  });
});

const visibleItems = computed(() => {
  if (showAll.value) return filteredItems.value;
  return filteredItems.value.slice(0, itemLimit);
});

const hasHiddenItems = computed(() => {
  return filteredItems.value.length > itemLimit;
});

function setFilter(value) {
  filter.value = value;
  selectedPath.value = "";
  pathChallenges.value = [];
  search.value = "";
  showAll.value = false;
}

async function selectPath(path) {
  selectedPath.value = path.key || path;
  filter.value = "available";
  search.value = "";
  showAll.value = true;

  if (path.path_id) {
    await loadPathChallenges(path.path_id);
    return;
  }

  pathChallenges.value = [];
  search.value = getSuggestedChallengeName(selectedPath.value);
}

function startSelectedPath() {
  if (!selectedPathChallenge.value) return;

  if (selectedPathChallenge.value.is_joined && selectedPathChallenge.value.enrollment_id) {
    router.push("/dashboard");
    return;
  }

  join(selectedPathChallenge.value);
}

function humanizeError(msg) {
  return humanizeJoinError(msg);
}

async function load() {
  loading.value = true;
  loadError.value = "";
  errors.value = {};

  try {
    const { data } = await api.get("/challenges");
    items.value = data.items || [];
    await loadPaths();
  } catch (e) {
    loadError.value = e?.response?.data?.error || e?.message || String(e);
    items.value = [];
  } finally {
    loading.value = false;
  }
}

async function loadPaths() {
  pathLoadError.value = "";

  try {
    const { data } = await api.get("/paths");
    pathItems.value = data?.items || [];
  } catch (e) {
    pathLoadError.value = e?.response?.data?.error || e?.message || String(e);
    pathItems.value = [];
  }
}

async function loadPathChallenges(pathId) {
  pathLoadError.value = "";

  try {
    const { data } = await api.get(`/paths/${pathId}/challenges`);
    pathChallenges.value = data?.items || [];
  } catch (e) {
    pathLoadError.value = e?.response?.data?.error || e?.message || String(e);
    pathChallenges.value = [];
  }
}

async function handleCoachAction(action) {
  if (!action) return;

  if (action.type === "start_selected_path") {
    startSelectedPath();
    return;
  }

  if (action.type === "clear_path") {
    setFilter("available");
    return;
  }

  if (action.type === "refresh") {
    await load();
    return;
  }

  if (action.type === "focus_paths") {
    document
      .getElementById("path-guide-title")
      ?.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

async function join(challenge) {
  errors.value[challenge.challenge_id] = "";
  joiningId.value = challenge.challenge_id;

  try {
    const result = await submitJoinFlow({
      apiClient: api,
      router,
      challenge,
      codes: codes.value,
    });
    await load();
    joinSuccess.value = {
      ...result,
      source: "challenges",
    };
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    errors.value[challenge.challenge_id] = msg;
  } finally {
    joiningId.value = null;
  }
}

onMounted(load);
</script>

<style scoped>
.challengesPage {
  display: grid;
  gap: var(--s-16);
}

.challengeCoach {
  border: 1px solid rgba(110, 229, 255, 0.14);
}

.heroCard {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background:
    radial-gradient(circle at 12% 18%, rgba(110, 229, 255, 0.18), transparent 34%),
    radial-gradient(circle at 88% 8%, rgba(195, 90, 214, 0.16), transparent 32%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.085), rgba(255, 255, 255, 0.025));
  box-shadow: 0 28px 90px rgba(0, 0, 0, 0.32);
}

.heroGlow {
  position: absolute;
  inset: -90px;
  background:
    linear-gradient(90deg, transparent, rgba(110, 229, 255, 0.07), transparent),
    radial-gradient(circle, rgba(255, 255, 255, 0.07), transparent 58%);
  pointer-events: none;
}

.heroContent {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: var(--s-24);
  align-items: center;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 7px;
  color: rgba(110, 229, 255, 0.9);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.14em;
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

.heroTitle {
  margin: 0;
  max-width: 820px;
  color: white;
  font-size: clamp(2rem, 4.4vw, 4.2rem);
  line-height: 0.96;
  letter-spacing: -0.06em;
}

.heroText {
  max-width: 720px;
  margin: var(--s-16) 0 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.7;
}

.heroPills {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  margin-top: var(--s-20);
}

.heroPill {
  padding: 7px 11px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.10);
  font-size: 0.78rem;
  font-weight: 750;
}

.journeySteps {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 9px;
  margin-top: var(--s-16);
  padding: 10px 12px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(253, 230, 138, 0.16);
  font-size: 0.82rem;
  font-weight: 850;
}

.heroStats {
  display: grid;
  gap: var(--s-12);
}

.heroStat {
  padding: 16px;
  border-radius: 22px;
  text-align: right;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.10), transparent 38%),
    rgba(0, 0, 0, 0.20);
  border: 1px solid rgba(255, 255, 255, 0.10);
  margin-top: 10px;
}

.heroStat.joined {
  border-color: rgba(74, 222, 128, 0.18);
}

.heroStat.invite {
  border-color: rgba(255, 228, 168, 0.18);
}

.statValue {
  display: block;
  color: white;
  font-size: 2rem;
  line-height: 1;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
}

.statLabel {
  display: block;
  margin-top: 5px;
  color: var(--muted2);
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.discoveryPanel {
  display: grid;
  gap: var(--s-12);
}

.pathGuide {
  display: grid;
  grid-template-columns: minmax(0, 0.82fr) minmax(0, 1.18fr);
  gap: var(--s-16);
  align-items: center;
  padding: 20px;
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background:
    radial-gradient(circle at 0% 0%, rgba(253, 230, 138, 0.09), transparent 35%),
    radial-gradient(circle at 100% 0%, rgba(110, 229, 255, 0.07), transparent 35%),
    rgba(255, 255, 255, 0.026);
}

.pathGrid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--s-12);
}

.pathOption {
  display: grid;
  gap: 8px;
  min-height: 112px;
  align-content: center;
  padding: 12px;
  border-radius: 18px;
  text-align: start;
  color: rgba(255, 255, 255, 0.84);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.085);
  font-size: 0.84rem;
  font-weight: 850;
  cursor: pointer;
  transition:
    transform 150ms ease,
    border-color 150ms ease,
    background 150ms ease;
}

.pathOption small {
  display: -webkit-box;
  overflow: hidden;
  color: rgba(255, 255, 255, 0.52);
  font-size: 0.74rem;
  font-weight: 650;
  line-height: 1.35;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.pathOption:hover,
.pathOption.active {
  transform: translateY(-1px);
  border-color: rgba(253, 230, 138, 0.24);
  background:
    radial-gradient(circle at 0% 0%, rgba(253, 230, 138, 0.11), transparent 36%),
    rgba(255, 255, 255, 0.055);
}

.pathOption:focus-visible {
  outline: none;
  box-shadow: var(--focus);
}

.pathDot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: var(--path-color);
  box-shadow: 0 0 18px color-mix(in srgb, var(--path-color) 42%, transparent);
}

.selectedPathPanel {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 0.42fr);
  gap: var(--s-20);
  align-items: center;
  padding: 24px;
  border-radius: 28px;
  border: 1px solid rgba(253, 230, 138, 0.18);
  background:
    radial-gradient(circle at 0% 0%, rgba(253, 230, 138, 0.13), transparent 35%),
    radial-gradient(circle at 100% 8%, rgba(110, 229, 255, 0.10), transparent 36%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.066), rgba(255, 255, 255, 0.024));
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.24);
}

.selectedPathPanel.missing {
  border-color: rgba(255, 255, 255, 0.11);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.08), transparent 35%),
    rgba(255, 255, 255, 0.025);
}

.selectedPathCopy,
.selectedPathAction {
  position: relative;
  z-index: 1;
}

.selectedLabel {
  margin: 0 0 9px;
  color: rgba(253, 230, 138, 0.92);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.selectedPathCopy h2 {
  max-width: 760px;
  margin: 0;
  color: rgba(255, 255, 255, 0.97);
  font-size: clamp(1.65rem, 4vw, 3rem);
  line-height: 1.05;
}

.selectedText {
  max-width: 760px;
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.70);
  line-height: 1.7;
}

.missionPreview {
  display: grid;
  gap: 6px;
  max-width: 720px;
  margin-top: var(--s-16);
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.04);
}

.missionPreview span,
.recommendedLabel {
  color: rgba(255, 255, 255, 0.54);
  font-size: 0.75rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.missionPreview strong {
  color: rgba(255, 255, 255, 0.92);
  line-height: 1.55;
}

.selectedPathAction {
  display: grid;
  gap: var(--s-12);
  padding: 16px;
  border-radius: 22px;
  background: rgba(0, 0, 0, 0.20);
  border: 1px solid rgba(255, 255, 255, 0.09);
}

:deep(.pathStartButton) {
  min-height: 58px;
  border-color: rgba(253, 230, 138, 0.44);
  background:
    linear-gradient(135deg, rgba(253, 230, 138, 0.25), rgba(99, 102, 241, 0.24)),
    rgba(99, 102, 241, 0.22);
  box-shadow: 0 16px 46px rgba(99, 102, 241, 0.22);
  font-size: 1rem;
  font-weight: 900;
}

:deep(.pathStartButton:hover) {
  background:
    linear-gradient(135deg, rgba(253, 230, 138, 0.31), rgba(99, 102, 241, 0.30)),
    rgba(99, 102, 241, 0.28);
}

.selectedHint {
  margin: 0;
  color: rgba(255, 255, 255, 0.60);
  line-height: 1.55;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--s-16);
  flex-wrap: wrap;
}

.sectionTitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  letter-spacing: -0.04em;
}

.sectionText {
  margin: 8px 0 0;
  max-width: 720px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.65;
}

.actions {
  display: flex;
  gap: var(--s-12);
  align-items: center;
  flex-wrap: wrap;
}

.controls {
  display: grid;
  grid-template-columns: minmax(240px, 0.8fr) minmax(0, 1.2fr);
  gap: var(--s-12);
  align-items: center;
}

.searchBox {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 44px;
  padding: 0 13px;
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.54);
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.085);
}

.searchBox input {
  width: 100%;
  border: 0;
  outline: 0;
  color: rgba(255, 255, 255, 0.92);
  background: transparent;
}

.searchBox input::placeholder {
  color: rgba(255, 255, 255, 0.42);
}

.segmentedControl {
  justify-self: end;
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.085);
}

.segmentedControl button {
  min-height: 34px;
  padding: 7px 12px;
  border: 0;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.60);
  background: transparent;
  cursor: pointer;
  font-weight: 850;
}

.segmentedControl button.active {
  color: rgba(255, 255, 255, 0.94);
  background: rgba(110, 229, 255, 0.13);
}

.listCard {
  background:
    radial-gradient(circle at 100% 0%, rgba(110, 229, 255, 0.045), transparent 34%),
    rgba(255, 255, 255, 0.024);
}

.list {
  margin-top: var(--s-16);
  display: grid;
  gap: var(--s-14);
}

.challengeShell {
  display: grid;
  gap: var(--s-8);
}

.inviteBox {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--s-12);
  padding: 14px;
  margin: 0 4px;
  border-radius: 18px;
  border: 1px solid rgba(255, 228, 168, 0.14);
  background:
    radial-gradient(circle at 0% 0%, rgba(255, 228, 168, 0.08), transparent 36%),
    rgba(255, 255, 255, 0.025);
  flex-wrap: wrap;
}

.inviteCopy {
  min-width: 220px;
}

.capLabel {
  display: block;
  color: rgba(255, 228, 168, 0.95);
  font-size: 0.78rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.10em;
  margin-bottom: 3px;
}

.inviteControls {
  display: flex;
  gap: var(--s-8);
  align-items: center;
  flex-wrap: wrap;
}

.input {
  width: 260px;
  max-width: 100%;
  padding: 11px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(0, 0, 0, 0.25);
  color: rgba(255, 255, 255, 0.92);
  outline: none;
}

.input:focus {
  border-color: rgba(110, 229, 255, 0.45);
  box-shadow: 0 0 0 3px rgba(110, 229, 255, 0.14);
}

.err {
  margin: 0 8px;
  color: rgba(255, 100, 100, 0.95);
  font-size: var(--cap);
  font-weight: 700;
}

.caption {
  color: var(--muted2);
  font-size: 0.85rem;
  line-height: 1.45;
}

.showMoreButton {
  justify-self: center;
  display: inline-flex;
  align-items: center;
  gap: var(--s-8);
  min-height: 40px;
  padding: 10px 15px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-weight: 850;
  margin-top: 10px;
}

.showMoreButton:hover {
  background: rgba(255, 255, 255, 0.065);
  border-color: rgba(110, 229, 255, 0.25);
}

@media (max-width: 900px) {

  .heroContent,
  .controls,
  .pathGuide,
  .selectedPathPanel {
    grid-template-columns: 1fr;
  }

  .pathGrid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .heroStats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .heroStat {
    text-align: left;
  }

  .segmentedControl {
    justify-self: start;
  }
}

@media (max-width: 620px) {
  .heroCard {
    padding: 22px;
    border-radius: 22px;
  }

  .heroStats {
    grid-template-columns: 1fr;
  }

  .heroTitle {
    font-size: 2.2rem;
  }

  .journeySteps {
    width: 100%;
    border-radius: 18px;
  }

  .pathGrid {
    grid-template-columns: 1fr;
  }

  .selectedPathPanel {
    padding: 20px;
    border-radius: 24px;
  }

  :deep(.pathStartButton) {
    width: 100%;
  }

  .segmentedControl {
    width: 100%;
    border-radius: 18px;
    flex-wrap: wrap;
  }

  .segmentedControl button {
    flex: 1;
    min-width: calc(50% - 4px);
    padding-inline: 10px;
    white-space: normal;
  }

  .inviteBox {
    margin-inline: 0;
  }

  .inviteCopy {
    min-width: 0;
    width: 100%;
  }

  .inviteControls {
    width: 100%;
  }

  .input {
    width: 100%;
  }
}
</style>
