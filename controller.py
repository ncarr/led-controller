from __future__ import annotations
from bisect import bisect
from dataclasses import dataclass, field
from typing import List, Union, Any
from time import time
from functools import total_ordering
from copy import copy, deepcopy
from sqlalchemy import Column, Integer, Float, String, ForeignKey, MetaData, Table
from sqlalchemy.orm import relationship, RelationshipProperty, ColumnProperty
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base(object):
  @declared_attr
  def __tablename__(cls):  # pylint: disable=no-self-argument
    return cls.__name__.lower()  # pylint: disable=no-member

  id = Column(Integer, primary_key=True)

  """
  Shallow-copies all related objects and values in all columns except for primary keys.
  Note: this means that the copy will still be connected to all objects in the original object's relationships.
  This could break the single_parent constraint.
  """
  def __copy__(self):
    cls = type(self)
    copied = cls()
    for attr in self.__mapper__.attrs:
      if isinstance(attr, ColumnProperty):
        if not attr.columns[0].primary_key:
          setattr(copied, attr.key, getattr(self, attr.key))
      elif isinstance(attr, RelationshipProperty):
        setattr(copied, attr.key, getattr(self, attr.key))
    return copied

  """
  Deep-copies all related objects and values in all columns, removing all primary keys and foreign keys.
  The copy can safely be saved into the same table
  """
  def __deepcopy__(self, memo):
    cls = type(self)
    copied = cls()
    for attr in self.__mapper__.attrs:
      if isinstance(attr, ColumnProperty):
        if not attr.columns[0].primary_key and not attr.columns[0].foreign_keys:
          setattr(copied, attr.key, deepcopy(getattr(self, attr.key), memo))
      elif isinstance(attr, RelationshipProperty):
        setattr(copied, attr.key, deepcopy(getattr(self, attr.key), memo))
    return copied

"""
Generic base class for anything that acts as a stop on a continuous spectrum
(i.e. keyframes, colorstops)
"""
@dataclass(order=True)
class Keyframe:
  # To make calculations easier, keyframes are compared by position, not by value
  value: Any = field(compare=False)
  position: float


def blend(keyframes: List[Keyframe], position: float):
  if position < keyframes[0].position:
    return keyframes[0].value
  if position >= keyframes[-1].position:
    return keyframes[-1].value
  # Find the index of the keyframe after the current position
  i: int = bisect(keyframes, Keyframe(None, position))
  # Find the distance between the current position and the previous keyframe
  # as a percentage of the position between the two keyframes
  distance: float = (position - keyframes[i - 1].position) / \
      (keyframes[i].position - keyframes[i - 1].position)
  # Take the weighted average for the value using the distance as weighting
  return (1 - distance) * keyframes[i - 1].value + distance * keyframes[i].value


class DimensionKeyframe(Keyframe, Base):
  animation_id = Column(Integer, ForeignKey('dimension.id'))
  value = Column(Float)
  position = Column(Float)


@total_ordering
class MathProxyMixin:
  def __mul__(self, other):
    return self.currentValue() * other

  def __rmul__(self, other):
    return other * self.currentValue()

  def __truediv__(self, other):
    return self.currentValue() / other

  def __rtruediv__(self, other):
    return other / self.currentValue()

  def __mod__(self, other):
    return self.currentValue() % other

  def __rmod__(self, other):
    return other % self.currentValue()

  def __add__(self, other):
    return self.currentValue() + other

  def __radd__(self, other):
    return other + self.currentValue()

  def __sub__(self, other):
    return self.currentValue() - other

  def __rsub__(self, other):
    return other - self.currentValue()

  def __lt__(self, other):
    return self.currentValue() < other

  def __eq__(self, other):
    return self.currentValue() == other

  def currentValue(self):
    raise NotImplementedError


class Sensor(Base):
  identity = Column(String)
  name = Column(String)

  __mapper_args__ = {
      'polymorphic_on': 'identity'
  }

  def currentValue(self):
    raise NotImplementedError

class Clock(Sensor):
  __tablename__ = None

__mapper_args__ = {
  'polymorphic_identity': 'clock'
}

reference = Column(Float)

def currentValue(self):
  return time() - self.reference


@dataclass
class Animation(MathProxyMixin):
  keyframes: List[Keyframe]
  repeat = Column(Float)

  @declared_attr
  def sensor_id(self):
    return Column(Integer, ForeignKey('sensor.id'))

  @declared_attr
  def sensor(self):
    return relationship(Sensor, cascade='all, delete-orphan', single_parent=True)

  def currentValue(self):
    pos = self.sensor.currentValue()
    length = self.keyframes[-1].position - self.keyframes[0].position

    return blend(self.keyframes, pos % length if pos <= self.repeat * length else length)


