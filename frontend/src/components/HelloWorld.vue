<template>
  <div>
    <color-layer :layer="colorLayer" />
    <color-layer :layer="colorLayer" />
  </div>
</template>

<script>
  import ColorLayer from './ColorLayer'
  export default {
    name: 'HelloWorld',

    components: {
      ColorLayer
    },

    data: () => ({
      colorLayer: {
        image: {
          red: 127,
          green: 127,
          blue: 0,
          white: 127,
          opacity: 0.7
        },
        size: 0.6,
        left: 0.1,
        repeat: 1
      }
    }),
  }
</script>
