<template>
  <div ref="image" class="image" :style="style"></div>
</template>

<script>
  import torgba from '@/plugins/torgba'
  import animate from '@/plugins/animate'
  export default {
    name: 'GradientLayer',

    props: {
        layer: Object
    },

    computed: {
        style() {
            return {
                background: `repeating-linear-gradient(to right, ${this.layer.image.colorstops.map(({ position, value }) => `${torgba(value)} ${position / this.layer.repeat * 100}%`).join(', ')})`,
                width: this.layer.size.__typename === 'StaticDimension' ? `${this.layer.size.value * this.layer.repeat * 100}%` : undefined,
                left: this.layer.left.__typename === 'StaticDimension' ? `${this.layer.left.value * 100}%` : undefined
            }
        }
    },

    methods: {
      setAnimation() {
        if (this.layer.size.__typename === 'DimensionAnimation') {
          animate(this.$refs.image, this.layer.size, value => ({ width: `${value * this.layer.repeat * 100}%` }))
        }
        if (this.layer.left.__typename === 'DimensionAnimation') {
          animate(this.$refs.image, this.layer.left, value => ({ left: `${value * 100}%` }))
        }
      }
    },

    mounted() {
        this.setAnimation()
    },

    watch: {
        layer: 'setAnimation'
    }
  }
</script>

<style>
.image {
    position: absolute;
    height: 100%;
}
</style>
