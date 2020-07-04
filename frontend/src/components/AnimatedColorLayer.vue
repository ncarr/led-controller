<template>
  <div ref="image" class="image" :style="style"></div>
</template>

<script>
  import torgba from '../plugins/torgba'
  export default {
    name: 'AnimatedColorLayer',

    props: {
        layer: Object
    },

    computed: {
        style() {
            return {
                width: `${this.layer.size * this.layer.repeat * 100}%`,
                left: `${this.layer.left * 100}%`
            }
        }
    },

    methods: {
      setAnimation() {
        if (this.layer.image.sensor.__typename === 'Clock') {
          const keyframes = this.layer.image.keyframes.map(({ position, value }) => ({ offset: position, backgroundColor: torgba(value) }))
          const timing = {
            duration: this.layer.image.sensor.duration,
            iterations: this.layer.image.repeat,
            fill: 'both',
            delay: this.layer.image.sensor.start - Date.now()
          }
          this.$refs.image.animate(keyframes, timing)
        }
      }
    },

    mounted() {
        this.setAnimation()
    },

    watch: {
        'layer.image': 'setAnimation'
    }
  }
</script>

<style>
.image {
    position: absolute;
    height: 100%;
}
</style>
