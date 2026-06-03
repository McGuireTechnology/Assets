<script setup lang="ts">
import type { HTMLAttributes } from 'vue';
import { cn } from '@/lib/utils';

defineOptions({ inheritAttrs: false });

const props = defineProps<{
  class?: HTMLAttributes['class'];
  modelValue?: boolean | string | number | null;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string | number | null];
}>();
</script>

<template>
  <select
    v-bind="$attrs"
    :value="props.modelValue ?? ''"
    :class="
      cn(
        'flex h-[42px] w-full rounded-md border border-[#cbd6d1] bg-white px-3 py-2 text-sm text-[#172026] outline-none transition-colors focus-visible:border-[#27645c] focus-visible:ring-2 focus-visible:ring-[#27645c]/20 disabled:cursor-not-allowed disabled:opacity-60',
        props.class,
      )
    "
    @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value || null)"
  >
    <slot />
  </select>
</template>
