<template>
  <header class="appHeader">
    <div class="headerBar">
      <RouterLink class="brand" to="/dashboard" @click="closeMenu">
        <span class="brandMark" aria-hidden="true">RS</span>
        <span class="brandText">RingoStrike</span>
      </RouterLink>

      <nav v-if="showNavigation" class="desktopNav" :aria-label="t('nav.primary')">
        <RouterLink
          v-for="item in navItems"
          :key="item.key"
          class="navLink"
          :class="{ active: isItemActive(item), hinted: hasHint(item.key) }"
          :to="item.to"
          :aria-current="isItemActive(item) ? 'page' : undefined"
        >
          <span class="navIcon" :data-icon="item.key" aria-hidden="true"></span>
          <span>{{ t(item.labelKey) }}</span>
          <span v-if="badgeFor(item.key)" class="navBadge">{{ badgeFor(item.key) }}</span>
        </RouterLink>
      </nav>

      <div class="headerActions">
        <LanguageSwitcher />

        <button
          v-if="showNavigation"
          type="button"
          class="menuButton"
          :aria-label="menuOpen ? t('nav.closeMenu') : t('nav.openMenu')"
          :aria-expanded="menuOpen"
          aria-controls="mobile-navigation"
          @click="menuOpen = !menuOpen"
        >
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </button>
      </div>
    </div>

    <Transition name="navSheet">
      <nav
        v-if="showNavigation && menuOpen"
        id="mobile-navigation"
        class="mobileSheet"
        :aria-label="t('nav.mobile')"
      >
        <RouterLink
          v-for="item in navItems"
          :key="item.key"
          class="sheetLink"
          :class="{ active: isItemActive(item), hinted: hasHint(item.key) }"
          :to="item.to"
          :aria-current="isItemActive(item) ? 'page' : undefined"
          @click="closeMenu"
        >
          <span class="navIcon" :data-icon="item.key" aria-hidden="true"></span>
          <span>
            <strong>{{ t(item.labelKey) }}</strong>
            <small>{{ t(item.hintKey) }}</small>
          </span>
          <span v-if="badgeFor(item.key)" class="navBadge">{{ badgeFor(item.key) }}</span>
        </RouterLink>
      </nav>
    </Transition>

    <nav v-if="showNavigation" class="mobileBottomNav" :aria-label="t('nav.mobilePrimary')">
      <RouterLink
        v-for="item in mobileItems"
        :key="item.key"
        class="bottomLink"
        :class="{ active: isItemActive(item), hinted: hasHint(item.key) }"
        :to="item.to"
        :aria-current="isItemActive(item) ? 'page' : undefined"
      >
        <span class="navIcon" :data-icon="item.key" aria-hidden="true"></span>
        <span>{{ t(item.labelKey) }}</span>
        <span v-if="badgeFor(item.key)" class="bottomBadge">{{ badgeFor(item.key) }}</span>
      </RouterLink>
    </nav>
  </header>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import LanguageSwitcher from "@/components/i18n/LanguageSwitcher.vue";
import { useNavigationStore } from "@/stores/navigation";

const route = useRoute();
const navigationStore = useNavigationStore();
const { t } = useI18n();

const menuOpen = ref(false);

const enrollmentId = computed(() => {
  const id = route.params.id;
  return typeof id === "string" ? id : "";
});

const leaderboardTo = computed(() => {
  return enrollmentId.value
    ? `/enrollment/${enrollmentId.value}/leaderboard`
    : { path: "/dashboard", hash: "#leaderboard" };
});

const navItems = computed(() => [
  {
    key: "dashboard",
    labelKey: "nav.dashboard",
    hintKey: "nav.hints.dashboard",
    to: "/dashboard",
  },
  {
    key: "paths",
    labelKey: "nav.paths",
    hintKey: "nav.hints.paths",
    to: "/paths",
  },
  {
    key: "challenges",
    labelKey: "nav.challenges",
    hintKey: "nav.hints.challenges",
    to: "/challenges",
  },
  {
    key: "leaderboard",
    labelKey: "nav.leaderboard",
    hintKey: "nav.hints.leaderboard",
    to: leaderboardTo.value,
  },
  {
    key: "activity",
    labelKey: "nav.activity",
    hintKey: "nav.hints.activity",
    to: { path: "/dashboard", hash: "#activity-feed" },
  },
  {
    key: "profile",
    labelKey: "nav.profile",
    hintKey: "nav.hints.profile",
    to: "/profile",
  },
  {
    key: "settings",
    labelKey: "nav.settings",
    hintKey: "nav.hints.settings",
    to: { path: "/profile", hash: "#settings" },
  },
]);

