<template>
  <div class="p-4 md:p-6 lg:p-10 space-y-6 md:space-y-10 max-w-[1600px] mx-auto overflow-hidden">
    <div class="flex items-end justify-between animate-fade-up">
      <div>
        <h2 class="text-4xl font-black text-slate-900 tracking-tight">定时任务</h2>
        <p class="hidden md:block text-slate-500 font-medium mt-2">配置自动运行的同步计划，保持数据实时更新。</p>
      </div>
      <button @click="showCreate = true" class="btn-primary flex items-center gap-3 shadow-blue-500/40 active:scale-95">
        <PlusIcon class="w-6 h-6" />
        <span class="font-black uppercase tracking-widest text-xs">创建定时任务</span>
      </button>
    </div>

    <div v-if="loading && schedules.length === 0" class="flex flex-col items-center justify-center py-32 text-slate-400 space-y-8 animate-fade-up">
      <div class="w-20 h-20 relative">
        <div class="absolute inset-0 border-4 border-slate-100 rounded-full"></div>
        <div class="absolute inset-0 border-4 border-transparent border-t-blue-600 rounded-full animate-spin"></div>
      </div>
      <p class="font-black text-[10px] uppercase tracking-[0.2em] animate-pulse">正在初始化...</p>
    </div>

    <div v-else-if="schedules.length === 0" class="card py-32 border-dashed border-slate-300 bg-slate-50/30 flex flex-col items-center justify-center text-center animate-fade-up delay-1 shadow-inner">
      <div class="w-24 h-24 bg-white rounded-3xl flex items-center justify-center mb-8 shadow-xl shadow-slate-200/50">
        <ClockIcon class="w-12 h-12 text-slate-300" />
      </div>
      <h3 class="text-2xl font-black text-slate-900 mb-2">暂无定时任务</h3>
      <p class="text-slate-500 max-w-sm mb-10 font-medium">创建一个定时同步计划，系统将在后台为您自动完成数据同步工作。</p>
      <button @click="showCreate = true" class="btn-secondary !px-10">
        立即创建
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-10">
      <div v-for="(s, index) in schedules" :key="s.id" 
        class="card group relative overflow-hidden flex flex-col justify-between border-slate-200/60 hover:border-blue-300 hover:shadow-2xl hover:shadow-blue-500/10 transition-all duration-500 animate-fade-up"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <!-- Dynamic Status Bar -->
        <div :class="s.enabled ? 'bg-blue-600' : 'bg-slate-300'" class="absolute top-0 left-0 w-2 h-full transition-all duration-500 group-hover:w-3"></div>

        <div>
          <div class="flex items-start justify-between mb-8">
            <div class="flex items-center gap-5">
              <div :class="s.enabled ? 'bg-gradient-to-br from-blue-500 to-indigo-600 shadow-blue-500/40' : 'bg-slate-400'" class="w-14 h-14 rounded-2xl flex items-center justify-center text-white shadow-xl transition-all duration-500 group-hover:rotate-6 group-hover:scale-110">
                <CalendarDaysIcon class="w-8 h-8" />
              </div>
              <div>
                <h4 class="font-black text-slate-900 text-xl leading-none group-hover:text-blue-600 transition-colors">{{ s.name }}</h4>
                <div class="flex items-center gap-2.5 mt-2">
                  <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400">Cron 表达式:</span>
                  <code class="text-[10px] font-black font-mono bg-blue-50 px-2 py-0.5 rounded text-blue-600 border border-blue-100">{{ s.cron }}</code>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300 -translate-y-2 group-hover:translate-y-0">
              <button @click="editSchedule(s)" class="p-2.5 text-slate-400 hover:text-blue-600 hover:bg-white rounded-xl shadow-sm border border-transparent hover:border-slate-200 transition-all">
                <PencilSquareIcon class="w-5 h-5" />
              </button>
              <button @click="deleteSchedule(s.id)" class="p-2.5 text-slate-400 hover:text-rose-600 hover:bg-white rounded-xl shadow-sm border border-transparent hover:border-slate-200 transition-all">
                <TrashIcon class="w-5 h-5" />
              </button>
            </div>
          </div>

          <div class="space-y-4 mb-8 bg-slate-50/50 p-6 rounded-2xl border border-slate-100/50">
            <div class="flex flex-col gap-1.5">
              <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400">本地路径</span>
              <span class="text-xs font-bold text-slate-700 font-mono truncate bg-white px-2 py-1 rounded border border-slate-100">{{ s.local_path }}</span>
            </div>
            <div class="flex items-center justify-between pt-2">
              <div class="flex flex-col gap-1.5">
                <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400">目标 Bucket</span>
                <span class="text-xs font-black text-slate-800">{{ s.bucket_id }}</span>
              </div>
              <div class="flex flex-col items-end gap-1.5 text-right">
                <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400">同步方向</span>
                <div class="flex items-center gap-2">
                  <span class="text-xs font-black text-slate-800 uppercase">{{ s.direction }}</span>
                  <div :class="s.direction === 'upload' ? 'bg-blue-100 text-blue-600' : 'bg-emerald-100 text-emerald-600'" class="p-1 rounded">
                    <ArrowUpIcon v-if="s.direction === 'upload'" class="w-3 h-3" />
                    <ArrowDownIcon v-else class="w-3 h-3" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between px-2">
          <div class="flex flex-col">
            <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400 mb-1">下次执行</span>
            <div class="flex items-center gap-3">
              <div v-if="s.enabled" class="flex gap-0.5">
                <div class="w-1 h-3 bg-blue-500 rounded-full animate-bounce"></div>
                <div class="w-1 h-3 bg-blue-500 rounded-full animate-bounce delay-100"></div>
                <div class="w-1 h-3 bg-blue-500 rounded-full animate-bounce delay-200"></div>
              </div>
              <span class="text-sm font-black text-slate-900 tracking-tight">
                {{ formatDate(s.next_run) }}
              </span>
            </div>
          </div>
          
          <div class="flex items-center gap-4">
            <span class="text-[10px] font-black uppercase tracking-widest" :class="s.enabled ? 'text-blue-600' : 'text-slate-400'">{{ s.enabled ? '启用' : '禁用' }}</span>
            <label class="relative flex items-center justify-center cursor-pointer group">
              <input
                type="checkbox"
                :checked="s.enabled"
                @change="toggleEnabled(s)"
                class="peer sr-only"
              />
              <div class="w-14 h-8 bg-slate-200 rounded-full peer-checked:bg-blue-600 transition-all duration-300"></div>
              <div class="absolute left-1.5 w-5 h-5 bg-white rounded-full transition-all duration-300 peer-checked:translate-x-6 shadow-lg group-hover:scale-110"></div>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Overlay -->
    <transition name="page">
      <div v-if="showCreate || editingSchedule" class="fixed inset-0 bg-slate-900/80 backdrop-blur-xl flex items-center justify-center z-50 p-6">
        <div class="bg-white rounded-[32px] shadow-[0_32px_64px_-12px_rgba(0,0,0,0.3)] w-full max-w-2xl overflow-hidden border border-white/20 animate-fade-up">
          <div class="p-10 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
            <div class="flex items-center gap-5">
              <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-blue-500/30">
                <PlusIcon v-if="!editingSchedule" class="w-8 h-8" />
                <PencilSquareIcon v-else class="w-8 h-8" />
              </div>
              <div>
                <h3 class="text-3xl font-black text-slate-900 tracking-tight">
                  {{ editingSchedule ? '编辑定时任务' : '创建定时任务' }}
                </h3>
              </div>
            </div>
            <button @click="closeModal()" class="w-12 h-12 flex items-center justify-center text-slate-400 hover:text-slate-900 hover:bg-slate-100 rounded-2xl transition-all">
              <XMarkIcon class="w-7 h-7" />
            </button>
          </div>

          <div class="p-12 space-y-10 max-h-[60vh] overflow-y-auto overflow-x-visible custom-scrollbar">
            <div class="space-y-3">
              <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">任务名称</label>
              <input v-model="form.name" type="text" class="input !py-4" placeholder="我的备份任务" />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
              <UISelect
                v-model="form.direction"
                :options="directionOptions"
                label="同步方向"
              />

              <UISelect
                v-model="form.bucketId"
                :options="bucketOptions"
                label="目标 Bucket"
                placeholder="请选择"
              />
            </div>

            <div class="space-y-3">
              <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">本地路径</label>
              <input v-model="form.localPath" type="text" class="input !py-4 font-mono" placeholder="/path/to/local" />
            </div>

            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Cron 表达式</label>
              </div>
              <div class="flex gap-4">
                <input v-model="form.cron" type="text" class="input !py-4 font-mono flex-1 text-blue-600 font-bold" placeholder="0 2 * * *" />
                <div class="shrink-0 flex items-center px-6 bg-slate-100 rounded-2xl border border-slate-200">
                  <ClockIcon class="w-6 h-6 text-slate-400" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4 mt-4">
                <button @click="form.cron = '0 2 * * *'" class="text-[10px] text-left p-3 bg-white hover:bg-blue-50 border border-slate-100 rounded-xl text-slate-500 hover:text-blue-600 transition-all hover:border-blue-200 hover:-translate-y-0.5 shadow-sm">
                  <b class="font-black uppercase tracking-tighter">每天凌晨2点:</b><br/>0 2 * * *
                </button>
                <button @click="form.cron = '0 */4 * * *'" class="text-[10px] text-left p-3 bg-white hover:bg-blue-50 border border-slate-100 rounded-xl text-slate-500 hover:text-blue-600 transition-all hover:border-blue-200 hover:-translate-y-0.5 shadow-sm">
                  <b class="font-black uppercase tracking-tighter">每4小时:</b><br/>0 */4 * * *
                </button>
              </div>
            </div>

            <div class="p-8 bg-rose-50 rounded-3xl border border-rose-100 border-dashed">
              <label class="flex items-center gap-6 cursor-pointer group">
                <input v-model="form.delete" type="checkbox" class="peer sr-only" />
                <div class="relative flex items-center justify-center">
                  <div class="w-14 h-8 bg-slate-200 rounded-full peer-checked:bg-rose-500 transition-all duration-300"></div>
                  <div class="absolute left-1.5 w-5 h-5 bg-white rounded-full transition-all duration-300 peer-checked:translate-x-6 shadow-md"></div>
                </div>
                <div>
                  <span class="text-sm font-black text-slate-900 group-hover:text-rose-600 transition-colors">删除目标端不存在的文件</span>
                </div>
              </label>
            </div>
          </div>

          <div class="p-10 bg-slate-50/50 border-t border-slate-100 flex justify-end gap-6">
            <button @click="closeModal()" class="btn-secondary !px-12 !py-4 active:scale-95">取消</button>
            <button @click="saveSchedule()" class="btn-primary !px-12 !py-4 shadow-blue-500/40 active:scale-95">
              {{ editingSchedule ? '更新' : '创建' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { bucketsApi, scheduleApi } from '@/api'
import UISelect from '@/components/UISelect.vue'
import {
  PlusIcon,
  ClockIcon,
  CalendarDaysIcon,
  PencilSquareIcon,
  TrashIcon,
  XMarkIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/vue/24/outline'

const schedules = ref([])
const buckets = ref([])
const loading = ref(false)
const showCreate = ref(false)
const editingSchedule = ref(null)

const form = ref({
  name: '',
  direction: 'upload',
  localPath: '',
  bucketId: '',
  bucketPrefix: '',
  cron: '0 2 * * *',
  delete: false
})

const directionOptions = [
  { label: '上传 (本地 → HF Bucket)', value: 'upload' },
  { label: '下载 (HF Bucket → 本地)', value: 'download' }
]

const bucketOptions = computed(() => {
  return buckets.value.map(b => ({ label: b.id, value: b.id }))
})

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

function resetForm() {
  form.value = {
    name: '',
    direction: 'upload',
    localPath: '',
    bucketId: '',
    bucketPrefix: '',
    cron: '0 2 * * *',
    delete: false
  }
}

function closeModal() {
  showCreate.value = false
  editingSchedule.value = null
  resetForm()
}

function editSchedule(s) {
  editingSchedule.value = s.id
  form.value = {
    name: s.name,
    direction: s.direction,
    localPath: s.local_path,
    bucketId: s.bucket_id,
    bucketPrefix: s.bucket_prefix,
    cron: s.cron,
    delete: s.delete
  }
}

async function saveSchedule() {
  try {
    const data = {
      name: form.value.name,
      direction: form.value.direction,
      local_path: form.value.localPath,
      bucket_id: form.value.bucketId,
      bucket_prefix: form.value.bucketPrefix,
      cron: form.value.cron,
      delete: form.value.delete,
      enabled: true,
      filter: {
        include_patterns: ['*'],
        exclude_patterns: []
      }
    }

    if (editingSchedule.value) {
      await scheduleApi.update(editingSchedule.value, data)
    } else {
      await scheduleApi.create(data)
    }

    closeModal()
    await loadSchedules()
  } catch (e) {
    console.error('Failed to save schedule:', e)
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function toggleEnabled(s) {
  try {
    await scheduleApi.update(s.id, { enabled: !s.enabled })
    await loadSchedules()
  } catch (e) {
    console.error('Failed to toggle schedule:', e)
  }
}

async function deleteSchedule(id) {
  if (!confirm('确定要删除这个定时任务吗？')) return
  try {
    await scheduleApi.delete(id)
    await loadSchedules()
  } catch (e) {
    console.error('Failed to delete schedule:', e)
    alert('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function loadSchedules() {
  loading.value = true
  try {
    const res = await scheduleApi.list()
    schedules.value = res.data || []
  } catch (e) {
    console.error('Failed to load schedules:', e)
  } finally {
    loading.value = false
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
  loadSchedules()
  loadBuckets()
})
</script>
