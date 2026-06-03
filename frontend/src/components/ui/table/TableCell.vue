<script setup lang="ts">
import type { HTMLAttributes } from 'vue';
import { cn } from '@/lib/utils';

const props = defineProps<{
  class?: HTMLAttributes['class'];
}>();
</script>

<template>
  <td :class="cn('border-b border-[#edf0ec] p-4 align-middle', props.class)">
    <slot />
  </td>
</template>
