import { computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth.store';

export function useLocale() {
  const { locale, availableLocales } = useI18n();
  const authStore = useAuthStore();

  // Initialize locale from user preference or default
  const initializeLocale = () => {
    const userLanguage = authStore.user?.language;
    if (userLanguage && availableLocales.includes(userLanguage)) {
      locale.value = userLanguage;
    } else {
      locale.value = 'en';
    }
  };

  // Watch for user changes and update locale immediately
  watch(
    () => authStore.user?.language,
    (newLanguage) => {
      if (newLanguage && availableLocales.includes(newLanguage)) {
        locale.value = newLanguage;
      } else if (newLanguage === undefined || newLanguage === null) {
        // User logged out or no language set, default to English
        locale.value = 'en';
      }
    },
    { immediate: true }
  );

  const currentLocale = computed(() => locale.value);

  const setLocale = (newLocale: string) => {
    if (availableLocales.includes(newLocale)) {
      locale.value = newLocale;
    }
  };

  return {
    currentLocale,
    availableLocales,
    setLocale,
    initializeLocale,
  };
}
