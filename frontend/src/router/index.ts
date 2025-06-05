import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const routes = [
  {
    path: "/",
    component: () => import("@/views/HomePage.vue"),
  },
  {
    path: "/auth",
    component: () => import("@/views/AuthPage.vue"),
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
    component: () => import("@/views/CreateRoom.vue"), 
    meta: { requiresAuth: true } 
  },
  {
    path: '/u/:userSlug',
    name: 'UserProfile',
    component: () => import('@/views/UserProfile.vue')
  },
  {
    path: "/u/:hostSlug/:roomSlug",
    component: () => import("@/views/RoomDetail.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  try {
    const isAuthenticated = authStore.isAuthenticated;

    if (to.meta.requireGuest && isAuthenticated) {
      next({ path: from.fullPath });
    } else if (to.meta.requiresAuth && !isAuthenticated) {
      next({ path: "/auth" });
    } else {
      next();
    }
  } catch (error) {
    console.error("Authentication check failed:", error);
    next({ path: "/auth" });
  }
});

export default router;
