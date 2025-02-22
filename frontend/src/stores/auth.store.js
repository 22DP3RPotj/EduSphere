import { defineStore } from "pinia";
import { apolloClient } from "@/api/apollo.client";
import { gql } from "@apollo/client/core";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: null,
  }),
  getters: {
    currentUser: (state) => state.user,
    isAuthenticated: (state) => !!state.token
  },
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem("token", token);
      this.fetchUser();
    },
    clearToken() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
    },
    async fetchUser() {
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
        });
        this.user = data.me;
      } catch (error) {
        console.error("Failed to fetch user", error);
      }
    },
  },
});