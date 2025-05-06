import { useToast } from "vue-toastification";

export function useNotifications() {
  const toast = useToast();
  
  const extractErrorMessages = (error) => {
    const errorMessages = [];
    
    if (error.graphQLErrors && error.graphQLErrors.length > 0) {
      const gqlError = error.graphQLErrors[0];
      
      const formErrors = gqlError.extensions?.errors;
      if (formErrors) {
        // Handle field-specific errors
        Object.entries(formErrors).forEach(([field, messages]) => {
          if (Array.isArray(messages)) {
            messages.forEach(msg => errorMessages.push(msg));
          } else if (typeof messages === 'string') {
            errorMessages.push(messages);
          }
        });
      }
      
      // If no structured formErrors but message exists, try to parse it
      if (errorMessages.length === 0 && gqlError.message && gqlError.message !== "Invalid data") {
        try {
          const parsed = JSON.parse(
            gqlError.message.replace(/'/g, '"')
          );
          
          if (Array.isArray(parsed.__all__)) {
            parsed.__all__.forEach(msg => errorMessages.push(msg));
          }
        } catch (e) {
          errorMessages.push(gqlError.message);
        }
      }

    }
  
    // Network or fallback error handling
    if (errorMessages.length === 0) {
      const fallbackMsg = error.message || String(error) || 'An unexpected error occurred';
      errorMessages.push(fallbackMsg);
    }
    
    return errorMessages;
  };

  return {
    success: (message) => toast.success(message),
    error: (error) => {
      extractErrorMessages(error).forEach(message => toast.error(message));
    },
    info: (message) => toast.info(message),
    warning: (message) => toast.warning(message)
  };
}