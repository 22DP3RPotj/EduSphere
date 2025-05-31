import Toast, { POSITION } from 'vue-toastification';
import 'vue-toastification/dist/index.css';

import type { App } from 'vue';
import type { PluginOptions } from 'vue-toastification';

const options: PluginOptions = {
  timeout: 3000,
  closeOnClick: true,
  toastClassName: "mobile-toast",
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: false,
  showCloseButtonOnHover: true,
  hideProgressBar: true,
  closeButton: "button",
  icon: true,
  rtl: false,
  transition: {
    enter: 'Vue-Toastification__slide',
    leave: 'Vue-Toastification__slide',
    move: 'Vue-Toastification__slide',
  },
  maxToasts: 3,
  newestOnTop: true,
  position: POSITION.TOP_RIGHT,
  filterBeforeCreate: (toast, toasts) => {
    if (toasts.some(t => t.content === toast.content)) return false;
    return toast;
  }
};

export default {
  install(app: App) {
    app.use(Toast, options);
  }
};
