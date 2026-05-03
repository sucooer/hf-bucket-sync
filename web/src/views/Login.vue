<template>
  <div
    class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
    :style="loginBgStyle"
  >
    <div class="absolute inset-0 bg-gradient-to-br from-black/55 via-black/45 to-slate-900/65"></div>
    <div class="absolute inset-0 backdrop-blur-[1px]"></div>

    <div class="relative w-full max-w-sm rounded-3xl border border-white/40 bg-white/15 backdrop-blur-2xl p-6 md:p-7 shadow-[0_20px_60px_rgba(0,0,0,0.45)]">
      <div class="w-14 h-14 mx-auto mb-4 rounded-2xl bg-white/85 text-cyan-700 flex items-center justify-center shadow-lg shadow-cyan-900/20">
        <LockClosedIcon class="w-7 h-7" />
      </div>
      <h1 class="text-4xl font-black text-white mb-2 tracking-tight text-center" style="font-family: 'Space Grotesk', 'DM Sans', sans-serif;">欢迎回来</h1>
      <p class="text-base text-cyan-50/90 mb-8 text-center">请输入密码以继续</p>
      <input
        v-model="password"
        type="password"
        class="input !bg-white/90 !border-cyan-100 !text-slate-800 mb-4 !placeholder:text-slate-400"
        placeholder="输入您的密码..."
        @keyup.enter="handleLogin"
      />
      <button @click="handleLogin" class="btn-primary w-full !rounded-2xl" :disabled="loading">
        {{ loading ? '登录中...' : '登录  →' }}
      </button>
      <p v-if="error" class="text-rose-400 text-sm mt-3 text-center">{{ error }}</p>
      <div class="mt-8 pt-5 border-t border-white/30 text-center">
        <p class="text-cyan-100 text-sm font-semibold flex items-center justify-center gap-2">
          <ShieldCheckIcon class="w-4 h-4" />
          安全连接
        </p>
        <p class="text-cyan-100/70 text-xs mt-1">仅授权用户可访问控制台</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api'
import { setAuthToken, setAuthExpiry, refreshAuthExpiry } from '@/composables/useAuth'
import { LockClosedIcon, ShieldCheckIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const password = ref('')
const loading = ref(false)
const error = ref('')
const SITE_TITLE = import.meta.env.VITE_SITE_TITLE || 'HF Bucket Sync'

const LOGIN_BG_DEFAULT = 'radial-gradient(ellipse at top right, rgba(91,120,255,0.25), transparent 40%), radial-gradient(ellipse at top left, rgba(57,255,207,0.15), transparent 35%), #0f1117'
const LOGIN_BG_PC = import.meta.env.VITE_LOGIN_BG_PC || ''
const LOGIN_BG_MOBILE = import.meta.env.VITE_LOGIN_BG_MOBILE || ''

const loginBgStyle = computed(() => {
  const isMobile = window.innerWidth < 768
  const bg = isMobile ? (LOGIN_BG_MOBILE || LOGIN_BG_PC) : (LOGIN_BG_PC || LOGIN_BG_MOBILE)
  if (!bg) return { background: LOGIN_BG_DEFAULT }
  return {
    backgroundImage: `url("${bg}")`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
    backgroundColor: '#0f1117'
  }
})

async function handleLogin() {
  if (!password.value.trim()) {
    error.value = '请输入密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await authApi.login(password.value.trim())
    if (!res?.data?.token) {
      throw new Error('登录响应缺少 token')
    }
    setAuthToken(res.data.token)
    refreshAuthExpiry()
    if (res.data.expires_at_epoch) {
      setAuthExpiry(Number(res.data.expires_at_epoch) * 1000)
    } else if (res.data.expires_at) {
      setAuthExpiry(res.data.expires_at)
    }
    router.replace('/')
  } catch (e) {
    error.value = e?.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>
