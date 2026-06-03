<script setup lang="ts">
import type { HTMLAttributes } from 'vue';
import { cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex min-w-6 items-center justify-center rounded-md px-2 py-0.5 text-xs font-bold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-[#27645c] text-white',
        secondary: 'bg-[#eef4f1] text-[#24332f]',
      },
    },
    defaultVariants: {
      variant: 'secondary',
    },
  },
);

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes['class'];
    variant?: 'default' | 'secondary';
  }>(),
  {
    variant: 'secondary',
  },
);
</script>

<template>
  <span :class="cn(badgeVariants({ variant }), props.class)">
    <slot />
  </span>
</template>
