import { ref, watch, onMounted } from 'vue'

const theme = ref('system')
const isDark = ref(false)

const STORAGE_KEY = 'hf-bucket-sync-theme'

function getSystemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function updateDarkMode() {
  const dark = theme.value === 'dark' || (theme.value === 'system' && getSystemTheme())
  isDark.value = dark

  if (dark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

function setTheme(newTheme) {
  theme.value = newTheme
  localStorage.setItem(STORAGE_KEY, newTheme)
  updateDarkMode()
}

function toggleTheme() {
  if (theme.value === 'light') {
    setTheme('dark')
  } else if (theme.value === 'dark') {
    setTheme('system')
  } else {
    setTheme('light')
  }
}

function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && ['light', 'dark', 'system'].includes(saved)) {
    theme.value = saved
  }
  updateDarkMode()

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (theme.value === 'system') {
      updateDarkMode()
    }
  })
}

export function useTheme() {
  onMounted(() => {
    initTheme()
  })

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme
  }
}

export default useTheme