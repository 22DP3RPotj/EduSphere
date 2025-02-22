<template>
    <div>
      <h2>Login</h2>
      <input v-model="email" placeholder="Email">
      <input v-model="password" type="password" placeholder="Password">
      <button @click="handleLogin">Login</button>
    </div>
  </template>
  
  <script>
  import { login } from "@/api/auth.api";
  
  export default {
    data() {
      return { email: "", password: "" };
    },
    methods: {
      async handleLogin() {
        const success = await login(this.email, this.password);
        if (success) this.$router.push("/create-room");
        else alert("Login failed!");
      }
    }
  };
  </script>
  