import { gql } from "@apollo/client/core";
import { apolloClient } from "./apollo";
import { useAuthStore } from "../stores/auth";

// GraphQL Login Mutation
const LOGIN_MUTATION = gql`
  mutation TokenAuth($email: String!, $password: String!) {
    tokenAuth(email: $email, password: $password) {
      token
    }
  }
`;

// Login Function
export async function login(email, password) {
  const { mutate } = apolloClient;
  try {
    const response = await mutate({
      mutation: LOGIN_MUTATION,
      variables: { email, password },
    });

    const token = response.data.tokenAuth.token;
    localStorage.setItem("token", token);
    useAuthStore().setToken(token);
    return true;
  } catch (error) {
    console.error("Login failed", error);
    return false;
  }
}

// Logout Function
export function logout() {
  localStorage.removeItem("token");
  useAuthStore().clearToken();
}
