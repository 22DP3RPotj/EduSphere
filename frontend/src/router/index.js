import { createRouter, createWebHistory } from "vue-router";
import { AuthService } from "@/services/authService";
import LoginForm from "@/components/LoginForm.vue";
import CreateRoom from "@/components/CreateRoom.vue";
import RegisterForm from "@/components/RegisterForm.vue";

// Define Routes
const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginForm },
  { 
    path: "/create-room", 
    component: CreateRoom, 
    meta: { requiresAuth: true } 
  },
  {
    path: "/register",
    component: RegisterForm
  }
];

// Create Router
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Use AuthService in Navigation Guards
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !AuthService.isAuthenticated()) {
    next({ path: '/login', query: { redirect: to.fullPath } });
  } else {
    next();
  }
});

export default router;
