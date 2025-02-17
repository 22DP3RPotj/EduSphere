import { createRouter, createWebHistory } from "vue-router";
import { AuthService } from "@/services/authService";
import LoginForm from "@/components/LoginForm.vue";
import CreateRoom from "@/components/CreateRoom.vue";

// Define Routes
const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginForm },
  { 
    path: "/create-room", 
    component: CreateRoom, 
    meta: { requiresAuth: true } 
  },
];

// Create Router
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Use AuthService in Navigation Guards
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !AuthService.isAuthenticated()) {
    next("/login");
  } else {
    next();
  }
});

export default router;
