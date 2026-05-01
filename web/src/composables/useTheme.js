import { ref, watch } from 'vue'

const STORAGE_KEY = 'hf-bucket-sync-theme'
const PALETTE_KEY = 'hf-bucket-sync-palette'
const themeMode = ref(localStorage.getItem(STORAGE_KEY) || 'light')
const themePalette = ref(localStorage.getItem(PALETTE_KEY) || 'ocean')

const PALETTES = {
  ocean: {
    name: '海洋蓝',
    shellBg: 'radial-gradient(ellipse at top right, rgba(91,120,255,0.14), transparent 40%),radial-gradient(ellipse at top left, rgba(57,255,207,0.08), transparent 35%),#111317',
    panelBg: 'rgba(0,0,0,0.25)',
    accent: '#2563eb',
    accentShadow: 'rgba(37,99,235,0.30)'
  },
  emerald: {
    name: '翡翠绿',
    shellBg: 'radial-gradient(ellipse at top right, rgba(16,185,129,0.16), transparent 42%),radial-gradient(ellipse at top left, rgba(45,212,191,0.10), transparent 35%),#0f1514',
    panelBg: 'rgba(5,25,20,0.30)',
    accent: '#059669',
    accentShadow: 'rgba(5,150,105,0.35)'
  },
  violet: {
    name: '紫罗兰',
    shellBg: 'radial-gradient(ellipse at top right, rgba(139,92,246,0.18), transparent 42%),radial-gradient(ellipse at top left, rgba(244,114,182,0.10), transparent 36%),#14101a',
    panelBg: 'rgba(20,10,28,0.32)',
    accent: '#7c3aed',
    accentShadow: 'rgba(124,58,237,0.35)'
  },
  amber: {
    name: '琥珀金',
    shellBg: 'radial-gradient(ellipse at top right, rgba(245,158,11,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(251,191,36,0.10), transparent 36%),#18140e',
    panelBg: 'rgba(28,20,8,0.32)',
    accent: '#d97706',
    accentShadow: 'rgba(217,119,6,0.35)'
  },
  red: {
    name: 'Material Red',
    shellBg: 'radial-gradient(ellipse at top right, rgba(244,67,54,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(255,138,128,0.10), transparent 36%),#1a1111',
    panelBg: 'rgba(35,12,12,0.32)',
    accent: '#f44336',
    accentShadow: 'rgba(244,67,54,0.35)'
  },
  pink: {
    name: 'Material Pink',
    shellBg: 'radial-gradient(ellipse at top right, rgba(233,30,99,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(244,143,177,0.10), transparent 36%),#1a1016',
    panelBg: 'rgba(33,10,24,0.32)',
    accent: '#e91e63',
    accentShadow: 'rgba(233,30,99,0.35)'
  },
  purple: {
    name: 'Material Purple',
    shellBg: 'radial-gradient(ellipse at top right, rgba(156,39,176,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(186,104,200,0.10), transparent 36%),#16101b',
    panelBg: 'rgba(25,10,36,0.32)',
    accent: '#9c27b0',
    accentShadow: 'rgba(156,39,176,0.35)'
  },
  deepPurple: {
    name: 'Deep Purple',
    shellBg: 'radial-gradient(ellipse at top right, rgba(103,58,183,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(149,117,205,0.10), transparent 36%),#12101a',
    panelBg: 'rgba(18,12,34,0.32)',
    accent: '#673ab7',
    accentShadow: 'rgba(103,58,183,0.35)'
  },
  indigo: {
    name: 'Material Indigo',
    shellBg: 'radial-gradient(ellipse at top right, rgba(63,81,181,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(121,134,203,0.10), transparent 36%),#101320',
    panelBg: 'rgba(10,14,35,0.32)',
    accent: '#3f51b5',
    accentShadow: 'rgba(63,81,181,0.35)'
  },
  blue: {
    name: 'Material Blue',
    shellBg: 'radial-gradient(ellipse at top right, rgba(33,150,243,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(100,181,246,0.10), transparent 36%),#0e1620',
    panelBg: 'rgba(8,20,35,0.32)',
    accent: '#2196f3',
    accentShadow: 'rgba(33,150,243,0.35)'
  },
  lightBlue: {
    name: 'Light Blue',
    shellBg: 'radial-gradient(ellipse at top right, rgba(3,169,244,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(79,195,247,0.10), transparent 36%),#0e1820',
    panelBg: 'rgba(8,22,35,0.32)',
    accent: '#03a9f4',
    accentShadow: 'rgba(3,169,244,0.35)'
  },
  cyan: {
    name: 'Material Cyan',
    shellBg: 'radial-gradient(ellipse at top right, rgba(0,188,212,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(77,208,225,0.10), transparent 36%),#0d1a1b',
    panelBg: 'rgba(7,28,30,0.32)',
    accent: '#00bcd4',
    accentShadow: 'rgba(0,188,212,0.35)'
  },
  teal: {
    name: 'Material Teal',
    shellBg: 'radial-gradient(ellipse at top right, rgba(0,150,136,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(77,182,172,0.10), transparent 36%),#0d1917',
    panelBg: 'rgba(8,25,20,0.32)',
    accent: '#009688',
    accentShadow: 'rgba(0,150,136,0.35)'
  },
  green: {
    name: 'Material Green',
    shellBg: 'radial-gradient(ellipse at top right, rgba(76,175,80,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(129,199,132,0.10), transparent 36%),#101a12',
    panelBg: 'rgba(12,28,14,0.32)',
    accent: '#4caf50',
    accentShadow: 'rgba(76,175,80,0.35)'
  },
  lime: {
    name: 'Material Lime',
    shellBg: 'radial-gradient(ellipse at top right, rgba(205,220,57,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(220,231,117,0.10), transparent 36%),#1a1b10',
    panelBg: 'rgba(30,30,10,0.32)',
    accent: '#cddc39',
    accentShadow: 'rgba(205,220,57,0.35)'
  },
  yellow: {
    name: 'Material Yellow',
    shellBg: 'radial-gradient(ellipse at top right, rgba(255,235,59,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(255,241,118,0.10), transparent 36%),#1d1a0d',
    panelBg: 'rgba(34,29,8,0.32)',
    accent: '#ffeb3b',
    accentShadow: 'rgba(255,235,59,0.35)'
  },
  orange: {
    name: 'Material Orange',
    shellBg: 'radial-gradient(ellipse at top right, rgba(255,152,0,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(255,183,77,0.10), transparent 36%),#1d140d',
    panelBg: 'rgba(34,20,8,0.32)',
    accent: '#ff9800',
    accentShadow: 'rgba(255,152,0,0.35)'
  },
  deepOrange: {
    name: 'Deep Orange',
    shellBg: 'radial-gradient(ellipse at top right, rgba(255,87,34,0.20), transparent 42%),radial-gradient(ellipse at top left, rgba(255,138,101,0.10), transparent 36%),#1d120f',
    panelBg: 'rgba(34,16,10,0.32)',
    accent: '#ff5722',
    accentShadow: 'rgba(255,87,34,0.35)'
  }
}

