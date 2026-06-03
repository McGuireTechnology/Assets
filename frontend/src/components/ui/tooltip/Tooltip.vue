<script setup lang="ts">
import type { HTMLAttributes } from 'vue';
import {
  TooltipArrow,
  TooltipContent,
  TooltipPortal,
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger,
} from 'reka-ui';
import { cn } from '@/lib/utils';

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes['class'];
    count?: number;
    side?: 'top' | 'right' | 'bottom' | 'left';
    text: string;
  }>(),
  {
    side: 'right',
  },
);
</script>

<template>
  <TooltipProvider :delay-duration="250" :skip-delay-duration="100">
    <TooltipRoot>
      <TooltipTrigger as-child>
        <slot />
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent
          :side="side"
          :side-offset="10"
          :class="cn('tooltip-content', props.class)"
        >
          <span class="tooltip-label">{{ text }}</span>
          <span v-if="count !== undefined" class="tooltip-count">
            Count: {{ count.toLocaleString() }}
          </span>
          <TooltipArrow class="tooltip-arrow" />
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>
