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
import i18n from "./i18n";
import { initializeLocaleSync } from "@/composables/useLocale";

library.add(fas);

const pinia = createPinia();
pinia.use(
  createPersistedStatePlugin({})
);

const app = createApp(App);

app.use(pinia);
app.use(router);
app.use(i18n);

provideApollo(app);

app.component('FontAwesomeIcon', FontAwesomeIcon);

const initApp = async () => {
  const authStore = useAuthStore();
  authStore.initialize();

  initializeLocaleSync({
    locale: i18n.global.locale as unknown as { value: string },
    availableLocales: i18n.global.availableLocales,
  });
  
  app.mount("#app");
};

initApp();
