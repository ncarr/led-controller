<template>
  <div>
    <color-layer :layer="colorLayer" />
    <animated-color-layer :layer="animatedColorLayer" />
  </div>
</template>

<script>
  import ColorLayer from './ColorLayer'
  import AnimatedColorLayer from './AnimatedColorLayer'
  export default {
    name: 'HelloWorld',

    components: {
      ColorLayer,
      AnimatedColorLayer
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
        left: 0.3,
        repeat: 1
      },
      animatedColorLayer: {
        image: {
          keyframes: [
            {
              position: 0,
              value: {
                red: 0,
                green: 0,
                blue: 0,
                white: 0,
                opacity: 0.7
              }
            },
            {
              position: 0.5,
              value: {
                red: 255,
                green: 255,
                blue: 255,
                white: 255,
                opacity: 0.7
              }
            },
            {
              position: 1,
              value: {
                red: 0,
                green: 0,
                blue: 0,
                white: 0,
                opacity: 0.7
              }
            }
          ],
          sensor: {
            __typename: 'Clock',
            start: 0,
            duration: 1000
          },
          repeat: Infinity
        },
        size: 0.6,
        left: 0.1,
        repeat: 1
      }
    }),
  }
</script>
