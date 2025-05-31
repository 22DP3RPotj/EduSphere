import { useNotifications } from './useNotifications';

type ApiFn<T> = () => Promise<T>;

interface CallApiOptions {
  suppressNotifications?: boolean;
  onError?: (_error: unknown) => void;
}

export function useApiWrapper() {
  const notifications = useNotifications();

  /**
   * Safely execute an API function with error handling
   */
  const callApi = async <T>(
    apiFn: ApiFn<T>,
    options: CallApiOptions = {}
  ): Promise<T> => {
    try {
      const result = await apiFn();
      return result;
    } catch (error) {
      if (options.onError) {
        options.onError(error);
      }

      if (!options.suppressNotifications) {
        notifications.error(error);
      }

      throw error;
    }
  };

  /**
   * Execute a GraphQL mutation with proper error extraction
   */
  const executeMutation = async <T>(
    mutationFn: ApiFn<T>
  ): Promise<T> => {
    return callApi(mutationFn);
  };

  return {
    callApi,
    executeMutation,
  };
}
