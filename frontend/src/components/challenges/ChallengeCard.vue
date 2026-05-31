<template>
  <BaseCard
    class="challengeCard"
    :class="{
      joined: isJoined,
      inviteOnly: isInviteOnly,
      compact,
    }"
  >
    <div class="ambientGlow"></div>

    <div class="cardContent">
      <div class="topRow">
        <div class="main">
          <div class="cardEyebrow">
            <span class="signalDot" :class="{ active: isActive }"></span>
            <span>{{ isJoined ? "Joined Path" : "Available Path" }}</span>
          </div>

          <div class="titleRow">
            <h3 class="title">
              {{ title }}
            </h3>

            <span class="statusBadge" :class="{ active: isActive }">
              {{ normalizedStatus }}
            </span>
          </div>

          <p v-if="challenge.description && !compact" class="desc">
            {{ challenge.description }}
          </p>
        </div>

        <div class="actionCol">
          <RouterLink
            v-if="isJoined && challenge.enrollment_id"
            class="actionLink primaryLink"
            :to="`/enrollment/${challenge.enrollment_id}`"
          >
            <span>Open</span>
            <span class="arrow">→</span>
          </RouterLink>

          <BaseButton
            v-if="isJoined && challenge.enrollment_id && showCheckin"
            variant="primary"
            :loading="loading"
            :disabled="isTodayChecked"
            @click="$emit('checkin', challenge.enrollment_id)"
          >
            <span v-if="isTodayChecked">Done Today</span>
            <span v-else>Check in</span>
          </BaseButton>

          <BaseButton
            v-if="!isJoined && showJoin"
            variant="primary"
            :loading="loading"
            @click="$emit('join')"
          >
            Join Challenge
          </BaseButton>
        </div>
      </div>

      <div class="metaGrid" :class="{ compactGrid: compact }">
        <div v-if="hasDuration" class="metaItem">
          <span class="metaIcon">⏱</span>
          <div>
            <div class="metaLabel">Duration</div>
            <div class="metaValue">{{ durationText }}</div>
          </div>
        </div>

        <div v-if="showMembersMeta" class="metaItem">
          <span class="metaIcon">👥</span>
          <div>
            <div class="metaLabel">Members</div>
            <div class="metaValue">{{ membersCount }}</div>
          </div>
        </div>

        <div v-if="hasVisibility || !compact" class="metaItem">
          <span class="metaIcon">{{ isInviteOnly ? "🔐" : "🔓" }}</span>
          <div>
            <div class="metaLabel">Access</div>
            <div class="metaValue">{{ visibilityText }}</div>
          </div>
        </div>

        <div v-if="!compact" class="metaItem">
          <span class="metaIcon">✨</span>
          <div>
            <div class="metaLabel">Reward</div>
            <div class="metaValue">+{{ xpReward }} XP</div>
          </div>
        </div>

        <div v-if="compact && hasStreak" class="metaItem">
          <span class="metaIcon">🔥</span>
          <div>
            <div class="metaLabel">Streak</div>
            <div class="metaValue">{{ streakValue }}</div>
          </div>
        </div>

        <div v-if="compact && hasTotalCheckins" class="metaItem">
          <span class="metaIcon">✅</span>
          <div>
            <div class="metaLabel">Check-ins</div>
            <div class="metaValue">{{ totalCheckinsValue }}</div>
          </div>
        </div>
      </div>

      <div class="bottomRow">
        <div v-if="showMemberPreview" class="memberPreview">
          <span class="avatarStack" aria-hidden="true">
            <span
              v-for="name in previewNames"
              :key="name"
              class="miniAvatar"
            >
              {{ name.slice(0, 1).toUpperCase() }}
            </span>
          </span>

          <span class="caption previewText">
            <span>Joined by</span>
            <b>{{ previewNames.join(", ") }}</b>
            <span v-if="moreCount > 0">+ {{ moreCount }} more</span>
          </span>
        </div>

        <div v-else-if="showEmptyMemberHint" class="memberPreview">
          <span class="caption muted">Be the first to start this path.</span>
        </div>

        <div v-else class="memberPreview compactHint">
          <span class="caption muted">{{ statusHintText }}</span>
        </div>

        <span
          v-if="isJoined"
          class="todayBadge"
          :class="{ done: isTodayChecked, pending: !isTodayChecked }"
        >
          {{ isTodayChecked ? "Completed today" : "Ready today" }}
        </span>

        <span v-else class="todayBadge pending">
          Ready to join
        </span>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from "vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

