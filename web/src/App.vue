<template>
  <div class="flex h-screen bg-[#0f1117] selection:bg-blue-100 selection:text-blue-700 text-slate-100">
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
      class="bg-white/[0.03] backdrop-blur-xl border-r border-white/10 text-white flex flex-col transition-all duration-500 shrink-0"
      :class="[
        sidebarCollapsed ? 'w-[92px]' : 'w-[220px]',
        isMobile ? 'w-[92px]' : '',
        {
          'fixed inset-y-0 left-0 z-40 translate-x-0': sidebarOpen && isMobile,
          'fixed inset-y-0 left-0 z-40 -translate-x-full lg:translate-x-0 lg:z-30': !sidebarOpen && isMobile,
          'hidden lg:flex': isMobile && !sidebarOpen
        }
      ]"
    >
      <div class="pt-6 pb-4 px-4 relative flex justify-center">
        <div class="w-12 h-12 bg-gradient-to-tr from-cyan-400 to-lime-300 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/30">
          <ArrowsRightLeftIcon class="w-6 h-6 text-slate-900" />
        </div>
      </div>
      
      <nav class="flex-1 px-3 space-y-3 relative">
        <router-link to="/" class="sidebar-link !py-3" :class="[ $route.path === '/' ? 'active' : '', sidebarCollapsed ? '!justify-center !px-0' : '!justify-start !px-4' ]" title="控制台">
          <ChartBarIcon class="w-5 h-5" />
          <span v-if="!sidebarCollapsed" class="text-sm">控制台</span>
        </router-link>
        <router-link to="/files" class="sidebar-link !py-3" :class="[ $route.path === '/files' ? 'active' : '', sidebarCollapsed ? '!justify-center !px-0' : '!justify-start !px-4' ]" title="文件浏览">
          <FolderIcon class="w-5 h-5" />
          <span v-if="!sidebarCollapsed" class="text-sm">文件浏览</span>
        </router-link>
        <router-link to="/sync" class="sidebar-link !py-3" :class="[ $route.path === '/sync' ? 'active' : '', sidebarCollapsed ? '!justify-center !px-0' : '!justify-start !px-4' ]" title="同步任务">
          <ArrowsRightLeftIcon class="w-5 h-5" />
          <span v-if="!sidebarCollapsed" class="text-sm">同步任务</span>
        </router-link>
        <router-link to="/schedule" class="sidebar-link !py-3" :class="[ $route.path === '/schedule' ? 'active' : '', sidebarCollapsed ? '!justify-center !px-0' : '!justify-start !px-4' ]" title="定时任务">
          <ClockIcon class="w-5 h-5" />
          <span v-if="!sidebarCollapsed" class="text-sm">定时任务</span>
        </router-link>
        <router-link to="/notifications" class="sidebar-link !py-3" :class="[ $route.path === '/notifications' ? 'active' : '', sidebarCollapsed ? '!justify-center !px-0' : '!justify-start !px-4' ]" title="通知设置">
          <BellIcon class="w-5 h-5" />
          <span v-if="!sidebarCollapsed" class="text-sm">通知设置</span>
        </router-link>
      </nav>

      <div class="pb-5 px-3">
        <button
          class="w-full h-11 rounded-xl border border-white/10 bg-white/[0.04] text-slate-300 hover:text-white hover:bg-white/10 transition-all"
          @click="toggleSidebarCollapse"
          :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
        >
          <ChevronRightIcon v-if="sidebarCollapsed" class="w-5 h-5 mx-auto" />
          <ChevronLeftIcon v-else class="w-5 h-5 mx-auto" />
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden relative bg-[radial-gradient(ellipse_at_top_right,_rgba(91,120,255,0.14),_transparent_40%),radial-gradient(ellipse_at_top_left,_rgba(57,255,207,0.08),_transparent_35%),#111317]">
      <div class="fixed top-6 right-6 z-30">
        <div class="h-16 px-4 rounded-3xl border border-white/10 bg-black/25 backdrop-blur-xl flex items-center gap-2 shadow-2xl">
          <button
            @click="isMobile ? (sidebarOpen = !sidebarOpen) : reloadPage()"
            class="p-2.5 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300"
            :title="isMobile ? (sidebarOpen ? '关闭菜单' : '打开菜单') : '刷新'"
          >
            <Bars3Icon v-if="isMobile && !sidebarOpen" class="w-5 h-5" />
            <XMarkIcon v-else-if="isMobile && sidebarOpen" class="w-5 h-5" />
            <ArrowPathIcon v-else class="w-5 h-5" />
          </button>
          <button
            @click="toggleTheme"
            class="p-2.5 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300"
            title="切换主题"
          >
            <SunIcon v-if="isDark" class="w-5 h-5" />
            <MoonIcon v-else class="w-5 h-5" />
          </button>

          <div class="relative">
            <button
              @click="notifOpen = !notifOpen"
              class="relative p-2.5 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300"
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

      <div class="flex-1 overflow-auto custom-scrollbar pt-20">
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
  ChevronRightIcon,
  ChevronLeftIcon,
  Bars3Icon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/vue/24/outline'
import { themeMode, initTheme, cycleTheme } from '@/composables/useTheme'

const route = useRoute()
const sidebarOpen = ref(false)
const notifOpen = ref(false)
const notifications = ref([])
const windowWidth = ref(window.innerWidth)
const sidebarCollapsed = ref(true)

const isDark = computed(() => {
  if (themeMode.value === 'dark') return true
  if (themeMode.value === 'light') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
})

const toggleTheme = cycleTheme

const isMobile = computed(() => windowWidth.value < 1024)

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
})

watch(() => route.path, () => {
  if (isMobile.value) {
    sidebarOpen.value = false
  }
  notifOpen.value = false
})

function reloadPage() {
  window.location.reload()
}

function toggleSidebarCollapse() {
  if (isMobile.value) return
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>
