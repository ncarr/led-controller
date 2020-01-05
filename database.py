from typing import get_type_hints, get_origin, get_args
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, MetaData, Table
from sqlalchemy.orm import relationship, mapper, sessionmaker
from controller import Scene, Animation, Keyframe, Image, AnimatedColor, Color, Gradient, Layer, ColorStop

engine = create_engine('sqlite:///:memory:')

metadata = MetaData()

Session = sessionmaker(bind=engine)

session = Session()

BLANK = object


def add_columns(cls, *columns):
    if not 'additional_columns' in cls._mapper_opts:
        cls._mapper_opts['additional_columns'] = []
    for column in columns:
        for existing_column in cls._mapper_opts['additional_columns']:
            if existing_column.key == column.key:
                break
        else:
            cls._mapper_opts['additional_columns'].add(column)

def recursive_mapper(cls, premapped_classes=set()):
    if cls in premapped_classes:
        return
    if not hasattr(cls, '_mapper_opts'):
        cls._mapper_opts = {}
    if 'exclude' in cls._mapper_opts and cls._mapper_opts['exclude'] == True:
        return
    premapped_classes.add(cls)
    attrs = get_type_hints(cls).items()
    for name, value in attrs:
        if value is not int and value is not float:
            if get_origin(value) is list:
                child, *_ = get_args(value)
                add_columns(child, Column(cls.__name__.lower() + '_id',
                                          Integer, ForeignKey(cls.__name__.lower() + '.id')))
                recursive_mapper(child, premapped_classes)
            else:
                add_columns(cls, Column(name + '_id', Integer,
                                        ForeignKey(value.name.lower() + '.id')))
                recursive_mapper(value, premapped_classes)
    for subclass in cls.__subclasses__():
        recursive_mapper(subclass, premapped_classes)
    return premapped_classes
        
def calculate_inheritance(mapped_classes):
    for cls in mapped_classes:
        if 'inherits' not in cls._mapper_opts:
            for parent in cls.__mro__[1:-1]:
                if parent in mapped_classes:
                    cls._mapper_opts['inherits'] = parent
                    for superclass in parent.__mro__[1:-1]:
                        if superclass in mapped_classes:
                            break
                    else:
                        parent._mapper_opts['istoplevel'] = True
                    break


def auto_mapper(mapped_classes):
    for cls in mapped_classes:
        columns = [Column('id', Integer, primary_key=True), *cls._mapper_opts['additional_columns']]
        properties = {}
        attrs = get_type_hints(cls).items()
        for name, value in attrs:
            if value is int:
                columns.append(Column(name, Integer))
            elif value is float:
                columns.append(Column(name, Float))
            elif get_origin(value) is list:
                child, *_ = get_args(value)
                properties[key] = relationship(child)
            else:
                properties[key] = relationship(value)
        table = Table(cls.__name__.lower(), metadata, *columns)
        mapper(cls, table, properties=properties, inherits=cls._mapper_opts.get('inherits', None), **cls._mapper_opts.get('raw', {}))




# Since we already have data classes defined, we use classical mapping

scene = Table('scene', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String),
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
                      Column('color_id', Integer, ForeignKey('image.id')),
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
                  Column('color_id', Integer, ForeignKey('image.id')),
                  Column('location', Float)
                  )
mapper(ColorStop, colorstop,
       properties={
           'color': relationship(Color)
       }
       )

layer = Table('layer', metadata,
              Column('id', Integer, primary_key=True),
              Column('scene_id', Integer, ForeignKey('scene.id')),
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
