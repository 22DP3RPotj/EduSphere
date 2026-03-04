import { createI18n } from 'vue-i18n';
import en from './locales/en.json';
import lv from './locales/lv.json';

export type MessageSchema = typeof en;

const i18n = createI18n<[MessageSchema], 'en' | 'lv'>({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en,
    lv
  }
});

export default i18n;
