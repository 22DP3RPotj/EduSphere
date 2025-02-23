import { useAuthStore } from "@/stores/auth.store";

export const AuthService = {
  isAuthenticated() {
    const authStore = useAuthStore();
    return authStore.isAuthenticated;
  },
  login(token) {
    const authStore = useAuthStore();
    authStore.setToken(token);
  },
  logout() {
    const authStore = useAuthStore();
    authStore.clearToken();
    localStorage.removeItem("token");
    window.dispatchEvent(new Event("storage"));
  },
};
