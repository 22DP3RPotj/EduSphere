import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const routes = [
  {
    path: "/",
    component: () => import("@/components/Home.vue"),
  },
  {
    path: "/login",
    component: () => import("@/components/LoginForm.vue"),
    meta: { requireGuest: true }
  },
  {
    path: "/register",
    component: () => import("@/components/RegisterForm.vue"),
    meta: { requireGuest: true }
  },
  { 
    path: "/create-room", 
    component: () => import("@/components/CreateRoom.vue"), 
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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  if (to.meta.requireGuest && isAuthenticated) {
    next({ path: "/" });
  } else if (to.meta.requiresAuth && !isAuthenticated) {
    next({ path: "/login", query: { redirect: to.fullPath } });
  } else {
    next();
  }
});

export default router;
