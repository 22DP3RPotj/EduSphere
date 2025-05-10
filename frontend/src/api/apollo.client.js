import { ApolloClient, InMemoryCache, createHttpLink, from } from "@apollo/client/core";
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";
import authTokenService from "@/services/refresh-token";
import { useAuthStore } from "@/stores/auth.store";

const httpLink = createHttpLink({
  uri: "/graphql/",
  credentials: "include"
});

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


const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    for (const err of graphQLErrors) {
      if (err.extensions?.code === 'UNAUTHENTICATED' || 
          err.message.includes('signature has expired') ||
          err.message.includes('Authentication credentials were not provided')) {
        
        const authStore = useAuthStore();
        
        if (authStore.isTokenExpired) {
          authStore.clearAuth();
          return;
        }
        
        return new Observable(observer => {
          authTokenService.refreshToken()
            .then(success => {
              if (success) {
                const subscriber = {
                  next: observer.next.bind(observer),
                  error: observer.error.bind(observer),
                  complete: observer.complete.bind(observer)
                };
                
                forward(operation).subscribe(subscriber);
              } else {
                authStore.clearAuth();
                observer.error(err);
              }
            })
            .catch(refreshError => {
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

export const apolloClient = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache(),
});