<template>
  <apollo-query
    :query="require('@/graphql/EditScene.gql')"
    :variables="{ scene: $route.params.scene }"
    v-slot="{ result: { error, data }, isLoading }"
  >
    <v-app>
      <v-app-bar app flat color="transparent">
        <v-app-bar-nav-icon>
          <v-btn icon :to="back" exact>
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
        </v-app-bar-nav-icon>
      </v-app-bar>

      <v-main>
        <error-handler :error="error || (!isLoading && !(data && data.scene) && 'Scene not found.')" text="An error occurred loading info for this device." v-slot>
          <v-container fluid>
            <v-row>
              <v-col cols="12">
                <v-card>
                  <scene-view v-if="data" :scene="data.scene" />
                  <v-card-title class="overline pb-0">Scene info</v-card-title>
                  <placeholder-block width="10em" :loading="isLoading" v-slot>
                    <v-card-title>
                      <template v-if="!editName">
                        {{data.scene.name}}
                        <v-btn icon @click="name = data.scene.name; editName = true">
                          <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                      </template>
                      <apollo-mutation
                        v-else
                        :mutation="require('@/graphql/EditSceneInfo.gql')"
                        :variables="{ id: $route.params.scene, scene: { name } }"
                        @done="editName = false"
                        v-slot="{ mutate, loading, error }"
                      >
                        <error-handler :error="error" text="An error occurred saving the scene name." />
                        <v-text-field
                          v-model="name"
                          :loading="loading"
                          autofocus
                          append-outer-icon="mdi-check"
                          @blur="mutate()"
                        />
                      </apollo-mutation>
                    </v-card-title>
                  </placeholder-block>

                  <v-card-actions>
                    <v-dialog v-model="confirmDelete">
                      <template #activator="{ on, attrs }">
                        <v-btn
                          text
                          color="red"
                          v-bind="attrs"
                          v-on="on"
                        >
                          Delete
                        </v-btn>
                      </template>

                      <apollo-mutation
                        :mutation="require('@/graphql/DeleteScene.gql')"
                        :variables="{ id: $route.params.scene }"
                        :update="updateCache"
                        @done="$router.push(back)"
                        v-slot="{ mutate, loading, error }"
                      >
                        <v-card>
                          <v-card-text>
                            <error-handler :error="error" text="An error occurred deleting the scene." />
                            Are you sure you want to delete this scene? This action cannot be undone.
                          </v-card-text>
                          <v-card-actions>
                            <v-btn @click="confirmDelete = false">
                              Cancel
                            </v-btn>
                            <v-btn
                              text
                              color="red"
                              :loading="loading"
                              :disabled="loading"
                              @click="mutate()"
                            >
                              Delete
                            </v-btn>
                          </v-card-actions>
                        </v-card>
                      </apollo-mutation>
                    </v-dialog>
                  </v-card-actions>
                </v-card>
              </v-col>

              <v-col cols="12">
                <v-card>
                  <v-card-title class="overline">Layers</v-card-title>
                  <grid-list :loading="isLoading" v-slot>
                    <v-container>
                      <v-row>
                        <v-col cols="12" v-if="data.scene.layers.length === 0">
                          <v-card>
                            <v-card-title>No layers yet...</v-card-title>
                          </v-card>
                        </v-col>

                        <v-col cols="12" v-for="layer in data.scene.layers" :key="layer.id">
                          <v-card>
                            <v-card-title>
                              {{layer.name}}
                            </v-card-title>
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
    name: 'EditScene',
    components: {
      SceneView,
      ErrorHandler,
      GridList,
      PlaceholderBlock,
    },
    data: () => ({
      name: '',
      editName: false,
      confirmDelete: false
    }),
    computed: {
      back() {
        if (this.$route.params.device) {
          return { name: 'EditDevice', params: { id: this.$route.params.device } }
        } else {
          return { name: 'Scenes' }
        }
      }
    },
    methods: {
      updateCache(cache, { data: { deleteScene: { result } } }) {
        cache.evict({ id: cache.identify(result) })
      }
    }
  }
</script>

<style>
.theme--dark.card-selection {
  border: 2px solid rgba(255, 255, 255, 0.12);
}
</style>