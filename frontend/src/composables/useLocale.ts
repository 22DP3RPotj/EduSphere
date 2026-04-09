import { computed, watch, type WatchStopHandle } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth.store';

type LocaleSyncParams = {
  locale: { value: string };
  availableLocales: readonly string[];
};

let localeSyncInitialized = false;
let localeSyncStopHandle: WatchStopHandle | null = null;

function applyLocaleFromUser(
  userLanguage: string | null | undefined,
  locale: { value: string },
  availableLocales: readonly string[]
) {
  if (userLanguage && availableLocales.includes(userLanguage)) {
    locale.value = userLanguage;
  } else if (userLanguage === undefined || userLanguage === null) {
    locale.value = 'en';
  }
}

export function initializeLocaleSync(params: LocaleSyncParams) {
  if (localeSyncInitialized) {
    return localeSyncStopHandle;
  }

  const { locale, availableLocales } = params;
  const authStore = useAuthStore();

  localeSyncStopHandle = watch(
    () => authStore.user?.language,
    (newLanguage) => {
      applyLocaleFromUser(newLanguage, locale, availableLocales);
    },
    { immediate: true }
  );

  localeSyncInitialized = true;
  return localeSyncStopHandle;
}

export function useLocale() {
  const { locale, availableLocales } = useI18n();

  // Initialize locale from user preference or default
  const initializeLocale = () => {
    const authStore = useAuthStore();
    const userLanguage = authStore.user?.language;
    applyLocaleFromUser(userLanguage, locale, availableLocales);
  };

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
