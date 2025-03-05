import { useNotifications } from './useNotifications';

export function useApi() {
  const notifications = useNotifications();
  
  return {
    async call(apiFn, successMessage) {
      try {
        const result = await apiFn();
        if (successMessage) {
          notifications.success(successMessage);
        }
        return result;
      } catch (error) {
        notifications.error(error);
        throw error;
      }
    }
  };
}