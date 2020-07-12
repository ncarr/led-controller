<template>
  <deferred-render :defer="loading">
    <template #placeholder>
      <div class="placeholder-block" :style="{ width: width || '10em' }" />
    </template>
    <template #default>
      <slot />
    </template>
  </deferred-render>
</template>

<script>
import DeferredRender from '@/components/DeferredRender'
export default {
  components: {
    DeferredRender
  },
  props: ['width', 'loading'],
}
</script>

<style>
.placeholder-block {
  background-color: rgba(255, 255, 255, 0.12);
  height: 1em;
}
</style>