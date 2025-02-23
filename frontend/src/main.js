import { createApp } from "vue";
import { createPinia } from "pinia";
import { useAuthStore } from "./stores/auth.store";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(router);
app.use(createPinia());
app.mount("#app");

const authStore = useAuthStore();
await authStore.initialize();
