<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-header">
          <h2>{{ t('auth.forgotPassword') }}</h2>
          <p class="form-subtitle">{{ t('auth.forgotPasswordMessage') }}</p>
        </div>

        <div class="form-content">
          <div v-if="emailSent" class="status-message success">
            <font-awesome-icon icon="check-circle" size="2x" />
            <h3>{{ t('auth.resetEmailSent') }}</h3>
            <p>{{ t('auth.resetEmailSentMessage') }}</p>
            <button class="submit-btn secondary" @click="router.push('/auth')">
              {{ t('auth.backToLogin') }}
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
              <label for="email">{{ t('auth.email') }}</label>
              <input
                id="email"
                v-model="email"
                type="email"
                :placeholder="t('auth.enterEmail')"
                autocomplete="email"
                required
                :disabled="sendPasswordResetLoading"
              />
            </div>

            <button type="submit" class="submit-btn" :disabled="sendPasswordResetLoading">
              <font-awesome-icon v-if="sendPasswordResetLoading" icon="spinner" spin />
              <span v-else>{{ t('auth.sendResetLink') }}</span>
            </button>

            <p class="switch-form">
              <router-link to="/auth">{{ t('auth.backToLogin') }}</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { t } = useI18n()
const { sendPasswordResetEmail, sendPasswordResetLoading } = useAuth()

const email = ref('')
const emailSent = ref(false)
const generalErrors = ref<string[]>([])

async function handleSubmit() {
  generalErrors.value = []
  const result = await sendPasswordResetEmail(email.value)

  if (result.success) {
    emailSent.value = true
  } else {
    generalErrors.value = ('generalErrors' in result ? result.generalErrors : undefined) || [result.error || 'Failed to send reset email']
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-layout.css';
@import '@/assets/styles/form-styles.css';

.form-subtitle {
  color: var(--text-light);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

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

.submit-btn.secondary {
  background-color: var(--bg-light);
  color: var(--text-color);
}

.switch-form {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.875rem;
}

.switch-form a {
  color: var(--primary-color);
  text-decoration: none;
}
</style>
