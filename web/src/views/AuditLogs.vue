<template>
  <div class="p-4 md:p-6 lg:p-10 space-y-6 md:space-y-8 max-w-[1600px] mx-auto overflow-hidden">
    <div class="flex items-end justify-between animate-fade-up">
      <div>
        <h2 class="text-4xl font-black text-slate-900 tracking-tight">审计日志</h2>
        <p class="hidden md:block text-slate-500 font-medium mt-2">记录登录、登出、配置变更与同步执行行为。</p>
      </div>
    </div>

    <div class="card glass space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-2 block">动作筛选</label>
          <UISelect v-model="actionFilter" :options="actionOptions" placeholder="全部动作" />
        </div>
        <div>
          <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-2 block">关键字</label>
          <input v-model="keyword" class="input" placeholder="搜索 actor/resource/summary" />
        </div>
        <div class="flex items-end">
          <button @click="loadLogs" class="btn-secondary w-full">刷新</button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-[900px]">
          <thead>
            <tr class="bg-slate-50/50 text-left border-b border-slate-100">
              <th class="px-4 py-3 text-[10px] font-black uppercase tracking-widest text-slate-400">时间</th>
              <th class="px-4 py-3 text-[10px] font-black uppercase tracking-widest text-slate-400">用户</th>
              <th class="px-4 py-3 text-[10px] font-black uppercase tracking-widest text-slate-400">动作</th>
              <th class="px-4 py-3 text-[10px] font-black uppercase tracking-widest text-slate-400">资源</th>
              <th class="px-4 py-3 text-[10px] font-black uppercase tracking-widest text-slate-400">摘要</th>
              <th class="px-4 py-3 text-[10px] font-black uppercase tracking-widest text-slate-400">IP</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100/50">
            <tr v-for="item in pagedLogs" :key="item.id" class="hover:bg-slate-50/50">
              <td class="px-4 py-3 text-xs font-mono text-slate-600">{{ formatDate(item.created_at) }}</td>
              <td class="px-4 py-3 text-xs font-bold text-slate-800">{{ item.actor }}</td>
              <td class="px-4 py-3"><span class="badge badge-info">{{ item.action }}</span></td>
              <td class="px-4 py-3 text-xs text-slate-600">{{ item.resource || '-' }}</td>
              <td class="px-4 py-3 text-xs text-slate-600 max-w-[420px] truncate">{{ item.summary || '-' }}</td>
              <td class="px-4 py-3 text-xs font-mono text-slate-500">{{ item.ip || '-' }}</td>
            </tr>
            <tr v-if="!loading && filteredLogs.length === 0">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400">暂无日志</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex items-center justify-between">
        <p class="text-xs text-slate-500">共 {{ filteredLogs.length }} 条</p>
        <div class="flex items-center gap-2">
          <button @click="page = Math.max(1, page - 1)" class="btn-secondary !px-3 !py-1.5 text-xs" :disabled="page === 1">上一页</button>
          <span class="text-xs text-slate-500">{{ page }} / {{ totalPages }}</span>
          <button @click="page = Math.min(totalPages, page + 1)" class="btn-secondary !px-3 !py-1.5 text-xs" :disabled="page >= totalPages">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { auditApi } from '@/api'
import UISelect from '@/components/UISelect.vue'

const logs = ref([])
const loading = ref(false)
const actionFilter = ref('')
const keyword = ref('')
const page = ref(1)
const pageSize = 20

const actionOptions = computed(() => {
  const actions = Array.from(new Set(logs.value.map(i => i.action))).filter(Boolean)
  return [{ label: '全部', value: '' }, ...actions.map(a => ({ label: a, value: a }))]
})

const filteredLogs = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return logs.value.filter(item => {
    if (actionFilter.value && item.action !== actionFilter.value) return false
    if (!kw) return true
    return [item.actor, item.resource, item.summary, item.action, item.ip]
      .join(' ')
      .toLowerCase()
      .includes(kw)
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredLogs.value.length / pageSize)))
const pagedLogs = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredLogs.value.slice(start, start + pageSize)
})

watch([actionFilter, keyword], () => {
  page.value = 1
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(dateStr)
  const normalized = hasTimezone ? dateStr : `${dateStr}Z`
  return new Date(normalized).toLocaleString('zh-CN')
}

async function loadLogs() {
  loading.value = true
  try {
    const res = await auditApi.logs(300)
    logs.value = res.data || []
  } catch (e) {
    logs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadLogs)
</script>
