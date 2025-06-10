import { ApolloClient, InMemoryCache, from, Observable } from "@apollo/client/core";

import { DefaultApolloClient } from '@vue/apollo-composable';
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";
import createUploadLink from "apollo-upload-client/createUploadLink.mjs";
import Cookies from "js-cookie";

import { useAuthStore } from "@/stores/auth.store";
import authTokenService from "@/services/refresh-token";

import type { FetchResult, Operation, NextLink } from "@apollo/client/core";
import type { App } from 'vue';

// Upload link
const uploadLink = createUploadLink({
  uri: "https://edusphere-backend.fly.dev/graphql/",
  credentials: "include"
});

// Auth context for CSRF token
const authLink = setContext((_, { headers }) => {
  return {
    headers: {
      ...headers,
      "X-CSRFToken": Cookies.get("csrftoken"),
    },
  };
});

// Token refresh logic
function handleAuthError(
  err: unknown,
  operation: Operation,
  forward: NextLink
): Observable<FetchResult> | void {
  const authStore = useAuthStore();

  if (authStore.isTokenExpired) {
    authStore.clearAuth();
    return;
  }

  return new Observable<FetchResult>(observer => {
    authTokenService.refreshToken()
      .then(success => {
        if (success) {
          forward(operation).subscribe({
            next: observer.next.bind(observer),
            error: observer.error.bind(observer),
            complete: observer.complete.bind(observer),
          });
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

// Error handling link
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    for (const err of graphQLErrors) {
      const isUnauthenticated =
        err.extensions?.code === 'UNAUTHENTICATED' ||
        err.message.includes('signature has expired') ||
        err.message.includes('Authentication credentials were not provided');

      if (isUnauthenticated) {
        return handleAuthError(err, operation, forward);
      }
    }
  }

  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
  }
});

// Apollo Client instance
export function createApolloClient() {
  return new ApolloClient({
    link: from([errorLink, authLink, uploadLink]),
    cache: new InMemoryCache({
      typePolicies: {
        Query: {
          fields: {
            rooms: {
              merge(_existing = { edges: [] }, incoming) {
                return incoming;
              }
            },
            messages: {
              merge(_existing = { edges: [] }, incoming) {
                return incoming;
              }
            }
          }
        }
      }
    }),
    defaultOptions: {
      watchQuery: {
        fetchPolicy: 'cache-and-network',
      },
      query: {
        fetchPolicy: 'network-only',
      }
    }
  });
}

// Exported client instance
export const apolloClient = createApolloClient();

export function provideApollo(app: App) {
  app.provide(DefaultApolloClient, apolloClient);
}
