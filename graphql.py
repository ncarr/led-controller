from graphene import relay, Mutation, ObjectType, Schema, String, Float, Field, InputObjectType, ID
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .database import session, Device as DeviceModel, Scene as SceneModel, Animation as AnimationModel, Layer as LayerModel, Image as ImageModel
from graphql_relay.node.node import from_global_id

def input_to_dictionary(user_input):
  dictionary = {}
  for key in user_input:
    if key.endswith('id'):
      dictionary[key] = from_global_id(user_input[key])[1]
    else:
      dictionary[key] = user_input[key]
  return dictionary

def create_mutation(name, properties, output_type, orm_model):
  class CreateInput(InputObjectType, properties):
    pass

  class CreateMutation(Mutation):
    class Meta:
      name = 'Create' + output_type.__name__
    class Arguments:
      pass

    @staticmethod
    def mutate(root, info, **kwargs):
      value = kwargs[name]
      orm_object = orm_model(**value)
      session.add(orm_object)
      session.commit()
      return CreateMutation(**{name: orm_object})
  setattr(CreateMutation.Arguments, name, CreateInput(required=True))
  setattr(CreateMutation, name, Field(lambda: output_type))
  return CreateMutation


def update_mutation(name, properties, output_type, orm_model):
  class UpdateInput(InputObjectType, properties):
    id = ID(required=True)
  
  class UpdateMutation(Mutation):
    class Meta:
      name = 'Update' + output_type.__name__
    class Arguments:
      pass

    @staticmethod
    def mutate(root, info, **kwargs):
      value = kwargs[name]
      orm_object = session.query(orm_model).filter(
          orm_model.id == value.id).one()
      for key in value:
        setattr(orm_object, key, value[key])
      session.commit()
      return UpdateMutation(**{name: orm_object})
  setattr(UpdateMutation.Arguments, name, UpdateInput(required=True))
  setattr(UpdateMutation, name, Field(lambda: output_type))
  return UpdateMutation


def delete_mutation(name, output_type, orm_model):
  class DeleteMutation(Mutation):
    class Meta:
      name = 'Delete' + output_type.__name__
    class Arguments:
      id = ID(required=True)

    @staticmethod
    def mutate(root, info, id):
      orm_object = session.query(orm_model).filter(
        orm_model.id == id).one()
      session.delete(orm_object)
      session.commit()
      return DeleteMutation(**{name: orm_object})
  setattr(DeleteMutation, name, Field(lambda: output_type))
  return DeleteMutation

class DeviceProperties:
    name = String()
    led_count = String()
    gpio_pin = String()
    led_strip = String()


class Device(SQLAlchemyObjectType):
  class Meta:
    model = DeviceModel
    interfaces = (relay.Node, )


class DeviceConnection(relay.Connection):
  class Meta:
    node = Device


CreateDevice = create_mutation(
    name='device', properties=DeviceProperties, output_type=Device, orm_model=DeviceModel)


UpdateDevice = create_mutation(
    name='device', properties=DeviceProperties, output_type=Device, orm_model=DeviceModel)


DeleteDevice = create_mutation(
    name='device', output_type=Device, orm_model=DeviceModel)


class SetScene(Mutation):
  class Arguments:
    device_id = ID(required=True)
    scene_id = ID(required=True)

  device = Field(lambda: Device)

  @staticmethod
  def mutate(root, info, device_id, scene_id):
    device_object = session.query(DeviceModel).filter(
        DeviceModel.id == id).one()
    device_object.scene_id = scene_id
    session.commit()
    return SetScene(device=device_object)


class SceneProperties:
    name = String()


class Scene(SQLAlchemyObjectType):
  class Meta:
    model = SceneModel
    interfaces = (relay.Node, )


CreateScene = create_mutation(
    name='scene', properties=SceneProperties, output_type=Scene, orm_model=SceneModel)


UpdateScene = update_mutation(
    name='scene', properties=SceneProperties, output_type=Scene, orm_model=SceneModel)


DeleteScene = delete_mutation(
    name='scene', output_type=Scene, orm_model=SceneModel)


class Image(SQLAlchemyObjectType):
  class Meta:
    model = ImageModel
    interfaces = (relay.Node, )


class LayerProperties:
    image = Field(lambda: Image)
    left = Float()
    size = Float()
    repeat = Float()


class Layer(SQLAlchemyObjectType):
  class Meta:
    model = SceneModel
    interfaces = (relay.Node, )


CreateLayer = create_mutation(
    name='layer', properties=LayerProperties, output_type=Layer, orm_model=LayerModel)


UpdateLayer = update_mutation(
    name='layer', properties=LayerProperties, output_type=Layer, orm_model=LayerModel)


DeleteLayer = delete_mutation(
    name='layer', output_type=Layer, orm_model=LayerModel)


class Query(ObjectType):
  node = relay.Node.Field()
  devices = SQLAlchemyConnectionField(DeviceConnection)

schema = Schema(query=Query)
