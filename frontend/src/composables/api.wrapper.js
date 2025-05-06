// api.wrapper.js
import { useNotifications } from './useNotifications';

export function useApiWrapper() {
  const notifications = useNotifications();
  
  /**
   * Safely execute an API function with error handling
   * @param {Function} apiFn - Async function to execute
   * @param {Object} options - Additional options
   * @param {Boolean} options.suppressNotifications - If true, don't show notifications
   * @param {Function} options.onError - Custom error handler that gets called with the error
   * @returns {Promise<any>} - The result of the API call
   */
  const callApi = async (apiFn, options = {}) => {
    try {
      // Execute the API function
      const result = await apiFn();
      return result;
    } catch (error) {
      console.error('API Error:', error);
      
      // Log the complete error structure to help with debugging
      try {
        console.log('Error full structure:', JSON.stringify(error, null, 2));
      } catch (e) {
        console.log('Error cannot be stringified, showing properties:', Object.keys(error));
      }
      
      // Execute custom error handler if provided
      if (options.onError) {
        options.onError(error);
      }
      
      // Show error notification if not suppressed
      if (!options.suppressNotifications) {
        notifications.error(error);
      }
      
      throw error; // Re-throw to allow component-level handling
    }
  };
  
  /**
   * Execute a GraphQL mutation with proper error extraction
   * @param {Function} mutationFn - GraphQL mutation function to execute 
   * @returns {Promise<any>} - The mutation result
   */
  const executeMutation = async (mutationFn) => {
    return callApi(mutationFn);
  };
  
  return {
    callApi,
    executeMutation
  };
}