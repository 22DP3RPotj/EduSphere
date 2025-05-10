import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';

const options = {
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
    exit: {
      name: 'Vue-Toastification__slide',
      mode: 'out-in',
      css: false,
      onEnter: (el) => {
        el.style.opacity = 1;
      },
      onLeave: (el, done) => {
        const moveY = window.innerHeight > 600 ? -30 : -15;
        el.style.transition = 'all 0.4s ease';
        el.style.opacity = '0';
        el.style.transform = `translateY(${moveY}px)`;
        el.addEventListener('transitionend', done);
      }
    }
  },
  maxToasts: 3,
  newestOnTop: true,
  position: 'top-right',
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