import { defineStore } from "pinia";
import api from "../lib/api";

export const useSessionStore = defineStore("session", {
  state: () => ({
    me: null,
    bootstrapped: false,
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.me,
  },

  actions: {
    setMe(user) {
      this.me = user || null;
    },

    async bootstrap() {
      this.loading = true;

      try {
        const { data } = await api.get("/me");

        if (data?.ok) {
          this.me = data;
          return true;
        }

        this.me = null;
        return false;
      } catch (error) {
        this.me = null;
        return false;
      } finally {
        this.loading = false;
        this.bootstrapped = true;
      }
    },

    async logout() {
      try {
        await api.post("/auth/logout");
      } catch (error) {
        // Keep logout resilient even if the backend request fails.
      } finally {
        try {
          localStorage.removeItem("ringo_token");
        } catch {
          // Ignore storage failures; the backend cookie clear is the primary logout path.
        }

        this.me = null;
        this.bootstrapped = true;
      }
    },
  },
});
