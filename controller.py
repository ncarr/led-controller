from __future__ import annotations
from math import inf
from bisect import bisect, insort_left, insort_right
from dataclasses import dataclass, field
from typing import List, Union, TypeVar
from time import monotonic

Animatable = Union[float, 'Color']


@dataclass(order=True)
class Keyframe:
  # To make calculations easier, keyframes are compared by time, not by value
  value: Animatable = field(compare=False)
  time: float


def blend(keyframes: List, position: float, keyframe_class=Keyframe, attr_name: str = 'time') -> Animatable:
  # Find the index of the keyframe after the current position
  i: int = bisect(keyframes, keyframe_class(None, position))
  # Find the distance between the current position and the previous keyframe
  # as a percentage of the position between the two keyframes
  distance: float = (position - getattr(keyframes[i - 1], attr_name)) / \
      (getattr(keyframes[i], attr_name) - getattr(keyframes[i - 1], attr_name))
  # Take the weighted average for the value using the distance as weighting
  return (1 - distance) * keyframes[i - 1].value + distance * keyframes[i].value


class RightMathMixin:
  def __rmul__(self, other):
    return self.__mul__(other)
  
  def __radd__(self, other):
    return self.__add__(other)


class AnimationMathMixin(RightMathMixin):
  def __mul__(self, scale):
    return ScaledAnimation(self, scale)

  def __add__(self, other):
    return AnimationSum(self, other)


@dataclass
class ScaledAnimation(AnimationMathMixin):
  value: Union[Animation, float, int]
  scale: Union[Animation, float, int]

  def getValueAtTime(self, time: float) -> Animatable:
    return self.value.getValueAtTime(time) * self.scale


@dataclass
class AnimationSum(AnimationMathMixin):
  value: Animation
  other: Animation

  def getValueAtTime(self, time: float) -> Animatable:
    return self.value.getValueAtTime(time) + self.other.getValueAtTime(time)


@dataclass
class Animation(AnimationMathMixin):
  keyframes: List[Keyframe]
  repeat: float = field(init=False, default=0.0)

  def start(self, repeat: float = inf) -> None:
    self.repeat = repeat
    self.length = self.keyframes[len(self.keyframes) - 1].time - self.keyframes[0].time
    self.epoch = monotonic()

  def getValueAtTime(self, time: float) -> Animatable:
    try:
      if self.length != 0 and (time - self.epoch) / self.length <= self.repeat:
        return blend(self.keyframes, position=(time - self.epoch) % self.length)
      else:
        # When the animation is not running, it uses the value of the first keyframe
        return self.keyframes[0].value
    except AttributeError:
      raise AttributeError('Animation not started')

  @classmethod
  def fromValue(cls, value: Animatable):
    animation = cls([Keyframe(value, time=0.0)])
    animation.start()
    return animation


class Image:
  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    pass


@dataclass
class Color(Image, RightMathMixin):
  red: float
  green: float
  blue: float
  white: float = 0.0
  opacity: float = 1.0

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

  # Implement basic arithmetic operations
  def __mul__(self, scale: Union[float, int]) -> Color:
    if not isinstance(scale, (float, int)):
      raise NotImplementedError
    result = Color.transparent()
    result.red = self.red * scale
    result.green = self.green * scale
    result.blue = self.blue * scale
    result.white = self.white * scale
    result.opacity = self.opacity * scale
    return result

  def __add__(self, other: Color) -> Color:
    if not isinstance(other, Color):
      raise NotImplementedError
    result = Color.transparent()
    result.red = self.red + other.red
    result.green = self.green + other.green
    result.blue = self.blue + other.blue
    result.white = self.white + other.white
    result.opacity = self.opacity + other.opacity
    return result

  # Implement image rendering
  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    return self.getValueAtTime(time)

  def getValueAtTime(self, time: float):
    return self

  # Returns a new instance of transparent black
  @classmethod
  def transparent(cls):
    return cls(red=0.0, green=0.0, blue=0.0, white=0.0, opacity=0.0)


class AnimatedColor(Animation, Color):
  # Yup, that's all the code we need to animate colours
  pass


@dataclass
class Gradient(Image):
  colorstops: List[ColorStop]

  def __init__(self, colorstops: List[ColorStop]):
    super().__init__()
    if len(colorstops) == 0:
      raise ValueError
    self.colorstops = colorstops
    # Colour in the endpoints
    insort_left(self.colorstops, ColorStop(self.colorstops[0].value, 0.0))
    insort_right(self.colorstops, ColorStop(self.colorstops[len(self.colorstops) - 1].value, 1.0))

  def getColorAtPositionAndTime(self, pos: float, time: float):
    return blend(self.colorstops, pos, keyframe_class=ColorStop, attr_name='location').getValueAtTime(time)


@dataclass(order=True)
class ColorStop:
  # To make calculations easier, colour stops are compared by location, not by colour
  value: Color = field(compare=False)
  location: float


@dataclass
class Scene(Image):
  layers: List[Layer]

  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    # Start with an opaque black background
    result = Color(0.0, 0.0, 0.0)
    # Blend colours layer by layer
    for layer in self.layers:
      color = layer.getColorAtPositionAndTime(pos, time)
      result = result * (1.0 - color.opacity) + color
    return result


@dataclass
class Layer(Image):
  image: Image
  size: Animation = field(default_factory=lambda: Animation.fromValue(1.0))
  left: Animation = field(default_factory=lambda: Animation.fromValue(0.0))
  repeat: float = 1.0

  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    left = self.left.getValueAtTime(time)
    size = self.size.getValueAtTime(time)
    if (pos - left) / size <= self.repeat:
      return self.image.getColorAtPositionAndTime(((pos - left) % size) / size, time)
    else:
      return Color.transparent()
