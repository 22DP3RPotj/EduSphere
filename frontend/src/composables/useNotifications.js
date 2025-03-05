import { useToast } from "vue-toastification";

export function useNotifications() {
  const toast = useToast();
  
  const extractErrorMessage = (error) => {
    return error?.response?.errors?.[0]?.message || 
           error?.message || 
           'An unexpected error occurred';
  };

  return {
    success: (message) => toast.success(message),
    error: (error) => toast.error(extractErrorMessage(error)),
    info: (message) => toast.info(message),
    warning: (message) => toast.warning(message)
  };
}