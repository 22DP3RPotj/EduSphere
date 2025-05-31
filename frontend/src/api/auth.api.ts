import { apolloClient } from "./apollo.client";
import { useAuthStore } from "../stores/auth.store";
import { useNotifications } from "@/composables/useNotifications";
import { useApiWrapper } from "@/composables/api.wrapper";

import {
  LOGIN_MUTATION,
  REFRESH_TOKEN_MUTATION,
  REGISTER_MUTATION,
  LOGOUT_MUTATION,
  UPDATE_USER_MUTATION
} from "./graphql/auth.mutations";

import {
  GET_AUTH_STATUS
} from "./graphql/auth.queries";

import type {
  User,
  LoginInput,
  RegisterInput,
  UpdateUserInput,
  AuthPayload,
  RegisterPayload,
  LogoutPayload,
  RefreshTokenPayload,
  AuthStatus
} from "@/types";

interface TokenPayload {
  exp: number;
  origIat?: number;
  [key: string]: unknown;
}

interface LoginResponse {
  data?: {
    tokenAuth?: AuthPayload;
  } | null;
}

interface RegisterResponse {
  data?: {
    registerUser?: RegisterPayload;
  } | null;
}

interface UpdateUserResponse {
  data?: {
    updateUser?: {
      user: User;
    };
  } | null;
}

interface LogoutResponse {
  data?: {
    deleteToken?: LogoutPayload;
  } | null;
}

interface RefreshTokenResponse {
  data?: {
    refreshToken?: RefreshTokenPayload;
  } | null;
}

interface AuthStatusResponse {
  data?: {
    authStatus?: AuthStatus;
  } | null;
}

// Return type for updateUser function
interface UpdateUserResult {
  success: boolean;
  user?: User;
  error?: unknown;
}

export function useAuthApi() {
  const authStore = useAuthStore();
  const notifications = useNotifications();
  const apiWrapper = useApiWrapper();

  function validateTokenPayload(payload: TokenPayload): boolean {
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

  async function login(email: string, password: string): Promise<boolean> {
    authStore.resetTokenRevoked();
    
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<LoginResponse> => apolloClient.mutate({
          mutation: LOGIN_MUTATION,
          variables: { email, password } satisfies LoginInput,
        }),
        { suppressNotifications: false }
      );

      if (!response?.data?.tokenAuth?.success) {
        notifications.error('Login failed. Please check your credentials.');
        return false;
      }

      const { payload, refreshExpiresIn, user } = response.data.tokenAuth;
      
      if (!validateTokenPayload(payload as TokenPayload)) {
        notifications.error('Authentication token is invalid or has too short a lifespan');
        return false;
      }
      
      if (!user?.id) {
        notifications.error('User information is incomplete');
        return false;
      }
      
      authStore.setTokenExpiration((payload as TokenPayload).exp);
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

  async function refreshToken(): Promise<boolean> {
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
        async (): Promise<RefreshTokenResponse> => apolloClient.mutate({
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
      
      if (!validateTokenPayload(payload as TokenPayload)) {
        console.error("Token refresh failed: invalid payload");
        return false;
      }
      
      authStore.setTokenExpiration((payload as TokenPayload).exp);
      if (refreshExpiresIn) {
        authStore.setRefreshTokenExpiration(refreshExpiresIn);
      }

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (errorMessage?.includes('Signature has expired')) {
        console.error("Token refresh failed: Signature has expired");
        authStore.clearAuth();
        notifications.error("Your session has expired. Please login again.");
      } else {
        console.error("Error refreshing token:", errorMessage);
      }
      return false;
    }
  }

  async function registerUser(
    username: string, 
    name: string, 
    email: string, 
    password1: string, 
    password2: string
  ): Promise<boolean> {
    try {
      if (password1 !== password2) {
        notifications.error("Passwords do not match");
        return false;
      }
  
      const registerResponse = await apiWrapper.callApi(
        async (): Promise<RegisterResponse> => apolloClient.mutate({
          mutation: REGISTER_MUTATION,
          variables: { username, name, email, password1, password2 } satisfies RegisterInput,
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

  async function updateUser(data: UpdateUserInput): Promise<UpdateUserResult> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<UpdateUserResponse> => apolloClient.mutate({
          mutation: UPDATE_USER_MUTATION,
          variables: data,
          context: {
            useMultipart: true
          }
        }),
        { suppressNotifications: false }
      );

      if (!response?.data?.updateUser?.user) {
        notifications.error('Failed to update profile');
        return { success: false };
      }

      const updatedUser = response.data.updateUser.user;
      
      authStore.setUser(updatedUser);
      
      return { success: true, user: updatedUser };
    } catch (error) {
      console.error("Update user error:", error);
      return { success: false, error };
    }
  }

  async function logout(): Promise<boolean> {
    try {
      authStore.markTokenRevoked();
      
      const response = await apiWrapper.callApi(
        async (): Promise<LogoutResponse> => apolloClient.mutate({
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
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Error during logout:", errorMessage);
      authStore.clearAuth();
      await apolloClient.clearStore();
      notifications.error('Logout completed with errors');
      return true; // Return true because logged out locally regardless
    }
  }

  async function verifyAuthState(): Promise<boolean> {
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

  async function fetchAuthStatus(): Promise<AuthStatus> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<AuthStatusResponse> => apolloClient.query({
          query: GET_AUTH_STATUS,
          fetchPolicy: 'network-only'
        }),
      );

      return response.data!.authStatus!;
    } catch (error) {
      console.error("Error checking auth status:", error);
      return { isAuthenticated: false, user: null };
    }
  }

  return {
    login,
    registerUser,
    updateUser,
    logout,
    refreshToken,
    verifyAuthState,
    fetchAuthStatus
  };
}