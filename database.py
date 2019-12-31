from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, MetaData, Table
from sqlalchemy.orm import relationship, mapper
from controller import Scene, Animation, Keyframe, Image, AnimatedColor, Color, Gradient, Layer, ColorStop

engine = create_engine('sqlite:///:memory:')

metadata = MetaData()

# Since we already have data classes defined, we use classical mapping

scene = Table('scene', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String)
              )
mapper(Scene, scene, properties={
    'layers': relationship(Layer)
})

device = Table('device', metadata,
               Column('id', Integer, primary_key=True),
               Column('led_count', Integer),
               Column('gpio_pin', Integer),
               Column('led_strip', Integer),
               Column('name', String),
               Column('scene_id', Integer, ForeignKey('scene.id'))
               )


class Device:
    pass


mapper(Device, device, properties={
    'scene': relationship(Scene)
})

animation = Table('animation', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('repeat', Float)
                  )
mapper(Animation, animation, properties={
    'keyframes': relationship(Keyframe)
})

keyframe = Table('keyframe', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('animation_id', Integer, ForeignKey('animation.id')),
                 Column('value', Float),
                 Column('time', Float)
                 )
mapper(Keyframe, keyframe)

# Images use single table inheritance

image = Table('image', metadata,
              # Common
              Column('id', Integer, primary_key=True),
              Column('type', String),
              # Animated colour
              Column('repeat', Float),
              # Colour
              Column('red', Float),
              Column('green', Float),
              Column('blue', Float),
              Column('white', Float),
              Column('opacity', Float)
              # Gradient has no columns
              )
mapper(Image, image,
       polymorphic_on=image.c.type,
       polymorphic_identity='image'
       )

colorkeyframe = Table('colorkeyframe', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('animation_id', Integer,
                             ForeignKey('animated_color.id')),
                      Column('color_id', Integer, ForeignKey('color.id')),
                      Column('time', Float)
                      )


class ColorKeyframe(Keyframe):
    pass


mapper(ColorKeyframe, colorkeyframe,
       properties={
           'value': relationship(Color)
       }
       )

mapper(Color,
       inherits=Image,
       polymorphic_identity='color',
       include_properties=['id', 'type', 'red',
                           'green', 'blue', 'white', 'opacity']
       )

mapper(AnimatedColor,
       inherits=Color,
       polymorphic_identity='animated_color',
       include_properties=['id', 'type', 'repeat'],
       properties={
           'keyframes': relationship(ColorKeyframe)
       }
       )

mapper(Gradient,
       inherits=Image,
       polymorphic_identity='gradient',
       include_properties=['id', 'type'],
       properties={
           'colorstops': relationship(ColorStop)
       }
       )

colorstop = Table('colorstop', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('gradient_id', Integer, ForeignKey('gradient.id')),
                  Column('color_id', Integer, ForeignKey('color.id')),
                  Column('location', Float)
                  )
mapper(ColorStop, colorstop,
       properties={
           'color': relationship(Color)
       }
       )

layer = Table('layer', metadata,
              Column('id', Integer, primary_key=True),
              Column('size_id', Integer, ForeignKey('animation.id')),
              Column('left_id', Integer, ForeignKey('animation.id')),
              Column('repeat', Float),
              Column('image_id', Integer, ForeignKey('image.id'))
              )
mapper(Layer, layer,
       properties={
           'size': relationship(Animation, foreign_keys=[layer.c.size_id]),
           'left': relationship(Animation, foreign_keys=[layer.c.left_id]),
           'image': relationship(Image)
       }
       )
