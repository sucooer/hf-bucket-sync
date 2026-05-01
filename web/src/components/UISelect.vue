<template>
  <Listbox v-model="modelValue" :disabled="disabled" as="div" class="relative">
    <ListboxLabel v-if="label" class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-3 block">
      {{ label }}
    </ListboxLabel>
    
    <div class="relative">
      <ListboxButton
        class="relative w-full cursor-pointer rounded-xl bg-slate-100/50 border border-slate-200 py-3 pl-4 pr-10 text-left transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 group hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50 sm:text-sm"
        :class="{ '!bg-slate-800 !border-slate-700 !text-white group-hover:!border-slate-600': dark }"
      >
        <span class="block truncate font-bold" :class="{ 'text-slate-400': !modelValue && placeholder }">
          {{ selectedLabel || placeholder || 'Select option' }}
        </span>
        <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
          <ChevronUpDownIcon class="h-5 h-5 text-slate-400 group-hover:text-blue-500 transition-colors" aria-hidden="true" />
        </span>
      </ListboxButton>

      <transition
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <ListboxOptions
          class="absolute z-50 mt-2 max-h-60 w-full overflow-auto rounded-2xl bg-white p-1.5 text-base shadow-2xl ring-1 ring-black/5 focus:outline-none sm:text-sm custom-scrollbar"
          :class="{ 'glass !bg-slate-900/90 !ring-white/10': dark }"
        >
          <ListboxOption
            v-slot="{ active, selected }"
            v-for="option in options"
            :key="option.value"
            :value="option.value"
            as="template"
          >
            <li
              :class="[
                active ? 'bg-blue-50 text-blue-700' : 'text-slate-700',
                active && dark ? 'bg-blue-600/20 text-blue-400' : '',
                !active && dark ? 'text-slate-300' : '',
                'relative cursor-pointer select-none rounded-xl py-2.5 pl-10 pr-4 transition-colors'
              ]"
            >
              <span :class="[selected ? 'font-black text-blue-600' : 'font-medium', 'block truncate']">
                {{ option.label }}
              </span>
              <span
                v-if="selected"
                class="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600"
              >
                <CheckIcon class="h-5 w-5" aria-hidden="true" />
              </span>
            </li>
          </ListboxOption>
        </ListboxOptions>
      </transition>
    </div>
  </Listbox>
</template>

<script setup>
import { computed } from 'vue'
import {
  Listbox,
  ListboxLabel,
  ListboxButton,
  ListboxOptions,
  ListboxOption,
} from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid'

const props = defineProps({
  modelValue: [String, Number, Boolean, Object],
  options: {
    type: Array,
    required: true,
  },
  label: String,
  placeholder: String,
  disabled: Boolean,
  dark: Boolean
})

const emit = defineEmits(['update:modelValue'])

const modelValue = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const selectedLabel = computed(() => {
  const selected = props.options.find(opt => opt.value === props.modelValue)
  return selected ? selected.label : ''
})
</script>