function getSystemDark() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function applyTheme() {
  const isDark = themeMode.value === 'dark' || (themeMode.value === 'system' && getSystemDark())
  if (isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

function applyPalette() {
  const palette = PALETTES[themePalette.value] || PALETTES.ocean
  document.documentElement.style.setProperty('--shell-bg', palette.shellBg)
  document.documentElement.style.setProperty('--panel-bg', palette.panelBg)
  document.documentElement.style.setProperty('--accent', palette.accent)
  document.documentElement.style.setProperty('--accent-shadow', palette.accentShadow)
}

export function setThemeMode(mode) {
  themeMode.value = mode
  localStorage.setItem(STORAGE_KEY, mode)
  applyTheme()
}

export function setThemePalette(palette) {
  if (!PALETTES[palette]) return
  themePalette.value = palette
  localStorage.setItem(PALETTE_KEY, palette)
  applyPalette()
}

export function cycleTheme() {
  if (themeMode.value === 'light') {
    setThemeMode('dark')
  } else if (themeMode.value === 'dark') {
    setThemeMode('system')
  } else {
    setThemeMode('light')
  }
}

export function initTheme() {
  applyTheme()
  applyPalette()
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (themeMode.value === 'system') {
      applyTheme()
    }
  })
}

export const paletteOptions = Object.entries(PALETTES).map(([key, value]) => ({
  key,
  name: value.name,
  accent: value.accent
}))

export { themeMode, themePalette }
