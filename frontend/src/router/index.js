import { createRouter, createWebHistory } from "vue-router";
import { AuthService } from "@/services/auth.service";

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
    path: "/rooms/:hostSlug/:roomSlug",
    component: () => import("@/components/RoomDetail.vue"),
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = AuthService.isAuthenticated();

  if (to.meta.requireGuest && isAuthenticated) {
    next({ path: '/' });
    return;
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath } });
    return;
  }

  next();
});

export default router;
