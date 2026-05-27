<template>
  <BaseCard class="challengeCard" :class="{ done: challenge.today_checked }">
    <div class="topRow">
      <div class="stack-8 main">
        <div class="titleWrap">
          <h3 class="h2 title">{{ challenge.enrollment_name }}</h3>
          <span class="statusBadge" :class="challenge.status === 'Active' ? 'active' : 'inactive'">{{ challenge.status || 'Unknown' }}</span>
        </div>
        <p v-if="challenge.description" class="desc">{{ challenge.description }}</p>
      </div>

      <div class="actionCol">
        <RouterLink class="openLink" :to="`/enrollment/${challenge.enrollment_id}`">Open →</RouterLink>
        <BaseButton
          variant="primary"
          :loading="loading"
          :disabled="challenge.today_checked"
          @click="$emit('checkin', challenge.enrollment_id)"
        >
          <span v-if="challenge.today_checked">✅ Done Today</span>
          <span v-else>Done</span>
        </BaseButton>
      </div>
    </div>

    <div class="metaRow">
      <span class="badge" :class="challenge.today_checked ? 'good' : 'wait'">
        {{ challenge.today_checked ? 'Completed today' : 'Ready for today' }}
      </span>
      <span class="badge">🔥 {{ challenge.current_streak || 0 }} day streak</span>
      <span class="badge">✨ +{{ xpReward }} XP</span>
      <span v-if="challenge.duration_days" class="badge">⏱ {{ challenge.duration_days }} days</span>
    </div>
  </BaseCard>
</template>

<script setup>
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

defineProps({
  challenge: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  xpReward: { type: Number, default: 10 },
});

defineEmits(["checkin"]);
</script>

<style scoped>
.challengeCard{background:rgba(255,255,255,.025);border-color:rgba(255,255,255,.11);transition:transform 160ms ease,border-color 160ms ease,background 160ms ease}
.challengeCard:hover{transform:translateY(-1px);background:rgba(255,255,255,.035);border-color:rgba(255,255,255,.18)}
.topRow{display:flex;justify-content:space-between;gap:var(--s-16);align-items:flex-start;flex-wrap:wrap}
.main{min-width:0;flex:1}
.titleWrap{display:flex;gap:var(--s-8);align-items:center;flex-wrap:wrap}
.title{margin:0}
.statusBadge,.badge{font-size:var(--cap);border:1px solid rgba(255,255,255,.14);padding:5px 8px;border-radius:999px;color:var(--muted)}
.statusBadge.active{background:rgba(16,185,129,.14);color:rgba(167,243,208,.95);border-color:rgba(16,185,129,.28)}
.statusBadge.inactive{background:rgba(255,255,255,.06)}
.desc{margin:0;color:var(--muted);max-width:68ch}
.actionCol{display:flex;gap:var(--s-8);align-items:center;flex-wrap:wrap}
.openLink{padding:8px 10px;border-radius:10px;text-decoration:none;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.02)}
.metaRow{margin-top:var(--s-12);display:flex;gap:var(--s-8);flex-wrap:wrap}
.badge.good{background:rgba(16,185,129,.14);color:rgba(167,243,208,.95)}
.badge.wait{background:rgba(99,102,241,.15);color:rgba(199,210,254,.95)}
.done{border-color:rgba(16,185,129,.28)}
</style>
