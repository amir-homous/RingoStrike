<template>
  <section class="remainingMissionExplorer">
    <div class="explorerHead">
      <div>
        <p class="eyebrow compact">{{ t("missions.optionalExplorerList.eyebrow") }}</p>
        <h3>{{ t("missions.optionalExplorerList.title") }}</h3>
        <p>{{ t("missions.optionalExplorerList.body") }}</p>
      </div>
      <!-- <BaseButton variant="secondary" @click="$emit('close')">
        {{ t("missions.optionalExplorerList.hide") }}
      </BaseButton> -->
    </div>

    <div class="pathGroups">
      <section v-for="path in visiblePathGroups" :key="path.key" class="pathGroup">
        <button type="button" class="groupToggle pathToggle" :class="{ selected: activePathKey === path.key }"
          @click="selectPath(path)">
          <span class="groupIcon pathIcon" aria-hidden="true">
            <img v-if="path.iconUrl" :src="path.iconUrl" :alt="path.title" />
            <span v-else>{{ initialsFor(path.title) }}</span>
          </span>
          <span>
            <small>{{ t("missions.optionalExplorerList.pathLabel") }}</small>
            <strong>{{ path.title }}</strong>
          </span>
          <i>{{ path.missions.length }}</i>
        </button>

        <div v-if="expandedPaths.has(path.key)" class="challengeGroups">
          <section v-for="challenge in path.challenges" :key="challenge.key" class="challengeGroup">
            <button type="button" class="groupToggle challengeToggle"
              :class="{ selected: activeChallengeKey === challenge.key }" @click="selectChallenge(path, challenge)">
              <span class="groupIcon challengeIcon" aria-hidden="true">
                <img v-if="challenge.iconUrl" :src="challenge.iconUrl" :alt="challenge.title" />
                <span v-else>{{ initialsFor(challenge.title) }}</span>
              </span>
              <span>
                <small>{{ t("missions.optionalExplorerList.challengeLabel") }}</small>
                <strong>{{ challenge.title }}</strong>
              </span>
              <i>{{ challenge.missions.length }}</i>
            </button>

            <div v-if="expandedChallenges.has(challenge.key)" class="missionRows">
              <button v-for="mission in challenge.missions" :key="mission.mission_id" type="button"
                class="missionChoiceRow"
                :class="[normalizedIntensity(mission), normalizedStatus(mission), { selected: isSelected(mission) }]"
                @click="$emit('select', mission)">
                <span class="missionChoiceMarker" aria-hidden="true"></span>
                <span class="missionChoiceCopy">
                  <strong>{{ mission.title }}</strong>
                  <small>{{ mission.description }}</small>
                </span>
                <span class="missionChoiceChips">
                  <span class="choiceChip intensity">{{ intensityLabel(mission) }}</span>
                  <span class="choiceChip status">{{ statusLabel(mission) }}</span>
                  <span v-if="timeLabel(mission)" class="choiceChip time">{{ timeLabel(mission) }}</span>
                  <span v-if="reminderLabel(mission)" class="choiceChip reminder">{{ reminderLabel(mission) }}</span>
                </span>
              </button>
            </div>
          </section>
        </div>
      </section>
    </div>

    <div class="explorerActions">
      <BaseButton variant="primary" @click="$emit('finish')">
        {{ t("missions.finishForToday") }}
      </BaseButton>
      <BaseButton v-if="activePathKey || activeChallengeKey" variant="secondary" @click="resetSelection">
        {{ t("missions.backToOptionalChoices") }}
      </BaseButton>
      <BaseButton variant="secondary" @click="$emit('close')">
        {{ t("missions.optionalExplorerList.hide") }}
      </BaseButton>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import BaseButton from "@/components/ui/BaseButton.vue";

const props = defineProps({
  missions: { type: Array, default: () => [] },
  selectedMissionId: { type: [String, Number], default: null },
});

const emit = defineEmits(["select", "select-path", "select-challenge", "back", "close", "finish"]);

