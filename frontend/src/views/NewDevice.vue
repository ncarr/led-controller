<template>
  <apollo-mutation
    :mutation="require('@/graphql/NewDevice.gql')"
    :variables="{ device }"
    :update="updateCache"
    @done="$router.push('/')"
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
            <v-container>
              <v-row>
                <v-col v-if="error">
                  <v-card color="error">
                    <v-card-title>An error occurred creating the device.</v-card-title>
                    <v-card-subtitle v-text="error" />
                  </v-card>
                </v-col>
                <v-col cols="12">
                  <v-text-field label="Device name" required v-model="device.name" :rules="[v => !!v || 'Name is required']" />
                </v-col>
                <v-col cols="12">
                  <v-text-field label="Number of LEDs" required v-model="device.ledCount" type="number" :rules="[v => !!v || 'LED count is required', v => v >= 1 || 'At least 1 LED is required', v => v % 1 === 0 || 'Must be an integer']" />
                </v-col>
                <v-col cols="12">
                  <v-text-field label="GPIO pin number" required v-model="device.gpioPin" type="number" :rules="[v => !!v || 'GPIO pin number is required', v => v >= 0 || 'Must be nonnegative', v => v % 1 === 0 || 'Must be an integer']" />
                </v-col>
                <v-col cols="12">
                  <v-radio-group label="LED strip type" v-model="device.ledStrip" :rules="[v => !!v || 'LED strip type is required']">
                    <v-radio label="SK6812 (without white channel) or WS2812" :value="0x00081000" />
                    <v-radio label="SK6812W" :value="0x18081000" />
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
  import query from '@/graphql/NewDeviceQuery.gql'
  export default {
    name: 'NewDevice',
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
      updateCache(store, { data: { createDevice: { result } } }) {
        const data = store.readQuery({ query })
        console.log(store)
        console.log(data)
        data.devices.push(result)
        console.log(data)
        store.writeQuery({
          query,
          data
        })
        console.log(data)
        console.log(store)
      }
    }
  }
</script>
