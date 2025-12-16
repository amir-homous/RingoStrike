import { defineStore } from "pinia";
import api from "../lib/api";

export const useSessionStore = defineStore("session", {
  state: () => ({
    token: localStorage.getItem("token") || "",
    me: null,
  }),
  actions: {
    setToken(t) {
      this.token = t || "";
      if (this.token) localStorage.setItem("token", this.token);
      else localStorage.removeItem("token");
      api.setToken(this.token);
    },
    async bootstrap() {
      try {
        api.setToken(this.token);
        const { data } = await api.get("/me");
        if (data?.ok) {
          this.me = data;
          return true;
        }
        return false;
      } catch (e) {
        return false;
      }
    },
    logout() {
      this.setToken("");
      this.me = null;
    },
  },
});
