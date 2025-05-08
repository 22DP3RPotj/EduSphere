import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const routes = [
  {
    path: "/",
    component: () => import("@/components/Home.vue"),
  },
  {
    path: "/auth",
    component: () => import("@/views/authPage.vue"),
    meta: { requireGuest: true }
  },
  {
    path: "/login",
    redirect: "/auth",
    meta: { requireGuest: true }
  },
  {
    path: "/register",
    redirect: "/auth",
    meta: { requireGuest: true }
  },
  { 
    path: "/create-room", 
    component: () => import("@/views/CreateRoomPage.vue"), 
    meta: { requiresAuth: true } 
  },
  {
    path: "/:hostSlug/:roomSlug",
    component: () => import("@/components/RoomDetail.vue"),
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  try {
    // Ensure auth state is initialized before proceeding
    await authStore.initialize();

    const isAuthenticated = authStore.isAuthenticated;
    console.log("Auth status:", isAuthenticated);

    if (to.meta.requireGuest && isAuthenticated) {
      // Redirect authenticated users away from guest-only pages
      next({ path: "/" });
    } else if (to.meta.requiresAuth && !isAuthenticated) {
      // Redirect unauthenticated users to the login page
      next({ path: "/auth", query: { redirect: to.fullPath } });
    } else {
      // Allow navigation
      next();
    }
  } catch (error) {
    console.error("Authentication check failed:", error);
    next({ path: "/auth" });
  }
});

export default router;