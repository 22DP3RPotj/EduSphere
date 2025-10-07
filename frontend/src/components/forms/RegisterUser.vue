<template>
  <form @submit.prevent="handleSubmit">
    <div v-if="generalErrors.length > 0" class="error-message">
      <font-awesome-icon icon="exclamation-circle" />
      <div class="error-list">
        <p v-for="(error, index) in generalErrors" :key="index">{{ error }}</p>
      </div>
    </div>

    <div class="form-group">
      <label for="username">Username</label>
      <input
        id="username"
        v-model="formData.username"
        type="text"
        required
        placeholder="Choose a username"
        autocomplete="username"
        :disabled="registerLoading"
        :class="{ 'input-error': fieldErrors.username }"
      />
      <div v-if="fieldErrors.username" class="field-error">
        <p v-for="(error, index) in fieldErrors.username" :key="index">{{ error }}</p>
      </div>
    </div>

    <div class="form-group">
      <label for="name">Full Name</label>
      <input
        id="name"
        v-model="formData.name"
        type="text"
        placeholder="Enter your full name"
        autocomplete="name"
        required
        :disabled="registerLoading"
        :class="{ 'input-error': fieldErrors.name }"
      />
      <div v-if="fieldErrors.name" class="field-error">
        <p v-for="(error, index) in fieldErrors.name" :key="index">{{ error }}</p>
      </div>
    </div>

    <div class="form-group">
      <label for="email">Email</label>
      <input
        id="email"
        v-model="formData.email"
        type="email"
        placeholder="Enter your email"
        autocomplete="email"
        required
        :disabled="registerLoading"
        :class="{ 'input-error': fieldErrors.email }"
      />
      <div v-if="fieldErrors.email" class="field-error">
        <p v-for="(error, index) in fieldErrors.email" :key="index">{{ error }}</p>
      </div>
    </div>

    <div class="form-group">
      <label for="password1">Password</label>
      <input
        id="password1"
        v-model="formData.password1"
        type="password"
        placeholder="Create a password"
        autocomplete="new-password"
        required
        :disabled="registerLoading"
        :class="{ 'input-error': fieldErrors.password1 }"
      />
      <div v-if="fieldErrors.password1" class="field-error">
        <p v-for="(error, index) in fieldErrors.password1" :key="index">{{ error }}</p>
      </div>
    </div>

    <div class="form-group">
      <label for="password2">Confirm Password</label>
      <input
        id="password2"
        v-model="formData.password2"
        type="password"
        placeholder="Confirm your password"
        autocomplete="new-password"
        required
        :disabled="registerLoading"
        :class="{ 'input-error': fieldErrors.password2 }"
      />
      <div v-if="fieldErrors.password2" class="field-error">
        <p v-for="(error, index) in fieldErrors.password2" :key="index">{{ error }}</p>
      </div>
    </div>

    <button type="submit" class="submit-btn" :disabled="registerLoading">
      <font-awesome-icon v-if="registerLoading" icon="spinner" spin />
      <span v-else>Register</span>
    </button>

    <p class="switch-form">
      Already have an account?
      <button type="button" @click="$emit('switch-to-login')">Login</button>
    </p>
  </form>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { parseGraphQLError } from '@/utils/errorParser'
import type { RegisterInput } from '@/types'

const emit = defineEmits<{
  'register-success': []
  'switch-to-login': []
}>()

const { register, registerLoading, registerError } = useAuth()

const formData = ref<RegisterInput>({
  username: '',
  name: '',
  email: '',
  password1: '',
  password2: '',
})

const parsedErrors = computed(() => {
  if (!registerError.value) {
    return { fieldErrors: {}, generalErrors: [] }
  }
  return parseGraphQLError(registerError.value)
})

const fieldErrors = computed(() => parsedErrors.value.fieldErrors)
const generalErrors = computed(() => parsedErrors.value.generalErrors)

watch(formData, () => {
  if (registerError.value) {
    // Errors will be cleared on next mutation attempt
  }
}, { deep: true })

async function handleSubmit() {
  const result = await register(formData.value)

  if (result.success) {
    emit('register-success')
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-styles.css';
@import '@/assets/styles/form-errors.css';
</style>
