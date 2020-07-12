<script>
export default {
  name: 'DeferredRender',
  functional: true,
  props: ['defer'],
  render(createElement, context) {
    if (context.props.defer) {
      return context.scopedSlots.placeholder()
    } else {
      return context.scopedSlots.default()
    }
  },
}
</script>
