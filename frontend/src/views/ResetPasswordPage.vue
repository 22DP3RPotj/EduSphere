<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-header">
          <h2>{{ t('auth.resetPassword') }}</h2>
        </div>

        <div class="form-content">
          <div v-if="resetSuccess" class="status-message success">
            <font-awesome-icon icon="check-circle" size="2x" />
            <h3>{{ t('auth.passwordResetSuccess') }}</h3>
            <p>{{ t('auth.passwordResetSuccessMessage') }}</p>
            <button class="submit-btn" @click="router.push('/auth')">
              {{ t('auth.backToLogin') }}
            </button>
          </div>

          <div v-else-if="!token" class="status-message error">
            <font-awesome-icon icon="exclamation-circle" size="2x" />
            <h3>{{ t('auth.invalidResetLink') }}</h3>
            <p>{{ t('auth.invalidResetLinkMessage') }}</p>
            <button class="submit-btn" @click="router.push('/forgot-password')">
              {{ t('auth.requestNewLink') }}
            </button>
          </div>

          <form v-else @submit.prevent="handleSubmit">
            <div v-if="generalErrors.length > 0" class="error-message">
              <font-awesome-icon icon="exclamation-circle" />
              <div class="error-list">
                <p v-for="(error, index) in generalErrors" :key="index">{{ error }}</p>
              </div>
            </div>

            <div class="form-group">
              <label for="newPassword">{{ t('auth.newPassword') }}</label>
              <input
                id="newPassword"
                v-model="newPassword"
                type="password"
                :placeholder="t('auth.enterNewPassword')"
                autocomplete="new-password"
                required
                :disabled="passwordResetLoading"
              />
            </div>

            <div class="form-group">
              <label for="confirmPassword">{{ t('auth.confirmPassword') }}</label>
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                type="password"
                :placeholder="t('auth.confirmYourPassword')"
                autocomplete="new-password"
                required
                :disabled="passwordResetLoading"
              />
            </div>

            <button type="submit" class="submit-btn" :disabled="passwordResetLoading">
              <font-awesome-icon v-if="passwordResetLoading" icon="spinner" spin />
              <span v-else>{{ t('auth.resetPassword') }}</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { resetPassword, passwordResetLoading } = useAuth()

const token = ref(route.query.token as string || '')
const newPassword = ref('')
const confirmPassword = ref('')
const resetSuccess = ref(false)
const generalErrors = ref<string[]>([])

async function handleSubmit() {
  generalErrors.value = []

  if (newPassword.value !== confirmPassword.value) {
    generalErrors.value = [t('auth.passwordsDoNotMatch')]
    return
  }

  const result = await resetPassword({
    token: token.value,
    newPassword: newPassword.value,
  })

  if (result.success) {
    resetSuccess.value = true
  } else {
    generalErrors.value = ('generalErrors' in result ? result.generalErrors : undefined) || [result.error || 'Password reset failed']
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-layout.css';
@import '@/assets/styles/form-styles.css';

.status-message {
  text-align: center;
  padding: 2rem 1rem;
}

.status-message h3 {
  margin: 1rem 0 0.5rem;
}

.status-message p {
  color: var(--text-light);
  margin-bottom: 1.5rem;
}

.status-message.success svg {
  color: var(--success-color, #10b981);
}

.status-message.error svg {
  color: var(--error-color, #ef4444);
}
</style>
