<template>
  <apollo-query
    :query="require('@/graphql/EditDevice.gql')"
    :variables="{ id: $route.params.id }"
    v-slot="{ result: { error, data }, isLoading }"
  >
    <v-app>
      <v-app-bar app flat color="transparent">
        <v-app-bar-nav-icon>
          <v-btn icon to="/">
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
        </v-app-bar-nav-icon>
      </v-app-bar>

      <v-main>
        <error-handler :error="error || (!isLoading && !(data && data.device) && 'Device not found.')" text="An error occurred loading info for this device." v-slot>
          <v-container fluid>
            <v-row>
              <v-col cols="12">
                <v-card>
                  <scene-view v-if="data && data.device.scene" :scene="data.device.scene" />
                  <v-card-title class="overline pb-0">Device info</v-card-title>
                  <placeholder-block width="10em" :loading="isLoading" v-slot>
                    <v-card-title v-text="data.device.name" />
                  </placeholder-block>
                  <placeholder-block width="20em" :loading="isLoading" v-slot>
                    <v-card-subtitle>{{data.device.ledCount}} LED {{data.device.ledStrip === 0x00081000 ? 'RGB' : 'RGBW'}} light strip</v-card-subtitle>
                  </placeholder-block>
                  <v-card-actions>
                    <v-btn
                      :disabled="!!isLoading"
                      text
                      :to="{ name: 'EditDeviceInfo', params: { id: $route.params.id } }"
                    >
                    Edit
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>

              <v-col cols="12">
                <v-card>
                  <v-card-title class="overline">Scene</v-card-title>
                  <grid-list :loading="isLoading" v-slot>
                    <v-container>
                      <v-row>
                        <v-col sm="12" md="6" lg="3">
                          <v-card :class="{ 'card-selection': !data.device.scene, 'text-center': true }">
                            <v-icon class="mt-4">mdi-cancel</v-icon>
                            <v-card-text>None</v-card-text>
                          </v-card>
                        </v-col>

                        <v-col sm="12" md="6" lg="3" v-for="scene in data.scenes" :key="scene.id">
                          <v-card
                            :class="{ 'card-selection': data.device.scene && data.device.scene.id === scene.id }"
                          >
                            <scene-view :scene="scene" />
                            <v-card-title>
                              {{scene.name}}
                              <v-spacer />
                              <v-btn icon>
                                <v-icon>mdi-pencil</v-icon>
                              </v-btn>
                            </v-card-title>
                          </v-card>
                        </v-col>

                        <v-col sm="12" md="6" lg="3">
                          <v-card class="text-center">
                            <v-icon class="mt-4">mdi-plus</v-icon>
                            <v-card-text>Add scene</v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>
                    </v-container>
                  </grid-list>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </error-handler>
        <router-view />
      </v-main>
    </v-app>
  </apollo-query>
</template>

<script>
  import SceneView from '@/components/SceneView'
  import ErrorHandler from '@/components/ErrorHandler'
  import GridList from '@/components/GridList'
  import PlaceholderBlock from '@/components/PlaceholderBlock'
  export default {
    name: 'EditDevice',
    components: {
      SceneView,
      ErrorHandler,
      GridList,
      PlaceholderBlock,
    },
  }
</script>

<style>
.theme--dark.card-selection {
  border: 2px solid rgba(255, 255, 255, 0.12);
}
</style>