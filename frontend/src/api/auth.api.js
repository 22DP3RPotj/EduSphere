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

  function validateTokenPayload(payload) {
    if (!payload) {
      console.error("Token payload is missing");
      return false;
    }

    if (!payload.exp) {
      console.error("Token payload missing expiration");
      return false;
    }
    
    const now = Math.floor(Date.now() / 1000);
    if (payload.exp <= now + 30) {
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
        { suppressNotifications: false }
      );

      if (!response?.data?.tokenAuth?.success) {
        notifications.error('Login failed. Please check your credentials.');
        return false;
      }

      const { payload, refreshExpiresIn, user } = response.data.tokenAuth;
      
      if (!validateTokenPayload(payload)) {
        notifications.error('Authentication token is invalid or has too short a lifespan');
        return false;
      }
      
      if (!user?.id) {
        notifications.error('User information is incomplete');
        return false;
      }
      
      authStore.setTokenExpiration(payload.exp);
      if (refreshExpiresIn) {
        authStore.setRefreshTokenExpiration(refreshExpiresIn);
      }
      authStore.setAuthenticated(true);
      authStore.setUser(user);
      
      return true;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    }
  }

  async function refreshToken() {
    if (authStore.tokenRevoked) {
      console.log("Token was revoked, skipping refresh");
      return false;
    }
    
    try {
      if (authStore.isRefreshTokenExpired) {
        console.log("Refresh token expired, cannot refresh");
        return false;
      }

      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: REFRESH_TOKEN_MUTATION,
          fetchPolicy: 'no-cache'
        }),
        { suppressNotifications: false }
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
      
      authStore.setTokenExpiration(payload.exp);
      if (refreshExpiresIn) {
        authStore.setRefreshTokenExpiration(refreshExpiresIn);
      }

      return true;
    } catch (error) {
      if (error.message?.includes('Signature has expired')) {
        console.error("Token refresh failed: Signature has expired");
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
        { suppressNotifications: false }
      );
      
      if (!registerResponse?.data?.registerUser?.success) {
        notifications.error('Registration failed');
        return false;
      }
      
      return await login(email, password1);
    } catch (error) {
      console.error("Registration error:", error);
      return false;
    }
  }

  async function logout() {
    try {
      authStore.markTokenRevoked();
      
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: LOGOUT_MUTATION
        }),
        { suppressNotifications: false }
      );

      authStore.clearAuth();
      await apolloClient.clearStore();
      
      if (!response?.data?.deleteToken?.deleted) {
        console.warn("Server logout may not have completed successfully");
      }
      return true;
    } catch (error) {
      console.error("Error during logout:", error?.message || error);
      authStore.clearAuth();
      await apolloClient.clearStore();
      notifications.error('Logout completed with errors');
      return true; // Return true because logged out locally regardless
    }
  }

  async function verifyAuthState() {
    if (!authStore.hasValidAuthState) {
      console.log("Auth state is invalid, clearing");
      authStore.clearAuth();
      return false;
    }
    
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