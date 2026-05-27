<template>
  <BaseCard class="challengeCard" :class="{ completed: challenge.today_checked }" :padded="true">
    <div class="cardTop">
      <div class="main">
        <div class="titleRow">
          <h3 class="h2 title">{{ challenge.enrollment_name }}</h3>
          <span class="statusPill">{{ challenge.status || "Active" }}</span>
        </div>
        <p v-if="challenge.description" class="desc">{{ challenge.description }}</p>
      </div>

      <div class="todayBadge" :class="challenge.today_checked ? 'done' : 'pending'">
        {{ challenge.today_checked ? "Done today" : "Ready today" }}
      </div>
    </div>

    <div class="metaRow">
      <span class="meta">🔥 {{ challenge.streak_text }}</span>
      <span class="meta">⭐ +{{ challenge.xp_reward }} XP</span>
      <span class="meta" v-if="challenge.duration_days">⏱ {{ challenge.duration_days }} days</span>
      <span class="meta">📈 {{ challenge.progress_text }}</span>
    </div>

    <div class="actions">
      <RouterLink class="openLink" :to="`/enrollment/${challenge.enrollment_id}`">Open details →</RouterLink>
      <BaseButton
        variant="primary"
        :loading="loading"
        :disabled="challenge.today_checked"
        class="doneBtn"
        @click="$emit('checkin', challenge.enrollment_id)"
      >
        <span v-if="challenge.today_checked">✅ Completed</span>
        <span v-else>Done</span>
      </BaseButton>
    </div>
  </BaseCard>
</template>

<script setup>
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

defineProps({
  challenge: { type: Object, required: true },
  loading: { type: Boolean, default: false },
});

defineEmits(["checkin"]);
</script>

<style scoped>
.challengeCard{background: rgba(255,255,255,0.03); border-color: rgba(255,255,255,0.12); transition: transform 160ms ease, border-color 160ms ease, box-shadow 220ms ease;}
.challengeCard:hover{transform: translateY(-1px); border-color: rgba(99,102,241,0.38); box-shadow: 0 14px 32px rgba(0,0,0,.3);}
.challengeCard.completed{border-color: rgba(34,197,94,.28);}
.cardTop{display:flex;justify-content:space-between;gap:var(--s-12);align-items:flex-start;}
.titleRow{display:flex;gap:var(--s-8);align-items:center;flex-wrap:wrap;}
.statusPill,.todayBadge{font-size:var(--cap);padding:4px 8px;border-radius:999px;border:1px solid var(--border);}
.todayBadge.done{background:rgba(34,197,94,.14);border-color:rgba(34,197,94,.45)}
.todayBadge.pending{background:rgba(245,158,11,.12);border-color:rgba(245,158,11,.3)}
.desc{margin:8px 0 0;color:var(--muted)}
.metaRow{display:flex;gap:var(--s-12);flex-wrap:wrap;margin-top:var(--s-12);}
.meta{font-size:var(--cap);color:var(--muted2);}
.actions{display:flex;justify-content:space-between;align-items:center;gap:var(--s-12);margin-top:var(--s-16);flex-wrap:wrap;}
.openLink{opacity:.9}
.doneBtn:deep(.btn){min-width:108px;}
</style>
