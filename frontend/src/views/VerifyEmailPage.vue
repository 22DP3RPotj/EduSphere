<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-content">
          <div v-if="verifying" class="status-message">
            <font-awesome-icon icon="spinner" spin size="2x" />
            <p>{{ t('auth.verifyingEmail') }}</p>
          </div>

          <div v-else-if="success" class="status-message success">
            <font-awesome-icon icon="check-circle" size="2x" />
            <h2>{{ t('auth.emailVerified') }}</h2>
            <p>{{ t('auth.emailVerifiedMessage') }}</p>
            <button class="submit-btn" @click="router.push('/')">
              {{ t('auth.goToHome') }}
            </button>
          </div>

          <div v-else class="status-message error">
            <font-awesome-icon icon="exclamation-circle" size="2x" />
            <h2>{{ t('auth.verificationFailed') }}</h2>
            <p>{{ errorMessage }}</p>
            <div class="action-buttons">
              <button class="submit-btn" :disabled="resendActivationLoading" @click="handleResend">
                <font-awesome-icon v-if="resendActivationLoading" icon="spinner" spin />
                <span v-else>{{ t('auth.resendVerificationEmail') }}</span>
              </button>
              <button class="submit-btn secondary" @click="router.push('/')">
                {{ t('auth.goToHome') }}
              </button>
            </div>
            <p v-if="resendSuccess" class="success-text">{{ t('auth.verificationEmailSent') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { verifyAccount, resendActivationEmail, resendActivationLoading } = useAuth()

const verifying = ref(true)
const success = ref(false)
const errorMessage = ref('')
const resendSuccess = ref(false)

onMounted(async () => {
  const token = route.query.token as string

  if (!token) {
    verifying.value = false
    errorMessage.value = t('auth.noVerificationToken')
    return
  }

  const result = await verifyAccount(token)
  verifying.value = false

  if (result.success) {
    success.value = true
  } else {
    errorMessage.value = ('generalErrors' in result ? result.generalErrors?.[0] : undefined) || result.error || t('auth.verificationFailed')
  }
})

async function handleResend() {
  resendSuccess.value = false
  const result = await resendActivationEmail()
  if (result.success) {
    resendSuccess.value = true
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

.status-message h2 {
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

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.submit-btn.secondary {
  background-color: var(--bg-light);
  color: var(--text-color);
}

.success-text {
  color: var(--success-color, #10b981);
  margin-top: 1rem;
}
</style>
