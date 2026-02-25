<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  email: '',
  password: '',
  passwordConfirm: '',
  full_name: '',
  phone: '',
  gender: null
})

const loading = ref(false)
const error = ref('')
const passwordError = ref('')
const formErrors = ref({
  email: '',
  full_name: '',
  phone: '',
  gender: ''
})

// Telefon input handler - sadece sayı ve tanınan karakterler
const handlePhoneInput = (event) => {
  let value = event.target.value
  // Sadece rakamlar, +, -, (, ), boşluk ve . karakterlerine izin ver
  const cleaned = value.replace(/[^\d\+\-() \.]/g, '')
  if (cleaned !== value) {
    formData.value.phone = cleaned
  }
}

// Ad-Soyad input handler - sadece harfler ve boşluk (Türkçe karakterler dahil)
const handleNameInput = (event) => {
  let value = event.target.value
  // Sadece harfler (Latin ve Türkçe), boşluk ve tire karakterine izin ver
  const cleaned = value.replace(/[^a-zA-ZçğıöşüÇĞİÖŞÜ\s\-]/g, '')
  if (cleaned !== value) {
    formData.value.full_name = cleaned
  }
}

// Email validasyonu
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Telefon validasyonu
const validatePhone = (phone) => {
  // Minimum 10 rakam gereksini
  const digits = phone.replace(/\D/g, '')
  return digits.length >= 10
}

// Password gücü göstergesi
const getPasswordStrength = () => {
  const pwd = formData.value.password
  let strength = 0
  if (pwd.length >= 8) strength++
  if (pwd.length >= 12) strength++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++
  if (/\d/.test(pwd)) strength++
  if (/[^a-zA-Z\d]/.test(pwd)) strength++
  return strength
}

const getPasswordStrengthLabel = () => {
  const strength = getPasswordStrength()
  const labels = ['', 'Zayıf', 'Orta', 'İyi', 'Güçlü', 'Çok Güçlü']
  return labels[strength] || ''
}

const getPasswordStrengthColor = () => {
  const strength = getPasswordStrength()
  const colors = ['', 'text-red-400', 'text-amber-400', 'text-yellow-400', 'text-lime-400', 'text-green-400']
  return colors[strength] || ''
}

const validateForm = () => {
  formErrors.value = {
    email: '',
    full_name: '',
    phone: '',
    gender: ''
  }

  if (!formData.value.email || !validateEmail(formData.value.email)) {
    formErrors.value.email = 'Geçerli bir email adresi girin'
  }

  if (!formData.value.full_name || formData.value.full_name.trim().length < 3) {
    formErrors.value.full_name = 'Ad Soyadı en az 3 karakter olmalıdır'
  }

  if (!formData.value.phone || !validatePhone(formData.value.phone)) {
    formErrors.value.phone = 'Geçerli bir telefon numarası girin (en az 10 rakam)'
  }

  if (!formData.value.gender) {
    formErrors.value.gender = 'Cinsiyet seçiniz'
  }

  return !Object.values(formErrors.value).some(err => err !== '')
}

const validatePasswords = () => {
  if (formData.value.password !== formData.value.passwordConfirm) {
    passwordError.value = 'Şifreler eşleşmiyor'
    return false
  }
  if (formData.value.password.length < 8) {
    passwordError.value = 'Şifre en az 8 karakter olmalıdır'
    return false
  }
  passwordError.value = ''
  return true
}

