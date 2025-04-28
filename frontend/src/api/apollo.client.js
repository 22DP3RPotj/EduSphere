import { ApolloClient, InMemoryCache, createHttpLink, from } from "@apollo/client/core";
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";
import authTokenService from "@/services/refresh-token";
import { useAuthStore } from "@/stores/auth.store";

const httpLink = createHttpLink({
  uri: "/graphql/",
  credentials: "include"
});

// No need to manually attach Authorization header
// The browser will automatically send the cookie with each request
const authLink = setContext((_, { headers }) => {
  return {
    headers: {
      ...headers,
    },
  };
});

class Observable {
  constructor(subscribeFn) {
    this.subscribeFn = subscribeFn;
  }

  subscribe(observer) {
    return this.subscribeFn(observer);
  }
}

// Error handling link with token refresh
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    for (const err of graphQLErrors) {
      // Check for authentication error
      if (err.extensions?.code === 'UNAUTHENTICATED' || 
          err.message.includes('signature has expired') ||
          err.message.includes('Authentication credentials were not provided')) {
        
        const authStore = useAuthStore();
        
        // If token is already expired in store, just log out
        if (authStore.isTokenExpired) {
          authStore.clearAuth();
          return;
        }
        
        // Try to refresh the token
        return new Observable(observer => {
          // Attempt token refresh
          authTokenService.refreshToken()
            .then(success => {
              if (success) {
                // Retry the failed request
                const subscriber = {
                  next: observer.next.bind(observer),
                  error: observer.error.bind(observer),
                  complete: observer.complete.bind(observer)
                };
                
                forward(operation).subscribe(subscriber);
              } else {
                // Token refresh failed, clear auth
                authStore.clearAuth();
                observer.error(err);
              }
            })
            .catch(refreshError => {
              // Refresh failed with an error
              authStore.clearAuth();
              observer.error(refreshError);
            });
        });
      }
    }
  }
  
  if (networkError) {
    console.log(`[Network error]: ${networkError}`);
  }
});

// Initialize Apollo Client
export const apolloClient = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache(),
});