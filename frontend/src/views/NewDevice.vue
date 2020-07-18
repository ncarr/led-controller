<template>
  <apollo-mutation
    :mutation="require('@/graphql/NewDevice.gql')"
    :variables="{ device }"
    :update="updateCache"
    @done="({ data: { createDevice: { result: { id } } } }) => $router.push({ name: 'EditDevice', params: { id } })"
    v-slot="{ mutate, loading, error }"
  >
    <v-dialog v-model="dialog">
      <v-card>
        <v-card-title>New device</v-card-title>
        <v-card-text>
          <v-form
            ref="form"
            v-model="valid"
            lazy-validation
          >
            <error-handler :error="error" text="An error occurred creating the device." />
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
  export default {
    name: 'NewDevice',
    components: {
      ErrorHandler
    },
    data: () => ({
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
          this.$router.push('/')
        }
      }
    },
    methods: {
      updateCache(cache, { data: { createDevice: { result } } }) {
        cache.modify({
          fields: {
            devices(existingRefs = [], { toReference }) {
              return [...existingRefs, toReference(result)]
            }
          }
        })
      }
    }
  }
</script>
