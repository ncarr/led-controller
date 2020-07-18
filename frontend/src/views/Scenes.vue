<template>
  <apollo-query
    :query="require('@/graphql/SceneList.gql')"
    v-slot="{ result: { error, data }, isLoading }"
  >
    <v-app>
      <v-app-bar app>
        <v-toolbar-title>Scenes</v-toolbar-title>
      </v-app-bar>

      <v-main>
        <grid-list :loading="isLoading" v-slot>
          <error-handler :error="error || (!isLoading && !data && 'No data.')" text="An error occurred looking for scenes." v-slot>
            <v-container class="fill-height" fluid>
              <v-row>
                <v-col v-if="data.scenes.length === 0">
                  <v-card>
                    <v-card-title>No scenes yet...</v-card-title>
                    <v-card-subtitle>Press the plus below to add a scene.</v-card-subtitle>
                  </v-card>
                </v-col>

                <v-col sm="12" md="6" lg="3" v-else v-for="scene in data.scenes" :key="scene.id">
                  <v-card :to="{ name: 'EditScene', params: { scene: scene.id } }">
                    <scene-view :scene="scene" />
                    <v-card-title v-text="scene.name" />
                  </v-card>
                </v-col>
              </v-row>
            </v-container>
          </error-handler>
        </grid-list>
        <v-btn
          fab
          to="/scenes/new"
          fixed
          bottom
          right
        >
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        <router-view />
      </v-main>

      <v-bottom-navigation>
        <v-btn to="/">
          <span>Lights</span>
          <v-icon>mdi-lightbulb-multiple</v-icon>
        </v-btn>
        <v-btn to="/scenes">
          <span>Scenes</span>
          <v-icon>mdi-image-filter-hdr</v-icon>
        </v-btn>
      </v-bottom-navigation>
    </v-app>
  </apollo-query>
</template>

<script>
  import SceneView from '@/components/SceneView'
  import ErrorHandler from '@/components/ErrorHandler'
  import GridList from '@/components/GridList'
  export default {
    name: 'Scenes',
    components: {
      SceneView,
      ErrorHandler,
      GridList,
    },
  }
</script>
