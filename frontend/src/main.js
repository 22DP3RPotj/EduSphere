import { createApp } from "vue";
import { createPinia } from "pinia";
import { useAuthStore } from "@/stores/auth.store";
import { createPersistedStatePlugin } from 'pinia-plugin-persistedstate-2'
import VueSweetalert2 from 'vue-sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css';
import "@/assets/styles/global.css";

import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

import App from "@/App.vue";
import router from "@/router";
import toast from "@/plugins/toast";

library.add(fas);

const pinia = createPinia();
pinia.use(
  createPersistedStatePlugin({})
);

const app = createApp(App);

app.use(pinia);
app.use(router);
app.use(toast);
app.use(VueSweetalert2);

app.component('font-awesome-icon', FontAwesomeIcon);

const initApp = async () => {
  const authStore = useAuthStore();
  await authStore.initialize();
  
  app.mount("#app");
};

initApp();
