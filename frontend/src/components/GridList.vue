<template>
  <deferred-render :defer="loading">
    <template #placeholder>
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col class="shrink">
            <v-progress-circular indeterminate />
          </v-col>
        </v-row>
      </v-container>
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
    DeferredRender,
  },
  props: ['loading']
}
</script>
