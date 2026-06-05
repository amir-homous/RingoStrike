<template>
  <div class="nav-container">
    <header class="hdr">
      <RouterLink class="brand" to="/dashboard">RingoStrike</RouterLink>
  
      <!-- Desktop Nav -->
      <nav class="desktop-nav">
        <RouterLink class="link" :class="{ active: isActive('/dashboard') }" to="/dashboard">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
          <span class="label">{{ t("nav.dashboard") }}</span>
        </RouterLink>
  
        <RouterLink class="link" :class="{ active: isActive('/challenges') }" to="/challenges">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>
          <span class="label">{{ t("nav.challenges") }}</span>
        </RouterLink>

        <RouterLink
          v-if="leaderboardTo"
          class="link"
          :class="{ active: isActive(`/enrollment/${enrollmentId}/leaderboard`) }"
          :to="leaderboardTo"
        >
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20v-6M6 20V10M18 20V4"></path></svg>
          <span class="label">{{ t("nav.leaderboard") }}</span>
        </RouterLink>

        <RouterLink class="link" :class="{ active: isActive('/profile') }" to="/profile">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          <span class="label">{{ t("nav.profile") }}</span>
        </RouterLink>
      </nav>

      <LanguageSwitcher />
    </header>

    <!-- Mobile Bottom Nav -->
    <nav class="mobile-bottom-nav">
      <RouterLink class="link" :class="{ active: isActive('/dashboard') }" to="/dashboard">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        <span class="label">{{ t("nav.dashboard") }}</span>
      </RouterLink>

      <RouterLink class="link" :class="{ active: isActive('/challenges') }" to="/challenges">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>
        <span class="label">{{ t("nav.challenges") }}</span>
      </RouterLink>

      <RouterLink
        v-if="leaderboardTo"
        class="link"
        :class="{ active: isActive(`/enrollment/${enrollmentId}/leaderboard`) }"
        :to="leaderboardTo"
      >
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20v-6M6 20V10M18 20V4"></path></svg>
        <span class="label">{{ t("nav.leaderboard") }}</span>
      </RouterLink>

      <RouterLink class="link" :class="{ active: isActive('/profile') }" to="/profile">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        <span class="label">{{ t("nav.profile") }}</span>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from "vue";
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
  return enrollmentId.value ? `/enrollment/${enrollmentId.value}/leaderboard` : "";
});

function isActive(prefix) {
  return route.path === prefix || route.path.startsWith(prefix + "/");
}

// Add body padding dynamically for mobile bottom nav
onMounted(() => {
  document.body.classList.add('has-bottom-nav');
});

onUnmounted(() => {
  document.body.classList.remove('has-bottom-nav');
});
</script>

<style>
/* Global body class to prevent content being hidden under mobile nav */
body.has-bottom-nav {
  padding-bottom: 0;
}
@media (max-width: 640px) {
  body.has-bottom-nav {
    padding-bottom: 80px; /* Space for bottom nav */
  }
}
</style>

<style scoped>
.hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s-16);
  padding: var(--s-12) var(--s-20);
  border: 1px solid var(--border);
  border-radius: var(--r-12);
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  margin-bottom: var(--s-24);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: var(--s-16);
  z-index: 50;
}

.brand {
  font-weight: 800;
  font-size: var(--h2);
  letter-spacing: -0.03em;
  color: rgba(255, 255, 255, 0.95);
  text-decoration: none;
  background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.desktop-nav {
  display: flex;
  gap: var(--s-8);
  align-items: center;
  flex: 1;
  justify-content: flex-end;
  margin-inline-end: var(--s-8);
}

.mobile-bottom-nav {
  display: none;
}

.link {
  display: flex;
  align-items: center;
  gap: var(--s-8);
  padding: var(--s-8) var(--s-12);
  border-radius: var(--r-10);
  border: 1px solid transparent;
  color: var(--muted);
  text-decoration: none;
  font-size: var(--body);
  font-weight: 500;
  transition: all 0.2s ease;
}

.icon {
  width: 18px;
  height: 18px;
  opacity: 0.8;
  transition: transform 0.2s ease;
}

.link:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.04);
}

.link.active {
  color: rgba(255, 255, 255, 0.95);
  border-color: rgba(99, 102, 241, 0.25);
  background: rgba(99, 102, 241, 0.12);
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.1);
}

.link.active .icon {
  color: #818cf8;
  opacity: 1;
  transform: scale(1.05);
}

@media (max-width: 640px) {
  .hdr {
    position: relative;
    top: 0;
    margin-bottom: var(--s-16);
    padding: var(--s-12) var(--s-16);
    border-radius: var(--r-12);
  }
  
  .desktop-nav {
    display: none;
  }

  .mobile-bottom-nav {
    display: flex;
    justify-content: space-around;
    align-items: center;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: var(--s-12) var(--s-8);
    padding-bottom: calc(var(--s-12) + env(safe-area-inset-bottom, 0px));
    background: rgba(11, 13, 18, 0.85); /* fallback var(--bg) with opacity */
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 1px solid var(--border);
    z-index: 100;
  }

  .mobile-bottom-nav .link {
    flex-direction: column;
    gap: var(--s-4);
    padding: var(--s-8);
    font-size: 11px;
    flex: 1;
    justify-content: center;
    border: none;
    background: transparent;
    box-shadow: none;
    border-radius: var(--r-10);
  }

  .mobile-bottom-nav .icon {
    width: 22px;
    height: 22px;
  }

  .mobile-bottom-nav .link.active {
    color: #818cf8;
    background: rgba(99, 102, 241, 0.08);
  }
}
</style>
