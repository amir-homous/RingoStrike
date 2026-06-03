<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>{{ isLogin ? $t('auth.login') : $t('auth.register') }}</h2>
      
      <form @submit.prevent="handleSubmit">
        <!-- Username -->
        <div class="form-group">
          <label>{{ $t('auth.username') }}</label>
          <input 
            v-model="form.username" 
            type="text" 
            :placeholder="$t('auth.usernamePlaceholder')"
            required
            minlength="3"
          />
        </div>

        <!-- Password -->
        <div class="form-group">
          <label>{{ $t('auth.password') }}</label>
          <input 
            v-model="form.password" 
            type="password" 
            :placeholder="$t('auth.passwordPlaceholder')"
            required
            :minlength="isLogin ? 1 : 6"
          />
        </div>

        <!-- Name (Register only) -->
        <div v-if="!isLogin" class="form-group">
          <label>{{ $t('auth.fullName') }}</label>
          <input 
            v-model="form.name" 
            type="text" 
            :placeholder="$t('auth.namePlaceholder')"
          />
        </div>

        <!-- Email (Register only) -->
        <div v-if="!isLogin" class="form-group">
          <label>{{ $t('auth.email') }}</label>
          <input 
            v-model="form.email" 
            type="email" 
            :placeholder="$t('auth.emailPlaceholder')"
          />
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-message">{{ error }}</div>
        
        <!-- Success Message -->
        <div v-if="success" class="success-message">{{ success }}</div>

        <!-- Loading State -->
        <button 
          type="submit" 
          :disabled="loading"
          class="btn-submit"
        >
          {{ loading ? $t('common.loading') : (isLogin ? $t('auth.login') : $t('auth.register')) }}
        </button>
      </form>

      <!-- Toggle Login/Register -->
      <p class="toggle">
        {{ isLogin ? $t('auth.noAccount') : $t('auth.hasAccount') }}
        <button 
          type="button" 
          @click="toggleMode"
          class="toggle-btn"
        >
          {{ isLogin ? $t('auth.register') : $t('auth.login') }}
        </button>
      </p>
    </div>
  </div>
</template>

<script>
import api from "../lib/api";
import { submitAuthFlow } from "./authFlow";

export default {
  name: 'AuthForm',
  data() {
    return {
      isLogin: true,
      form: {
        username: '',
        password: '',
        name: '',
        email: ''
      },
      loading: false,
      error: null,
      success: null
    }
  },
  methods: {
    toggleMode() {
      this.isLogin = !this.isLogin
      this.error = null
      this.success = null
      this.form = {
        username: '',
        password: '',
        name: '',
        email: ''
      }
    },
    async handleSubmit() {
      this.error = null
      this.success = null
      this.loading = true

      try {
        const result = await submitAuthFlow({
          apiClient: api,
          router: this.$router,
          route: this.$route,
          form: this.form,
          isLogin: this.isLogin,
        })

        this.success = result.success
      } catch (err) {
        const apiError = err.response?.data?.error
        this.error = apiError || err.message || this.$t('auth.fallbackError')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 5px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.success-message {
  background: #efe;
  color: #3c3;
  padding: 0.75rem;
  border-radius: 5px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.btn-submit {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.toggle-btn {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

.toggle-btn:hover {
  color: #764ba2;
}
</style>
