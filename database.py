from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, MetaData, Table
from sqlalchemy.orm import relationship, mapper
from controller import Scene, Animation, Keyframe, Image, AnimatedColor, Color, Gradient

engine = create_engine('sqlite:///:memory:')

metadata = MetaData(bind=engine)

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
  'keyframes': relationship()
})

keyframe = Table('keyframe', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('animation_id', Integer, ForeignKey('animation.id')),
                 Column('value', Float),
                 Column('time', Float)
                 )
mapper(Keyframe, keyframe)

image = Table('image', metadata,
              Column('id', Integer, primary_key=True)
              )
mapper(Image, image)

animatedcolor = Table('animatedcolor', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('repeat', Float)
                      )
mapper(AnimatedColor, animatedcolor)

color = Table('color', metadata,
              Column('id', Integer, primary_key=True),
              Column('red', Float),
              Column('green', Float),
              Column('blue', Float),
              Column('white', Float),
              Column('opacity', Float)
              )
mapper(Color, color)

colorkeyframe = Table('colorkeyframe', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('color_id', Integer, ForeignKey('color.id')),
                      Column('time', Float)
                      )


class ColorKeyframe(Keyframe):
    pass


mapper(ColorKeyframe, colorkeyframe)

gradient = Table('gradient', metadata,
                 Column('id', Integer, primary_key=True)
                 )
mapper(Gradient, gradient)

colorstop = Table('colorstop', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('color_id', Integer, ForeignKey('color.id')),
                  Column('location', Float)
                  )

layer = Table('layer', metadata,
              Column('id', Integer, primary_key=True),
              Column('size_id', Integer, ForeignKey('animation.id')),
              Column('left_id', Integer, ForeignKey('animation.id')),
              Column('repeat', Float),
              Column('image_id', Integer, ForeignKey('image.id'))
              )
