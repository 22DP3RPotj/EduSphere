import { createApp } from "vue";
import { createPinia } from "pinia";
import { useAuthStore } from "@/stores/auth.store";
import { createPersistedStatePlugin } from 'pinia-plugin-persistedstate-2'

import "@/assets/styles/main.css";
import "@/assets/styles/theme.css";
import "@/assets/styles/toasts.css";

import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

import App from "@/App.vue";
import router from "@/router";
import { provideApollo } from "./api/apollo.client";

library.add(fas);

const pinia = createPinia();
pinia.use(
  createPersistedStatePlugin({})
);

const app = createApp(App);

app.use(pinia);
app.use(router);

provideApollo(app);

app.component('FontAwesomeIcon', FontAwesomeIcon);

const initApp = async () => {
  const authStore = useAuthStore();
  authStore.initialize();

  // TODO: Come up with a better way to handle CSRF tokens
  // This is a temporary solution to fetch the CSRF token from the backend
  // await fetch('/api/csrf/', {
  //   method: 'GET',
  //   credentials: 'include',
  // });
  
  app.mount("#app");
};

initApp();
