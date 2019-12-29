from rpi_ws281x import Color, PixelStrip, ws
from controller import Scene, Layer, Color

LED_COUNT = 150
GPIO_PIN = 21
LED_STRIP = ws.SK6812W_STRIP

strip = PixelStrip(LED_COUNT, GPIO_PIN, strip_type=LED_STRIP)
scene = Scene([Layer(Color(0, 255, 0, 255))])


def drawFrame(strip: PixelStrip, scene: Scene, time: float) -> None:
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, scene.getColorAtPositionAndTime(
        (i + 0.5) / strip.numPixels(), time))
  strip.show()

drawFrame(strip, scene, 0.0)