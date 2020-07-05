<template>
  <apollo-query
    :query="require('@/graphql/DeviceList.gql')"
    v-slot="{ result: { error, data }, isLoading }"
  >
    <v-app>
      <v-app-bar app>
        <v-toolbar-title>Lights</v-toolbar-title>
      </v-app-bar>

      <v-main>
        <v-container
          class="fill-height"
          fluid
        >
          <v-row align="center" justify="center" v-if="isLoading">
            <v-col class="shrink">
              <v-progress-circular indeterminate />
            </v-col>
          </v-row>

          <v-row align="center" justify="center" v-else-if="error">
            <v-col>
              <v-card color="error">
                <v-card-title>An error occurred looking for devices.</v-card-title>
                <v-card-subtitle v-text="error" />
              </v-card>
            </v-col>
          </v-row>

          <v-row v-else-if="data">
            <v-col v-if="data.devices.length === 0">
              <v-card>
                <v-card-title>No devices yet...</v-card-title>
                <v-card-subtitle>Press the plus below to add a device.</v-card-subtitle>
              </v-card>
            </v-col>

            <v-col sm="12" md="6" lg="3" v-else v-for="device in data.devices" :key="device.id">
              <v-card>
                <scene-view v-if="device.scene" :scene="device.scene" />
                <v-card-title v-text="device.name" />
                <v-card-subtitle v-if="device.scene">Scene: {{device.scene.name}}</v-card-subtitle>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
        <v-btn
          fab
          to="new"
          fixed
          bottom
          right
        >
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        <router-view />
      </v-main>
    </v-app>
  </apollo-query>
</template>

<script>
  import SceneView from '@/components/SceneView'
  export default {
    name: 'Home',
    components: {
      SceneView,
    },
  }
</script>
