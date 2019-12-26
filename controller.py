from math import inf
from bisect import bisect, insort_left, insort_right
from typing import List, Protocol, Union, TypeVar
from rpi_ws281x import Color, PixelStrip, ws

# Defaults for testing. TODO delete
LED_COUNT = 150
GPIO_PIN = 21
LED_STRIP = ws.SK6812W_STRIP

strip = PixelStrip(LED_COUNT, GPIO_PIN, strip_type=LED_STRIP)
scene = Scene([Layer(Color(0, 255, 0, 255))])

def drawFrame(strip: PixelStrip, scene: Scene, time: float) -> None:
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, scene.getColorAtPositionAndTime((i + 0.5) / strip.numPixels(), time))
  strip.show()

Animatable = Union[float, Color]

def blend(keyframes: List, position: float, keyframe_class=Keyframe, attr_name: str ='time') -> Animatable:
  # Find the index of the keyframe after the current position
  i: int = bisect(keyframes, keyframe_class(None, position))
  # Find the distance between the current position and the previous keyframe
  # as a percentage of the position between the two keyframes
  distance: float = (position - getattr(keyframes[i - 1], attr_name)) / \
    (getattr(keyframes[i], attr_name) - getattr(keyframes[i - 1], attr_name))
  # Take the weighted average for the value using the distance as weighting
  return (1 - distance) * keyframes[i - 1].value + distance * keyframes[i].value


class Animation(Protocol):
  def __init__(self, keyframes: List[Keyframe], repeat = inf) -> None:
    self.keyframes = keyframes
    self.repeat = repeat
    self.length = self.keyframes[len(self.keyframes) - 1].time - self.keyframes[0].time

  def getValueAtTime(self, time: float) -> Animatable:
    if self.length != 0 and time / self.length <= self.repeat:
      return blend(self.keyframes, time % self.length)
    else:
      # When the animation is not running, it uses the value of the first keyframe
      return self.keyframes[0].value

  @classmethod
  def fromValue(cls, value: Animatable):
    return cls([Keyframe(0, value)])


class Keyframe(Protocol):
  def __init__(self, value: Animatable, time: float):
    self.value = value
    self.time = time

  # To make calculations easier, keyframes are compared by time, not by value
  def __lt__(self, other):
    return self.time < other.time


class Image(Protocol):
  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    pass


class Scene(Image):
  def __init__(self, layers: List[Layer]) -> None:
    super().__init__()
    self.layers = layers

  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    # Start with an opaque black background
    result = Color(0.0, 0.0, 0.0)
    # Blend colours layer by layer
    for layer in self.layers:
      color = layer.getColorAtPositionAndTime(pos, time)
      result = result * (1.0 - color.opacity) + color
    return result


class Layer(Image):
  def __init__(self, image: Image, size=Animation.fromValue(1.0), left=Animation.fromValue(0.0), repeat=1.0) -> None:
    super().__init__()
    self.image = image
    self.size = size
    self.left = left
    self.repeat = repeat

  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    left = self.left.getValueAtTime(time)
    size = self.size.getValueAtTime(time)
    if (pos - left) / size <= self.repeat:
      return self.image.getColorAtPositionAndTime(((pos - left) % size) / size)
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
    self.colorstops = colorstops
    # Colour in the endpoints
    insort_left(self.colorstops, ColorStop(self.colorstops[0].color, 0.0))
    insort_right(self.colorstops, ColorStop(self.colorstops[len(self.colorstops) - 1].color, 1.0))

  def getColorAtPositionAndTime(self, pos: float, time: float):
    return blend(self.colorstops, pos, ColorStop, 'location')


class ColorStop(object):
  def __init__(self, color: Color, location: float):
    self.color = color
    self.location = location

  def __lt__(self, other):
    return self.location < other.location
