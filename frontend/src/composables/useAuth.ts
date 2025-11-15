import { computed } from "vue"
import { useMutation, useQuery } from "@vue/apollo-composable"
import { useAuthStore } from "@/stores/auth.store"

import {
  LOGIN_MUTATION,
  REFRESH_TOKEN_MUTATION,
  REGISTER_MUTATION,
  LOGOUT_MUTATION,
  UPDATE_USER_MUTATION,
  GET_AUTH_STATUS,
} from "@/api/graphql"

import type { LoginInput, RegisterInput, UpdateUserInput, TokenPayload } from "@/types"
import { parseGraphQLError } from "@/utils/errorParser"

export function useAuth() {
  const authStore = useAuthStore()

  // Login mutation
  const {
    mutate: loginMutate,
    loading: loginLoading,
    error: loginError,
  } = useMutation(LOGIN_MUTATION)

  // Register mutation
  const {
    mutate: registerMutate,
    loading: registerLoading,
    error: registerError,
  } = useMutation(REGISTER_MUTATION)

  // Update user mutation
  const {
    mutate: updateUserMutate,
    loading: updateUserLoading,
    error: updateUserError,
  } = useMutation(UPDATE_USER_MUTATION)

  // Logout mutation
  const { mutate: logoutMutate, loading: logoutLoading, error: logoutError } = useMutation(LOGOUT_MUTATION)

  // Refresh token mutation
  const { mutate: refreshTokenMutate } = useMutation(REFRESH_TOKEN_MUTATION)

  // Auth status query
  const {
    result: authStatusResult,
    loading: authStatusLoading,
    error: authStatusError,
    refetch: refetchAuthStatus,
  } = useQuery(GET_AUTH_STATUS, null, {
    fetchPolicy: "network-only",
    enabled: computed(() => authStore.isAuthenticated),
  })

  function validateTokenPayload(payload: TokenPayload): boolean {
    if (!payload || !payload.exp) {
      return false
    }

    const now = Math.floor(Date.now() / 1000)
    if (payload.exp <= now + 30) {
      return false
    }

    if (payload.origIat && payload.exp - payload.origIat < 30) {
      return false
    }

    return true
  }

  async function login(email: string, password: string) {
    authStore.resetTokenRevoked();

    try {
      const result = await loginMutate({ email, password } satisfies LoginInput);

      if (result?.data?.tokenAuth?.success) {
        const { payload, refreshExpiresIn, user } = result.data.tokenAuth;

        if (!validateTokenPayload(payload as TokenPayload) || !user?.id) {
          return { 
            success: false, 
            error: "Invalid authentication token",
            fieldErrors: {},
            generalErrors: ["Invalid authentication token"]
          };
        }

        authStore.setTokenExpiration((payload as TokenPayload).exp);
        if (refreshExpiresIn) {
          authStore.setRefreshTokenExpiration(refreshExpiresIn);
        }
        authStore.setAuthenticated(true);
        authStore.setUser(user);

        return { success: true };
      }

      return { 
        success: false, 
        error: "Login failed",
        fieldErrors: {},
        generalErrors: ["Login failed"]
      };
    } catch (error) {
      const parsedError = parseGraphQLError(error);
      return {
        success: false,
        error: "Login failed",
        ...parsedError
      };
    }
  }

  async function register(data: RegisterInput) {
    if (data.password1 !== data.password2) {
      return { success: false, error: "Passwords do not match" }
    }

    const result = await registerMutate(data)

    if (result?.data?.registerUser?.success) {
      // Auto-login after registration
      return await login(data.email, data.password1)
    }

    return { success: false, error: "Registration failed" }
  }

  async function updateUser(data: UpdateUserInput) {
    const result = await updateUserMutate(data, {
      context: {
        useMultipart: true,
      },
    })

    if (result?.data?.updateUser?.user) {
      const updatedUser = result.data.updateUser.user
      authStore.setUser(updatedUser)
      return { success: true, user: updatedUser }
    }

    return { success: false, error: "Failed to update profile" }
  }

  async function logout() {
    authStore.markTokenRevoked()

    try {
      await logoutMutate()
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      authStore.clearAuth()
    }

    return { success: true }
  }

  async function refreshToken() {
    if (authStore.tokenRevoked || authStore.isRefreshTokenExpired) {
      return { success: false }
    }

    try {
      const result = await refreshTokenMutate(null, {
        fetchPolicy: "no-cache",
      })

      if (result?.data?.refreshToken?.payload) {
        const { payload, refreshExpiresIn } = result.data.refreshToken

        if (!validateTokenPayload(payload as TokenPayload)) {
          return { success: false }
        }

        authStore.setTokenExpiration((payload as TokenPayload).exp)
        if (refreshExpiresIn) {
          authStore.setRefreshTokenExpiration(refreshExpiresIn)
        }

        return { success: true }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      if (errorMessage?.includes("Signature has expired")) {
        authStore.clearAuth()
      }
    }

    return { success: false }
  }

  async function verifyAuthState() {
    if (!authStore.hasValidAuthState) {
      authStore.clearAuth()
      return false
    }

    if (authStore.isTokenExpired && !authStore.isRefreshTokenExpired) {
      const result = await refreshToken()
      return result.success
    }

    return true
  }

  return {
    // State
    loginLoading,
    loginError,
    registerLoading,
    registerError,
    updateUserLoading,
    updateUserError,
    logoutLoading,
    logoutError,
    authStatusLoading,
    authStatusError,
    authStatus: computed(() => authStatusResult.value?.authStatus),

    // Methods
    login,
    register,
    updateUser,
    logout,
    refreshToken,
    verifyAuthState,
    refetchAuthStatus,
  }
}
