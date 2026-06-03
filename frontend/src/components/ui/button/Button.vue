<script setup lang="ts">
import type { HTMLAttributes } from 'vue';
import { Primitive } from 'reka-ui';
import { cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-bold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#27645c] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-60 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default: 'bg-[#27645c] text-white hover:bg-[#1f524b]',
        secondary: 'border border-[#ccd7d2] bg-white text-[#24332f] hover:bg-[#eef4f1]',
        destructive: 'bg-[#a94432] text-white hover:bg-[#873728]',
        ghost: 'text-[#24332f] hover:bg-[#eef4f1]',
      },
      size: {
        default: 'h-10 px-4',
        sm: 'h-9 px-3',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
);

const props = withDefaults(
  defineProps<{
    asChild?: boolean;
    class?: HTMLAttributes['class'];
    size?: 'default' | 'sm' | 'icon';
    variant?: 'default' | 'secondary' | 'destructive' | 'ghost';
  }>(),
  {
    asChild: false,
    size: 'default',
    variant: 'default',
  },
);
</script>

<template>
  <Primitive
    :as="asChild ? undefined : 'button'"
    :as-child="asChild"
    :class="cn(buttonVariants({ variant, size }), props.class)"
  >
    <slot />
  </Primitive>
</template>
