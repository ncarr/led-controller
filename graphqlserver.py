from copy import deepcopy
from graphene import Mutation, ObjectType, Schema, String, Float, Argument, Field, ID, Union, List, Enum
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from controller import Device as DeviceModel, Scene as SceneModel, Animation as AnimationModel, Layer as LayerModel, Color as ColorModel, ColorAnimation as ColorAnimationModel, Gradient as GradientModel, ColorStop as ColorStopModel, ColorKeyframe as ColorKeyframeModel, DimensionAnimation as DimensionAnimationModel, StaticDimension as StaticDimensionModel, Clock as ClockModel, DimensionKeyframe as DimensionKeyframeModel
from graphqlutils import SQLAlchemyInputObjectType, AnimationType, DimensionType

class Device(SQLAlchemyObjectType):
  class Meta:
    model = DeviceModel
    exclude_fields = ('scene_id',)

class DeviceInput(SQLAlchemyInputObjectType):
  class Meta:
    model = DeviceModel
    exclude_fields = ('scene_id', 'scene')

class CreateDevice(Mutation):
  class Arguments:
    fields = Argument(DeviceInput)
  result = Field(Device)
  mutate = lambda root, info, fields: CreateDevice(result=DeviceModel.create(root, info, fields))

class UpdateDevice(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(DeviceInput)
  result = Field(Device)
  mutate = lambda root, info, id, fields: UpdateDevice(result=DeviceModel.update(root, info, id, fields))

class DeleteDevice(Mutation):
  class Arguments:
    id = ID(required=True)
  result = Field(Device)
  mutate = lambda root, info, id: DeleteDevice(result=DeviceModel.delete(root, info, id))


class SetScene(Mutation):
  class Arguments:
    device_id = ID(required=True)
    scene_id = ID()

  device = Field(lambda: Device)

  @staticmethod
  def mutate(root, info, device_id, scene_id=None):
    device_object = info.context['session'].query(DeviceModel).filter(DeviceModel.id == device_id).one()
    if scene_id:
      device_object.scene = info.context['session'].query(SceneModel).filter(SceneModel.id == scene_id).one()
    else:
      device_object.scene = None
    info.context['session'].commit()
    return SetScene(device=device_object)

class Scene(SQLAlchemyObjectType):
  class Meta:
    model = SceneModel

class SceneInput(SQLAlchemyInputObjectType):
  class Meta:
    model = SceneModel
    exclude_fields = ('layers',)

class CreateScene(Mutation):
  class Arguments:
    fields = Argument(SceneInput)
  result = Field(Scene)
  mutate = lambda root, info, fields: CreateScene(
      result=SceneModel.create(root, info, fields))

class UpdateScene(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(SceneInput)
  result = Field(Scene)
  mutate = lambda root, info, id, fields: UpdateScene(
      result=SceneModel.update(root, info, id, fields))

class DeleteScene(Mutation):
  class Arguments:
    id = ID(required=True)
  result = Field(Scene)
  mutate = lambda root, info, id: DeleteScene(
      result=SceneModel.delete(root, info, id))


class Clock(SQLAlchemyObjectType):
  class Meta:
    model = ClockModel
    exclude_fields = ('identity',)

class ClockInput(SQLAlchemyInputObjectType):
  class Meta:
    model = ClockModel
    exclude_fields = ('identity',)

class CreateClock(Mutation):
  class Arguments:
    animation_id = ID(required=True)
    animation_type = Argument(AnimationType)
    fields = Argument(ClockInput)
  result = Field(Clock)
  mutate = lambda root, info, animation_id, animation_type, fields: CreateClock(
      result=ClockModel.create(root, info, animation_id, animation_type, fields))

class UpdateClock(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(ClockInput)
  result = Field(Clock)
  mutate = lambda root, info, id, fields: UpdateClock(
      result=ClockModel.update(root, info, id, fields))


class Sensor(Union):
  class Meta:
    types = (Clock,)

class DimensionAnimation(SQLAlchemyObjectType):
  class Meta:
    model = DimensionAnimationModel
    exclude_fields = ('identity', 'sensor_id')

class DimensionAnimationInput(SQLAlchemyInputObjectType):
  class Meta:
    model = DimensionAnimationModel
    exclude_fields = ('identity', 'sensor_id', 'sensor', 'keyframes')

class CreateDimensionAnimation(Mutation):
  class Arguments:
    layer_id = ID(required=True)
    dimension_type = Argument(DimensionType)
    fields = Argument(DimensionAnimationInput)
  result = Field(lambda: Layer)
  mutate = lambda root, info, layer_id, dimension_type, fields: CreateDimensionAnimation(
      result=DimensionAnimationModel.create(root, info, layer_id, dimension_type, fields))

class UpdateDimensionAnimation(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(DimensionAnimationInput)
  result = Field(DimensionAnimation)
  mutate = lambda root, info, id, fields: UpdateDimensionAnimation(
      result=DimensionAnimationModel.update(root, info, id, fields))

class DimensionKeyframe(SQLAlchemyObjectType):
  class Meta:
    model = DimensionKeyframeModel
    exclude_fields = ('animation_id',)

class DimensionKeyframeInput(SQLAlchemyInputObjectType):
  class Meta:
    model = DimensionKeyframeModel
    exclude_fields = ('animation_id',)
  
class CreateDimensionKeyframe(Mutation):
  class Arguments:
    animation_id = ID(required=True)
    fields = Argument(DimensionKeyframeInput)
  result = Field(DimensionKeyframe)
  mutate = lambda root, info, animation_id, fields: CreateDimensionKeyframe(
      result=DimensionKeyframeModel.create(root, info, animation_id, fields))

class UpdateDimensionKeyframe(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(DimensionKeyframeInput)
  result = Field(DimensionKeyframe)
  mutate = lambda root, info, id, fields: UpdateDimensionKeyframe(
      result=DimensionKeyframeModel.update(root, info, id, fields))

class DeleteDimensionKeyframe(Mutation):
  class Arguments:
    id = ID(required=True)
  result = Field(DimensionKeyframe)
  mutate = lambda root, info, id: DeleteDimensionKeyframe(
      result=DimensionKeyframeModel.delete(root, info, id))

class StaticDimension(SQLAlchemyObjectType):
  class Meta:
    model = StaticDimensionModel
    exclude_fields = ('identity',)

class StaticDimensionInput(SQLAlchemyInputObjectType):
  class Meta:
    model = StaticDimensionModel
    exclude_fields = ('identity',)

class CreateStaticDimension(Mutation):
  class Arguments:
    layer_id = ID(required=True)
    dimension_type = Argument(DimensionType)
    fields = Argument(StaticDimensionInput)
  result = Field(lambda: Layer)
  mutate = lambda root, info, layer_id, dimension_type, fields: CreateStaticDimension(
      result=StaticDimensionModel.create(root, info, layer_id, dimension_type, fields))

class UpdateStaticDimension(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(StaticDimensionInput)
  result = Field(StaticDimension)
  mutate = lambda root, info, id, fields: UpdateStaticDimension(
      result=StaticDimensionModel.update(root, info, id, fields))

class Dimension(Union):
  class Meta:
    types = (DimensionAnimation, StaticDimension)


class Color(SQLAlchemyObjectType):
  class Meta:
    model = ColorModel
    exclude_fields = ('identity',)

class ColorInput(SQLAlchemyInputObjectType):
  class Meta:
    model = ColorModel
    exclude_fields = ('identity',)

class CreateColor(Mutation):
  class Arguments:
    layer_id = ID(required=True)
    fields = Argument(ColorInput)
  result = Field(lambda: Layer)
  mutate = lambda root, info, layer_id, fields: CreateColor(
      result=ColorModel.create(root, info, layer_id, fields))

class UpdateColor(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(ColorInput)
  result = Field(Color)
  mutate = lambda root, info, id, fields: UpdateColor(
      result=ColorModel.update(root, info, id, fields))

class ColorAnimation(SQLAlchemyObjectType):
  class Meta:
    model = ColorAnimationModel
    exclude_fields = ('identity', 'sensor_id')
  sensor = Field(Sensor)

class ColorAnimationInput(SQLAlchemyInputObjectType):
  class Meta:
    model = ColorAnimationModel
    exclude_fields = ('identity', 'sensor_id', 'keyframes', 'sensor')

class CreateColorAnimation(Mutation):
  class Arguments:
    layer_id = ID(required=True)
    fields = Argument(ColorAnimationInput)
  result = Field(lambda: Layer)
  mutate = lambda root, info, layer_id, fields: CreateColorAnimation(
      result=ColorAnimationModel.create(root, info, layer_id, fields))

class UpdateColorAnimation(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(ColorAnimationInput)
  result = Field(ColorAnimation)
  mutate = lambda root, info, id, fields: UpdateColorAnimation(
      result=ColorAnimationModel.update(root, info, id, fields))

class ColorKeyframe(SQLAlchemyObjectType):
  class Meta:
    model = ColorKeyframeModel
    exclude_fields = ('animation_id', 'color_id')

class ColorKeyframeInput(SQLAlchemyInputObjectType):
  class Meta:
    model = ColorKeyframeModel
    exclude_fields = ('animation_id', 'color_id')
  
class CreateColorKeyframe(Mutation):
  class Arguments:
    animation_id = ID(required=True)
    fields = Argument(ColorKeyframeInput)
  result = Field(ColorKeyframe)
  mutate = lambda root, info, animation_id, fields: CreateColorKeyframe(
      result=ColorKeyframeModel.create(root, info, animation_id, fields))

class UpdateColorKeyframe(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(ColorKeyframeInput)
  result = Field(ColorKeyframe)
  mutate = lambda root, info, id, fields: UpdateColorKeyframe(
      result=ColorKeyframeModel.update(root, info, id, fields))

class DeleteColorKeyframe(Mutation):
  class Arguments:
    id = ID(required=True)
  result = Field(ColorKeyframe)
  mutate = lambda root, info, id: DeleteColorKeyframe(
      result=ColorKeyframeModel.delete(root, info, id))

class Gradient(SQLAlchemyObjectType):
  class Meta:
    model = GradientModel
    exclude_fields = ('identity',)

class CreateGradient(Mutation):
  class Arguments:
    layer_id = ID(required=True)
  result = Field(lambda: Layer)
  mutate = lambda root, info, layer_id, fields: CreateGradient(
      result=GradientModel.create(root, info, layer_id))


class ColorStop(SQLAlchemyObjectType):
  class Meta:
    model = ColorStopModel
    exclude_fields = ('gradient_id', 'color_id')

class ColorStopInput(SQLAlchemyInputObjectType):
  class Meta:
    model = ColorStopModel
    exclude_fields = ('gradient_id', 'color_id')
  
class CreateColorStop(Mutation):
  class Arguments:
    gradient_id = ID(required=True)
    fields = Argument(ColorStopInput)
  result = Field(ColorStop)
  mutate = lambda root, info, gradient_id, fields: CreateColorStop(
      result=ColorStopModel.create(root, info, gradient_id, fields))

class UpdateColorStop(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(ColorStopInput)
  result = Field(ColorStop)
  mutate = lambda root, info, id, fields: UpdateColorStop(
      result=ColorStopModel.update(root, info, id, fields))

class DeleteColorStop(Mutation):
  class Arguments:
    id = ID(required=True)
  result = Field(ColorStop)
  mutate = lambda root, info, id: DeleteColorStop(
      result=ColorStopModel.delete(root, info, id))


class Image(Union):
  class Meta:
    types = (Color, ColorAnimation, Gradient)


class Layer(SQLAlchemyObjectType):
  class Meta:
    model = LayerModel
    exclude_fields = ('scene_id', 'image_id', 'size_id', 'left_id')
  image = Field(Image)
  size = Field(Dimension)
  left = Field(Dimension)

class LayerInput(SQLAlchemyInputObjectType):
  class Meta:
    model = LayerModel
    exclude_fields = ('scene_id', 'image_id', 'size_id', 'left_id')

class CreateLayer(Mutation):
  class Arguments:
    scene_id = ID(required=True)
    fields = Argument(LayerInput)
  result = Field(Layer)
  mutate = lambda root, info, scene_id, fields: CreateLayer(
      result=LayerModel.create(root, info, scene_id, fields))

class UpdateLayer(Mutation):
  class Arguments:
    id = ID(required=True)
    fields = Argument(LayerInput)
  result = Field(Layer)
  mutate = lambda root, info, id, fields: UpdateLayer(
      result=LayerModel.update(root, info, id, fields))

class DeleteLayer(Mutation):
  class Arguments:
    id = ID(required=True)
  result = Field(Layer)
  mutate = lambda root, info, id: DeleteLayer(
      result=LayerModel.delete(root, info, id))


class RootQuery(ObjectType):
  devices = List(Device)
  device = Field(Device, id=ID(required=True))
  scenes = List(Scene)
  scene = Field(Scene, id=ID(required=True))

  def resolve_devices(self, info):
    query = Device.get_query(info)
    return query.all()

  def resolve_device(self, info, id):
    query = Device.get_query(info)
    return query.filter(DeviceModel.id == id).one_or_none()

  def resolve_scenes(self, info):
    query = Scene.get_query(info)
    return query.all()

  def resolve_scene(self, info, id):
    query = Scene.get_query(info)
    return query.filter(SceneModel.id == id).one_or_none()


class RootMutation(ObjectType):
  createDevice = CreateDevice.Field()
  updateDevice = UpdateDevice.Field()
  deleteDevice = DeleteDevice.Field()
  setScene = SetScene.Field()
  createScene = CreateScene.Field()
  updateScene = UpdateScene.Field()
  deleteScene = DeleteScene.Field()
  createClock = CreateClock.Field()
  updateClock = UpdateClock.Field()
  createDimensionAnimation = CreateDimensionAnimation.Field()
  updateDimensionAnimation = UpdateDimensionAnimation.Field()
  createDimensionKeyframe = CreateDimensionKeyframe.Field()
  updateDimensionKeyframe = UpdateDimensionKeyframe.Field()
  deleteDimensionKeyframe = DeleteDimensionKeyframe.Field()
  createStaticDimension = CreateStaticDimension.Field()
  updateStaticDimension = UpdateStaticDimension.Field()
  createColor = CreateColor.Field()
  updateColor = UpdateColor.Field()
  createColorAnimation = CreateColorAnimation.Field()
  updateColorAnimation = UpdateColorAnimation.Field()
  createColorKeyframe = CreateColorKeyframe.Field()
  updateColorKeyframe = UpdateColorKeyframe.Field()
  deleteColorKeyframe = DeleteColorKeyframe.Field()
  createGradient = CreateGradient.Field()
  createColorStop = CreateColorStop.Field()
  updateColorStop = UpdateColorStop.Field()
  deleteColorStop = DeleteColorStop.Field()
  createLayer = CreateLayer.Field()
  updateLayer = UpdateLayer.Field()
  deleteLayer = DeleteLayer.Field()


schema = Schema(query=RootQuery, mutation=RootMutation)
