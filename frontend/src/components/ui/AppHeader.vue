<template>
    <header class="hdr">
      <RouterLink class="brand" to="/dashboard">RingoStrike</RouterLink>
  
      <nav class="nav">
        <RouterLink class="link" :class="{ active: isActive('/dashboard') }" to="/dashboard">
          {{ t("nav.dashboard") }}
        </RouterLink>
  
        <RouterLink class="link" :class="{ active: isActive('/challenges') }" to="/challenges">
          {{ t("nav.challenges") }}
        </RouterLink>

        <RouterLink class="link" :class="{ active: isActive('/profile') }" to="/profile">
          {{ t("nav.profile") }}
        </RouterLink>
  
        <!-- فقط وقتی داخل enrollment هستیم یا id داریم -->
        <RouterLink
          v-if="leaderboardTo"
          class="link"
          :class="{ active: isActive(`/enrollment/${enrollmentId}/leaderboard`) }"
          :to="leaderboardTo"
        >
          {{ t("nav.leaderboard") }}
        </RouterLink>
      </nav>

      <LanguageSwitcher />
    </header>
  </template>
  
  <script setup>
  import { computed } from "vue";
  import { useRoute } from "vue-router";
  import { useI18n } from "vue-i18n";
  import LanguageSwitcher from "@/components/i18n/LanguageSwitcher.vue";
  
  const route = useRoute();
  const { t } = useI18n();
  
  const enrollmentId = computed(() => {
    const id = route.params.id;
    return typeof id === "string" ? id : "";
  });
  
  const leaderboardTo = computed(() => {
    // فقط در صفحاتی که context enrollment دارن
    return enrollmentId.value ? `/enrollment/${enrollmentId.value}/leaderboard` : "";
  });
  
  function isActive(prefix) {
    return route.path === prefix || route.path.startsWith(prefix + "/");
  }
  </script>
  
  <style scoped>
  .hdr{
    display:flex;
    align-items:center;
    justify-content: space-between;
    gap: var(--s-16);
    padding: var(--s-12) var(--s-16);
    border: 1px solid var(--border);
    border-radius: var(--r-12);
    background: rgba(255,255,255,0.04);
    margin-bottom: var(--s-24);
  }
  .brand{
    font-weight: 800;
    letter-spacing: -0.02em;
    color: rgba(255,255,255,0.92);
    text-decoration: none;
  }
  .nav{ display:flex; gap: var(--s-8); flex-wrap: wrap; justify-content:flex-end; margin-inline-start: auto; }
  .link{
    padding: 8px 10px;
    border-radius: 10px;
    border: 1px solid transparent;
    color: var(--muted);
    text-decoration:none;
  }
  .link:hover{ background: rgba(255,255,255,0.05); }
  .link.active{
    color: rgba(255,255,255,0.92);
    border-color: rgba(99,102,241,0.35);
    background: rgba(99,102,241,0.18);
  }

  @media (max-width: 640px) {
    .hdr {
      align-items: flex-start;
      flex-wrap: wrap;
    }

    .nav {
      order: 3;
      width: 100%;
      justify-content: flex-start;
      margin-inline-start: 0;
    }
  }
  </style>
  
