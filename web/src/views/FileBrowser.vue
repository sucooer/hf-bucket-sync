<template>
  <div class="p-4 md:p-6 lg:p-10 space-y-6 md:space-y-10 max-w-[1600px] mx-auto overflow-hidden">
    <div class="flex items-end justify-between animate-fade-up">
      <div>
        <h2 class="text-4xl font-black text-slate-900 tracking-tight">文件浏览</h2>
        <p class="text-slate-500 font-medium mt-2">浏览并管理您 HF Bucket 中的文件内容。</p>
      </div>
    </div>

    <!-- Filters Card -->
    <div class="card glass !bg-slate-900 !border-slate-800 shadow-2xl shadow-blue-900/20 animate-fade-up delay-1 overflow-visible">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 items-end">
        <div class="space-y-0">
          <UISelect
            v-model="selectedBucket"
            :options="bucketOptions"
            label="选择 Bucket"
            placeholder="请选择 Bucket"
            dark
            @update:modelValue="loadBucketTree()"
          />
        </div>

        <div class="space-y-3 lg:col-span-2">
          <label class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">路径前缀</label>
          <div class="relative group">
            <input
              v-model="prefix"
              type="text"
              class="input !bg-slate-800 !border-slate-700 !text-white !focus:ring-blue-500/30 pl-12 group-hover:border-slate-600 transition-all"
              placeholder="输入路径前缀，留空表示根目录"
              @keyup.enter="loadBucketTree()"
            />
            <MagnifyingGlassIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-hover:text-blue-400 transition-colors" />
          </div>
        </div>

        <div class="flex items-center gap-6">
          <label class="flex items-center gap-4 cursor-pointer group shrink-0">
            <div class="relative flex items-center justify-center">
              <input v-model="recursive" type="checkbox" class="peer sr-only" @change="loadBucketTree()" />
              <div class="w-12 h-7 bg-slate-800 rounded-full border border-slate-700 peer-checked:bg-blue-600 peer-checked:border-blue-500 transition-all duration-300"></div>
              <div class="absolute left-1.5 w-4 h-4 bg-white rounded-full transition-all duration-300 peer-checked:translate-x-5 peer-checked:bg-white shadow-lg"></div>
            </div>
            <span class="text-xs font-bold text-slate-400 group-hover:text-white transition-colors">递归显示</span>
          </label>
          <button @click="loadBucketTree()" class="btn-primary w-full !py-3 shadow-blue-900/40 active:scale-95">
            浏览
          </button>
        </div>
      </div>
    </div>

    <!-- Table Card -->
    <div class="card !p-0 overflow-hidden animate-fade-up delay-2">
      <div class="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-white border border-slate-200 rounded-2xl flex items-center justify-center text-blue-600 shadow-sm">
            <FolderOpenIcon class="w-6 h-6" />
          </div>
          <div>
            <h3 class="text-xl font-black text-slate-900 tracking-tight leading-none">
              {{ selectedBucket || '请选择 Bucket' }}
            </h3>
            <div class="flex items-center gap-2 mt-1.5">
              <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
              <p class="text-xs font-bold text-slate-400 font-mono tracking-tight truncate max-md">
                /{{ prefix || '根目录' }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div class="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-[10px] font-black uppercase tracking-widest border border-blue-100">
            {{ files.length }} 个项目
          </div>
        </div>
      </div>

      <div class="relative min-h-[500px]">
        <div v-if="loading" class="absolute inset-0 z-20 bg-white/80 backdrop-blur-md flex flex-col items-center justify-center space-y-6">
          <div class="w-20 h-20 relative">
            <div class="absolute inset-0 border-4 border-slate-100 rounded-full"></div>
            <div class="absolute inset-0 border-4 border-transparent border-t-blue-600 rounded-full animate-spin"></div>
          </div>
          <p class="text-slate-500 font-black text-xs uppercase tracking-[0.2em] animate-pulse">正在读取...</p>
        </div>

        <div v-if="!selectedBucket" class="flex flex-col items-center justify-center py-32 text-slate-300 animate-fade-up">
          <div class="w-32 h-32 bg-slate-50 rounded-full flex items-center justify-center mb-8 border border-slate-100">
            <CubeIcon class="w-16 h-16 opacity-10" />
          </div>
          <p class="text-xl font-bold text-slate-400">请选择一个 Bucket 开始浏览</p>
        </div>

        <div v-else-if="files.length === 0 && !loading" class="flex flex-col items-center justify-center py-32 text-slate-300">
          <InboxIcon class="w-32 h-32 mb-8 opacity-5" />
          <p class="text-xl font-bold text-slate-400">该目录下没有文件</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-slate-50/50 text-left border-b border-slate-100">
                <th class="px-8 py-5 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">名称</th>
                <th class="px-8 py-5 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">类型</th>
                <th class="px-8 py-5 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">大小</th>
                <th class="px-8 py-5 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">直链</th>
                <th class="px-8 py-5 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">CDN</th>
                <th class="px-8 py-5 text-right text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100/50">
              <tr
                v-for="(file, index) in files"
                :key="file.path"
                class="group hover:bg-blue-50/40 transition-all duration-300 animate-fade-up"
                :style="{ animationDelay: `${index * 0.02}s` }"
                :class="{ 'cursor-pointer': file.type === 'directory' }"
                @click="file.type === 'directory' && navigateToFolder(file.path)"
              >
                <td class="px-8 py-5">
                  <div class="flex items-center gap-5 min-w-0">
                    <div :class="file.type === 'directory' ? 'bg-amber-50 text-amber-500' : 'bg-blue-50 text-blue-500'" class="w-12 h-12 shrink-0 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-sm group-hover:shadow-md">
                      <FolderIcon v-if="file.type === 'directory'" class="w-6 h-6" />
                      <DocumentIcon v-else class="w-6 h-6" />
                    </div>
                    <div class="min-w-0">
                      <p class="font-bold text-slate-900 truncate group-hover:text-blue-600 transition-colors">{{ getFileName(file.path) }}</p>
                      <p class="text-[10px] text-slate-400 font-mono truncate mt-1">{{ file.path }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-8 py-5">
                  <span :class="file.type === 'directory' ? 'badge-warning' : 'badge-info'" class="badge !px-3 shadow-sm">
                    {{ file.type === 'directory' ? '目录' : '文件' }}
                  </span>
                </td>
                <td class="px-8 py-5">
                  <span class="text-sm font-bold text-slate-600">
                    {{ file.type === 'directory' ? '--' : formatSize(file.size) }}
                  </span>
                </td>
                <td class="px-8 py-5">
                  <template v-if="file.type === 'file'">
                    <div class="flex flex-col gap-1">
                      <span class="text-[9px] text-slate-400 font-mono truncate max-w-[200px]">{{ getDirectLink(file.path) }}</span>
                      <button
                        @click="copyLink(getDirectLink(file.path))"
                        class="text-[10px] px-2 py-1 bg-slate-100 hover:bg-blue-100 text-blue-600 rounded-lg transition-colors w-fit"
                      >
                        复制
                      </button>
                    </div>
                  </template>
                </td>
                <td class="px-8 py-5">
                  <template v-if="file.type === 'file'">
                    <div class="flex flex-col gap-1">
                      <span class="text-[9px] text-slate-400 font-mono truncate max-w-[200px]">{{ getCdnLink(file.path) }}</span>
                      <button
                        @click="copyLink(getCdnLink(file.path))"
                        class="text-[10px] px-2 py-1 bg-slate-100 hover:bg-green-100 text-green-600 rounded-lg transition-colors w-fit"
                      >
                        复制
                      </button>
                    </div>
                  </template>
                </td>
                <td class="px-8 py-5">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      v-if="file.type === 'file'"
                      @click="openRenameModal(file)"
                      class="p-2.5 text-slate-400 hover:text-blue-600 hover:bg-white rounded-xl shadow-sm border border-transparent hover:border-slate-200 transition-all"
                      title="重命名"
                    >
                      <PencilIcon class="w-5 h-5" />
                    </button>
                    <button
                      v-if="file.type === 'file'"
                      @click="confirmDelete(file)"
                      class="p-2.5 text-slate-400 hover:text-red-600 hover:bg-white rounded-xl shadow-sm border border-transparent hover:border-slate-200 transition-all"
                      title="删除"
                    >
                      <TrashIcon class="w-5 h-5" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Toast notification -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-4 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform translate-y-4 opacity-0"
    >
      <div v-if="toastShow" class="fixed bottom-8 right-8 z-50 px-6 py-3 bg-slate-900 text-white rounded-xl shadow-2xl flex items-center gap-3">
        <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
        <span class="font-bold text-sm">{{ toastMessage }}</span>
      </div>
    </Transition>

    <!-- Rename Modal -->
    <Teleport to="body">
      <div v-if="showRenameModal" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showRenameModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md mx-4 animate-fade-up">
          <h3 class="text-xl font-black text-slate-900 mb-6">重命名文件</h3>
          <input
            v-model="newFileName"
            type="text"
            class="input !bg-slate-50 !border-slate-200 !text-slate-900 mb-6"
            placeholder="输入新名称"
            @keyup.enter="executeRename()"
          />
          <div class="flex gap-3">
            <button @click="showRenameModal = false" class="btn-secondary flex-1">取消</button>
            <button @click="executeRename()" class="btn-primary flex-1">确定</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showDeleteModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md mx-4 animate-fade-up">
          <h3 class="text-xl font-black text-slate-900 mb-2">确认删除</h3>
          <p class="text-slate-500 mb-6">确定要删除 <span class="font-bold text-slate-900">{{ fileToDelete?.name }}</span> 吗？此操作不可撤销。</p>
          <div class="flex gap-3">
            <button @click="showDeleteModal = false" class="btn-secondary flex-1">取消</button>
            <button @click="executeDelete()" class="btn-primary flex-1 !bg-red-500 hover:!bg-red-600">删除</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { bucketsApi } from '@/api'
import UISelect from '@/components/UISelect.vue'
import {
  FolderIcon,
  FolderOpenIcon,
  DocumentIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
  InboxIcon,
  CubeIcon,
  ArrowDownTrayIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const buckets = ref([])
const selectedBucket = ref('')
const prefix = ref('')
const recursive = ref(false)
const files = ref([])
const loading = ref(false)
const error = ref('')

const showRenameModal = ref(false)
const showDeleteModal = ref(false)
const fileToRename = ref(null)
const fileToDelete = ref(null)
const newFileName = ref('')
const toastShow = ref(false)
const toastMessage = ref('')

const CDN_BASE_URL = import.meta.env.VITE_CDN_BASE_URL || 'https://hug.520717.xyz'

const bucketOptions = computed(() => {
  return buckets.value.map(b => ({ label: b.id.split('/')[1] || b.id, value: b.id }))
})

function getFileName(path) {
  const parts = path.split('/')
  return parts[parts.length - 1] || path
}

function formatSize(bytes) {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(1)} ${units[i]}`
}

function normalizeBucketPath(path) {
  const bucketName = selectedBucket.value.split('/')[1] || selectedBucket.value
  const bucketPrefix = bucketName + '/'
  const pathInBucket = path.startsWith(bucketPrefix) ? path.slice(bucketPrefix.length) : path
  const encodedPath = pathInBucket.split('/').map(p => encodeURIComponent(p)).join('/')
  return { bucketName, encodedPath }
}

function getDirectLink(path) {
  const { encodedPath } = normalizeBucketPath(path)
  return `https://huggingface.co/buckets/${selectedBucket.value}/resolve/${encodedPath}`
}

function getCdnLink(path) {
  const { bucketName, encodedPath } = normalizeBucketPath(path)
  return `${CDN_BASE_URL}/${bucketName}/${encodedPath}`
}

function copyLink(url) {
  const textArea = document.createElement('textarea')
  textArea.value = url
  textArea.style.position = 'fixed'
  textArea.style.left = '-999999px'
  textArea.style.top = '-999999px'
  document.body.appendChild(textArea)
  textArea.focus()
  textArea.select()
  try {
    document.execCommand('copy')
    showToast('链接已复制到剪贴板')
  } catch (err) {
    prompt('复制链接:', url)
  }
  document.body.removeChild(textArea)
}

function showToast(message) {
  toastMessage.value = message
  toastShow.value = true
  setTimeout(() => { toastShow.value = false }, 2000)
}

function openRenameModal(file) {
  fileToRename.value = file
  newFileName.value = getFileName(file.path)
  showRenameModal.value = true
}

async function executeRename() {
  if (!newFileName.value.trim() || !fileToRename.value) return
  try {
    await bucketsApi.renameFile(selectedBucket.value, fileToRename.value.path, newFileName.value.trim())
    showRenameModal.value = false
    fileToRename.value = null
    newFileName.value = ''
    await loadBucketTree()
    showToast('文件重命名成功')
  } catch (e) {
    alert(e.response?.data?.detail || '重命名失败')
  }
}

function confirmDelete(file) {
  fileToDelete.value = file
  showDeleteModal.value = true
}

async function executeDelete() {
  if (!fileToDelete.value) return
  try {
    await bucketsApi.deleteFile(selectedBucket.value, fileToDelete.value.path)
    showDeleteModal.value = false
    fileToDelete.value = null
    await loadBucketTree()
    showToast('文件删除成功')
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

async function loadBuckets() {
  try {
    const res = await bucketsApi.list()
    buckets.value = res.data || []
    if (buckets.value.length > 0 && !selectedBucket.value) {
      selectedBucket.value = buckets.value[0].id
      loadBucketTree()
    }
  } catch (e) {
    console.error('Failed to load buckets:', e)
  }
}

async function loadBucketTree() {
  if (!selectedBucket.value) return

  loading.value = true
  error.value = ''
  files.value = []

  try {
    const res = await bucketsApi.tree(selectedBucket.value, prefix.value, recursive.value)
    files.value = res.data || []
  } catch (e) {
    error.value = e.response?.data?.detail || '加载失败'
    console.error('Failed to load bucket tree:', e)
  } finally {
    loading.value = false
  }
}

function navigateToFolder(folderPath) {
  prefix.value = folderPath + '/'
  loadBucketTree()
}

onMounted(() => {
  loadBuckets()
})
</script>
