import { useAuthApi } from "@/api/auth.api";
import { useAuthStore } from "@/stores/auth.store";

type RefreshResolveFn = (_value: boolean) => void;

class AuthTokenService {
  private refreshTimer: ReturnType<typeof setTimeout> | null = null;
  private initialized: boolean = false;
  private refreshInProgress: boolean = false;
  private refreshQueue: RefreshResolveFn[] = [];

  private REFRESH_PERCENTAGE: number = 75;
  private MIN_REFRESH_TIME: number = 15 * 1000;
  private MAX_REFRESH_TIME: number = 30 * 60 * 1000;
  private RETRY_DELAY: number = 5 * 1000;
  private MAX_RETRY_COUNT: number = 3;
  private retryCount: number = 0;

  // Add event emitter for auth state changes
  private authStateListeners: ((isAuthenticated: boolean, error?: string) => void)[] = [];

  onAuthStateChange(callback: (isAuthenticated: boolean, error?: string) => void): void {
    this.authStateListeners.push(callback);
  }

  private notifyAuthStateChange(isAuthenticated: boolean, error?: string): void {
    this.authStateListeners.forEach(callback => callback(isAuthenticated, error));
  }

  init(): void {
    if (this.initialized) return;

    const authStore = useAuthStore();
    if (authStore.hasValidAuthState) {
      this.startRefreshTimer();
    }

    document.addEventListener("visibilitychange", this.handleVisibilityChange.bind(this));
    window.addEventListener("beforeunload", this.cleanup.bind(this));

    this.initialized = true;
    console.log("Auth token service initialized");
  }

  private handleVisibilityChange(): void {
    if (document.visibilityState === "visible") {
      const authStore = useAuthStore();
      if (authStore.isAuthenticated) {
        this.checkAndRefreshToken();
      }
    }
  }

  private calculateRefreshTime(): number | null {
    const authStore = useAuthStore();
    if (!authStore.hasValidAuthState) return null;

    const totalLifespan = authStore.tokenTotalLifespan;
    const remaining = authStore.tokenRemainingSeconds;

    if (totalLifespan <= 0 || remaining <= 0) return 0;

    const elapsedPercentage = ((totalLifespan - remaining) / totalLifespan) * 100;

    if (elapsedPercentage >= this.REFRESH_PERCENTAGE) return 0;

    const percentageRemaining = this.REFRESH_PERCENTAGE - elapsedPercentage;
    const secondsUntilRefresh = (percentageRemaining / 100) * totalLifespan;
    const msUntilRefresh = secondsUntilRefresh * 1000;

    return Math.max(this.MIN_REFRESH_TIME, Math.min(msUntilRefresh, this.MAX_REFRESH_TIME));
  }

  private startRefreshTimer(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }

    const authStore = useAuthStore();
    if (!authStore.hasValidAuthState) return;
    if (authStore.isRefreshTokenExpired) {
      console.log("Refresh token expired, cannot schedule refresh");
      this.handleSessionExpired();
      return;
    }

    if (authStore.isTokenExpired) {
      this.refreshToken();
      return;
    }

    const refreshTime = this.calculateRefreshTime();

    if (!refreshTime || refreshTime <= 1000) {
      this.refreshToken();
      return;
    }

    this.refreshTimer = setTimeout(() => {
      this.refreshToken();
    }, refreshTime);
  }

  private stopRefreshTimer(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
      console.log("Token refresh timer stopped");
    }
  }

  async checkAndRefreshToken(): Promise<boolean> {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return false;

    if (authStore.isRefreshTokenExpired) {
      this.handleSessionExpired();
      return false;
    }

    if (authStore.tokenRevoked) return false;

    if (authStore.isTokenExpired) {
      return await this.refreshToken();
    }

    if (authStore.tokenLifePercentage >= this.REFRESH_PERCENTAGE) {
      return await this.refreshToken();
    }

    this.startRefreshTimer();
    return true;
  }

  private handleSessionExpired(): void {
    const authStore = useAuthStore();
    console.log("Session expired, clearing auth state");
    authStore.clearAuth();
    this.notifyAuthStateChange(false, "Your session has expired. Please log in again.");
  }

  setRefreshPercentage(percentage: number): void {
    if (percentage < 10 || percentage > 90) {
      console.warn("Refresh percentage must be between 10 and 90, defaulting to 75");
      this.REFRESH_PERCENTAGE = 75;
    } else {
      this.REFRESH_PERCENTAGE = percentage;
      console.log(`Token refresh percentage set to ${percentage}%`);
    }

    const authStore = useAuthStore();
    if (authStore.hasValidAuthState) {
      this.startRefreshTimer();
    }
  }

  waitForRefresh(): Promise<boolean> {
    if (!this.refreshInProgress) {
      return Promise.resolve(true);
    }

    return new Promise((resolve) => {
      this.refreshQueue.push(resolve);
    });
  }

  private processRefreshQueue(success: boolean): void {
    const queue = this.refreshQueue;
    this.refreshQueue = [];
    queue.forEach((resolve) => resolve(success));
  }

  async refreshToken(): Promise<boolean> {
    const authStore = useAuthStore();

    if (!authStore.isAuthenticated || authStore.tokenRevoked || authStore.isRefreshTokenExpired) {
      this.handleSessionExpired();
      return false;
    }

    if (this.refreshInProgress) {
      return await this.waitForRefresh();
    }

    try {
      this.refreshInProgress = true;
      const { refreshToken } = useAuthApi();

      console.log("Refreshing token...");
      const success = await refreshToken();

      if (success) {
        this.retryCount = 0;
        this.startRefreshTimer();
        this.processRefreshQueue(true);
        this.notifyAuthStateChange(true);
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

  private handleRefreshFailure(): void {
    const authStore = useAuthStore();
    this.retryCount++;

    if (this.retryCount < this.MAX_RETRY_COUNT && !authStore.isRefreshTokenExpired) {
      console.log(
        `Token refresh failed, retrying in ${this.RETRY_DELAY / 1000} seconds (attempt ${this.retryCount}/${this.MAX_RETRY_COUNT})`
      );

      setTimeout(() => {
        if (authStore.isAuthenticated && !authStore.tokenRevoked) {
          this.refreshToken();
        }
      }, this.RETRY_DELAY);
    } else {
      console.log("Max token refresh attempts exceeded or refresh token expired");
      this.handleSessionExpired();
    }
  }

  handleAuthChange(isAuthenticated: boolean): void {
    if (isAuthenticated) {
      this.retryCount = 0;
      this.startRefreshTimer();
      this.notifyAuthStateChange(true);
    } else {
      this.stopRefreshTimer();
      this.notifyAuthStateChange(false);
    }
  }

  cleanup(): void {
    this.stopRefreshTimer();
    document.removeEventListener("visibilitychange", this.handleVisibilityChange);
    window.removeEventListener("beforeunload", this.cleanup);
    this.initialized = false;
    this.authStateListeners = [];
  }
}

const authTokenService = new AuthTokenService();
export default authTokenService;
