import { useAuthApi } from "@/api/auth.api";
import { useAuthStore } from "@/stores/auth.store";
import { useNotifications } from "@/composables/useNotifications";

class AuthTokenService {
  constructor() {
    this.refreshTimer = null;
    this.refreshing = false;
    this.initialized = false;
    this.refreshInProgress = false;
    this.refreshQueue = [];
    
    // Default refresh at 75% of token lifetime
    this.REFRESH_PERCENTAGE = 75;
    
    // Minimum time before refresh (15 seconds)
    this.MIN_REFRESH_TIME = 15 * 1000;
    
    // Maximum time before refresh (30 minutes)
    this.MAX_REFRESH_TIME = 30 * 60 * 1000;
    
    // Time to wait before retrying after a failed refresh (5 seconds)
    this.RETRY_DELAY = 5 * 1000;
    
    // Maximum number of consecutive refresh failures before giving up
    this.MAX_RETRY_COUNT = 3;
    this.retryCount = 0;
  }

  init() {
    if (this.initialized) return;
    
    const authStore = useAuthStore();
    
    if (authStore.hasValidAuthState) {
      this.startRefreshTimer();
    }
    
    // Listen for visibility changes to handle browser tab becoming active
    document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    
    // Set up cleanup for when app is closed
    window.addEventListener('beforeunload', this.cleanup.bind(this));
    
    this.initialized = true;
    console.log("Auth token service initialized");
  }

  // Handle visibility change (tab focus/blur)
  handleVisibilityChange() {
    if (document.visibilityState === 'visible') {
      const authStore = useAuthStore();
      if (authStore.isAuthenticated) {
        // User came back to the tab, verify auth state
        this.checkAndRefreshToken();
      }
    }
  }

  // Calculate when to refresh based on percentage of token lifetime
  calculateRefreshTime() {
    const authStore = useAuthStore();
    if (!authStore.hasValidAuthState) return null;
    
    // Get total token lifespan and remaining time
    const totalLifespanSeconds = authStore.tokenTotalLifespan;
    const remainingSeconds = authStore.tokenRemainingSeconds;
    
    if (totalLifespanSeconds <= 0 || remainingSeconds <= 0) {
      return 0; // Refresh immediately
    }
    
    // Calculate elapsed percentage
    const elapsedPercentage = ((totalLifespanSeconds - remainingSeconds) / totalLifespanSeconds) * 100;
    
    // If the refresh threshold already passed
    if (elapsedPercentage >= this.REFRESH_PERCENTAGE) {
      return 0; // Refresh immediately
    }
    
    // Calculate time until refresh threshold is reached
    const percentageRemaining = this.REFRESH_PERCENTAGE - elapsedPercentage;
    const secondsUntilRefresh = (percentageRemaining / 100) * totalLifespanSeconds;
    const millisecondsUntilRefresh = secondsUntilRefresh * 1000;
    
    // Apply min/max constraints
    return Math.max(
      this.MIN_REFRESH_TIME,
      Math.min(millisecondsUntilRefresh, this.MAX_REFRESH_TIME)
    );
  }

  // Start timer for token refresh
  startRefreshTimer() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
    
    const authStore = useAuthStore();
    if (!authStore.hasValidAuthState) return;
    
    // If refresh token is expired, can't refresh anymore
    if (authStore.isRefreshTokenExpired) {
      console.log("Refresh token expired, cannot schedule refresh");
      return;
    }
    
    // If token is already expired or close to expiration, refresh immediately
    if (authStore.isTokenExpired) {
      this.refreshToken();
      return;
    }
    
    const refreshTime = this.calculateRefreshTime();
    
    // If refresh time is very small, refresh immediately
    if (!refreshTime || refreshTime <= 1000) {
      this.refreshToken();
      return;
    }
    
    this.refreshTimer = setTimeout(() => {
      this.refreshToken();
    }, refreshTime);
    