const handleSignUp = async () => {
  if (!validateForm()) {
    return
  }

  if (!validatePasswords()) {
    return
  }

  loading.value = true
  error.value = ''
  try {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
    
    const registerData = {
      email: formData.value.email,
      password: formData.value.password,
      full_name: formData.value.full_name,
      phone: formData.value.phone,
      gender: formData.value.gender
    }

    const response = await fetch(`${baseUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(registerData)
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || 'Kayıt başarısız')
    }

    // Register endpoint returns Token with access_token and user
    const data = await response.json()
    
    // Set auth state with returned token and user data
    authStore.token = data.access_token
    authStore.user = data.user
    
    // Persist to localStorage
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    
    // Navigate to home
    router.push('/')
  } catch (err) {
    error.value = err.message || 'Kayıt sırasında bir hata oluştu'
    console.error('Sign up error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-dark-bg">
    <div class="relative hh-section min-h-screen flex items-center justify-center px-4 sm:px-6 py-10">
      <div class="w-full max-w-md">
        <!-- Sign Up Form -->
        <div class="w-full">
          <!-- Mobile Logo/Branding -->
          <div class="lg:hidden text-center mb-8">
            <div class="inline-flex items-center justify-center p-3 rounded-2xl bg-gradient-to-br from-primary to-blue-600 shadow-lg shadow-primary/30 mb-4">
              <span class="material-symbols-outlined text-white text-3xl">hourglass_top</span>
            </div>
            <h1 class="text-2xl font-bold text-white mb-2">HotHour</h1>
            <p class="text-slate-400 text-sm">Pilates Oturumları Platformu</p>
          </div>

          <div class="hh-glass-card rounded-2xl p-6 sm:p-8 border border-white/10 shadow-glow backdrop-blur-xl bg-dark-bg/80">
            <div class="mb-6 text-center lg:text-left">
              <p class="text-neon-blue text-xs uppercase tracking-widest mb-2 font-bold">Yeni Hesap Oluştur</p>
              <h2 class="text-2xl sm:text-3xl font-bold text-white">Katılın</h2>
              <p class="text-slate-400 mt-2 text-sm">Harika pilates oturumları için hesap oluşturun</p>
            </div>

            <form @submit.prevent="handleSignUp" class="space-y-4">
              <div v-if="error" class="bg-red-500/10 border border-red-500 text-red-300 p-3 rounded-lg text-sm text-center">
                {{ error }}
              </div>

              <!-- Full Name -->
              <div>
                <label for="full_name" class="block text-sm font-medium text-slate-300 mb-1.5">Ad Soyadı</label>
                <input
                  v-model="formData.full_name"
                  @input="handleNameInput"
                  id="full_name"
                  type="text"
                  required
                  class="block w-full bg-dark-bg/60 border rounded-lg py-2.5 px-3 text-white focus:outline-none focus:ring-1 transition"
                  :class="formErrors.full_name ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-slate-700 focus:border-neon-blue focus:ring-neon-blue'"
                  placeholder="Adınız Soyadınız"
                />
                <div v-if="formErrors.full_name" class="text-red-400 text-xs mt-1">{{ formErrors.full_name }}</div>
              </div>

              <!-- Email -->
              <div>
                <label for="email" class="block text-sm font-medium text-slate-300 mb-1.5">E-posta Adresi</label>
                <input
                  v-model="formData.email"
                  id="email"
                  type="email"
                  required
                  class="block w-full bg-dark-bg/60 border rounded-lg py-2.5 px-3 text-white focus:outline-none focus:ring-1 transition"
                  :class="formErrors.email ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-slate-700 focus:border-neon-blue focus:ring-neon-blue'"
                  placeholder="ornek@email.com"
                />
                <div v-if="formErrors.email" class="text-red-400 text-xs mt-1">{{ formErrors.email }}</div>
              </div>

              <!-- Phone -->
              <div>
                <label for="phone" class="block text-sm font-medium text-slate-300 mb-1.5">Telefon</label>
                <input
                  v-model="formData.phone"
                  @input="handlePhoneInput"
                  id="phone"
                  type="tel"
                  required
                  class="block w-full bg-dark-bg/60 border rounded-lg py-2.5 px-3 text-white focus:outline-none focus:ring-1 transition"
                  :class="formErrors.phone ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-slate-700 focus:border-neon-blue focus:ring-neon-blue'"
                  placeholder="+90 (5XX) XXX XX XX"
                />
                <div v-if="formErrors.phone" class="text-red-400 text-xs mt-1">{{ formErrors.phone }}</div>
              </div>

              <!-- Gender -->
              <div>
                <label for="gender" class="block text-sm font-medium text-slate-300 mb-1.5">Cinsiyet</label>
                <select
                  v-model="formData.gender"
                  id="gender"
                  required
                  class="block w-full bg-dark-bg/60 border rounded-lg py-2.5 px-3 text-white focus:outline-none focus:ring-1 transition"
                  :class="formErrors.gender ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-slate-700 focus:border-neon-blue focus:ring-neon-blue'"
                >
                  <option :value="null">Seçiniz</option>
                  <option value="FEMALE">Kadın</option>
                  <option value="MALE">Erkek</option>
                </select>
                <div v-if="formErrors.gender" class="text-red-400 text-xs mt-1">{{ formErrors.gender }}</div>
              </div>

              <!-- Password -->
              <div>
                <label for="password" class="block text-sm font-medium text-slate-300 mb-1.5">
                  Şifre
                  <span v-if="formData.password" :class="getPasswordStrengthColor()" class="text-xs ml-2">
                    ({{ getPasswordStrengthLabel() }})
                  </span>
                </label>
                <input
                  v-model="formData.password"
                  id="password"
                  type="password"
                  required
                  class="block w-full bg-dark-bg/60 border border-slate-700 rounded-lg py-2.5 px-3 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue"
                  placeholder="En az 8 karakter"
                />
                <div v-if="formData.password" class="mt-1.5 text-xs text-slate-400">
                  <div class="flex items-center gap-2 mb-1">
                    <div class="h-1 w-16 bg-slate-700 rounded flex-1" :class="{
                      'bg-red-500': getPasswordStrength() === 1,
                      'bg-amber-500': getPasswordStrength() === 2,
                      'bg-yellow-500': getPasswordStrength() === 3,
                      'bg-lime-500': getPasswordStrength() === 4,
                      'bg-green-500': getPasswordStrength() === 5
                    }"></div>
                  </div>
                  <ul class="space-y-0.5">
                    <li :class="formData.password.length >= 8 ? 'text-green-400' : 'text-slate-500'">✓ En az 8 karakter</li>
                    <li :class="/[A-Z]/.test(formData.password) && /[a-z]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'">✓ Büyük ve küçük harf</li>
                    <li :class="/\d/.test(formData.password) ? 'text-green-400' : 'text-slate-500'">✓ En az bir sayı</li>
                    <li :class="/[^a-zA-Z\d]/.test(formData.password) ? 'text-green-400' : 'text-slate-500'">✓ Özel karakter</li>
                  </ul>
                </div>
              </div>

              <!-- Password Confirmation -->
              <div>
                <label for="passwordConfirm" class="block text-sm font-medium text-slate-300 mb-1.5">Şifre Tekrarı</label>
                <input
                  v-model="formData.passwordConfirm"
                  id="passwordConfirm"
                  type="password"
                  required
                  class="block w-full bg-dark-bg/60 border rounded-lg py-2.5 px-3 text-white focus:outline-none focus:ring-1 transition"
                  :class="passwordError && formData.passwordConfirm ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-slate-700 focus:border-neon-blue focus:ring-neon-blue'"
                  placeholder="Şifreyi tekrarla"
                />
              </div>

              <!-- Password Validation Error -->
              <div v-if="passwordError" class="bg-amber-500/10 border border-amber-500 text-amber-300 p-2.5 rounded-lg text-xs text-center">
                {{ passwordError }}
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="w-full hh-btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed mt-5"
              >
                <span v-if="loading" class="flex items-center justify-center gap-2">
                  <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Hesap Oluşturuluyor...
                </span>
                <span v-else>Kayıt Ol</span>
              </button>
            </form>

            <div class="mt-5 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-slate-500">
              <span>Şifreleme ile korunan kayıt</span>
              <router-link to="/login" class="text-neon-blue hover:text-white transition-colors">Giriş Yap</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
