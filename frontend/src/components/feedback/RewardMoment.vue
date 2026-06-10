<template>
  <Teleport to="body">
    <Transition name="reward">
      <div v-if="open" class="rewardOverlay" role="presentation" @click.self="close">
        <section class="rewardPanel" role="dialog" aria-modal="true" :aria-label="t('rewardMoment.title')">
          <div class="rewardAura" aria-hidden="true"></div>

          <div class="rewardHero">
            <div>
              <p class="eyebrow">{{ t("rewardMoment.eyebrow") }}</p>
              <h2>{{ t("rewardMoment.title") }}</h2>
              <p class="message">{{ motivationLine }}</p>
            </div>

            <RingoMoodFigure
              class="rewardRingo"
              :mood="rewardMood"
              :alt="t('rewardMoment.title')"
              size="md"
              floating
            />
          </div>

          <div v-if="missionContext" class="missionReceipt">
            <div class="receiptHead">
              <span>{{ t("rewardMoment.mission.label") }}</span>
              <strong>{{ missionContext.title }}</strong>
            </div>

            <dl class="receiptDetails">
              <div v-if="securedTime">
                <dt>{{ t("rewardMoment.mission.securedAt") }}</dt>
                <dd>{{ securedTime }}</dd>
              </div>

              <div v-if="missionContext.challengeName">
                <dt>{{ t("rewardMoment.mission.challenge") }}</dt>
                <dd>{{ missionContext.challengeName }}</dd>
              </div>
            </dl>

            <p v-if="missionContext.summary" class="missionSummary">
              {{ missionContext.summary }}
            </p>

            <p v-if="socialProofLine" class="socialProof">
              {{ socialProofLine }}
            </p>
          </div>

          <div class="rewardStats">
            <div class="statItem primary">
              <span>{{ t("rewardMoment.xpEarned") }}</span>
              <strong>{{ t("rewardMoment.xpValue", { count: xpEarned }) }}</strong>
            </div>

            <div v-if="streakLabel" class="statItem">
              <span>{{ t("rewardMoment.streak") }}</span>
              <strong>{{ streakLabel }}</strong>
            </div>

            <div v-if="totalXp != null" class="statItem">
              <span>{{ t("rewardMoment.totalXp") }}</span>
              <strong>{{ t("common.xp", { count: totalXp }) }}</strong>
            </div>
          </div>

          <div v-if="achievements.length" class="achievements">
            <p>{{ t("rewardMoment.achievements") }}</p>

            <ul>
              <li v-for="achievement in achievements" :key="achievement.key || achievement.title">
                <span class="achievementDot" aria-hidden="true"></span>
                <div>
                  <strong>{{ achievement.title }}</strong>
                  <small v-if="achievement.xp_reward">
                    {{ t("rewardMoment.bonusXp", { count: achievement.xp_reward }) }}
                  </small>
                </div>
              </li>
            </ul>
          </div>

          <!-- Progressive unlock hints: Activity, Achievements, and Public Profile unlock inside this modal. -->
          <div v-if="unlockedFeatures.length" class="featureUnlocks">
            <p class="unlockIntro">{{ t("rewardMoment.unlocks.intro") }}</p>

            <article v-for="feature in unlockedFeatures" :key="feature.key" class="unlockCard">
              <div>
                <h3>{{ t(`rewardMoment.unlocks.${feature.key}.title`) }}</h3>
                <p>{{ t(`rewardMoment.unlocks.${feature.key}.description`) }}</p>
              </div>

              <RouterLink v-if="feature.to" v-slot="{ navigate }" :to="feature.to" custom>
                <BaseButton class="unlockCta" variant="secondary" @click="handleNavigate(navigate)">
                  {{ t(`rewardMoment.unlocks.${feature.key}.cta`) }}
                </BaseButton>
              </RouterLink>
            </article>
          </div>

          <BaseButton class="continueButton" variant="primary" @click="close">
            {{ t("rewardMoment.continue") }}
          </BaseButton>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";

import BaseButton from "@/components/ui/BaseButton.vue";
import RingoMoodFigure from "@/components/ringo/RingoMoodFigure.vue";
import { resolveRingoMood } from "@/constants/ringoSprites";

const props = defineProps({
  open: { type: Boolean, default: false },
  reward: { type: Object, default: null },
});

const emit = defineEmits(["close"]);

const { t } = useI18n();

const achievements = computed(() => {
  return Array.isArray(props.reward?.achievements) ? props.reward.achievements : [];
});

