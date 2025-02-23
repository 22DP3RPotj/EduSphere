import { defineStore } from "pinia";
import { apolloClient } from "@/api/apollo.client";
import { gql } from "@apollo/client/core";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: null,
    isLoadingUser: false,
  }),
  getters: {
    currentUser: (state) => state.user,
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    setToken(token) {
      if (token) {
        localStorage.setItem("token", token);
        this.token = token;
      } else {
        this.clearToken();
      }
    },
    clearToken() {
      localStorage.removeItem("token");
      this.token = null;
      this.user = null;
    },
    async fetchUser() {
      if (!this.token) return;
      this.isLoadingUser = true;
      try {
        const { data } = await apolloClient.query({
          query: gql`
            query GetCurrentUser {
              me {
                id
                username
                email
                name
              }
            }
          `,
          fetchPolicy: "network-only",
        });
        this.user = data.me;
        return data.me;
      } catch (error) {
        console.error("Error fetching user:", error);
        this.clearToken();
        throw error;
      } finally {
        this.isLoadingUser = false;
      }
    },
    async initialize() {
      window.addEventListener("storage", (event) => {
        if (event.key === "token") {
          this.token = event.newValue;
          this.token ? this.fetchUser() : this.clearToken();
        }
      });

      if (this.token && !this.user) {
        await this.fetchUser();
      }
    },
  },
});
