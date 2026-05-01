import { ref, watch } from 'vue'

const STORAGE_KEY = 'hf-bucket-sync-theme'
const themeMode = ref(localStorage.getItem(STORAGE_KEY) || 'light')

function getSystemDark() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function applyTheme() {
  const isDark = themeMode.value === 'dark' || (themeMode.value === 'system' && getSystemDark())
  if (isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

export function setThemeMode(mode) {
  themeMode.value = mode
  localStorage.setItem(STORAGE_KEY, mode)
  applyTheme()
}

export function cycleTheme() {
  if (themeMode.value === 'light') {
    setThemeMode('dark')
  } else if (themeMode.value === 'dark') {
    setThemeMode('system')
  } else {
    setThemeMode('light')
  }
}

export function initTheme() {
  applyTheme()
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (themeMode.value === 'system') {
      applyTheme()
    }
  })
}

export { themeMode }