import axios from 'axios'
import { getAuthToken, clearAuth } from '@/composables/useAuth'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.request.use(
  config => {
    const token = getAuthToken()
    if (token) {
      config.headers['x-auth-token'] = token
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error?.response?.status === 401 && window.location.pathname !== '/login') {
      clearAuth()
      window.location.href = '/login'
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (password) => api.post('/auth/login', null, { params: { password } }),
  check: () => api.get('/auth/check'),
  logout: () => api.post('/auth/logout')
}

export const filesApi = {
  list: (path, includeHidden = false) =>
    api.get('/files/list', { params: { path, include_hidden: includeHidden } }),

  tree: (path, maxDepth = 3, includeHidden = false) =>
    api.get('/files/tree', { params: { path, max_depth: maxDepth, include_hidden: includeHidden } }),

  size: (path) =>
    api.get('/files/size', { params: { path } }),

  exists: (path) =>
    api.get('/files/exists', { params: { path } }),

  delete: (path) =>
    api.delete('/files/delete', { params: { path } }),

  rename: (path, newName) =>
    api.post('/files/rename', null, { params: { path, new_name: newName } })
}

export const bucketsApi = {
  list: () => api.get('/buckets'),

  info: (bucketId) => api.get('/buckets/info', { params: { bucket_id: bucketId } }),

  tree: (bucketId, prefix = '', recursive = true) =>
    api.get('/buckets/tree', { params: { bucket_id: bucketId, prefix, recursive } }),

  deleteFile: (bucketId, path) =>
    api.delete('/buckets/file', { params: { bucket_id: bucketId, path } }),

  renameFile: (bucketId, oldPath, newPath) =>
    api.post('/buckets/file/rename', null, { params: { bucket_id: bucketId, old_path: oldPath, new_path: newPath } })
}

export const syncApi = {
  dryRun: (data) => api.post('/sync/dry-run', data),

  execute: (data) => api.post('/sync/execute', data),

  history: (limit = 50) => api.get('/sync/history', { params: { limit } }),

  getTask: (taskId) => api.get(`/sync/task/${taskId}`)
}

export const scheduleApi = {
  list: () => api.get('/schedules'),

  create: (data) => api.post('/schedules', data),

  update: (id, data) => api.put(`/schedules/${id}`, data),

  delete: (id) => api.delete(`/schedules/${id}`)
}

export const auditApi = {
  logs: (limit = 100) => api.get('/audit/logs', { params: { limit } })
}

export default api
