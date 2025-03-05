import { useToast } from "vue-toastification";

export function useNotifications() {
  const toast = useToast();
  
  const extractErrorMessage = (error) => {
    if (error?.response?.errors) {
      return error.response.errors.map(e => e.message).join(', ');
    }
    
    if (error?.graphQLErrors) {
      return error.graphQLErrors.map(e => e.message).join(', ');
    }
    
    return error?.message || 
           error?.toString() || 
           'An unexpected error occurred';
  };

  return {
    success: (message) => toast.success(message),
    error: (error) => toast.error(extractErrorMessage(error)),
    info: (message) => toast.info(message),
    warning: (message) => toast.warning(message)
  };
}