const { t } = useI18n();

const expandedPaths = ref(new Set());
const expandedChallenges = ref(new Set());
const activePathKey = ref("");
const activeChallengeKey = ref("");
const pathIconModules = import.meta.glob("../../assets/path-icons/*.png", { eager: true, import: "default" });
const challengeIconModules = import.meta.glob("../../assets/challenge-icons/*.png", { eager: true, import: "default" });

const pathGroups = computed(() => {
  const paths = new Map();

  props.missions.forEach((mission) => {
    const pathKey = stableGroupKey("path", mission.path_id || mission.path_title || "default");
    const pathTitle = mission.path_title || t("missions.fallbackPath");
    const pathIconName = pathIconNameFor(mission);
    const challengeKey = stableGroupKey(
      "challenge",
      mission.challenge_id || mission.challenge_name || mission.enrollment_id || "default",
    );
    const challengeTitle = mission.challenge_name || t("missions.fallbackChallenge");
    const challengeIconName = String(mission.challenge_id || "").trim();

    if (!paths.has(pathKey)) {
      paths.set(pathKey, {
        key: pathKey,
        title: pathTitle,
        iconUrl: resolvePathIcon(pathIconName),
        missions: [],
        challenges: new Map(),
      });
    }

    const path = paths.get(pathKey);
    if (!path.challenges.has(challengeKey)) {
      path.challenges.set(challengeKey, {
        key: challengeKey,
        title: challengeTitle,
        iconUrl: resolveChallengeIcon(challengeIconName),
        missions: [],
      });
    }

    path.missions.push(mission);
    path.challenges.get(challengeKey).missions.push(mission);
  });

  return Array.from(paths.values()).map((path) => ({
    ...path,
    challenges: Array.from(path.challenges.values()),
  }));
});

const visiblePathGroups = computed(() => {
  if (activeChallengeKey.value) {
    return pathGroups.value
      .map((path) => ({
        ...path,
        challenges: path.challenges.filter((challenge) => challenge.key === activeChallengeKey.value),
      }))
      .filter((path) => path.challenges.length);
  }

  if (activePathKey.value) {
    return pathGroups.value.filter((path) => path.key === activePathKey.value);
  }

  return pathGroups.value;
});

watch(pathGroups, (groups) => {
  if (groups.length === 1) {
    expandedPaths.value = new Set([groups[0].key]);
    expandedChallenges.value = new Set();
    return;
  }

  expandedPaths.value = new Set();
  expandedChallenges.value = new Set();
}, { immediate: true });

watch(() => props.selectedMissionId, (missionId) => {
  if (!missionId) return;

  const mission = props.missions.find((item) => {
    return String(item.mission_id) === String(missionId);
  });
  if (!mission) return;

  const pathKey = stableGroupKey("path", mission.path_id || mission.path_title || "default");
  const challengeKey = stableGroupKey(
    "challenge",
    mission.challenge_id || mission.challenge_name || mission.enrollment_id || "default",
  );

  expandedPaths.value = new Set([pathKey]);
  expandedChallenges.value = new Set([challengeKey]);
}, { immediate: true });

