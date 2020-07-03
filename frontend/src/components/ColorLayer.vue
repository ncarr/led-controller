<template>
  <div class="image" :style="style"></div>
</template>

<script>
  import toRGBA from '../plugins/torgba'
  export default {
    name: 'ColorLayer',

    props: {
        layer: Object
    },

    computed: {
        style() {
            return {
                backgroundColor: toRGBA(this.layer.image),
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