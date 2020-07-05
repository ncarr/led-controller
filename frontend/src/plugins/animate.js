export default function animate(element, data, valueTransform) {
  if (data.sensor.__typename === 'Clock') {
    const keyframes = data.keyframes.map(({ position, value }) => ({ offset: position, ...valueTransform(value) }))
    const timing = {
      duration: data.sensor.duration,
      iterations: data.repeat,
      fill: 'both',
      delay: data.sensor.start - Date.now()
    }
    element.animate(keyframes, timing)
  }
}