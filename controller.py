from math import inf
from typing import List, Protocol, Union, TypeVar
from rpi_ws281x import Color, PixelStrip, ws

# Defaults for testing. TODO delete
LED_COUNT = 150
GPIO_PIN = 21
LED_STRIP = ws.SK6812W_STRIP

strip = PixelStrip(LED_COUNT, GPIO_PIN, strip_type=LED_STRIP)
scene = Scene([Layer(Color(0, 255, 0, 255))])

def drawFrame(strip: PixelStrip, scene: Scene) -> None:
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, scene.getColorAtPosition((i + 0.5) / strip.numPixels()))
  strip.show()


class Image(Protocol):
  def getColorAtPosition(self, pos: float) -> Color:
    pass


class Scene(Image):
  def __init__(self, layers: List[Layer]) -> None:
    super().__init__()
    self.layers = layers

  def getColorAtPosition(self, pos: float) -> Color:
    # Start with an opaque black background
    result = Color(0.0, 0.0, 0.0)
    # Blend colours layer by layer
    for layer in self.layers:
      color = layer.getColorAtPosition(pos)
      result = result * (1.0 - color.opacity) + color
    return result


class Layer(Image):
  def __init__(self, image: Image, size=1.0, left=0.0, repeat=1.0) -> None:
    super().__init__()
    self.image = image
    self.size = size
    self.left = left
    self.repeat = repeat

  def getColorAtPosition(self, pos: float) -> Color:
    if (pos - self.left) / self.size <= self.repeat:
      return self.image.getColorAtPosition(((pos - self.left) % self.size) / self.size)
    else:
      return Color.transparent()


class Color(Image):
  def __init__(self, red: float, green: float, blue: float, white=0.0, opacity=1.0) -> None:
    super().__init__()
    # Premultiply the colours for easier processing
    self.red = red * opacity
    self.green = green * opacity
    self.blue = blue * opacity
    self.white = white * opacity
    self.opacity = opacity

  # Converts to WS281x Color object
  def toWS281xColor(self) -> int:
    return int(self.white) << 24 | \
      int(self.red) << 16 | \
      int(self.green) << 8 | \
      int(self.blue)

  # Also known as an integer
  def __int__(self) -> int:
    return self.toWS281xColor()

  # Implement basic arithmentic operations
  def __mul__(self, scale: Union[float, int]) -> Color:
    if not isinstance(scale, float, int):
      raise TypeError
    result = Color.transparent()
    result.red = self.red * scale
    result.green = self.green * scale
    result.blue = self.blue * scale
    result.white = self.white * scale
    result.opacity = self.opacity * scale
    return result

  def __add__(self, other: Color) -> Color:
    if not isinstance(other, Color):
      raise TypeError
    result = Color.transparent()
    result.red = self.red + other.red
    result.green = self.green + other.green
    result.blue = self.blue + other.blue
    result.white = self.white + other.white
    result.opacity = self.opacity + other.opacity
    return result

  # Implement image rendering
  def getColorAtPosition(self, pos: float) -> Color:
    return self

  # Returns a new instance of transparent black
  @classmethod
  def transparent(cls):
    return cls(0.0, 0.0, 0.0, 0.0, 0.0)


class Gradient(Image):
  def __init__(self, colorstops: List[ColorStop]):
    super().__init__()
    if len(colorstops) == 0:
      raise ValueError
    self.colorstops: List[ColorStop] = sorted(colorstops, key=lambda colorstop: colorstop.location)
    # Colour in the endpoints if not defined
    if (first := self.colorstops[0]).location > 0.0:
      self.colorstops.append(ColorStop(first.color, 0.0))
    if (last := self.colorstops[len(self.colorstops) - 1]).location < 1.0:
      self.colorstops.append(ColorStop(last.color, 1.0))
    self.colorstops.sort(key=lambda colorstop: colorstop.location)

  def getColorAtPosition(self, pos):
    # Find the colour stops to the left and right of the current position
    leftStop: ColorStop = self.colorstops[len(self.colorstops) - 2]
    rightStop: ColorStop = self.colorstops[len(self.colorstops) - 1]
    for i, colorstop in enumerate(self.colorstops):
      if colorstop.location > pos:
        leftStop = self.colorstops[i - 1]
        rightStop = colorstop
        break
    # Blend the two colours
    distance: float = (pos - leftStop.location) / (rightStop.location - leftStop.location)
    return (1 - distance) * leftStop.color + distance * rightStop.color


class ColorStop(object):
  def __init__(self, color: Color, location: float):
    self.color = color
    self.location = location
