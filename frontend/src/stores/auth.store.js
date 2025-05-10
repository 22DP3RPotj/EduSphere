import { defineStore } from "pinia";

// Grace period in seconds for token expiration checks
const TOKEN_EXPIRATION_GRACE_PERIOD = 30;

export const useAuthStore = defineStore("auth", {
  state: () => ({
    isAuthenticated: false,
    user: null,
    tokenExpiration: null, // JWT token exp claim (in seconds)
    tokenIssueTime: null,  // Time when token was issued/refreshed (in seconds)
    refreshTokenExpiration: null, // When the refresh token expires (in seconds)
    tokenRevoked: false,  // Flag to track if token has been manually revoked
  }),

  getters: {
    currentUser: (state) => state.user,
    
    isTokenExpired: (state) => {
      if (!state.tokenExpiration) return true;
      
      const currentTime = Math.floor(Date.now() / 1000);
      // Subtract grace period from expiration to give buffer time for operations
      return currentTime >= (state.tokenExpiration - TOKEN_EXPIRATION_GRACE_PERIOD);
    },
    
    isRefreshTokenExpired: (state) => {
      if (!state.refreshTokenExpiration) return true;
      
      const currentTime = Math.floor(Date.now() / 1000);
      return currentTime >= state.refreshTokenExpiration;
    },
    
    // Calculate percentage of token life elapsed
    tokenLifePercentage: (state) => {
      if (!state.tokenExpiration || !state.tokenIssueTime) return 100;
      
      const currentTime = Math.floor(Date.now() / 1000);
      const totalLifespan = state.tokenExpiration - state.tokenIssueTime;
      
      if (totalLifespan <= 0) return 100;
      
      const elapsed = currentTime - state.tokenIssueTime;
      const percentage = (elapsed / totalLifespan) * 100;
      
      return Math.max(0, Math.min(100, percentage));
    },
    
    // Calculate remaining token lifetime in seconds
    tokenRemainingSeconds: (state) => {
      if (!state.tokenExpiration) return 0;
      
      const currentTime = Math.floor(Date.now() / 1000);
      const remaining = state.tokenExpiration - currentTime;
      
      return Math.max(0, remaining);
    },
    
    // Calculate total token lifespan in seconds
    tokenTotalLifespan: (state) => {
      if (!state.tokenExpiration || !state.tokenIssueTime) return 0;
      
      return Math.max(0, state.tokenExpiration - state.tokenIssueTime);
    },
    
    // Check if auth state is valid
    hasValidAuthState: (state) => {
      return state.isAuthenticated && 
             state.user && 
             state.tokenExpiration && 
             !state.tokenRevoked &&
             !state.isTokenExpired;
    }
  },

  actions: {
    /**
     * @param {boolean} status
     */
    setAuthenticated(status) {
      this.isAuthenticated = status;
    },

     /**
     * @param {object|null} user
     */
    setUser(user) {
      this.user = user;
    },

    /**
     * @param {number} exp
     */
    setTokenExpiration(exp) {
      this.tokenExpiration = exp;
      // Store the issue time when setting expiration
      this.tokenIssueTime = Math.floor(Date.now() / 1000);
    },
    
    /**
     * @param {number} exp
     */
    setRefreshTokenExpiration(exp) {
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
      // Check if stored auth state is valid
      if (this.isAuthenticated) {
        // Check if token is expired or refresh token is expired
        if (this.isTokenExpired || this.isRefreshTokenExpired || this.tokenRevoked) {
          console.log("Auth state invalid during initialization, clearing auth");
          this.clearAuth();
        }
      }
    }
  },
  
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'auth',
        storage: localStorage,
        paths: [
          'isAuthenticated', 
          'user', 
          'tokenExpiration', 
          'tokenIssueTime',
          'refreshTokenExpiration',
          'tokenRevoked'
        ]
      }
    ]
  }
});