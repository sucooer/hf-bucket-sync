<template>
  <div class="flex h-screen bg-slate-50/50 selection:bg-blue-100 selection:text-blue-700">
    <!-- Mobile Menu Button -->
    <button
      v-if="isMobile"
      @click="sidebarOpen = !sidebarOpen"
      class="fixed top-5 left-4 z-50 p-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all duration-300"
    >
      <Bars3Icon v-if="!sidebarOpen" class="w-6 h-6" />
      <XMarkIcon v-else class="w-6 h-6" />
    </button>

    <!-- Mobile Overlay -->
    <transition name="fade">
      <div
        v-if="isMobile && sidebarOpen"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-30"
        @click="sidebarOpen = false"
      ></div>
    </transition>

    <!-- Sidebar -->
    <aside
      class="w-64 bg-slate-900 text-white flex flex-col transition-all duration-500 shrink-0"
      :class="{
        'fixed inset-y-0 left-0 z-40 translate-x-0': sidebarOpen && isMobile,
        'fixed inset-y-0 left-0 z-40 -translate-x-full lg:translate-x-0 lg:z-30': !sidebarOpen && isMobile,
        'hidden lg:flex': isMobile && !sidebarOpen
      }"
    >
      <!-- Sidebar Pattern Overlay -->
      <div class="absolute inset-0 opacity-[0.03] pointer-events-none overflow-hidden">
        <div class="absolute -top-24 -left-24 w-64 h-64 bg-blue-500 rounded-full blur-[100px]"></div>
        <div class="absolute top-1/2 left-1/2 w-48 h-48 bg-purple-500 rounded-full blur-[100px]"></div>
      </div>

      <div class="p-8 relative">
        <div class="flex items-center gap-4 group cursor-pointer">
          <div class="w-12 h-12 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-blue-500/50 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500">
            <ArrowsRightLeftIcon class="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 class="text-xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">HF Sync</h1>
            <p class="text-[10px] font-bold text-blue-400 tracking-[0.2em] uppercase opacity-70">Engine</p>
          </div>
        </div>
      </div>
      
      <nav class="flex-1 px-6 space-y-2 relative">
        <router-link to="/" class="sidebar-link group" :class="{ active: $route.path === '/' }">
          <ChartBarIcon class="w-5 h-5 group-hover:scale-110 transition-transform" />
          控制台
        </router-link>
        <router-link to="/files" class="sidebar-link group" :class="{ active: $route.path === '/files' }">
          <FolderIcon class="w-5 h-5 group-hover:scale-110 transition-transform" />
          文件浏览
        </router-link>
        <router-link to="/sync" class="sidebar-link group" :class="{ active: $route.path === '/sync' }">
          <ArrowsRightLeftIcon class="w-5 h-5 group-hover:scale-110 transition-transform" />
          同步任务
        </router-link>
        <router-link to="/schedule" class="sidebar-link group" :class="{ active: $route.path === '/schedule' }">
          <ClockIcon class="w-5 h-5 group-hover:scale-110 transition-transform" />
          定时任务
        </router-link>
        <router-link to="/notifications" class="sidebar-link group" :class="{ active: $route.path === '/notifications' }">
          <BellIcon class="w-5 h-5 group-hover:scale-110 transition-transform" />
          通知设置
        </router-link>
      </nav>

      <div class="p-8 mt-auto relative">
        <div class="glass p-4 rounded-2xl bg-white/5 border-white/5 space-y-3">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Node Status</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-500">v1.0.0</span>
            <span class="text-[10px] font-mono text-blue-400/50">STABLE</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden relative bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-50/50 via-slate-50 to-slate-50">
      <header class="h-20 glass sticky top-0 z-20 flex items-center justify-between px-4 md:px-10 border-b border-slate-200/50">
        <div class="flex items-center gap-4 pl-10 lg:pl-0">
          <div class="hidden md:flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-full border border-slate-200">
            <div class="w-2 h-2 rounded-full bg-blue-500"></div>
            <span class="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Hugging Face Cluster</span>
          </div>
          <span class="hidden md:inline text-slate-300">/</span>
          <h2 class="text-slate-900 font-bold tracking-tight">{{ currentRouteName }}</h2>
        </div>
        
        <div class="flex items-center gap-4 md:gap-6">
          <div class="relative">
            <button
              @click="notifOpen = !notifOpen"
              class="relative p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all duration-300"
            >
              <BellIcon class="w-6 h-6" />
              <span v-if="notifications.length" class="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
            </button>

            <transition name="fade">
              <div v-if="notifOpen" class="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden z-50">
                <div class="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                  <h4 class="font-bold text-slate-900">通知消息</h4>
                  <router-link to="/notifications" @click="notifOpen = false" class="text-xs text-blue-600 hover:underline">设置</router-link>
                </div>
                <div class="max-h-96 overflow-y-auto">
                  <div v-if="notifications.length === 0" class="p-8 text-center text-slate-400 text-sm">
                    暂无通知消息
                  </div>
                  <div v-else>
                    <div
                      v-for="n in notifications"
                      :key="n.id"
                      class="px-4 py-3 border-b border-slate-50 hover:bg-slate-50 transition-colors"
                    >
                      <div class="flex items-start gap-3">
                        <div :class="n.type === 'success' ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'" class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0">
                          <CheckCircleIcon v-if="n.type === 'success'" class="w-4 h-4" />
                          <ExclamationCircleIcon v-else class="w-4 h-4" />
                        </div>
                        <div class="min-w-0 flex-1">
                          <p class="text-sm font-medium text-slate-900 truncate">{{ n.title }}</p>
                          <p class="text-xs text-slate-500 mt-0.5 truncate">{{ n.message }}</p>
                          <p class="text-[10px] text-slate-400 mt-1">{{ n.time }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>

        <div v-if="notifOpen" class="fixed inset-0 z-40" @click="notifOpen = false"></div>
      </header>

      <div class="flex-1 overflow-auto custom-scrollbar">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  ChartBarIcon,
  FolderIcon,
  ArrowsRightLeftIcon,
  ClockIcon,
  BellIcon,
  Bars3Icon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const sidebarOpen = ref(false)
const notifOpen = ref(false)
const windowWidth = ref(window.innerWidth)
const notifications = ref([
  { id: 1, type: 'success', title: '同步任务完成', message: 'anyaer007/nixeu 同步成功，上传 12 个文件', time: '2分钟前' },
  { id: 2, type: 'error', title: '同步任务失败', message: 'anyaer007/wolf 连接超时', time: '15分钟前' },
  { id: 3, type: 'success', title: '定时任务执行', message: '每日备份任务已执行完成', time: '2小时前' }
])

const isMobile = computed(() => windowWidth.value < 1024)

const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (!isMobile.value) {
    sidebarOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize()
})

watch(() => route.path, () => {
  if (isMobile.value) {
    sidebarOpen.value = false
  }
  notifOpen.value = false
})

const currentRouteName = computed(() => {
  const map = {
    '/': 'System Overview',
    '/files': 'File Explorer',
    '/sync': 'Transfer Hub',
    '/schedule': 'Automation Engine',
    '/notifications': 'Notification Settings'
  }
  return map[route.path] || 'Dashboard'
})
</script>
