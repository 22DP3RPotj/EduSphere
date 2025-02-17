import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";  // Import Vue Router
import { createPinia } from "pinia";

const app = createApp(App);
app.use(router);
app.use(createPinia()); // Use Pinia for authentication state
app.mount("#app");
