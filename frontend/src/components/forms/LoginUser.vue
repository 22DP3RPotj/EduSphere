<template>
  <form @submit.prevent="handleSubmit">
    <!-- Added inline error display -->
    <div v-if="generalErrors.length > 0" class="error-message">
      <font-awesome-icon icon="exclamation-circle" />
      <div class="error-list">
        <p v-for="(error, index) in generalErrors" :key="index">{{ error }}</p>
      </div>
    </div>

    <div class="form-group">
      <label for="email">{{ t('auth.email') }}</label>
      <input
        id="email"
        v-model="formData.email"
        type="email"
        :placeholder="t('auth.enterEmail')"
        autocomplete="email"
        required
        :disabled="loginLoading"
        :class="{ 'input-error': fieldErrors.email }"
      />
      <!-- Added field-specific error display -->
      <div v-if="fieldErrors.email" class="field-error">
        <p v-for="(error, index) in fieldErrors.email" :key="index">{{ error }}</p>
      </div>
    </div>

    <div class="form-group">
      <label for="password">{{ t('auth.password') }}</label>
      <input
        id="password"
        v-model="formData.password"
        type="password"
        :placeholder="t('auth.enterPassword')"
        autocomplete="current-password"
        required
        :disabled="loginLoading"
        :class="{ 'input-error': fieldErrors.password }"
      />
      <div v-if="fieldErrors.password" class="field-error">
        <p v-for="(error, index) in fieldErrors.password" :key="index">{{ error }}</p>
      </div>
    </div>

    <button type="submit" class="submit-btn" :disabled="loginLoading">
      <font-awesome-icon v-if="loginLoading" icon="spinner" spin />
      <span v-else>{{ t('common.login') }}</span>
    </button>

    <p class="forgot-password">
      <router-link to="/forgot-password">{{ t('auth.forgotPassword') }}?</router-link>
    </p>

    <p class="switch-form">
      {{ t('auth.dontHaveAccount') }}
      <button type="button" @click="$emit('switch-to-register')">{{ t('common.register') }}</button>
    </p>
  </form>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuth } from '@/composables/useAuth';
import { parseGraphQLError } from '@/utils/errorParser';

const emit = defineEmits<{
  'login-success': [];
  'switch-to-register': [];
}>();

const { t } = useI18n();
const { login, loginLoading, loginError } = useAuth();

const formData = ref({
  email: '',
  password: ''
});

const parsedErrors = computed(() => {
  if (!loginError.value) {
    return { fieldErrors: {}, generalErrors: [] }
  }
  return parseGraphQLError(loginError.value)
});

const fieldErrors = computed(() => parsedErrors.value.fieldErrors);
const generalErrors = computed(() => parsedErrors.value.generalErrors);

watch(formData, () => {
  if (loginError.value) {
    // Errors will be cleared on next mutation attempt
  }
}, { deep: true });

async function handleSubmit() {
  const result = await login(formData.value.email, formData.value.password);
  
  if (result.success) {
    emit('login-success');
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-styles.css';
@import '@/assets/styles/form-errors.css';

.forgot-password {
  text-align: right;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.forgot-password a {
  color: var(--primary-color);
  text-decoration: none;
}

.forgot-password a:hover {
  text-decoration: underline;
}
</style>
