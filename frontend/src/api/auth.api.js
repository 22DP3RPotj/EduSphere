import { gql } from "@apollo/client/core";
import { apolloClient } from "./apollo.client";
import { useAuthStore } from "../stores/auth.store";
import { useNotifications } from "@/composables/useNotifications";

export function useAuthApi() {
  const authStore = useAuthStore();
  const notifications = useNotifications();

  const LOGIN_MUTATION = gql`
    mutation TokenAuth($email: String!, $password: String!) {
      tokenAuth(email: $email, password: $password) {
        token
      }
    }
  `;

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
          username
          email
        }
        token
      }
    }
  `;

  async function login(email, password) {
    try {
      const response = await apolloClient.mutate({
        mutation: LOGIN_MUTATION,
        variables: { email, password },
      });

      const token = response.data.tokenAuth.token;
      localStorage.setItem("token", token);
      authStore.setToken(token);
      
      notifications.success('Login successful!');
      return true;
    } catch (error) {
      notifications.error(error);
      return false;
    }
  }

  async function registerUser(username, name, email, password1, password2) {
    try {
      if (password1 !== password2) {
        throw new Error("Passwords do not match");
      }

      const response = await apolloClient.mutate({
        mutation: REGISTER_MUTATION,
        variables: { username, name, email, password1, password2 },
      });

      const token = response.data.registerUser.token;
      if (token) {
        authStore.setToken(token);
      }
      
      notifications.success('Registration successful!');
      return true;
    } catch (error) {
      notifications.error(error);
      return false;
    }
  }

  function logout() {
    localStorage.removeItem("token");
    authStore.clearToken();
    notifications.info('Logged out successfully');
  }

  return {
    login,
    registerUser,
    logout
  };
}