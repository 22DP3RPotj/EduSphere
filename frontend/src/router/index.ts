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
    meta: { requireAuth: true } 
  },
  {
    path: '/u/:userSlug',
    name: 'UserProfile',
    component: () => import('@/views/UserProfile.vue')
  },
  {
    path: "/r/:roomId",
    component: () => import("@/views/RoomDetail.vue"),
    meta: { requireAuth: true }
  },
  {
    path: "/admin",
    component: () => import("@/views/AdminPanel.vue"),
    meta: { requireAuth: true, requireAdmin: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;
  const user = authStore.user;

  if (to.meta.requireGuest && isAuthenticated) {
    return next({ path: from.fullPath });
  }
  
  if (to.meta.requireAuth && !isAuthenticated) {
    return next({ path: "/auth" });
  }
  
  if (to.meta.requireAdmin && !user?.isSuperuser) {
    return next({ path: from.fullPath });
  }
  
  return next();
});

export default router;
