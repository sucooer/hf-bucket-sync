<template>
  <router-view v-if="isLoginPage" />
  <div v-else class="flex h-screen app-shell selection:bg-blue-100 selection:text-blue-700 text-slate-100">
    <!-- Mobile Overlay -->
    <transition name="fade">
      <div
        v-if="isMobile && sidebarOpen"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-30"
        @click="sidebarOpen = false"
      ></div>
    </transition>

    <!-- Sidebar Container -->
    <div
      class="md:m-4 md:h-[calc(100vh-32px)] rounded-3xl border border-white/10 app-panel backdrop-blur-xl shadow-2xl overflow-hidden"
      :class="[
        isMobile ? (sidebarOpen ? 'w-[220px]' : 'w-[92px]') : (sidebarCollapsed ? 'w-[92px]' : 'w-[220px]'),
        {
          'fixed top-3 bottom-3 left-3 z-40 translate-x-0 h-auto': sidebarOpen && isMobile,
          'fixed top-3 bottom-3 left-3 z-40 -translate-x-full lg:translate-x-0 lg:z-30 h-auto': !sidebarOpen && isMobile,
          'hidden lg:flex': isMobile && !sidebarOpen
        }
      ]"
    >
    <aside
      class="h-full text-white flex flex-col transition-all duration-500 shrink-0"
    >
      <div class="pt-5 pb-4 px-3 relative flex items-center justify-center">
        <button
          class="w-11 h-11 bg-gradient-to-tr from-cyan-400 to-lime-300 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/30 shrink-0 hover:brightness-110 transition-all"
          @click="toggleSidebarCollapse"
          :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
        >
          <ArrowsRightLeftIcon class="w-5 h-5 text-slate-900" />
        </button>
      </div>
      
      <nav class="flex-1 px-3 space-y-3 relative">
        <router-link to="/" class="sidebar-link !py-3" :class="[ $route.path === '/' ? 'active' : '', showSidebarLabels ? '!justify-start !px-4' : '!justify-center !px-0' ]" title="控制台">
          <ChartBarIcon class="w-5 h-5" />
          <span v-if="showSidebarLabels" class="text-sm">控制台</span>
        </router-link>
        <router-link to="/files" class="sidebar-link !py-3" :class="[ $route.path === '/files' ? 'active' : '', showSidebarLabels ? '!justify-start !px-4' : '!justify-center !px-0' ]" title="文件浏览">
          <FolderIcon class="w-5 h-5" />
          <span v-if="showSidebarLabels" class="text-sm">文件浏览</span>
        </router-link>
        <router-link to="/sync" class="sidebar-link !py-3" :class="[ $route.path === '/sync' ? 'active' : '', showSidebarLabels ? '!justify-start !px-4' : '!justify-center !px-0' ]" title="同步任务">
          <ArrowsRightLeftIcon class="w-5 h-5" />
          <span v-if="showSidebarLabels" class="text-sm">同步任务</span>
        </router-link>
        <router-link to="/schedule" class="sidebar-link !py-3" :class="[ $route.path === '/schedule' ? 'active' : '', showSidebarLabels ? '!justify-start !px-4' : '!justify-center !px-0' ]" title="定时任务">
          <ClockIcon class="w-5 h-5" />
          <span v-if="showSidebarLabels" class="text-sm">定时任务</span>
        </router-link>
        <router-link to="/notifications" class="sidebar-link !py-3" :class="[ $route.path === '/notifications' ? 'active' : '', showSidebarLabels ? '!justify-start !px-4' : '!justify-center !px-0' ]" title="通知设置">
          <BellIcon class="w-5 h-5" />
          <span v-if="showSidebarLabels" class="text-sm">通知设置</span>
        </router-link>
        <router-link to="/theme" class="sidebar-link !py-3" :class="[ $route.path === '/theme' ? 'active' : '', showSidebarLabels ? '!justify-start !px-4' : '!justify-center !px-0' ]" title="主题设置">
          <SwatchIcon class="w-5 h-5" />
          <span v-if="showSidebarLabels" class="text-sm">主题设置</span>
        </router-link>
        <router-link to="/audit" class="sidebar-link !py-3" :class="[ $route.path === '/audit' ? 'active' : '', showSidebarLabels ? '!justify-start !px-4' : '!justify-center !px-0' ]" title="审计日志">
          <DocumentTextIcon class="w-5 h-5" />
          <span v-if="showSidebarLabels" class="text-sm">审计日志</span>
        </router-link>
      </nav>

    </aside>
    </div>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden relative app-shell">
      <div class="fixed top-4 right-4 md:top-6 md:right-6 z-30">
        <div class="h-12 md:h-16 px-2.5 md:px-4 rounded-2xl md:rounded-3xl border border-white/10 bg-black/25 backdrop-blur-xl flex items-center gap-1 md:gap-2 shadow-2xl">
          <button
            @click="isMobile ? (sidebarOpen = !sidebarOpen) : reloadPage()"
            class="p-2 md:p-2.5 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg md:rounded-xl transition-all duration-300"
            :title="isMobile ? (sidebarOpen ? '关闭菜单' : '打开菜单') : '刷新'"
          >
            <Bars3Icon v-if="isMobile && !sidebarOpen" class="w-5 h-5" />
            <XMarkIcon v-else-if="isMobile && sidebarOpen" class="w-5 h-5" />
            <ArrowPathIcon v-else class="w-5 h-5" />
          </button>
          <button
            v-if="isMobile"
            @click="reloadPage"
            class="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-300"
            title="刷新"
          >
            <ArrowPathIcon class="w-5 h-5" />
          </button>
          <button
            @click="doLogout()"
            class="p-2 md:p-2.5 text-slate-300 hover:text-rose-300 hover:bg-white/10 rounded-lg md:rounded-xl transition-all duration-300"
            title="退出登录"
          >
            <ArrowRightOnRectangleIcon class="w-5 h-5" />
          </button>

          <div class="relative">
            <button
              @click="notifOpen = !notifOpen"
              class="relative p-2 md:p-2.5 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg md:rounded-xl transition-all duration-300"
            >
              <BellIcon class="w-5 h-5" />
              <span v-if="notifications.length > 0" class="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border border-slate-900"></span>
            </button>

            <transition name="fade">
              <div v-if="notifOpen" class="absolute right-0 mt-2 w-80 bg-slate-900/95 text-slate-100 rounded-2xl shadow-2xl border border-white/10 overflow-hidden z-50 backdrop-blur-xl">
                <div class="px-4 py-3 bg-white/5 border-b border-white/10 flex items-center justify-between">
                  <h4 class="font-bold text-slate-100">通知消息</h4>
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
                      class="px-4 py-3 border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      <div class="flex items-start gap-3">
                        <div :class="n.type === 'success' ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'" class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0">
                          <CheckCircleIcon v-if="n.type === 'success'" class="w-4 h-4" />
                          <ExclamationCircleIcon v-else class="w-4 h-4" />
                        </div>
                        <div class="min-w-0 flex-1">
                          <p class="text-sm font-medium text-slate-100 truncate">{{ n.title }}</p>
                          <p class="text-xs text-slate-400 mt-0.5 truncate">{{ n.message }}</p>
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
      </div>

      <div v-if="notifOpen" class="fixed inset-0 z-20" @click="notifOpen = false"></div>

      <div class="flex-1 overflow-auto custom-scrollbar pt-20 md:pt-10 lg:pt-6">
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
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { authApi } from '@/api'
import {
  ChartBarIcon,
  FolderIcon,
  ArrowsRightLeftIcon,
  ClockIcon,
  BellIcon,
  SwatchIcon,
  DocumentTextIcon,
  Bars3Icon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline'
import { initTheme } from '@/composables/useTheme'
import { isAuthenticated, isAuthExpired, refreshAuthExpiry, logout } from '@/composables/useAuth'

const route = useRoute()
const sidebarOpen = ref(false)
const notifOpen = ref(false)
const notifications = ref([])
const windowWidth = ref(window.innerWidth)
const sidebarCollapsed = ref(true)
let authTimer = null
const activityEvents = ['click', 'keydown', 'touchstart', 'mousemove', 'scroll']

const isMobile = computed(() => windowWidth.value < 1024)
const showSidebarLabels = computed(() => !sidebarCollapsed.value || (isMobile.value && sidebarOpen.value))
const isLoginPage = computed(() => route.path === '/login')

const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (!isMobile.value) {
    sidebarOpen.value = false
  }
}

