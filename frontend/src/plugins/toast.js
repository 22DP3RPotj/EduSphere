import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';

const options = {
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: false,
  showCloseButtonOnHover: true,
  hideProgressBar: true,
  closeButton: "button",
  icon: true,
  rtl: false,
  transition: 'Vue-Toastification__bounce',
  maxToasts: 3,
  newestOnTop: true,
  position: 'bottom-right',
  filterBeforeCreate: (toast, toasts) => {
    if (toasts.some(t => t.content === toast.content)) return null;
    return toast;
  }
};

export default {
  install(app) {
    app.use(Toast, options);
  }
};