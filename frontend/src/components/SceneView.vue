<template>
  <div class="scene-view">
    <template v-for="layer in scene.layers">
      <color-layer v-if="layer.__typename === 'Color'" :layer="layer" :key="layer.id" />
      <animated-color-layer v-if="layer.__typename === 'ColorAnimation'" :layer="layer" :key="layer.id" />
      <gradient-layer v-if="layer.__typename === 'Gradient'" :layer="layer" :key="layer.id" />
    </template>
  </div>
</template>

<script>
import ColorLayer from './ColorLayer'
import AnimatedColorLayer from './AnimatedColorLayer'
import GradientLayer from './GradientLayer'
export default {
  components: {
    ColorLayer,
    AnimatedColorLayer,
    GradientLayer
  },

  props: {
    scene: Object
  }
}
</script>

<style>
.scene-view {
  position: relative;
  height: 10px;
}
</style>