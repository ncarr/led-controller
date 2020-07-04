<template>
  <div>
    <scene-view :scene="testScene" />
  </div>
</template>

<script>
  import SceneView from './SceneView'
  export default {
    name: 'HelloWorld',

    components: {
      SceneView
    },

    data: () => ({
      testScene: {
        layers: [
          {
            __typename: 'Color',
            id: 0,
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
          {
            __typename: 'ColorAnimation',
            id: 1,
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
          },
          {
            __typename: 'Gradient',
            id: 2,
            image: {
              colorstops: [
                {
                  position: 0,
                  value: {
                    red: 255,
                    green: 0,
                    blue: 0,
                    white: 0,
                    opacity: 0.7
                  }
                },
                {
                  position: 1,
                  value: {
                    red: 0,
                    green: 0,
                    blue: 255,
                    white: 0,
                    opacity: 0.7
                  }
                }
              ]
            },
            size: 0.2,
            left: 0.4,
            repeat: 2
          }
        ]
      }

    }),
  }
</script>
