<script setup lang="ts">
import type { HTMLAttributes } from 'vue';
import { cn } from '@/lib/utils';

const props = defineProps<{
  class?: HTMLAttributes['class'];
}>();
</script>

<template>
  <label :class="cn('text-sm font-bold leading-none text-[#4d5c55]', props.class)">
    <slot />
  </label>
</template>
