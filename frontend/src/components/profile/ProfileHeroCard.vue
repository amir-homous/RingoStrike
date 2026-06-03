<template>
  <BaseCard>
    <div class="row">
      <UserAvatar
  :src="profile.avatar_url"
  :name="profile.name"
  size="xl"
/>

      <div class="stack-8 hero-copy">
        <h2 class="h2">
          {{ profile.name }}
        </h2>

        <p class="caption">
          @{{ profile.username }}
        </p>
        <p
          v-if="profile.bio"
          class="bio"
        >
          {{ profile.bio }}
        </p>

        <p class="caption">
          {{ t("profileComponents.levelTitle", { level: profile.stats.level, title: profile.title.label }) }}
        </p>

        <p class="quote">
          "{{ profile.tagline }}"
        </p>
      </div>

      <div class="meta">
        <span>
          🔥 {{ profile.stats.current_streak }}
          {{ t("profileComponents.dayStreak") }}
        </span>

        <span>
          🏆 {{ profile.stats.achievements_unlocked }}
          {{ t("profileComponents.achievements") }}
        </span>

        <span>
          ⚡ {{ profile.stats.total_xp }}
          XP
        </span>

        <button
        v-if="isOwner"
        class="edit"
        @click="openEditProfile"
        >
        {{ t("profileComponents.edit") }}
        </button>

        <button
          class="share"
          @click="shareProfile"
        >
          {{ copied ? t("profileComponents.copied") : t("profileComponents.share") }}
        </button>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { ref } from "vue";
import { useI18n } from "vue-i18n";

import BaseCard from "@/components/ui/BaseCard.vue";
import UserAvatar from "./UserAvatar.vue";

const props = defineProps({
  profile: Object,

  isOwner: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits([
  "edit-profile",
]);

const copied = ref(false);
const { t } = useI18n();

async function shareProfile() {
  const url =
    `${window.location.origin}/u/${props.profile.username}`;

  try {
    await navigator.clipboard.writeText(url);

    copied.value = true;

    setTimeout(() => {
      copied.value = false;
    }, 2200);
  } catch (err) {
    console.error("share failed", err);
  }
}


function openEditProfile() {

  emit("edit-profile");
}

</script>

<style scoped>
.row{
  display:flex;
  gap:16px;
  justify-content:space-between;
  flex-wrap:wrap;
  align-items:flex-start;
}

.hero-copy{
  flex:1;
  min-width:220px;
}

.quote{
  margin:0;
  color:var(--muted);
}

.meta{
  display:grid;
  gap:8px;
}

.share{
  border:1px solid rgba(255,255,255,.14);
  background:rgba(255,255,255,.06);
  color:white;
  border-radius:10px;
  padding:10px 12px;
  cursor:pointer;
  transition:all .18s ease;
  font-weight:600;
}

.share:hover{
  background:rgba(255,255,255,.1);
}


.edit{
  border:1px solid rgba(255,255,255,.14);
  background:rgba(255,255,255,.04);
  color:white;
  border-radius:10px;
  padding:10px 12px;
  cursor:pointer;
  transition:all .18s ease;
  font-weight:600;
}

.edit:hover{
  background:rgba(255,255,255,.10);
  transform:translateY(-1px);
}

.edit:active{
  transform:translateY(0);
}

.edit:focus-visible{
  outline:none;
  border-color:rgba(99,102,241,.6);
  box-shadow:
    0 0 0 2px rgba(99,102,241,.2);
}

</style>
