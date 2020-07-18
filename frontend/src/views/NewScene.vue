<template>
  <apollo-mutation
    :mutation="require('@/graphql/NewScene.gql')"
    :variables="{ scene }"
    :update="updateCache"
    @done="done"
    v-slot="{ mutate, loading, error }"
  >
    <v-dialog v-model="dialog">
      <v-card>
        <v-card-title>New scene</v-card-title>
        <v-card-text>
          <v-form
            ref="form"
            v-model="valid"
            lazy-validation
          >
            <error-handler :error="mutationError || error" text="An error occurred creating the scene." />
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field label="Scene name" required v-model="scene.name" :rules="[v => !!v || 'Name is required']" />
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialog = false">Cancel</v-btn>
          <v-btn
            text
            :loading="loading"
            :disabled="loading || !valid"
            @click="$refs.form.validate() && mutate()"
          >
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </apollo-mutation>
</template>

<script>
  import ErrorHandler from '@/components/ErrorHandler'
  import mutation from '@/graphql/SetScene.gql'
  export default {
    name: 'NewScene',
    components: {
      ErrorHandler
    },
    data: () => ({
      dialog: true,
      valid: false,
      mutationError: null,
      scene: {
        name: '',
      }
    }),
    watch: {
      dialog() {
        if (!this.dialog) {
          if (this.$route.params.id) {
            this.$router.push({ name: 'EditDevice', params: { id: this.$route.params.id } })
          } else {
            this.$router.push({ name: 'Scenes' })
          }
        }
      }
    },
    methods: {
      updateCache(cache, { data: { createScene: { result } } }) {
        cache.modify({
          fields: {
            scenes(existingRefs = [], { toReference }) {
              return [...existingRefs, toReference(result)]
            }
          }
        })
      },
      async done({ data: { createScene: { result: { id: sceneId } } } }) {
        this.mutationError = null
        if (this.$route.params.id) {
          try {
            await this.$apollo.mutate({
              mutation,
              variables: {
                deviceId: this.$route.params.id,
                sceneId
              }
            })
            return this.$router.push({
              name: 'DeviceEditScene',
              params: {
                device: this.$route.params.id,
                scene: sceneId
              }
            })
          } catch (err) {
            this.mutationError = err
          }
        } else {
          return this.$router.push({
            name: 'EditScene',
            params: {
              scene: sceneId
            }
          })
        }
      }
    }
  }
</script>
