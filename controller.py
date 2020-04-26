from __future__ import annotations
from math import inf
from bisect import bisect, insort_left, insort_right
from dataclasses import dataclass, field
from typing import List, Union, TypeVar, Any
from time import monotonic
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, MetaData, Table
from sqlalchemy.orm import relationship, mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

"""
Generic base class for anything that acts as a stop on a continuous spectrum
(i.e. keyframes, colorstops)
"""
@dataclass(order=True)
class Keyframe:
  # To make calculations easier, keyframes are compared by position, not by value
  value: Any = field(compare=False)
  position: float


def blend(keyframes: List[Keyframe], position: float) -> Any:
  # Find the index of the keyframe after the current position
  i: int = bisect(keyframes, Keyframe(None, position))
  # Find the distance between the current position and the previous keyframe
  # as a percentage of the position between the two keyframes
  distance: float = (position - keyframes[i - 1].position) / \
      (keyframes[i].position - keyframes[i - 1].position)
  # Take the weighted average for the value using the distance as weighting
  return (1 - distance) * keyframes[i - 1].value + distance * keyframes[i].value


class DimensionKeyframe(Keyframe, Base):
  animation_id = Column(Integer, ForeignKey('dimensionanimation.id'))
  value = Column(Float)
  position = Column(Float)

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

  def getValueAtTime(self, time: float) -> Any:
    return self.value.getValueAtTime(time) * self.scale


@dataclass
class AnimationSum(AnimationMathMixin):
  value: Animation
  other: Animation

  def getValueAtTime(self, time: float) -> Any:
    return self.value.getValueAtTime(time) + self.other.getValueAtTime(time)


@dataclass
class Animation(AnimationMathMixin):
  keyframes: List[Keyframe]
  repeat: float = field(init=False, default=0.0)
  reference: float = field(init=False, default=0.0)

  def start(self, repeat: float = inf) -> None:
    self.repeat = repeat
    self.length = self.keyframes[len(self.keyframes) - 1].position - self.keyframes[0].position
    self.reference = monotonic()

  def getValueAtTime(self, time: float) -> Any:
    try:
      if self.length != 0 and (time - self.reference) / self.length <= self.repeat:
        return blend(self.keyframes, position=(time - self.reference) % self.length)
      else:
        # When the animation is not running, it uses the value of the first keyframe
        return self.keyframes[0].value
    except AttributeError:
      raise AttributeError('Animation not started')

  @classmethod
  def fromValue(cls, value: Any):
    animation = cls([Keyframe(value, position=0.0)])
    animation.start()
    return animation


class DimensionAnimation(Animation, Base):
  repeat = Column(Float)
  keyframes = relationship(DimensionKeyframe)


class Image(Base):
  identity = Column(String)

  __mapper_args__ = {
    'polymorphic_identity': 'image',
    'polymorphic_on': 'identity'
  }

  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    pass



class Color(Image, RightMathMixin):
  __tablename__ = None

  __mapper_args__ = {
      'polymorphic_identity': 'color'
  }

  red = Column(Float)
  green = Column(Float)
  blue = Column(Float)
  white = Column(Float)
  opacity = Column(Float)

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


class ColorKeyframe(Keyframe, Base):
  animation_id = Column(Integer, ForeignKey('image.id'))
  color_id = Column(Integer, ForeignKey('image.id'))
  value = relationship(Color, foreign_keys=color_id)
  position = Column(Float)


class ColorAnimation(Animation, Image):
  __tablename__ = None

  __mapper_args__ = {
      'polymorphic_identity': 'coloranimation'
  }

  repeat = Column(Float)
  keyframes = relationship(ColorKeyframe, foreign_keys=ColorKeyframe.animation_id)

  # Implement image rendering
  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    return self.getValueAtTime(time)


class ColorStop(Keyframe, Base):
  gradient_id = Column(Integer, ForeignKey('image.id'))
  color_id = Column(Integer, ForeignKey('image.id'))
  value = relationship(Color, foreign_keys=color_id)
  position = Column(Float)


class Gradient(Image):
  __tablename__ = None

  __mapper_args__ = {
      'polymorphic_identity': 'gradient'
  }

  colorstops = relationship(ColorStop, foreign_keys=ColorStop.gradient_id)

  def __init__(self, colorstops: List[ColorStop]):
    super().__init__()
    if len(colorstops) == 0:
      raise ValueError
    self.colorstops = colorstops
    # Colour in the endpoints
    insort_left(self.colorstops, ColorStop(self.colorstops[0].value, 0.0))
    insort_right(self.colorstops, ColorStop(self.colorstops[len(self.colorstops) - 1].value, 1.0))

  def getColorAtPositionAndTime(self, pos: float, time: float):
    return blend(self.colorstops, pos).getValueAtTime(time)


class Layer(Base):
  scene_id = Column(Integer, ForeignKey('scene.id'))
  image_id = Column(Integer, ForeignKey('image.id'))
  image = relationship(Image)
  size_id = Column(Integer, ForeignKey('dimensionanimation.id'))
  size = relationship(DimensionAnimation, foreign_keys=size_id)
  left_id = Column(Integer, ForeignKey('dimensionanimation.id'))
  left = relationship(DimensionAnimation, foreign_keys=left_id)
  repeat = Column(Float)

  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    left = self.left.getValueAtTime(time)
    size = self.size.getValueAtTime(time)
    if (pos - left) / size <= self.repeat:
      return self.image.getColorAtPositionAndTime(((pos - left) % size) / size, time)
    else:
      return Color.transparent()


class Scene(Base):
  name = Column(String)
  layers = relationship(Layer)

  def getColorAtPositionAndTime(self, pos: float, time: float) -> Color:
    # Start with an opaque black background
    result = Color(0.0, 0.0, 0.0)
    # Blend colours layer by layer
    for layer in self.layers:
      color = layer.getColorAtPositionAndTime(pos, time)
      result = result * (1.0 - color.opacity) + color
    return result


class Device(Base):
  led_count = Column(Integer)
  gpio_pin = Column(Integer)
  led_strip = Column(Integer)
  name = Column(String)
  scene_id = Column(Integer, ForeignKey('scene.id'))
  scene = relationship(Scene)

# TODO: id, tablename