const unlockedFeatures = computed(() => {
  return Array.isArray(props.reward?.unlockedFeatures)
    ? props.reward.unlockedFeatures.filter((feature) => feature?.key)
    : [];
});

const xpEarned = computed(() => {
  const value = Number(props.reward?.xpEarned ?? 0);
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, value);
});

const totalXp = computed(() => {
  const value = props.reward?.xpTotal;
  if (value == null) return null;

  const numeric = Number(value);
  return Number.isFinite(numeric) ? Math.max(0, numeric) : null;
});

const missionContext = computed(() => {
  const mission = props.reward?.mission;
  if (!mission?.title) return null;

  return {
    title: String(mission.title),
    challengeName: String(mission.challengeName || ""),
    summary: String(mission.summary || ""),
    securedAt: mission.securedAt || "",
    todayDoneBeforeYou: Number.isFinite(Number(mission.todayDoneBeforeYou))
      ? Number(mission.todayDoneBeforeYou)
      : null,
    todayDoneCount: Number.isFinite(Number(mission.todayDoneCount))
      ? Number(mission.todayDoneCount)
      : null,
  };
});

const securedTime = computed(() => {
  if (!missionContext.value?.securedAt) return "";

  const date = new Date(missionContext.value.securedAt);
  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
});

const streakValue = computed(() => {
  const value = Number(props.reward?.streak ?? 0);
  if (!Number.isFinite(value) || value <= 0) return null;
  return Math.round(value);
});

const streakLabel = computed(() => {
  if (!streakValue.value) return "";
  return t("rewardMoment.streakValue", { count: streakValue.value });
});

const rewardMood = computed(() => {
  if (achievements.value.length) return resolveRingoMood("rewardAchievement");
  if (unlockedFeatures.value.length) return resolveRingoMood("rewardUnlock");
  if (streakValue.value && streakValue.value >= 3) return resolveRingoMood("rewardStreak");
  if (xpEarned.value > 0) return resolveRingoMood("rewardXp");
  return resolveRingoMood("rewardDefault");
});

const motivationLine = computed(() => {
  const seed = xpEarned.value + achievements.value.length + (streakValue.value || 0);
  const index = seed % 4;
  return t(`rewardMoment.lines.${index}`);
});

const socialProofLine = computed(() => {
  const beforeYou = missionContext.value?.todayDoneBeforeYou;
  const total = missionContext.value?.todayDoneCount;

  if (!Number.isFinite(beforeYou)) return "";
  if (beforeYou <= 0) return t("rewardMoment.mission.firstToday");

  return t("rewardMoment.mission.othersBefore", {
    count: beforeYou,
    total: Number.isFinite(total) ? total : beforeYou + 1,
  });
});

function close() {
  emit("close");
}

function handleNavigate(navigate) {
  close();
  navigate();
}

function onKeydown(event) {
  if (event.key === "Escape" && props.open) {
    close();
  }
}

onMounted(() => {
  window.addEventListener("keydown", onKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", onKeydown);
});
</script>

<style scoped>
.rewardOverlay {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: var(--s-20);
  background: rgba(4, 7, 14, 0.68);
  backdrop-filter: blur(14px);
}

.rewardPanel {
  position: relative;
  overflow: hidden;
  width: min(520px, 100%);
  max-height: calc(100vh - 40px);
  padding: 28px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.13);
  background:
    radial-gradient(circle at 12% 0%, rgba(74, 222, 128, 0.14), transparent 34%),
    radial-gradient(circle at 92% 8%, rgba(110, 229, 255, 0.12), transparent 34%),
    linear-gradient(145deg, rgba(18, 24, 38, 0.96), rgba(10, 14, 25, 0.96));
  box-shadow: 0 34px 110px rgba(0, 0, 0, 0.46);
  overflow-y: auto;
}

.rewardAura {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.04), transparent);
  pointer-events: none;
}

.rewardHero,
.eyebrow,
h2,
.message,
.rewardStats,
.missionReceipt,
.achievements,
.featureUnlocks,
.continueButton {
  position: relative;
  z-index: 1;
}

.rewardHero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--s-16);
  align-items: center;
}

.rewardHero > div:first-child {
  min-width: 0;
}

.rewardRingo {
  align-self: start;
}

.eyebrow {
  margin: 0 0 8px;
  color: rgba(134, 239, 172, 0.90);
  font-size: 0.74rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 2.4rem;
  line-height: 1.02;
  letter-spacing: 0;
}

.message {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.7;
}

