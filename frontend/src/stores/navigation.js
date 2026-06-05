import { defineStore } from "pinia";

const NAV_KEYS = Object.freeze([
  "dashboard",
  "challenges",
  "leaderboard",
  "activity",
  "profile",
  "settings",
]);

function clampBadge(value) {
  const count = Number(value);
  return Number.isFinite(count) ? Math.max(0, Math.floor(count)) : 0;
}

export const useNavigationStore = defineStore("navigation", {
  state: () => ({
    badges: NAV_KEYS.reduce((result, key) => {
      result[key] = 0;
      return result;
    }, {}),
    unlockHints: [],
    nextStepKey: "",
  }),

  getters: {
    badgeFor: (state) => (key) => clampBadge(state.badges[key]),
    hasUnlockHint: (state) => (key) => state.unlockHints.includes(key),
    hasNextStep: (state) => Boolean(state.nextStepKey),
  },

  actions: {
    setBadge(key, value) {
      if (!NAV_KEYS.includes(key)) return;
      this.badges[key] = clampBadge(value);
    },

    clearBadge(key) {
      if (!NAV_KEYS.includes(key)) return;
      this.badges[key] = 0;
    },

    setUnlockHints(keys = []) {
      this.unlockHints = keys.filter((key) => NAV_KEYS.includes(key));
    },

    clearUnlockHint(key) {
      this.unlockHints = this.unlockHints.filter((item) => item !== key);
    },

    setNextStep(key) {
      this.nextStepKey = NAV_KEYS.includes(key) ? key : "";
    },
  },
});