class Dimension(Base):
  identity = Column(String)

  __mapper_args__ = {
      'polymorphic_on': 'identity'
  }


class StaticDimension(Dimension, MathProxyMixin):
  __tablename__ = None

  value = Column(Float)

  def currentValue(self):
    return self.value

  __mapper_args__ = {
      'polymorphic_identity': 'static'
  }


class DimensionAnimation(Animation, Dimension):
  __tablename__ = None

  keyframes = relationship(DimensionKeyframe, cascade='all, delete-orphan', order_by=DimensionKeyframe.position)

  __mapper_args__ = {
    'polymorphic_identity': 'animation'
  }


class Image(Base):
  identity = Column(String)

  __mapper_args__ = {
    'polymorphic_on': 'identity'
  }

  def getColorAtPosition(self, pos: float) -> Color:
    raise NotImplementedError



class Color(Image):
  __tablename__ = None

  __mapper_args__ = {
      'polymorphic_identity': 'color'
  }

  # Colours should be in the premultiplied space
  # e.g. the RGBWA values for pure red at 50% opacity
  # are (127.5, 0, 0, 0, 0.5), not (255, 0, 0, 0, 0.5)
  red = Column(Float)
  green = Column(Float)
  blue = Column(Float)
  white = Column(Float)
  opacity = Column(Float)

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    if self.white is None:
      self.white = 0.0
    if self.opacity is None:
      self.opacity = 1.0

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

  def __rmul__(self, other):
    return self.__mul__(other)

  def __radd__(self, other):
    return self.__add__(other)

  # Implement image rendering
  def getColorAtPosition(self, pos: float) -> Color:
    return self

  # Returns a new instance of transparent black
  @classmethod
  def transparent(cls):
    return cls(red=0.0, green=0.0, blue=0.0, white=0.0, opacity=0.0)


class ColorKeyframe(Keyframe, Base):
  animation_id = Column(Integer, ForeignKey('image.id'))
  color_id = Column(Integer, ForeignKey('image.id'))
  value = relationship(Color, foreign_keys=color_id, cascade='all, delete-orphan', single_parent=True)
  position = Column(Float)


class ColorAnimation(Animation, Image):
  __tablename__ = None

  __mapper_args__ = {
      'polymorphic_identity': 'coloranimation'
  }

  keyframes = relationship(ColorKeyframe, foreign_keys=ColorKeyframe.animation_id, cascade='all, delete-orphan', order_by=ColorKeyframe.position)

  # Implement image rendering
  def getColorAtPosition(self, pos: float) -> Color:
    return self.currentValue()


class ColorStop(Keyframe, Base):
  gradient_id = Column(Integer, ForeignKey('image.id'))
  color_id = Column(Integer, ForeignKey('image.id'))
  value = relationship(Color, foreign_keys=color_id, cascade='all, delete-orphan', single_parent=True)
  position = Column(Float)


class Gradient(Image):
  __tablename__ = None

  __mapper_args__ = {
      'polymorphic_identity': 'gradient'
  }

  colorstops = relationship(ColorStop, foreign_keys=ColorStop.gradient_id, cascade='all, delete-orphan', order_by=ColorStop.position)

  def getColorAtPosition(self, pos: float):
    return blend(self.colorstops, pos)


class Layer(Base):
  scene_id = Column(Integer, ForeignKey('scene.id'))
  image_id = Column(Integer, ForeignKey('image.id'))
  image = relationship(Image, cascade='all, delete-orphan', single_parent=True)
  size_id = Column(Integer, ForeignKey('dimension.id'))
  size = relationship(Dimension, foreign_keys=size_id,
                      cascade='all, delete-orphan', single_parent=True)
  left_id = Column(Integer, ForeignKey('dimension.id'))
  left = relationship(Dimension, foreign_keys=left_id,
                      cascade='all, delete-orphan', single_parent=True)
  repeat = Column(Float)

  def getColorAtPosition(self, pos: float) -> Color:
    if (pos - self.left) / self.size <= self.repeat:
      return self.image.getColorAtPosition(((pos - self.left) % self.size) / self.size)
    else:
      return Color.transparent()


class Scene(Base):
  name = Column(String)
  layers = relationship(Layer, cascade='all, delete-orphan')

  def getColorAtPosition(self, pos: float) -> Color:
    # Start with an opaque black background
    result = Color(red=0.0, green=0.0, blue=0.0)
    # Blend colours layer by layer
    for layer in self.layers:
      color = layer.getColorAtPosition(pos)
      result = result * (1.0 - color.opacity) + color
    return result


class Device(Base):
  led_count = Column(Integer)
  gpio_pin = Column(Integer)
  led_strip = Column(Integer)
  name = Column(String)
  scene_id = Column(Integer, ForeignKey('scene.id'))
  scene = relationship(Scene, cascade='all, delete-orphan', single_parent=True)

