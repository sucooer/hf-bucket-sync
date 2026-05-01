const AUTH_TOKEN_KEY = 'auth_token'
const AUTH_EXPIRES_AT_KEY = 'auth_expires_at'

function getTimeoutMinutes() {
  const raw = Number(import.meta.env.VITE_AUTH_TIMEOUT_MINUTES)
  if (!Number.isFinite(raw) || raw <= 0) return 60
  return raw
}

export function getTimeoutMs() {
  return getTimeoutMinutes() * 60 * 1000
}

export function setAuthToken(token) {
  localStorage.setItem(AUTH_TOKEN_KEY, token)
  refreshAuthExpiry()
}

export function setAuthExpiry(expiresAt) {
  let value = Number(expiresAt)
  if (!Number.isFinite(value) || value <= 0) {
    const parsed = new Date(expiresAt).getTime()
    value = Number(parsed)
  }
  if (!Number.isFinite(value) || value <= 0) return false
  localStorage.setItem(AUTH_EXPIRES_AT_KEY, String(value))
  return true
}

export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY) || ''
}

export function clearAuth() {
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem(AUTH_EXPIRES_AT_KEY)
}

export function refreshAuthExpiry() {
  const token = getAuthToken()
  if (!token) return
  localStorage.setItem(AUTH_EXPIRES_AT_KEY, String(Date.now() + getTimeoutMs()))
}

export function isAuthExpired() {
  const expiresAt = Number(localStorage.getItem(AUTH_EXPIRES_AT_KEY) || 0)
  if (!expiresAt) return true
  return Date.now() > expiresAt
}

export function isAuthenticated() {
  const token = getAuthToken()
  return !!token && !isAuthExpired()
}

export function logout() {
  clearAuth()
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}
