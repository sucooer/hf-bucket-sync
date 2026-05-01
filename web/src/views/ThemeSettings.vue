<template>
  <div class="p-4 md:p-6 lg:p-10 space-y-6 md:space-y-10 max-w-[1600px] mx-auto overflow-hidden">
    <div class="flex items-end justify-between animate-fade-up">
      <div>
        <h2 class="text-4xl font-black text-slate-900 tracking-tight">主题设置</h2>
        <p class="hidden md:block text-slate-500 font-medium mt-2">切换显示模式和网站配色方案。</p>
      </div>
    </div>

    <div class="card glass !bg-slate-900 !border-slate-800 shadow-2xl shadow-blue-900/20 animate-fade-up delay-1">
      <h3 class="text-sm font-black tracking-wider uppercase text-slate-300 mb-4">显示模式</h3>
      <div class="flex gap-3">
        <button class="btn-secondary !bg-white/10 !border-white/20 !text-white" :class="themeMode==='light' ? '!bg-white/25' : ''" @click="setThemeMode('light')">亮色</button>
        <button class="btn-secondary !bg-white/10 !border-white/20 !text-white" :class="themeMode==='dark' ? '!bg-white/25' : ''" @click="setThemeMode('dark')">暗色</button>
        <button class="btn-secondary !bg-white/10 !border-white/20 !text-white" :class="themeMode==='system' ? '!bg-white/25' : ''" @click="setThemeMode('system')">系统</button>
      </div>
    </div>

    <div class="card animate-fade-up delay-2">
      <h3 class="text-sm font-black tracking-wider uppercase text-slate-500 mb-4">配色方案（Material 风格）</h3>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <button
          v-for="palette in paletteOptions"
          :key="palette.key"
          @click="setThemePalette(palette.key)"
          class="rounded-2xl border p-3 text-left transition-all hover:shadow-lg"
          :class="themePalette === palette.key ? 'border-slate-900 dark:border-white shadow-md' : 'border-slate-200 dark:border-slate-700'"
        >
          <div class="h-10 rounded-xl mb-2" :style="{ background: palette.accent }"></div>
          <p class="text-xs font-bold text-slate-900 dark:text-slate-100 truncate">{{ palette.name }}</p>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { paletteOptions, setThemeMode, setThemePalette, themeMode, themePalette } from '@/composables/useTheme'
</script>

