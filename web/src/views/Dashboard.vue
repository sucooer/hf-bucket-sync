<template>
  <div class="p-4 md:p-6 lg:p-10 space-y-6 md:space-y-10 max-w-[1600px] mx-auto overflow-hidden">
    <!-- Header Section -->
    <div class="flex items-end justify-between animate-fade-up">
      <div>
        <h2 class="text-4xl font-black text-slate-900 tracking-tight">控制台</h2>
        <p class="text-slate-500 font-medium mt-2">实时监控您的 Hugging Face Bucket 同步状态。</p>
      </div>
      <div class="flex items-center gap-3 px-4 py-2 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div class="w-2 h-2 rounded-full bg-blue-500 animate-ping"></div>
        <span class="text-xs font-bold text-slate-600 uppercase tracking-widest">实时监控中</span>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div class="card card-hover group overflow-hidden relative animate-fade-up delay-1">
        <div class="absolute -right-6 -top-6 w-32 h-32 bg-blue-600/5 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
        <div class="relative flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">Bucket 数量</p>
            <p class="text-5xl font-black text-slate-900">{{ stats.totalBuckets }}</p>
          </div>
          <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-xl shadow-blue-500/30 group-hover:rotate-6 transition-all duration-500">
            <CubeIcon class="w-8 h-8 text-white" />
          </div>
        </div>
        <div class="mt-6 pt-6 border-t border-slate-100 flex items-center gap-2">
          <div class="px-2 py-0.5 bg-blue-50 text-blue-600 text-[10px] font-black rounded-md uppercase tracking-wider">存储</div>
          <span class="text-slate-400 text-xs font-medium">远程数据源</span>
        </div>
      </div>

      <div class="card card-hover group overflow-hidden relative animate-fade-up delay-2">
        <div class="absolute -right-6 -top-6 w-32 h-32 bg-emerald-600/5 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
        <div class="relative flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">定时任务</p>
            <p class="text-5xl font-black text-slate-900">{{ stats.totalSchedules }}</p>
          </div>
          <div class="w-16 h-16 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-2xl flex items-center justify-center shadow-xl shadow-emerald-500/30 group-hover:rotate-6 transition-all duration-500">
            <ClockIcon class="w-8 h-8 text-white" />
          </div>
        </div>
        <div class="mt-6 pt-6 border-t border-slate-100 flex items-center gap-2">
          <div class="px-2 py-0.5 bg-emerald-50 text-emerald-600 text-[10px] font-black rounded-md uppercase tracking-wider">自动化</div>
          <span class="text-slate-400 text-xs font-medium">后台运行中</span>
        </div>
      </div>

      <div class="card card-hover group overflow-hidden relative animate-fade-up delay-3">
        <div class="absolute -right-6 -top-6 w-32 h-32 bg-amber-600/5 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
        <div class="relative flex items-center justify-between">
          <div class="space-y-1">
            <p class="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">最近同步</p>
            <p class="text-5xl font-black text-slate-900">{{ stats.recentSyncs }}</p>
          </div>
          <div class="w-16 h-16 bg-gradient-to-br from-amber-400 to-amber-600 rounded-2xl flex items-center justify-center shadow-xl shadow-amber-500/30 group-hover:rotate-6 transition-all duration-500">
            <ArrowsRightLeftIcon class="w-8 h-8 text-white" />
          </div>
        </div>
        <div class="mt-6 pt-6 border-t border-slate-100 flex items-center gap-2 text-slate-400 text-xs font-medium">
          <span class="text-amber-600 font-black">历史记录</span>
          <span>最近的同步活动</span>
        </div>
      </div>
    </div>

    <!-- Lists Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
      <!-- Buckets List -->
      <div class="card glass flex flex-col h-[600px] animate-fade-up delay-4">
        <div class="flex items-center justify-between mb-8">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center shadow-inner">
              <CubeIcon class="w-5 h-5" />
            </div>
            <h3 class="text-2xl font-black text-slate-900 tracking-tight">您的 Bucket</h3>
          </div>
          <router-link to="/files" class="group flex items-center gap-2 text-blue-600 hover:text-blue-700 text-xs font-black uppercase tracking-widest transition-all">
            查看全部
            <ArrowRightIcon class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </router-link>
        </div>
        
        <div class="flex-1 overflow-y-auto pr-4 custom-scrollbar">
          <div v-if="loading.buckets" class="flex flex-col items-center justify-center h-full space-y-6">
            <div class="relative">
              <div class="w-16 h-16 border-4 border-slate-100 border-t-blue-500 rounded-full animate-spin"></div>
            </div>
            <p class="text-slate-400 font-black text-[10px] uppercase tracking-[0.2em]">数据加载中...</p>
          </div>
          <div v-else-if="buckets.length === 0" class="flex flex-col items-center justify-center h-full text-slate-300">
            <p class="font-bold">暂无数据</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="bucket in buckets"
              :key="bucket.id"
              class="group flex items-center justify-between p-5 bg-white rounded-2xl border border-slate-100 hover:border-blue-200 hover:shadow-xl hover:shadow-blue-500/5 hover:-translate-y-0.5 transition-all duration-300 cursor-pointer"
            >
              <div class="flex items-center gap-5">
                <div class="w-14 h-14 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 group-hover:border-blue-100 transition-all duration-500 group-hover:rotate-3">
                  <FolderIcon class="w-6 h-6" />
                </div>
                <div class="space-y-1">
                  <p class="font-black text-slate-900 leading-none group-hover:text-blue-600 transition-colors">{{ bucket.id }}</p>
                  <p class="text-[10px] text-slate-400 font-black uppercase tracking-wider">{{ bucket.total_files }} 个文件 • {{ formatSize(bucket.size) }}</p>
                </div>
              </div>
              <div class="shrink-0">
                <span
                  :class="bucket.private ? 'badge-error' : 'badge-success'"
                  class="badge px-4 shadow-sm"
                >
                  {{ bucket.private ? '私有' : '公开' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent History List -->
      <div class="card glass flex flex-col h-[600px] animate-fade-up delay-4">
        <div class="flex items-center justify-between mb-8">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-amber-100 text-amber-600 rounded-xl flex items-center justify-center shadow-inner">
              <ArrowsRightLeftIcon class="w-5 h-5" />
            </div>
            <h3 class="text-2xl font-black text-slate-900 tracking-tight">最近同步任务</h3>
          </div>
          <router-link to="/sync" class="group flex items-center gap-2 text-blue-600 hover:text-blue-700 text-xs font-black uppercase tracking-widest transition-all">
            同步历史
            <ArrowRightIcon class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </router-link>
        </div>

        <div class="flex-1 overflow-y-auto pr-4 custom-scrollbar">
          <div v-if="loading.history" class="flex flex-col items-center justify-center h-full space-y-6">
            <div class="w-16 h-16 border-4 border-slate-100 border-t-amber-500 rounded-full animate-spin"></div>
            <p class="text-slate-400 font-black text-[10px] uppercase tracking-[0.2em]">日志获取中...</p>
          </div>
          <div v-else-if="recentTasks.length === 0" class="flex flex-col items-center justify-center h-full text-slate-300">
            <p class="font-bold">暂无同步记录</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="task in recentTasks"
              :key="task.id"
              class="group flex items-center justify-between p-5 bg-white/50 hover:bg-white rounded-2xl border border-transparent hover:border-slate-200 hover:shadow-lg transition-all duration-300"
            >
              <div class="min-w-0 flex-1 flex items-center gap-5 mr-4">
                <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-amber-50 group-hover:text-amber-600 transition-colors">
                  <ChevronRightIcon class="w-4 h-4" />
                </div>
                <div class="min-w-0">
                  <p class="font-bold text-slate-900 truncate text-sm">{{ task.local_path }}</p>
                  <div class="flex items-center gap-3 mt-1.5">
                    <p class="text-[10px] text-slate-400 font-bold uppercase tracking-tighter truncate max-w-[120px]">{{ task.bucket_id }}</p>
                    <div class="w-1 h-1 bg-slate-200 rounded-full"></div>
                    <p class="text-[10px] text-slate-400 font-bold">{{ formatDate(task.created_at) }}</p>
                  </div>
                </div>
              </div>
              <div class="shrink-0">
                <span :class="getStatusClass(task.status)" class="badge px-4">
                  {{ getStatusText(task.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { bucketsApi, syncApi, scheduleApi } from '@/api'
import {
  CubeIcon,
  ClockIcon,
  ArrowsRightLeftIcon,
  FolderIcon,
  ArrowRightIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

const stats = ref({
  totalBuckets: 0,
  totalSchedules: 0,
  recentSyncs: 0
})

const buckets = ref([])
const recentTasks = ref([])
const loading = ref({ buckets: true, history: true })

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(1)} ${units[i]}`
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { 
    month: 'short', 
    day: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

function getStatusClass(status) {
  const map = {
    completed: 'badge-success',
    running: 'badge-warning',
    failed: 'badge-error',
    pending: 'badge-info'
  }
  return map[status] || 'badge-info'
}

function getStatusText(status) {
  const map = {
    completed: '已完成',
    running: '运行中',
    failed: '失败',
    pending: '等待中'
  }
  return map[status] || status
}

async function loadData() {
  loading.value = { buckets: true, history: true }

  try {
    const [bucketsRes, historyRes, scheduleRes] = await Promise.all([
      bucketsApi.list(),
      syncApi.history(5),
      scheduleApi.list()
    ])
    buckets.value = bucketsRes.data || []
    recentTasks.value = historyRes.data || []
    stats.value.totalBuckets = buckets.value.length
    stats.value.totalSchedules = scheduleRes.data?.length || 0
    stats.value.recentSyncs = historyRes.data?.length || 0
  } catch (e) {
    console.error('Failed to load data:', e)
  } finally {
    loading.value = { buckets: false, history: false }
  }
}

onMounted(() => {
  loadData()
})
</script>