const props = defineProps({
  challenge: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  xpReward: { type: Number, default: 10 },
  showJoin: { type: Boolean, default: false },
  showCheckin: { type: Boolean, default: true },
  compact: { type: Boolean, default: false },
});

defineEmits(["checkin", "join"]);

const title = computed(() => {
  return props.challenge.name || props.challenge.enrollment_name || props.challenge.challenge_name || "Challenge";
});

const isJoined = computed(() => Boolean(props.challenge.is_joined || props.challenge.enrollment_id));

const isTodayChecked = computed(() => {
  const value = props.challenge.today_checked ?? props.challenge.todayChecked ?? false;

  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value === 1;
  if (typeof value === "string") {
    return ["true", "1", "yes", "done", "checked"].includes(value.toLowerCase());
  }

  return false;
});

const normalizedStatus = computed(() => {
  const value = String(props.challenge.status || "active").toLowerCase();
  return value.charAt(0).toUpperCase() + value.slice(1);
});

const isActive = computed(() => normalizedStatus.value.toLowerCase() === "active");

const hasVisibility = computed(() => {
  return Object.prototype.hasOwnProperty.call(props.challenge, "visibility");
});

const visibilityText = computed(() => {
  const value = String(props.challenge.visibility || "public").toLowerCase();
  if (value === "invite-only") return "Invite-only";
  if (value === "private") return "Private";
  return "Public";
});

const isInviteOnly = computed(() => {
  return visibilityText.value === "Invite-only" || Boolean(props.challenge.needs_code);
});

const hasDuration = computed(() => {
  return Boolean(props.challenge.duration_days);
});

const durationText = computed(() => {
  const days = props.challenge.duration_days;
  return days ? `${days} days` : "Flexible";
});

const hasMembersField = computed(() => {
  return Object.prototype.hasOwnProperty.call(props.challenge, "members_count");
});

const membersCount = computed(() => {
  if (!hasMembersField.value) return null;
  return Number(props.challenge.members_count || 0);
});

const previewNames = computed(() => {
  return Array.isArray(props.challenge.members_preview)
    ? props.challenge.members_preview.filter(Boolean).slice(0, 3)
    : [];
});

const hasPreviewNames = computed(() => previewNames.value.length > 0);

const showMembersMeta = computed(() => {
  return !props.compact && hasMembersField.value;
});

const showMemberPreview = computed(() => {
  return !props.compact && hasMembersField.value && membersCount.value > 0 && hasPreviewNames.value;
});

const showEmptyMemberHint = computed(() => {
  return !props.compact && hasMembersField.value && membersCount.value === 0 && !isJoined.value;
});

const moreCount = computed(() => {
  if (membersCount.value == null) return 0;
  return Math.max(0, membersCount.value - previewNames.value.length);
});

const streakValue = computed(() => {
  return props.challenge.current_streak ?? props.challenge.currentStreak ?? 0;
});

const hasStreak = computed(() => {
  return props.compact && (
    Object.prototype.hasOwnProperty.call(props.challenge, "current_streak") ||
    Object.prototype.hasOwnProperty.call(props.challenge, "currentStreak")
  );
});

const totalCheckinsValue = computed(() => {
  return props.challenge.total_checkins ?? props.challenge.totalCheckins ?? 0;
});

const hasTotalCheckins = computed(() => {
  return props.compact && (
    Object.prototype.hasOwnProperty.call(props.challenge, "total_checkins") ||
    Object.prototype.hasOwnProperty.call(props.challenge, "totalCheckins")
  );
});

const statusHintText = computed(() => {
  if (props.compact) {
    return isTodayChecked.value
      ? "Momentum secured for today."
      : "Your daily strike is ready.";
  }

  return isJoined.value
    ? "Momentum path active."
    : "Ready to begin.";
});
</script>

<style scoped>
.challengeCard {
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.075), transparent 36%),
    rgba(255, 255, 255, 0.024);
  border-color: rgba(255, 255, 255, 0.10);
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    background 180ms ease,
    box-shadow 180ms ease;
    margin-top: 10px;
    
}

.challengeCard:hover {
  transform: translateY(-2px);
  border-color: rgba(110, 229, 255, 0.20);
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.11), transparent 38%),
    rgba(255, 255, 255, 0.034);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.20);
}

