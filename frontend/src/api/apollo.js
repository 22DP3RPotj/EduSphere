import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client/core";
import { setContext } from "@apollo/client/link/context";

// API Endpoint (Django GraphQL)
const httpLink = createHttpLink({
  uri: "http://localhost:8000/graphql/",
});

// Attach Authorization Header
const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem("token");  // Retrieve token from storage
  return {
    headers: {
      ...headers,
      authorization: token ? `JWT ${token}` : "",  // Attach JWT token
    },
  };
});

// Initialize Apollo Client
export const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
