import { defineStore } from "pinia";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
  }),
  actions: {
    setToken(token) {
      this.token = token;
    },
    clearToken() {
      this.token = null;
    },
  },
});