.challengeCard.joined {
  border-color: rgba(74, 222, 128, 0.18);
}

.challengeCard.inviteOnly {
  border-color: rgba(255, 228, 168, 0.16);
}

.challengeCard.compact {
  background: rgba(255, 255, 255, 0.022);
}

.ambientGlow {
  position: absolute;
  inset: -120px;
  background:
    radial-gradient(circle at 82% 0%, rgba(195, 90, 214, 0.08), transparent 36%),
    linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.035), transparent);
  pointer-events: none;
}

.cardContent {
  position: relative;
  z-index: 1;
}

.topRow {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 22px;
  align-items: flex-start;
}

.main {
  min-width: 0;
}

.cardEyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 11px;
  color: rgba(110, 229, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  white-space: nowrap;
}

.signalDot {
  width: 7px;
  height: 7px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.32);
}

.signalDot.active {
  background: #4ade80;
  box-shadow: 0 0 16px rgba(74, 222, 128, 0.65);
}

.titleRow {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.title {
  margin: 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: 1.24rem;
  line-height: 1.15;
  letter-spacing: -0.03em;
}

.statusBadge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 27px;
  padding: 5px 11px;
  border-radius: 999px;
  color: var(--muted2);
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.09);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: capitalize;
  white-space: nowrap;
}

.statusBadge.active {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.10);
  border-color: rgba(74, 222, 128, 0.18);
}

.desc {
  margin: var(--s-12) 0 0;
  max-width: 72ch;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.65;
}

.actionCol {
  display: flex;
  gap: 11px;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  min-width: 190px;
}

.actionLink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  padding: 10px 15px;
  border-radius: 15px;
  text-decoration: none;
  font-weight: 850;
  white-space: nowrap;
  transition:
    transform 160ms ease,
    background 160ms ease,
    border-color 160ms ease;
}

.primaryLink {
  color: rgba(255, 255, 255, 0.94);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.16), rgba(195, 90, 214, 0.11)),
    rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(110, 229, 255, 0.20);
}

.primaryLink:hover {
  transform: translateY(-1px);
  border-color: rgba(110, 229, 255, 0.34);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.22), rgba(195, 90, 214, 0.16)),
    rgba(255, 255, 255, 0.065);
}

.arrow {
  opacity: 0.9;
}

.metaGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 11px;
  margin-top: 18px;
}

.compactGrid {
  grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
}

.metaItem {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  padding: 11px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.075);
}

.metaIcon {
  width: 31px;
  height: 31px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.055);
}

.metaLabel {
  color: var(--muted2);
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.metaValue {
  margin-top: 3px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.82rem;
  font-weight: 800;
  white-space: nowrap;
}

.bottomRow {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 24px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.065);
}

.memberPreview {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 13px;
}

.compactHint {
  min-height: 32px;
}

.avatarStack {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  padding-left: 7px;
  padding-right: 4px;
}

.miniAvatar {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  margin-left: -7px;
  border-radius: 999px;
  color: white;
  font-size: 0.72rem;
  font-weight: 900;
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.22), transparent 35%),
    rgba(110, 229, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.16);
}

.miniAvatar:first-child {
  margin-left: 0;
}

.caption {
  color: var(--muted2);
  font-size: 0.82rem;
  line-height: 1.45;
}

.previewText {
  display: flex;
  gap: 6px;
  align-items: baseline;
  flex-wrap: wrap;
}

.caption b {
  color: rgba(255, 255, 255, 0.80);
}

.caption.muted {
  font-style: italic;
}

.todayBadge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
  padding: 8px 13px;
  border-radius: 999px;
  color: var(--muted2);
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.72rem;
  font-weight: 850;
  white-space: nowrap;
  justify-self: end;
}

.todayBadge.done {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.10);
  border-color: rgba(74, 222, 128, 0.18);
}

.todayBadge.pending {
  color: rgba(199, 210, 254, 0.95);
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.20);
}

@media (max-width: 860px) {
  .topRow,
  .bottomRow {
    grid-template-columns: 1fr;
  }

  .actionCol {
    justify-content: flex-start;
    min-width: 0;
  }

  .todayBadge {
    justify-self: start;
  }
}

@media (max-width: 520px) {
  .memberPreview {
    align-items: flex-start;
  }
}
</style>