onMounted(() => {
  initTheme()
  window.addEventListener('resize', handleResize)
  handleResize()
  startAuthSessionWatcher()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  stopAuthSessionWatcher()
})

watch(() => route.path, (newPath) => {
  if (isMobile.value) {
    sidebarOpen.value = false
  }
  notifOpen.value = false
  if (newPath === '/login') {
    stopAuthSessionWatcher()
  } else {
    startAuthSessionWatcher()
  }
})

function reloadPage() {
  window.location.reload()
}

async function doLogout() {
  try {
    await authApi.logout()
  } catch (e) {
  } finally {
    logout()
  }
}

function toggleSidebarCollapse() {
  if (isMobile.value) return
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function handleUserActivity() {
  if (isLoginPage.value) return
  if (!isAuthenticated()) return
  refreshAuthExpiry()
}

function startAuthSessionWatcher() {
  if (isLoginPage.value) return
  activityEvents.forEach(eventName => {
    window.addEventListener(eventName, handleUserActivity, { passive: true })
  })
  authTimer = window.setInterval(() => {
    if (isLoginPage.value) return
    if (isAuthExpired()) {
      logout()
    }
  }, 5000)
}

function stopAuthSessionWatcher() {
  activityEvents.forEach(eventName => {
    window.removeEventListener(eventName, handleUserActivity)
  })
  if (authTimer) {
    window.clearInterval(authTimer)
    authTimer = null
  }
}
</script>
