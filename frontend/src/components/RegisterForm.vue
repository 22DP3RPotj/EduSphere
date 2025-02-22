<template>
    <div>
      <h2>Register</h2>
      <input v-model="username" placeholder="Username">
      <input v-model="name" placeholder="Name">
      <input v-model="email" placeholder="Email">
      <input v-model="password1" type="password" placeholder="Password">
      <input v-model="password2" type="password" placeholder="Confirm Password">
      <button @click="handleRegister">Register</button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </template>
  
  <script>
  import { registerUser } from "@/api/auth.api";
  
  export default {
    data() {
      return {
        username: "",
        name: "",
        email: "",
        password1: "",
        password2: "",
        error: null
      };
    },
    methods: {
      async handleRegister() {
        if (this.password1 !== this.password2) {
          this.error = "Passwords don't match";
          return;
        }
        
        try {
          await registerUser(this.username, this.name, this.email, this.password1, this.password2);
          this.$router.push("/create-room");
        } catch (error) {
          this.error = error.message;
        }
      }
    }
  };
  </script>