import { gql } from "@apollo/client/core";
import { apolloClient } from "./apollo.client";
import { useAuthStore } from "../stores/auth.store";

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

// Add to existing auth.js API
const REGISTER_MUTATION = gql`
  mutation RegisterUser(
    $username: String!
    $name: String!
    $email: String!
    $password1: String!
    $password2: String!
  ) {
    registerUser(
      username: $username
      name: $name
      email: $email
      password1: $password1
      password2: $password2
    ) {
      user {
        id
        username
        email
      }
      token
    }
  }
`;

export async function registerUser(username, name, email, password1, password2) {
  try {
    const response = await apolloClient.mutate({
      mutation: REGISTER_MUTATION,
      variables: { username, name, email, password1, password2 },
    });

    const token = response.data.registerUser.token;
    if (token) {
      useAuthStore().setToken(token);
    }

    return true;
  } catch (error) {
    console.error("Registration failed", error);
    throw new Error(error.message);
  }
}