const mobileItems = computed(() => navItems.value.filter((item) => {
  return ["dashboard", "paths", "challenges", "profile"].includes(item.key);
}));

const showNavigation = computed(() => route.meta.requiresAuth !== false);

function closeMenu() {
  menuOpen.value = false;
}

function badgeFor(key) {
  return navigationStore.badgeFor(key);
}

function hasHint(key) {
  return navigationStore.hasUnlockHint(key) || navigationStore.nextStepKey === key;
}

function isItemActive(item) {
  if (item.key === "leaderboard") {
    return route.path.includes("/leaderboard") ||
      (route.path === "/dashboard" && route.hash === "#leaderboard");
  }

  if (item.key === "activity") {
    return route.path === "/dashboard" && route.hash === "#activity-feed";
  }

  if (item.key === "settings") {
    return route.path === "/profile" && route.hash === "#settings";
  }

  if (item.key === "dashboard") {
    return route.path === "/dashboard" && !route.hash;
  }

  if (item.key === "profile") {
    return route.path === "/profile" && route.hash !== "#settings";
  }

  if (item.key === "challenges") {
    return route.path === "/challenges";
  }

  if (item.key === "paths") {
    return route.path === "/paths";
  }

  return false;
}

watch(
  () => route.fullPath,
  () => closeMenu(),
);
</script>

<style scoped>
.appHeader {
  position: sticky;
  top: 12px;
  z-index: 30;
  margin-bottom: var(--s-24);
}

.headerBar {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--s-12);
  min-height: 68px;
  padding: 9px 10px 9px 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 22px;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.12), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.035));
  box-shadow: 0 20px 55px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(18px);
}

.headerBar::after {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: 21px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.04), transparent);
  pointer-events: none;
}

.brand,
.desktopNav,
.headerActions {
  position: relative;
  z-index: 1;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  min-width: max-content;
  color: rgba(255, 255, 255, 0.95);
  text-decoration: none;
}

.brand:hover {
  text-decoration: none;
}

.brandMark {
  display: inline-grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 13px;
  color: rgba(255, 255, 255, 0.96);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.30), rgba(195, 90, 214, 0.24)),
    rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(110, 229, 255, 0.24);
  box-shadow: 0 12px 30px rgba(110, 229, 255, 0.10);
  font-size: 0.72rem;
  font-weight: 950;
}

.brandText {
  font-weight: 900;
  letter-spacing: 0;
}

.desktopNav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex: 1;
  min-width: 0;
  margin-inline-start: var(--s-8);
}

.navLink,
.sheetLink,
.bottomLink {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid transparent;
  color: rgba(255, 255, 255, 0.66);
  text-decoration: none;
  transition:
    transform 140ms ease,
    background 140ms ease,
    border-color 140ms ease,
    color 140ms ease;
}

.navLink {
  min-height: 42px;
  padding: 9px 11px;
  border-radius: 15px;
  font-size: 0.86rem;
  font-weight: 800;
  white-space: nowrap;
}

.navLink:hover,
.sheetLink:hover,
.bottomLink:hover {
  color: rgba(255, 255, 255, 0.94);
  text-decoration: none;
  background: rgba(255, 255, 255, 0.065);
}

.navLink:focus-visible,
.sheetLink:focus-visible,
.bottomLink:focus-visible,
.brand:focus-visible,
.menuButton:focus-visible {
  outline: none;
  box-shadow: var(--focus);
}

.navLink.active,
.sheetLink.active,
.bottomLink.active {
  color: rgba(255, 255, 255, 0.96);
  border-color: rgba(110, 229, 255, 0.24);
  background:
    linear-gradient(135deg, rgba(110, 229, 255, 0.14), rgba(195, 90, 214, 0.10)),
    rgba(255, 255, 255, 0.055);
}

.navLink.hinted::after,
.sheetLink.hinted::after,
.bottomLink.hinted::after {
  content: "";
  position: absolute;
  width: 7px;
  height: 7px;
  inset-block-start: 7px;
  inset-inline-end: 7px;
  border-radius: 999px;
  background: #f7d774;
  box-shadow: 0 0 18px rgba(247, 215, 116, 0.52);
}

.navIcon {
  display: inline-grid;
  place-items: center;
  width: 24px;
  height: 24px;
  flex: 0 0 auto;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.80);
  background: rgba(255, 255, 255, 0.055);
}

.navIcon::before {
  content: "";
  width: 11px;
  height: 11px;
  border: 1.5px solid currentColor;
  border-radius: 4px;
}

