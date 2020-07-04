<template>
  <div ref="image" class="image" :style="style"></div>
</template>

<script>
  import torgba from '../plugins/torgba'
  export default {
    name: 'GradientLayer',

    props: {
        layer: Object
    },

    computed: {
        style() {
            return {
                background: `repeating-linear-gradient(to right, ${this.layer.image.colorstops.map(({ position, value }) => `${torgba(value)} ${position / this.layer.repeat * 100}%`).join(', ')})`,
                width: `${this.layer.size * this.layer.repeat * 100}%`,
                left: `${this.layer.left * 100}%`
            }
        }
    }
  }
</script>

<style>
.image {
    position: absolute;
    height: 100%;
}
</style>