    // const minutesUntilRefresh = Math.round(refreshTime / 60000);
    // console.log(`Token refresh scheduled in ${minutesUntilRefresh} ${minutesUntilRefresh === 1 ? 'minute' : 'minutes'} ` +
    //             `(${this.REFRESH_PERCENTAGE}% of token lifetime)`);
  }

  // Stop refresh timer
  stopRefreshTimer() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
      console.log("Token refresh timer stopped");
    }
  }

  // Check if token needs refresh and do it if needed
  async checkAndRefreshToken() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return false;
    
    // Check if refresh token is expired
    if (authStore.isRefreshTokenExpired) {
      const notifications = useNotifications();
      authStore.clearAuth();
      notifications.error("Your refresh token has expired. Please login again.");
      return false;
    }
    
    // If token is revoked, don't attempt refresh
    if (authStore.tokenRevoked) {
      return false;
    }
    
    // If token is expired or close to expiration, refresh immediately
    if (authStore.isTokenExpired) {
      return await this.refreshToken();
    }
    
    // Calculate token life percentage
    const tokenPercentage = authStore.tokenLifePercentage;
    
    // If token has exceeded the refresh percentage threshold, refresh it
    if (tokenPercentage >= this.REFRESH_PERCENTAGE) {
      return await this.refreshToken();
    }
    
    // Token is still valid, just make sure timer is set correctly
    this.startRefreshTimer();
    return true;
  }

  // Set the percentage of token lifetime at which to refresh
  setRefreshPercentage(percentage) {
    if (percentage < 10 || percentage > 90) {
      console.warn("Refresh percentage must be between 10 and 90, defaulting to 75");
      this.REFRESH_PERCENTAGE = 75;
    } else {
      this.REFRESH_PERCENTAGE = percentage;
      console.log(`Token refresh percentage set to ${percentage}%`);
    }
    
    // Restart timer with new percentage if authenticated
    const authStore = useAuthStore();
    if (authStore.hasValidAuthState) {
      this.startRefreshTimer();
    }
  }

  // Return a promise that resolves when refresh is complete
  waitForRefresh() {
    if (!this.refreshInProgress) {
      return Promise.resolve(true);
    }
    
    return new Promise((resolve) => {
      this.refreshQueue.push(resolve);
    });
  }

  // Process the queue of waiting callbacks
  processRefreshQueue(success) {
    const queue = this.refreshQueue;
    this.refreshQueue = [];
    queue.forEach(resolve => resolve(success));
  }

  // Refresh the token
  async refreshToken() {
    const authStore = useAuthStore();
    
    // Don't refresh if not authenticated
    if (!authStore.isAuthenticated) return false;
    
    // Don't refresh if token is revoked
    if (authStore.tokenRevoked) return false;
    
    // Check if refresh token is expired
    if (authStore.isRefreshTokenExpired) {
      const notifications = useNotifications();
      authStore.clearAuth();
      notifications.error("Your refresh token has expired. Please login again.");
      return false;
    }
    
    // If a refresh is already in progress, wait for it to complete
    if (this.refreshInProgress) {
      return await this.waitForRefresh();
    }
    
    try {
      this.refreshInProgress = true;
      const { refreshToken } = useAuthApi();
      
      console.log("Refreshing token...");
      const success = await refreshToken();
      
      if (success) {
        // Reset retry counter on success
        this.retryCount = 0;
        // Set up next refresh based on new expiration time
        this.startRefreshTimer();
        this.processRefreshQueue(true);
        return true;
      } else {
        this.handleRefreshFailure();
        this.processRefreshQueue(false);
        return false;
      }
    } catch (error) {
      console.error("Error refreshing token:", error);
      this.handleRefreshFailure();
      this.processRefreshQueue(false);
      return false;
    } finally {
      this.refreshInProgress = false;
    }
  }
  
  // Handle refresh failures with retry logic
  handleRefreshFailure() {
    const authStore = useAuthStore();
    this.retryCount++;
    
    // If max retries haven't exceeded and the refresh token isn't expired
    if (this.retryCount < this.MAX_RETRY_COUNT && !authStore.isRefreshTokenExpired) {
      console.log(`Token refresh failed, retrying in ${this.RETRY_DELAY/1000} seconds (attempt ${this.retryCount}/${this.MAX_RETRY_COUNT})`);
      
      // Schedule a retry
      setTimeout(() => {
        if (authStore.isAuthenticated && !authStore.tokenRevoked) {
          this.refreshToken();
        }
      }, this.RETRY_DELAY);
    } else {
      // If max retries have exceeded  or refresh token is expired
      console.log("Max token refresh attempts exceeded or refresh token expired");
      const notifications = useNotifications();
      authStore.clearAuth();
      notifications.error("Your session has expired. Please login again.");
    }
  }

  // Handle authentication state change
  handleAuthChange(isAuthenticated) {
    if (isAuthenticated) {
      // Reset retry counter on new login
      this.retryCount = 0;
      this.startRefreshTimer();
    } else {
      this.stopRefreshTimer();
    }
  }

  // Clean up resources
  cleanup() {
    this.stopRefreshTimer();
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    window.removeEventListener('beforeunload', this.cleanup);
    this.initialized = false;
  }
}

// Create a singleton instance
const authTokenService = new AuthTokenService();

export default authTokenService;
