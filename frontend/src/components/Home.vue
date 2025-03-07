<template>
    <div>
        <h1>Welcome to Chat App</h1>
        <div class="actions">
            <router-link to="/create-room" class="btn btn-primary">Create Room</router-link>
            <button v-if="isAuthenticated" @click="handleLogout" class="btn btn-danger">Logout</button>
            <router-link v-else to="/login" class="btn btn-secondary">Login</router-link>
        </div>
    </div>
</template>

<script setup>
import { useAuthApi } from "@/api/auth.api";
import { useAuthStore } from "@/stores/auth.store";
import { useRouter, useRoute } from "vue-router";
import { computed } from "vue";

const authApi = useAuthApi();
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const isAuthenticated = computed(() => authStore.isAuthenticated);

const handleLogout = () => {
    authApi.logout();
    
    if (route.meta.requiresAuth) {
        router.push('/');
    }
};
</script>

<style scoped>
.actions {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}
.btn {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    cursor: pointer;
    font-weight: bold;
    border: none;
}
.btn-primary {
    background-color: #4CAF50;
    color: white;
}
.btn-danger {
    background-color: #f44336;
    color: white;
}
.btn-secondary {
    background-color: #2196F3;
    color: white;
}
</style>