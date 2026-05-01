import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/main.css'

import Dashboard from './views/Dashboard.vue'
import FileBrowser from './views/FileBrowser.vue'
import SyncTask from './views/SyncTask.vue'
import Schedule from './views/Schedule.vue'
import NotificationSettings from './views/NotificationSettings.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/files', name: 'FileBrowser', component: FileBrowser },
  { path: '/sync', name: 'SyncTask', component: SyncTask },
  { path: '/schedule', name: 'Schedule', component: Schedule },
  { path: '/notifications', name: 'NotificationSettings', component: NotificationSettings },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')