import { apolloClient } from "./apollo.client";
import { useAuthStore } from "../stores/auth.store";
import { useNotifications } from "@/composables/useNotifications";
import { useApiWrapper } from "@/composables/api.wrapper";

import {
  LOGIN_MUTATION,
  REFRESH_TOKEN_MUTATION,
  REGISTER_MUTATION,
  LOGOUT_MUTATION
} from "./graphql/auth.mutations";

export function useAuthApi() {
  const authStore = useAuthStore();
  const notifications = useNotifications();
  const apiWrapper = useApiWrapper();

  // Helper function to validate JWT payload
  function validateTokenPayload(payload) {
    if (!payload) {
      console.error("Token payload is missing");
      return false;
    }

    // Check for required JWT fields
    if (!payload.exp) {
      console.error("Token payload missing expiration");
      return false;
    }
    
    // Ensure exp is in the future with a reasonable window
    const now = Math.floor(Date.now() / 1000);
    if (payload.exp <= now + 30) { // At least 30 seconds in the future
      console.error("Token expiration too close or already expired");
      return false;
    }

    // Ensure the token has a reasonable lifespan (at least 30 seconds)
    if (payload.origIat && (payload.exp - payload.origIat < 30)) {
      console.error("Token lifespan too short");
      return false;
    }

    return true;
  }

  async function login(email, password) {
    authStore.resetTokenRevoked();
    
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: LOGIN_MUTATION,
          variables: { email, password },
        }),
        { suppressNotifications: false}
      );

      if (!response?.data?.tokenAuth?.success) {
        notifications.error('Login failed. Please check your credentials.');
        return false;
      }

      // Extract payload and user data from response
      const { payload, refreshExpiresIn, user } = response.data.tokenAuth;
      
      if (!validateTokenPayload(payload)) {
        notifications.error('Authentication token is invalid or has too short a lifespan');
        return false;
      }
      
      if (!user?.id) {
        notifications.error('User information is incomplete');
        return false;
      }
      
      // Set auth state
      authStore.setTokenExpiration(payload.exp);
      if (refreshExpiresIn) {
        authStore.setRefreshTokenExpiration(refreshExpiresIn);
      }
      authStore.setAuthenticated(true);
      authStore.setUser(user);
      
      // Log token lifespan for debugging
      const lifespan = payload.exp - Math.floor(Date.now() / 1000);
      console.log(`Token lifespan: ${lifespan} seconds`);
      
      return true;
    } catch (error) {
      console.error("Login error:", error);
      // Don't show notification here as apiWrapper already did
      return false;
    }
  }

  async function refreshToken() {
    // Don't attempt refresh if token has been revoked
    if (authStore.tokenRevoked) {
      console.log("Token was revoked, skipping refresh");
      return false;
    }
    
    try {
      // Check if refresh token is expired
      if (authStore.isRefreshTokenExpired) {
        console.log("Refresh token expired, cannot refresh");
        return false;
      }

      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: REFRESH_TOKEN_MUTATION,
          fetchPolicy: 'no-cache' // Always get a fresh token from server
        }),
        { suppressNotifications: false}
      );
      
      if (!response?.data?.refreshToken?.payload) {
        console.error("Token refresh failed: missing payload");
        return false;
      }
      
      const { payload, refreshExpiresIn } = response.data.refreshToken;
      
      if (!validateTokenPayload(payload)) {
        console.error("Token refresh failed: invalid payload");
        return false;
      }
      
      // Update token expiration times
      authStore.setTokenExpiration(payload.exp);
      if (refreshExpiresIn) {
        authStore.setRefreshTokenExpiration(refreshExpiresIn);
      }
      
      // Log token lifespan for debugging
      const lifespan = payload.exp - Math.floor(Date.now() / 1000);
      console.log(`New token lifespan: ${lifespan} seconds`);
      
      return true;
    } catch (error) {
      // Special handling for expired signatures
      if (error.message?.includes('Signature has expired')) {
        console.error("Token refresh failed: Signature has expired");
        // Mark auth as invalid immediately
        authStore.clearAuth();
        notifications.error("Your session has expired. Please login again.");
      } else {
        console.error("Error refreshing token:", error?.message || error);
      }
      return false;
    }
  }

  async function registerUser(username, name, email, password1, password2) {
    try {
      if (password1 !== password2) {
        notifications.error("Passwords do not match");
        return false;
      }
  
      const registerResponse = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: REGISTER_MUTATION,
          variables: { username, name, email, password1, password2 },
        }),
        { suppressNotifications: false}
      );
      
      if (!registerResponse?.data?.registerUser?.success) {
        notifications.error('Registration failed');
        return false;
      }
      
      // Auto-login after registration
      return await login(email, password1);
    } catch (error) {
      console.error("Registration error:", error);
      return false;
    }
  }

  async function logout() {
    try {
      // Mark token as revoked to prevent refresh attempts during logout
      authStore.markTokenRevoked();
      
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: LOGOUT_MUTATION
        }),
        { suppressNotifications: false}
      );

      // Always clear client-side auth state
      authStore.clearAuth();
      await apolloClient.clearStore();
      
      if (!response?.data?.deleteToken?.deleted) {
        console.warn("Server logout may not have completed successfully");
      }
      return true;
    } catch (error) {
      console.error("Error during logout:", error?.message || error);
      // Still clear local auth even if server request fails
      authStore.clearAuth();
      await apolloClient.clearStore();
      notifications.error('Logout completed with errors');
      return true; // Return true because we've logged out locally regardless
    }
  }

  async function verifyAuthState() {
    // Check if auth store has valid state
    if (!authStore.hasValidAuthState) {
      console.log("Auth state is invalid, clearing");
      authStore.clearAuth();
      return false;
    }
    
    // If token is near expiration, try to refresh
    if (authStore.isTokenExpired && !authStore.isRefreshTokenExpired) {
      console.log("Auth token near expiration, attempting refresh");
      return await refreshToken();
    }
    
    return true;
  }

  return {
    login,
    registerUser,
    logout,
    refreshToken,
    verifyAuthState
  };
}