.missionReceipt {
  display: grid;
  gap: var(--s-12);
  margin-top: var(--s-20);
  padding: 15px;
  border: 1px solid rgba(134, 239, 172, 0.16);
  border-radius: 20px;
  background:
    linear-gradient(135deg, rgba(74, 222, 128, 0.09), rgba(110, 229, 255, 0.045)),
    rgba(255, 255, 255, 0.036);
}

.receiptHead span,
.receiptDetails dt {
  display: block;
  color: rgba(187, 247, 208, 0.80);
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}

.receiptHead strong {
  display: block;
  margin-top: 5px;
  color: rgba(255, 255, 255, 0.96);
  font-size: 1.08rem;
  line-height: 1.35;
}

.receiptDetails {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--s-10);
  margin: 0;
}

.receiptDetails div {
  min-width: 0;
}

.receiptDetails dd {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.84);
  font-weight: 760;
  line-height: 1.35;
}

.missionSummary,
.socialProof {
  margin: 0;
  color: rgba(255, 255, 255, 0.66);
  line-height: 1.6;
}

.socialProof {
  padding-top: var(--s-10);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(253, 230, 138, 0.88);
  font-weight: 760;
}

.rewardStats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--s-12);
  margin-top: var(--s-20);
}

.statItem {
  min-width: 0;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(255, 255, 255, 0.045);
}

.statItem.primary {
  border-color: rgba(110, 229, 255, 0.22);
  background: rgba(110, 229, 255, 0.08);
}

.statItem span {
  display: block;
  color: rgba(255, 255, 255, 0.54);
  font-size: 0.76rem;
  font-weight: 720;
}

.statItem strong {
  display: block;
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.94);
  font-size: 1.08rem;
}

.achievements {
  margin-top: var(--s-20);
  padding-top: var(--s-16);
  border-top: 1px solid rgba(255, 255, 255, 0.10);
}

.achievements p {
  margin: 0 0 10px;
  color: rgba(255, 255, 255, 0.74);
  font-weight: 760;
}

.achievements ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.achievements li {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 10px 12px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.042);
}

.achievementDot {
  width: 10px;
  height: 10px;
  flex: 0 0 auto;
  margin-top: 6px;
  border-radius: 999px;
  background: #fde68a;
  box-shadow: 0 0 18px rgba(253, 230, 138, 0.44);
}

.achievements strong,
.achievements small {
  display: block;
}

.achievements small {
  margin-top: 3px;
  color: rgba(255, 255, 255, 0.56);
}

.featureUnlocks {
  display: grid;
  gap: 10px;
  margin-top: var(--s-20);
  padding-top: var(--s-16);
  border-top: 1px solid rgba(255, 255, 255, 0.10);
}

.unlockIntro {
  margin: 0;
  color: rgba(255, 255, 255, 0.74);
  font-weight: 760;
}

.unlockCard {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s-12);
  padding: 12px;
  border-radius: 17px;
  border: 1px solid rgba(110, 229, 255, 0.14);
  background: rgba(110, 229, 255, 0.055);
}

.unlockCard h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 0.96rem;
  line-height: 1.35;
}

.unlockCard p {
  margin: 5px 0 0;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.55;
}

.unlockCta {
  flex: 0 0 auto;
}

.continueButton {
  width: 100%;
  margin-top: var(--s-20);
}

.reward-enter-active,
.reward-leave-active {
  transition: opacity 180ms ease;
}

.reward-enter-active .rewardPanel,
.reward-leave-active .rewardPanel {
  transition: transform 180ms ease, opacity 180ms ease;
}

.reward-enter-from,
.reward-leave-to {
  opacity: 0;
}

.reward-enter-from .rewardPanel,
.reward-leave-to .rewardPanel {
  opacity: 0;
  transform: translateY(10px) scale(0.985);
}

@media (prefers-reduced-motion: reduce) {

  .reward-enter-active,
  .reward-leave-active,
  .reward-enter-active .rewardPanel,
  .reward-leave-active .rewardPanel {
    transition: none;
  }
}

@media (max-width: 560px) {
  .rewardOverlay {
    place-items: center;
    padding: var(--s-12);
  }

  .rewardPanel {
    padding: 22px;
    border-radius: 24px;
  }

  .rewardHero {
    grid-template-columns: 1fr;
  }

  .rewardRingo {
    order: -1;
    justify-self: center;
  }

  h2 {
    font-size: 1.9rem;
  }

  .rewardStats {
    grid-template-columns: 1fr;
  }

  .receiptDetails {
    grid-template-columns: 1fr;
  }

  .unlockCard {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
