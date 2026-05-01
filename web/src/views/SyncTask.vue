<template>
  <div class="p-4 md:p-6 lg:p-10 space-y-6 md:space-y-10 max-w-[1600px] mx-auto overflow-hidden">
    <div class="flex items-end justify-between animate-fade-up">
      <div>
        <h2 class="text-4xl font-black text-slate-900 tracking-tight">同步任务</h2>
        <p class="text-slate-500 font-medium mt-2">手动触发本地目录与远程 Bucket 之间的同步。</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
      <!-- Configuration Form -->
      <div class="lg:col-span-8 space-y-8 animate-fade-up delay-1">
        <div class="card glass shadow-2xl shadow-slate-200/50 overflow-visible">
          <div class="flex items-center gap-4 mb-10">
            <div class="w-12 h-12 bg-gradient-to-br from-slate-700 to-slate-900 rounded-2xl flex items-center justify-center shadow-lg shadow-slate-900/20">
              <Cog6ToothIcon class="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 class="text-2xl font-black text-slate-900 tracking-tight">创建同步任务</h3>
              <p class="text-[10px] font-black uppercase tracking-widest text-slate-400 mt-1">配置参数</p>
            </div>
          </div>

          <div class="space-y-10">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <UISelect
                v-model="form.direction"
                :options="directionOptions"
                label="同步方向"
              />

              <UISelect
                v-model="form.bucketId"
                :options="bucketOptions"
                label="目标 Bucket"
                placeholder="请选择 Bucket"
              />
            </div>

            <div class="space-y-3">
              <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">本地路径</label>
              <div class="relative group">
                <input v-model="form.localPath" type="text" class="input pl-12 group-hover:border-slate-300 transition-all font-mono" placeholder="/path/to/local" />
                <ComputerDesktopIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-300 group-hover:text-blue-500 transition-colors" />
              </div>
            </div>

            <div class="space-y-3">
              <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Bucket 前缀 (可选)</label>
              <input v-model="form.bucketPrefix" type="text" class="input font-mono" placeholder="prefix/path" />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="space-y-3">
                <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">包含规则</label>
                <input v-model="form.includePatterns" type="text" class="input" placeholder="*.safetensors, *.bin" />
                <p class="text-[10px] text-slate-400 font-medium">逗号分隔，默认为 * (所有文件)</p>
              </div>

              <div class="space-y-3">
                <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">排除规则</label>
                <input v-model="form.excludePatterns" type="text" class="input" placeholder="*.tmp, .git/*" />
              </div>
            </div>

            <div class="p-6 bg-slate-50 rounded-2xl border border-slate-100 border-dashed">
              <label class="flex items-center gap-5 cursor-pointer group">
                <div class="relative flex items-center justify-center">
                  <input v-model="form.delete" type="checkbox" class="peer sr-only" />
                  <div class="w-14 h-8 bg-slate-200 rounded-full peer-checked:bg-rose-500 transition-all duration-300"></div>
                  <div class="absolute left-1.5 w-5 h-5 bg-white rounded-full transition-all duration-300 peer-checked:translate-x-6 shadow-md"></div>
                </div>
                <div>
                  <span class="text-sm font-black text-slate-900 group-hover:text-rose-600 transition-colors">删除目标端不存在的文件</span>
                </div>
              </label>
            </div>

            <div class="flex gap-6 pt-4">
              <button @click="dryRun()" class="btn-secondary flex-1 !py-4 shadow-slate-100 hover:shadow-lg active:scale-95" :disabled="!isValid || running">
                <div class="flex items-center justify-center gap-3">
                  <MagnifyingGlassIcon v-if="!running" class="w-6 h-6" />
                  <div v-else class="w-5 h-5 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin"></div>
                  <span class="font-black uppercase tracking-widest text-xs">预览</span>
                </div>
              </button>
              <button @click="execute()" class="btn-primary flex-1 !py-4 shadow-blue-500/30 active:scale-95" :disabled="!isValid || running">
                <div class="flex items-center justify-center gap-3">
                  <PlayIcon v-if="!running" class="w-6 h-6" />
                  <div v-else class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span class="font-black uppercase tracking-widest text-xs">执行同步</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Preview Panel -->
      <div class="lg:col-span-4 space-y-8 animate-fade-up delay-2">
        <div class="card glass border-dashed border-slate-300 min-h-[500px] flex flex-col shadow-inner">
          <div class="flex items-center gap-3 mb-8">
            <h3 class="text-xl font-black text-slate-900 tracking-tight">同步预览</h3>
            <span v-if="planReady" class="px-2 py-0.5 bg-emerald-100 text-emerald-600 rounded text-[9px] font-black uppercase tracking-widest animate-pulse">就绪</span>
          </div>

          <div v-if="running" class="flex-1 flex flex-col items-center justify-center text-slate-400 space-y-8">
            <div class="w-24 h-24 relative">
              <div class="absolute inset-0 border-4 border-slate-100 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-transparent border-t-blue-500 rounded-full animate-spin"></div>
            </div>
            <p class="font-black text-[10px] uppercase tracking-[0.2em] animate-pulse">正在分析...</p>
          </div>

          <div v-else-if="!planReady" class="flex-1 flex flex-col items-center justify-center text-slate-300 text-center px-10">
            <div class="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mb-8 border border-slate-100">
              <DocumentMagnifyingGlassIcon class="w-12 h-12 opacity-10" />
            </div>
            <p class="font-bold text-slate-400">点击"预览"查看同步计划</p>
          </div>

          <div v-else class="space-y-8 animate-fade-up">
            <div class="grid grid-cols-2 gap-6">
              <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm group hover:border-blue-200 transition-colors">
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">上传</p>
                <p class="text-4xl font-black text-blue-600 mt-2 group-hover:scale-110 transition-transform origin-left">
                  {{ plan.uploads?.length || 0 }}
                </p>
              </div>
              <div class="bg-green-50/50 p-5 rounded-2xl border border-green-100 shadow-sm group hover:border-green-300 transition-colors">
                <p class="text-[10px] font-black text-green-600 uppercase tracking-widest">下载</p>
                <p class="text-4xl font-black text-green-600 mt-2 group-hover:scale-110 transition-transform origin-left">
                  {{ plan.downloads?.length || 0 }}
                </p>
              </div>
              <div class="bg-rose-50/50 p-5 rounded-2xl border border-rose-100 shadow-sm group hover:border-rose-300 transition-colors">
                <p class="text-[10px] font-black text-rose-400 uppercase tracking-widest">删除</p>
                <p class="text-4xl font-black text-rose-600 mt-2 group-hover:scale-110 transition-transform origin-left">{{ plan.deletes?.length || 0 }}</p>
              </div>
              <div class="bg-gray-50/50 p-5 rounded-2xl border border-slate-200 shadow-sm group hover:border-slate-300 transition-colors">
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">跳过</p>
                <p class="text-4xl font-black text-slate-600 mt-2 group-hover:scale-110 transition-transform origin-left">{{ plan.skips?.length || 0 }}</p>
              </div>
            </div>

            <div v-if="plan.uploads?.length > 0">
              <div class="flex items-center justify-between mb-4">
                <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest">将上传的文件:</p>
              </div>
              <div class="space-y-2 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
                <div v-for="f in plan.uploads.slice(0, 10)" :key="f.path" class="p-3 bg-white/50 rounded-xl border border-slate-100 text-[11px] font-mono text-slate-600 truncate hover:bg-white transition-colors">
                  {{ f.path }}
                </div>
                <div v-if="plan.uploads.length > 10" class="text-[10px] text-center text-slate-400 font-black uppercase tracking-widest pt-4 animate-pulse">
                  ... 还有 {{ plan.uploads.length - 10 }} 个文件
                </div>
              </div>
            </div>

            <div v-if="plan.deletes?.length > 0" class="p-4 bg-rose-50 border border-rose-100 rounded-2xl flex gap-4">
              <ExclamationTriangleIcon class="w-6 h-6 text-rose-500 shrink-0" />
              <div>
                <p class="text-xs font-black text-rose-600 uppercase tracking-widest">警告</p>
                <p class="text-[11px] text-rose-500 font-bold mt-1 leading-relaxed">将删除目标端的 {{ plan.deletes.length }} 个文件</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- History Table -->
    <div class="card !p-0 overflow-hidden animate-fade-up delay-3 shadow-xl">
      <div class="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/20">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center text-slate-600">
            <ClockIcon class="w-6 h-6" />
          </div>
          <h3 class="text-xl font-black text-slate-900 tracking-tight">同步历史</h3>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-50/50 text-left border-b border-slate-100">
              <th class="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-slate-400">本地路径</th>
              <th class="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-slate-400">Bucket</th>
              <th class="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-slate-400">方向</th>
              <th class="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-slate-400">状态</th>
              <th class="px-8 py-5 text-right text-[10px] font-black uppercase tracking-widest text-slate-400">时间</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100/50">
            <tr v-for="task in history" :key="task.id" class="group hover:bg-slate-50/30 transition-all duration-300">
              <td class="px-8 py-5">
                <p class="font-black text-slate-900 text-sm truncate max-w-lg leading-none">{{ task.local_path }}</p>
              </td>
              <td class="px-8 py-5">
                <p class="text-[10px] text-slate-400 font-mono uppercase tracking-tighter">{{ task.bucket_id }}</p>
              </td>
              <td class="px-8 py-5">
                <div class="flex items-center gap-3">
                  <div :class="task.direction === 'upload' ? 'bg-blue-100 text-blue-600' : 'bg-emerald-100 text-emerald-600'" class="p-1.5 rounded-lg">
                    <ArrowUpIcon v-if="task.direction === 'upload'" class="w-4 h-4" />
                    <ArrowDownIcon v-else class="w-4 h-4" />
                  </div>
                  <span class="text-xs font-black text-slate-600 uppercase tracking-wider">{{ task.direction === 'upload' ? '上传' : '下载' }}</span>
                </div>
              </td>
              <td class="px-8 py-5">
                <span :class="getStatusClass(task.status)" class="badge !px-4 shadow-sm border-transparent group-hover:border-current transition-all">{{ getStatusText(task.status) }}</span>
              </td>
              <td class="px-8 py-5 text-right">
                <span class="text-xs font-black text-slate-500 font-mono uppercase">{{ formatDate(task.created_at) }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { bucketsApi, syncApi } from '@/api'
import UISelect from '@/components/UISelect.vue'
import {
  Cog6ToothIcon,
  MagnifyingGlassIcon,
  PlayIcon,
  DocumentMagnifyingGlassIcon,
  ArrowPathIcon,
  ClockIcon,
  ComputerDesktopIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ChevronDownIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

const form = ref({
  direction: 'upload',
  localPath: '',
  bucketId: '',
  bucketPrefix: '',
  includePatterns: '*',
  excludePatterns: '',
  delete: false
})

const buckets = ref([])
const history = ref([])
const plan = ref({})
const planReady = ref(false)
const running = ref(false)
const loading = ref(false)

const isValid = computed(() => {
  return form.value.localPath && form.value.bucketId
})

const directionOptions = [
  { label: '上传 (本地 → HF Bucket)', value: 'upload' },
  { label: '下载 (HF Bucket → 本地)', value: 'download' }
]

const bucketOptions = computed(() => {
  return buckets.value.map(b => ({ label: b.id, value: b.id }))
})

function parsePatterns(str) {
  if (!str || str === '*') return ['*']
  return str.split(',').map(p => p.trim()).filter(Boolean)
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

async function dryRun() {
  if (!isValid.value) return
  running.value = true
  planReady.value = false
  try {
    const data = {
      local_path: form.value.localPath,
      bucket_id: form.value.bucketId,
      bucket_prefix: form.value.bucketPrefix,
      direction: form.value.direction,
      filter: {
        include_patterns: parsePatterns(form.value.includePatterns),
        exclude_patterns: parsePatterns(form.value.excludePatterns)
      },
      delete: form.value.delete
    }
    const res = await syncApi.dryRun(data)
    plan.value = res.data || {}
    planReady.value = true
  } catch (e) {
    console.error('Preview failed:', e)
    alert('预览失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    running.value = false
  }
}

async function execute() {
  if (!isValid.value) return
  running.value = true
  try {
    const data = {
      local_path: form.value.localPath,
      bucket_id: form.value.bucketId,
      bucket_prefix: form.value.bucketPrefix,
      direction: form.value.direction,
      filter: {
        include_patterns: parsePatterns(form.value.includePatterns),
        exclude_patterns: parsePatterns(form.value.excludePatterns)
      },
      delete: form.value.delete
    }
    const res = await syncApi.execute(data)
    alert(res.data?.message || '同步完成')
    await loadHistory()
    planReady.value = false
  } catch (e) {
    console.error('Sync failed:', e)
    alert('同步失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    running.value = false
  }
}

async function loadHistory() {
  try {
    const res = await syncApi.history()
    history.value = res.data || []
  } catch (e) {
    console.error('Failed to load history:', e)
  }
}

async function loadBuckets() {
  try {
    const res = await bucketsApi.list()
    buckets.value = res.data || []
  } catch (e) {
    console.error('Failed to load buckets:', e)
  }
}

onMounted(() => {
  loadBuckets()
  loadHistory()
})
</script>
