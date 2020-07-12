<template>
  <deferred-render :defer="error">
    <template #placeholder>
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col>
            <v-card color="error">
              <v-card-title v-text="text || 'An error occurred.'"></v-card-title>
              <v-card-subtitle v-text="error" />
            </v-card>
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
    DeferredRender
  },
  props: ['error', 'text']
}
</script>