function stableGroupKey(prefix, value) {
  return `${prefix}-${String(value || "default").trim().toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
}

function togglePath(key) {
  if (expandedPaths.value.has(key)) {
    expandedPaths.value = new Set();
    expandedChallenges.value = new Set();
    return;
  }

  expandedPaths.value = new Set([key]);
  expandedChallenges.value = new Set();
}

function toggleChallenge(key) {
  expandedChallenges.value = expandedChallenges.value.has(key)
    ? new Set()
    : new Set([key]);
}

function selectPath(path) {
  activePathKey.value = path.key;
  activeChallengeKey.value = "";
  expandedPaths.value = new Set([path.key]);
  expandedChallenges.value = new Set();
  emit("select-path", {
    key: path.key,
    title: path.title,
    missions: path.missions,
  });
}

function selectChallenge(path, challenge) {
  activePathKey.value = path.key;
  activeChallengeKey.value = challenge.key;
  expandedPaths.value = new Set([path.key]);
  expandedChallenges.value = new Set([challenge.key]);
  emit("select-challenge", {
    key: challenge.key,
    title: challenge.title,
    pathTitle: path.title,
    missions: challenge.missions,
  });
}

function resetSelection() {
  activePathKey.value = "";
  activeChallengeKey.value = "";
  expandedChallenges.value = new Set();
  if (pathGroups.value.length === 1) {
    expandedPaths.value = new Set([pathGroups.value[0].key]);
  } else {
    expandedPaths.value = new Set();
  }
  emit("back");
}

function normalizedIntensity(mission) {
  const value = String(mission?.mission_intensity || "main").toLowerCase();
  return ["main", "tiny", "bonus"].includes(value) ? value : "main";
}

function normalizedStatus(mission) {
  const value = String(mission?.status || "pending").toLowerCase();
  return ["pending", "done", "remind_later", "skipped"].includes(value) ? value : "pending";
}

function intensityLabel(mission) {
  return t(`missions.typeChips.${normalizedIntensity(mission)}`);
}

function statusLabel(mission) {
  return t(`missions.status.${normalizedStatus(mission)}`);
}

function timeLabel(mission) {
  const minutes = Number(mission?.estimated_minutes || 0);
  if (!Number.isFinite(minutes) || minutes <= 0) return "";

  return t("missionContext.time.minutes", { count: minutes });
}

function reminderLabel(mission) {
  if (!mission?.reminder_at) return "";

  try {
    return new Intl.DateTimeFormat(undefined, {
      hour: "numeric",
      minute: "2-digit",
    }).format(new Date(mission.reminder_at));
  } catch {
    return "";
  }
}

function isSelected(mission) {
  return props.selectedMissionId && String(mission.mission_id) === String(props.selectedMissionId);
}

function iconFromModules(modules, name) {
  const normalizedName = String(name || "").trim().toLowerCase();
  if (!normalizedName) return "";

  const match = Object.entries(modules).find(([path]) => {
    return path.toLowerCase().endsWith(`/${normalizedName}.png`);
  });

  return match?.[1] || "";
}

function resolvePathIcon(name) {
  return iconFromModules(pathIconModules, name)
    || iconFromModules(pathIconModules, "default_path_icon");
}

function resolveChallengeIcon(challengeId) {
  return iconFromModules(challengeIconModules, challengeId)
    || iconFromModules(challengeIconModules, "default_challenge_icon");
}

function pathIconNameFor(mission) {
  const explicit = mission?.path_icon || mission?.pathIcon || mission?.icon;
  if (explicit) return explicit;

  const title = String(mission?.path_title || "").toLowerCase();
  if (title.includes("fitness") || title.includes("تناسب") || title.includes("حرکت")) return "activity";
  if (title.includes("learning") || title.includes("یادگیری")) return "book";
  if (title.includes("career") || title.includes("شغلی")) return "briefcase";
  if (title.includes("creative") || title.includes("خلاق")) return "sparkles";
  if (title.includes("sleep") || title.includes("آرامش") || title.includes("خواب")) return "moon";

  return "";
}

function initialsFor(value) {
  const words = String(value || "").trim().split(/\s+/).filter(Boolean);
  const initials = words.slice(0, 2).map((word) => word.slice(0, 1)).join("");
  return initials || "•";
}
</script>

<style scoped>
.remainingMissionExplorer {
  display: grid;
  gap: var(--s-16);
  padding: 20px;
  /* border-color: rgba(110, 229, 255, 0.14); */
  /* background: linear-gradient(145deg, rgba(15, 23, 42, 0.88), rgba(5, 10, 18, 0.72)); */
}

.explorerHead,
.groupToggle,
.missionChoiceRow {
  min-width: 0;
}

.explorerHead {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-12);
  align-items: flex-start;
  justify-content: space-between;
}

.explorerHead h3,
.explorerHead p {
  margin: 0;
}

.explorerHead h3 {
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.05rem;
}

.explorerHead p:not(.eyebrow) {
  margin-top: 5px;
  max-width: 58ch;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.55;
}

.pathGroups,
.challengeGroups,
.missionRows,
.explorerActions {
  display: grid;
  gap: var(--s-8);
}

.explorerActions {
  grid-template-columns: repeat(auto-fit, minmax(150px, max-content));
  align-items: center;
}

.pathGroup,
.challengeGroup {
  display: grid;
  gap: var(--s-8);
}

.challengeGroups {
  padding-inline-start: 10px;
}

.groupToggle,
.missionChoiceRow {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.09);
  color: inherit;
  background: rgba(255, 255, 255, 0.035);
  text-align: start;
  cursor: pointer;
}

.groupToggle {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: var(--s-8);
  align-items: center;
  padding: 10px 12px;
  border-radius: 14px;
}

.pathToggle {
  background: rgba(110, 229, 255, 0.055);
}

.challengeToggle {
  background: rgba(255, 255, 255, 0.028);
}

.groupToggle.selected {
  border-color: rgba(110, 229, 255, 0.25);
  background: rgba(110, 229, 255, 0.08);
}

.groupToggle>span:not(.groupIcon),
.missionChoiceCopy,
.missionChoiceChips {
  min-width: 0;
}

.groupToggle small,
.missionChoiceCopy small {
  display: block;
  color: rgba(255, 255, 255, 0.52);
  font-size: var(--cap);
  font-weight: 800;
}

.groupToggle strong,
.missionChoiceCopy strong {
  display: block;
  color: rgba(255, 255, 255, 0.92);
  overflow-wrap: anywhere;
}

.groupToggle i {
  display: inline-flex;
  min-width: 28px;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 999px;
  color: rgba(219, 244, 255, 0.92);
  background: rgba(110, 229, 255, 0.10);
  font-style: normal;
  font-size: var(--cap);
  font-weight: 900;
}

.groupIcon {
  display: inline-grid;
  place-items: center;
  width: 60px;
  height: 60px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 50%;
  /* color: rgba(219, 244, 255, 0.92); */
  /* background: rgba(110, 229, 255, 0.08); */
  padding: 8px;
  font-size: var(--cap);
  font-weight: 950;
}

.challengeIcon {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
}

.groupIcon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0) invert(1);
}

.missionRows {
  padding-inline-start: 10px;
}

.missionChoiceRow {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 8px 10px;
  align-items: center;
  padding: 10px;
  border-radius: 14px;
}

.missionChoiceRow.selected {
  border-color: rgba(110, 229, 255, 0.32);
  background: rgba(110, 229, 255, 0.075);
}

.missionChoiceMarker {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(110, 229, 255, 0.72);
  box-shadow: 0 0 0 4px rgba(110, 229, 255, 0.08);
}

.missionChoiceRow.tiny .missionChoiceMarker {
  background: rgba(74, 222, 128, 0.78);
  box-shadow: 0 0 0 4px rgba(74, 222, 128, 0.08);
}

.missionChoiceRow.bonus .missionChoiceMarker {
  background: rgba(247, 215, 116, 0.84);
  box-shadow: 0 0 0 4px rgba(247, 215, 116, 0.08);
}

.missionChoiceRow.done {
  opacity: 0.76;
}

.missionChoiceChips {
  grid-column: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.choiceChip {
  display: inline-flex;
  max-width: 100%;
  padding: 4px 7px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.04);
  font-size: var(--cap);
  font-weight: 850;
}

.choiceChip.reminder {
  color: rgba(219, 244, 255, 0.92);
  background: rgba(110, 229, 255, 0.08);
}

.selectedMissionContext {
  padding-top: var(--s-8);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

@media (max-width: 720px) {

  .challengeGroups,
  .missionRows {
    padding-inline-start: 0;
  }
}
</style>
