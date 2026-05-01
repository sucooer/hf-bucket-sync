<template>
  <div class="p-4 md:p-6">
    <h2 class="text-xl md:text-2xl font-bold mb-4 md:mb-6 text-slate-900 dark:text-white">通知设置</h2>

    <div class="card mb-6">
      <h3 class="text-base md:text-lg font-semibold mb-4 text-slate-900 dark:text-white">通知渠道</h3>

      <div class="space-y-6">
        <div class="border-b border-gray-200 dark:border-slate-700 pb-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
                </svg>
              </div>
              <div>
                <h4 class="font-semibold text-slate-900 dark:text-white">Telegram 机器人</h4>
                <p class="text-sm text-gray-500 dark:text-gray-400">通过 Telegram Bot 发送通知</p>
              </div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="settings.telegram.enabled" type="checkbox" class="sr-only peer" @change="saveSettings">
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div v-if="settings.telegram.enabled" class="space-y-4 pl-13">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Bot Token</label>
              <input v-model="settings.telegram.bot_token" type="text" class="input" placeholder="123456:ABC-DEF..." @blur="saveSettings" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Chat ID</label>
              <input v-model="settings.telegram.chat_id" type="text" class="input" placeholder="-1001234567890" @blur="saveSettings" />
            </div>
            <button @click="testChannel('telegram')" class="btn-secondary text-sm">测试通知</button>
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-green-600 dark:text-green-400" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                </svg>
              </div>
              <div>
                <h4 class="font-semibold text-slate-900 dark:text-white">方塘 (ServerChan)</h4>
                <p class="text-sm text-gray-500 dark:text-gray-400">通过方塘服务发送通知</p>
              </div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="settings.serverchan.enabled" type="checkbox" class="sr-only peer" @change="saveSettings">
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div v-if="settings.serverchan.enabled" class="space-y-4 pl-13">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">SendKey</label>
              <input v-model="settings.serverchan.sendkey" type="text" class="input" placeholder="您的 SendKey" @blur="saveSettings" />
            </div>
            <button @click="testChannel('serverchan')" class="btn-secondary text-sm">测试通知</button>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-6">
      <h3 class="text-base md:text-lg font-semibold mb-4 text-slate-900 dark:text-white">通知规则</h3>

      <div class="space-y-4">
        <label class="flex items-center gap-3">
          <input v-model="settings.notify_on_success" type="checkbox" class="w-4 h-4" @change="saveSettings" />
          <span class="text-sm text-slate-700 dark:text-slate-300">同步成功时发送通知</span>
        </label>

        <label class="flex items-center gap-3">
          <input v-model="settings.notify_on_failure" type="checkbox" class="w-4 h-4" @change="saveSettings" />
          <span class="text-sm text-slate-700 dark:text-slate-300">同步失败时发送通知</span>
        </label>
      </div>
    </div>

    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-base md:text-lg font-semibold text-slate-900 dark:text-white">通知模板</h3>
        <button @click="resetTemplates" class="btn-secondary text-sm">恢复默认</button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            成功通知模板
            <span class="text-xs text-gray-400 ml-2">支持 Markdown，使用 {"{变量}"} 插入动态内容</span>
          </label>
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">
            可用变量: {"{task_name}"}, {"{datetime}"}, {"{uploads}"}, {"{downloads}"}, {"{deletes}"}, {"{skips}"}, {"{total}"}, {"{message}"}
          </p>
          <textarea
            v-model="settings.template_success"
            rows="8"
            class="input font-mono text-sm"
            placeholder="输入成功通知模板..."
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            失败通知模板
            <span class="text-xs text-gray-400 ml-2">支持 Markdown，使用 {"{变量}"} 插入动态内容</span>
          </label>
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">
            可用变量: {"{task_name}"}, {"{datetime}"}, {"{message}"}, {"{status}"}
          </p>
          <textarea
            v-model="settings.template_failure"
            rows="8"
            class="input font-mono text-sm"
            placeholder="输入失败通知模板..."
          ></textarea>
        </div>

        <div class="flex gap-3">
          <button @click="saveSettings" class="btn-primary">保存模板</button>
          <button @click="testTemplates" class="btn-secondary">预览模板</button>
        </div>
      </div>

      <div v-if="previewText" class="mt-4 p-4 bg-gray-50 dark:bg-slate-700/50 rounded-lg">
        <h4 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">模板预览:</h4>
        <div class="text-xs text-slate-700 dark:text-slate-300 space-y-2 leading-relaxed" v-html="previewHtml"></div>
      </div>
    </div>

    <div v-if="testResult" class="mt-4 p-4 rounded-lg" :class="testResult.success ? 'bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400'">
      {{ testResult.message || testResult.error }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'

const settings = ref({
  telegram: {
    enabled: false,
    bot_token: '',
    chat_id: ''
  },
  serverchan: {
    enabled: false,
    sendkey: ''
  },
  notify_on_success: true,
  notify_on_failure: true,
  template_success: '',
  template_failure: ''
})

const testResult = ref(null)
const previewText = ref('')
const previewHtml = computed(() => renderMarkdownSafe(previewText.value))

const defaultSuccessTemplate = `## ✅ 同步任务完成

**任务**: \`{task_name}\`

**状态**: 成功完成

**时间**: {datetime}

### 同步统计
- 📤 上传: {uploads} 个文件
- 📥 下载: {downloads} 个文件
- 🗑️ 删除: {deletes} 个文件
- ⏭️ 跳过: {skips} 个文件

---
**由 HF Bucket Sync 发送**`

const defaultFailureTemplate = `## ❌ 同步任务失败

**任务**: \`{task_name}\`

**状态**: 执行失败

**时间**: {datetime}

### 错误信息
\`\`\`
{message}
\`\`\`

---
**由 HF Bucket Sync 发送**`

async function loadSettings() {
  try {
    const res = await api.get('/notifications/settings')
    settings.value = res.data
    if (!settings.value.template_success) {
      settings.value.template_success = defaultSuccessTemplate
    }
    if (!settings.value.template_failure) {
      settings.value.template_failure = defaultFailureTemplate
    }
  } catch (e) {
    console.error('Failed to load settings:', e)
  }
}

async function saveSettings() {
  try {
    await api.post('/notifications/settings', settings.value)
    testResult.value = null
  } catch (e) {
    console.error('Failed to save settings:', e)
  }
}

async function testChannel(channel) {
  try {
    testResult.value = null
    const res = await api.post('/notifications/test', null, { params: { channel } })
    testResult.value = res.data[channel]
  } catch (e) {
    testResult.value = {
      success: false,
      error: e.response?.data?.detail || '测试失败'
    }
  }
}

function resetTemplates() {
  settings.value.template_success = defaultSuccessTemplate
  settings.value.template_failure = defaultFailureTemplate
  saveSettings()
}

function testTemplates() {
  const now = new Date().toLocaleString('zh-CN')

  let text = settings.value.template_success || defaultSuccessTemplate
  text = text.replace(/{task_name}/g, '测试任务')
  text = text.replace(/{datetime}/g, now)
  text = text.replace(/{uploads}/g, '3')
  text = text.replace(/{downloads}/g, '2')
  text = text.replace(/{deletes}/g, '1')
  text = text.replace(/{skips}/g, '0')
  text = text.replace(/{total}/g, '6')
  text = text.replace(/{message}/g, '测试消息内容')
  text = text.replace(/{status}/g, '✅ 成功')

  previewText.value = text
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function renderInline(text) {
  return text
    .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 rounded bg-slate-200 dark:bg-slate-600">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}

function renderMarkdownSafe(markdown) {
  if (!markdown) return ''

  const escaped = escapeHtml(markdown)
  const lines = escaped.split('\n')
  const out = []
  let inList = false
  let inCode = false

  for (const rawLine of lines) {
    const line = rawLine.trimEnd()

    if (line.startsWith('```')) {
      if (!inCode) {
        out.push('<pre class="p-3 rounded bg-slate-200/60 dark:bg-slate-800/60 overflow-x-auto"><code>')
        inCode = true
      } else {
        out.push('</code></pre>')
        inCode = false
      }
      continue
    }

    if (inCode) {
      out.push(`${line}\n`)
      continue
    }

    if (!line.trim()) {
      if (inList) {
        out.push('</ul>')
        inList = false
      }
      continue
    }

    if (line.startsWith('### ')) {
      if (inList) {
        out.push('</ul>')
        inList = false
      }
      out.push(`<h4 class="text-sm font-bold mt-2">${renderInline(line.slice(4))}</h4>`)
      continue
    }

    if (line.startsWith('## ')) {
      if (inList) {
        out.push('</ul>')
        inList = false
      }
      out.push(`<h3 class="text-base font-bold">${renderInline(line.slice(3))}</h3>`)
      continue
    }

    if (line.startsWith('- ')) {
      if (!inList) {
        out.push('<ul class="list-disc pl-5 space-y-1">')
        inList = true
      }
      out.push(`<li>${renderInline(line.slice(2))}</li>`)
      continue
    }

    if (line === '---') {
      if (inList) {
        out.push('</ul>')
        inList = false
      }
      out.push('<hr class="border-slate-300 dark:border-slate-600 my-2" />')
      continue
    }

    if (inList) {
      out.push('</ul>')
      inList = false
    }
    out.push(`<p>${renderInline(line)}</p>`)
  }

  if (inList) out.push('</ul>')
  if (inCode) out.push('</code></pre>')

  return out.join('')
}

onMounted(() => {
  loadSettings()
})
</script>