.navIcon[data-icon="dashboard"]::before {
  border-radius: 3px;
  box-shadow: 8px 0 0 -5px currentColor, 0 8px 0 -5px currentColor;
}

.navIcon[data-icon="challenges"]::before {
  border-radius: 999px;
  box-shadow: inset 0 0 0 3px rgba(110, 229, 255, 0.18);
}

.navIcon[data-icon="leaderboard"]::before {
  width: 13px;
  height: 10px;
  border-top: 0;
  border-radius: 2px;
  box-shadow: inset 4px 0 0 rgba(255, 255, 255, 0.18), inset -4px 0 0 rgba(255, 255, 255, 0.18);
}

.navIcon[data-icon="activity"]::before {
  width: 14px;
  height: 8px;
  border-inline-start: 0;
  border-inline-end: 0;
  border-radius: 0;
  transform: skewX(-18deg);
}

.navIcon[data-icon="profile"]::before {
  border-radius: 999px;
  box-shadow: 0 9px 0 -4px currentColor;
}

.navIcon[data-icon="settings"]::before {
  border-radius: 999px;
  box-shadow: inset 0 0 0 3px rgba(195, 90, 214, 0.20);
}

.navBadge,
.bottomBadge {
  display: inline-grid;
  place-items: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  color: #101217;
  background: #f7d774;
  font-size: 0.68rem;
  font-weight: 950;
}

.headerActions {
  display: inline-flex;
  align-items: center;
  gap: var(--s-8);
  margin-inline-start: auto;
}

.menuButton {
  display: none;
  place-items: center;
  width: 40px;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.055);
  color: rgba(255, 255, 255, 0.92);
  cursor: pointer;
}

.menuButton span {
  grid-area: 1 / 1;
  width: 16px;
  height: 2px;
  border-radius: 999px;
  background: currentColor;
  transition: transform 160ms ease;
}

.menuButton span:first-child {
  transform: translateY(-4px);
}

.menuButton span:last-child {
  transform: translateY(4px);
}

.menuButton[aria-expanded="true"] span:first-child {
  transform: rotate(45deg);
}

.menuButton[aria-expanded="true"] span:last-child {
  transform: rotate(-45deg);
}

.mobileSheet {
  display: none;
}

.mobileBottomNav {
  display: none;
}

.navSheet-enter-active,
.navSheet-leave-active {
  transition: opacity 150ms ease, transform 150ms ease;
}

.navSheet-enter-from,
.navSheet-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 980px) {
  .desktopNav {
    display: none;
  }

  .menuButton {
    display: grid;
  }

  .mobileSheet {
    position: absolute;
    inset-inline: 0;
    display: grid;
    gap: 6px;
    margin-top: var(--s-8);
    padding: 8px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 22px;
    background:
      radial-gradient(circle at 100% 0%, rgba(195, 90, 214, 0.14), transparent 34%),
      rgba(12, 14, 20, 0.94);
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
    backdrop-filter: blur(18px);
  }

  .sheetLink {
    min-height: 58px;
    justify-content: flex-start;
    padding: 10px 12px;
    border-radius: 16px;
  }

  .sheetLink > span:nth-child(2) {
    display: grid;
    gap: 1px;
    min-width: 0;
  }

  .sheetLink strong {
    font-size: 0.92rem;
    font-weight: 900;
  }

  .sheetLink small {
    color: rgba(255, 255, 255, 0.52);
    font-size: 0.76rem;
    line-height: 1.35;
  }
}

@media (max-width: 720px) {
  .appHeader {
    top: 8px;
  }

  .headerBar {
    min-height: 62px;
    border-radius: 20px;
  }

  .brandText {
    max-width: 128px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .mobileBottomNav {
    position: fixed;
    z-index: 28;
    inset-inline: max(10px, env(safe-area-inset-left)) max(10px, env(safe-area-inset-right));
    inset-block-end: max(10px, env(safe-area-inset-bottom));
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 4px;
    padding: 6px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 22px;
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.085), rgba(255, 255, 255, 0.045)),
      rgba(10, 12, 18, 0.90);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.40);
    backdrop-filter: blur(18px);
  }

  .bottomLink {
    justify-content: center;
    min-width: 0;
    min-height: 54px;
    padding: 7px 5px;
    border-radius: 17px;
    flex-direction: column;
    gap: 3px;
    font-size: 0.68rem;
    font-weight: 850;
  }

  .bottomLink .navIcon {
    width: 25px;
    height: 22px;
  }

  :global(body) {
    padding-bottom: 84px;
  }
}

@media (max-width: 430px) {
  .headerActions {
    gap: 6px;
  }

  .brandText {
    max-width: 108px;
  }
}
</style>
