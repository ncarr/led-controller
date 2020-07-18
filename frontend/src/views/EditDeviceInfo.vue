<template>
  <apollo-mutation
    :mutation="require('@/graphql/EditDeviceInfo.gql')"
    :variables="{ id: $route.params.id, device }"
    @done="$router.push('.')"
    v-slot="{ mutate, loading, error: editError }"
  >
    <apollo-query
      :query="require('@/graphql/GetDeviceInfo.gql')"
      :variables="{ id: $route.params.id }"
      :update="({ device: { __typename, id, ...data } }) => data"
      @result="device = $event.data"
      v-slot="{ error: queryError }"
    >
      <v-dialog v-model="dialog">
        <v-card>
          <v-card-title>Edit device</v-card-title>
          <v-card-text>
            <v-form
              ref="form"
              v-model="valid"
              lazy-validation
            >
              <error-handler :error="editError || queryError" text="An error occurred editing the device." />
              <v-container>
                <v-row>
                  <v-col cols="12">
                    <v-text-field label="Device name" required v-model="device.name" :rules="[v => !!v || 'Name is required']" />
                  </v-col>
                  <v-col cols="12">
                    <v-text-field label="Number of LEDs" required v-model.number="device.ledCount" type="number" :rules="[v => !!v || 'LED count is required', v => v >= 1 || 'At least 1 LED is required', v => v % 1 === 0 || 'Must be an integer']" />
                  </v-col>
                  <v-col cols="12">
                    <v-text-field label="GPIO pin number" required v-model.number="device.gpioPin" type="number" :rules="[v => !!v || 'GPIO pin number is required', v => v >= 0 || 'Must be nonnegative', v => v % 1 === 0 || 'Must be an integer']" />
                  </v-col>
                  <v-col cols="12">
                    <v-radio-group label="LED strip type" v-model="device.ledStrip" :rules="[v => !!v || 'LED strip type is required']">
                      <v-radio label="RGB" :value="0x00081000" />
                      <v-radio label="RGBW" :value="0x18081000" />
                    </v-radio-group>
                  </v-col>
                </v-row>
              </v-container>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-dialog v-model="confirmModal">
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
                :mutation="require('@/graphql/DeleteDevice.gql')"
                :variables="{ id: $route.params.id }"
                :update="updateCache"
                @done="$router.push('/')"
                v-slot="{ mutate: deleteMutate, loading: deleteLoading, error: deleteError }"
              >
                <v-card>
                  <v-card-text>
                    <error-handler :error="deleteError" text="An error occurred deleting the device." />
                    Are you sure you want to delete this device? This action cannot be undone.
                  </v-card-text>
                  <v-card-actions>
                    <v-btn @click="confirmModal = false">
                      Cancel
                    </v-btn>
                    <v-btn
                      text
                      color="red"
                      :loading="deleteLoading"
                      :disabled="deleteLoading"
                      @click="deleteMutate()"
                    >
                      Delete
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </apollo-mutation>
            </v-dialog>
            <v-spacer />
            <v-btn text @click="dialog = false">Cancel</v-btn>
            <v-btn
              text
              :loading="loading"
              :disabled="loading || !valid"
              @click="$refs.form.validate() && mutate()"
            >
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </apollo-query>
  </apollo-mutation>
</template>

<script>
  import ErrorHandler from '@/components/ErrorHandler'
  export default {
    name: 'EditDeviceInfo',
    components: {
      ErrorHandler
    },
    data: () => ({
      confirmModal: false,
      dialog: true,
      valid: false,
      device: {
        name: '',
        ledCount: 1,
        gpioPin: 1,
        ledStrip: 0x00081000,
      }
    }),
    watch: {
      dialog() {
        if (!this.dialog) {
          this.$router.push('.')
        }
      }
    },
    methods: {
      updateCache(cache, { data: { deleteDevice: { result } } }) {
        cache.evict({ id: cache.identify(result) })
      }
    }
  }
</script>
