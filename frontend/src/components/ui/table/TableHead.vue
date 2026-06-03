<script setup lang="ts">
import type { HTMLAttributes } from 'vue';
import { cn } from '@/lib/utils';

const props = defineProps<{
  class?: HTMLAttributes['class'];
}>();
</script>

<template>
  <th
    :class="
      cn(
        'border-b border-[#edf0ec] p-4 text-left align-middle text-xs font-bold uppercase text-[#59655f]',
        props.class,
      )
    "
  >
    <slot />
  </th>
</template>
