import { defineStore } from 'pinia';
import type { User } from '@/types';

// Grace period in seconds for token expiration checks
const TOKEN_EXPIRATION_GRACE_PERIOD = 30;

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  tokenExpiration: number | null;
  tokenIssueTime: number | null;
  refreshTokenExpiration: number | null;
  tokenRevoked: boolean;
}

const persistPaths: (keyof AuthState)[] = [
  'isAuthenticated',
  'user',
  'tokenExpiration',
  'tokenIssueTime',
  'refreshTokenExpiration',
  'tokenRevoked',
];


export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    isAuthenticated: false,
    user: null,
    tokenExpiration: null,
    tokenIssueTime: null,
    refreshTokenExpiration: null,
    tokenRevoked: false,
  }),

  getters: {
    currentUser: (state): User | null => state.user,

    isTokenExpired: (state): boolean => {
      if (!state.tokenExpiration) return true;
      const currentTime = Math.floor(Date.now() / 1000);
      return currentTime >= state.tokenExpiration - TOKEN_EXPIRATION_GRACE_PERIOD;
    },

    isRefreshTokenExpired: (state): boolean => {
      if (!state.refreshTokenExpiration) return true;
      const currentTime = Math.floor(Date.now() / 1000);
      return currentTime >= state.refreshTokenExpiration;
    },

    tokenLifePercentage: (state): number => {
      if (!state.tokenExpiration || !state.tokenIssueTime) return 100;
      const currentTime = Math.floor(Date.now() / 1000);
      const totalLifespan = state.tokenExpiration - state.tokenIssueTime;
      if (totalLifespan <= 0) return 100;
      const elapsed = currentTime - state.tokenIssueTime;
      return Math.max(0, Math.min(100, (elapsed / totalLifespan) * 100));
    },

    tokenRemainingSeconds: (state): number => {
      if (!state.tokenExpiration) return 0;
      const currentTime = Math.floor(Date.now() / 1000);
      return Math.max(0, state.tokenExpiration - currentTime);
    },

    tokenTotalLifespan: (state): number => {
      if (!state.tokenExpiration || !state.tokenIssueTime) return 0;
      return Math.max(0, state.tokenExpiration - state.tokenIssueTime);
    },

    hasValidAuthState(): boolean {
      if (
        !this.isAuthenticated ||
        !this.user ||
        !this.tokenExpiration ||
        this.tokenRevoked
      ) {
        return false;
      }

      return !this.isTokenExpired;
    },
  },

  actions: {
    setAuthenticated(status: boolean) {
      this.isAuthenticated = status;
    },

    setUser(user: User | null) {
      this.user = user;
    },

    setTokenExpiration(exp: number) {
      this.tokenExpiration = exp;
      this.tokenIssueTime = Math.floor(Date.now() / 1000);
    },

    setRefreshTokenExpiration(exp: number) {
      this.refreshTokenExpiration = exp;
    },

    markTokenRevoked() {
      this.tokenRevoked = true;
    },

    resetTokenRevoked() {
      this.tokenRevoked = false;
    },

    clearAuth() {
      this.isAuthenticated = false;
      this.user = null;
      this.tokenExpiration = null;
      this.tokenIssueTime = null;
      this.refreshTokenExpiration = null;
      this.tokenRevoked = false;
    },

    initialize() {
      if (
        this.isAuthenticated &&
        (this.isTokenExpired || this.isRefreshTokenExpired || this.tokenRevoked)
      ) {
        console.log('Auth state invalid during initialization, clearing auth');
        this.clearAuth();
      }
    }
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'auth',
        storage: localStorage,
        paths: persistPaths,
      },
    ],
  },
});
