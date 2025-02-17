import { useAuthStore } from "@/stores/auth";

export const AuthService = {
  // Check if user is authenticated
  isAuthenticated() {
    const authStore = useAuthStore();
    return authStore.token || localStorage.getItem("token");
  },

  // Login: Save token and update state
  login(token) {
    const authStore = useAuthStore();
    authStore.setToken(token);
  },

  // Logout: Remove token and update state
  logout() {
    const authStore = useAuthStore();
    authStore.clearToken();
  }
};
