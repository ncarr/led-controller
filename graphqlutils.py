from graphene import InputObjectType, Field, Enum
from graphql_relay.node.node import from_global_id
from graphene.relay import Connection, Node
from graphene.types.inputobjecttype import InputObjectTypeOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene_sqlalchemy.types import construct_fields
from graphene_sqlalchemy.enums import enum_for_field, sort_argument_for_object_type, sort_enum_for_object_type
from graphene_sqlalchemy.registry import Registry
from graphene_sqlalchemy.utils import is_mapped_class, is_mapped_instance, get_query
from sqlalchemy.orm.exc import NoResultFound

def input_to_dictionary(user_input):
  dictionary = {}
  for key in user_input:
    if key.endswith('id'):
      dictionary[key] = from_global_id(user_input[key])[1]
    else:
      dictionary[key] = user_input[key]
  return dictionary


class SQLAlchemyInputObjectTypeOptions(InputObjectTypeOptions):
    model = None
    registry = None
    connection = None
    id = None


class SQLAlchemyInputObjectType(InputObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model=None,
        registry=None,
        skip_registry=False,
        only_fields=(),
        exclude_fields=(),
        connection=None,
        connection_class=None,
        use_connection=None,
        interfaces=(),
        id=None,
        batching=False,
        connection_field_factory=None,
        _meta=None,
        **options
    ):
        assert is_mapped_class(model), (
            "You need to pass a valid SQLAlchemy Model in " '{}.Meta, received "{}".'
        ).format(cls.__name__, model)

        if not registry:
            registry = get_global_registry()

        assert isinstance(registry, InputRegistry), (
            "The attribute registry in {} needs to be an instance of "
            'InputRegistry, received "{}".'
        ).format(cls.__name__, registry)

        if only_fields and exclude_fields:
            raise ValueError(
                "The options 'only_fields' and 'exclude_fields' cannot be both set on the same type.")

        sqla_fields = yank_fields_from_attrs(
            construct_fields(
                obj_type=cls,
                model=model,
                registry=registry,
                only_fields=only_fields,
                exclude_fields=exclude_fields+('id',),
                batching=batching,
                connection_field_factory=connection_field_factory,
            ),
            _as=Field,
            sort=False,
        )

        if use_connection is None and interfaces:
            use_connection = any(
                (issubclass(interface, Node) for interface in interfaces)
            )

        if use_connection and not connection:
            # We create the connection automatically
            if not connection_class:
                connection_class = Connection

            connection = connection_class.create_type(
                "{}Connection".format(cls.__name__), node=cls
            )

        if connection is not None:
            assert issubclass(connection, Connection), (
                "The connection must be a Connection. Received {}"
            ).format(connection.__name__)

        if not _meta:
            _meta = SQLAlchemyInputObjectTypeOptions(cls)

        _meta.model = model
        _meta.registry = registry

        if _meta.fields:
            _meta.fields.update(sqla_fields)
        else:
            _meta.fields = sqla_fields

        _meta.connection = connection
        _meta.id = id or "id"

        super(SQLAlchemyInputObjectType, cls).__init_subclass_with_meta__(
            _meta=_meta, interfaces=interfaces, **options
        )

        if not skip_registry:
            registry.register(cls)

    @classmethod
    def is_type_of(cls, root, info):
        if isinstance(root, cls):
            return True
        if not is_mapped_instance(root):
            raise Exception(
                ('Received incompatible instance "{}".').format(root))
        return isinstance(root, cls._meta.model)

    @classmethod
    def get_query(cls, info):
        model = cls._meta.model
        return get_query(model, info.context)

    @classmethod
    def get_node(cls, info, id):
        try:
            return cls.get_query(info).get(id)
        except NoResultFound:
            return None

    def resolve_id(self, info):
        # graphene_type = info.parent_type.graphene_type
        keys = self.__mapper__.primary_key_from_instance(self)
        return tuple(keys) if len(keys) > 1 else keys[0]

    @classmethod
    def enum_for_field(cls, field_name):
        return enum_for_field(cls, field_name)

    sort_enum = classmethod(sort_enum_for_object_type)

    sort_argument = classmethod(sort_argument_for_object_type)


class InputRegistry(Registry):
  def register(self, obj_type):
    if not isinstance(obj_type, type) or not issubclass(
        obj_type, SQLAlchemyInputObjectType
    ):
        raise TypeError(
            "Expected SQLAlchemyInputObjectType, but got: {!r}".format(
                obj_type)
        )
    assert obj_type._meta.registry == self, "Registry for a Model have to match."
    self._registry[obj_type._meta.model] = obj_type

  def register_orm_field(self, obj_type, field_name, orm_field):
      if not isinstance(obj_type, type) or not issubclass(
          obj_type, SQLAlchemyInputObjectType
      ):
          raise TypeError(
              "Expected SQLAlchemyInputObjectType, but got: {!r}".format(
                  obj_type)
          )
      if not field_name or not isinstance(field_name, str):
          raise TypeError(
              "Expected a field name, but got: {!r}".format(field_name))
      self._registry_orm_fields[obj_type][field_name] = orm_field

  def register_sort_enum(self, obj_type, sort_enum):
      if not isinstance(obj_type, type) or not issubclass(
          obj_type, SQLAlchemyInputObjectType
      ):
          raise TypeError(
              "Expected SQLAlchemyInputObjectType, but got: {!r}".format(
                  obj_type)
          )
      if not isinstance(sort_enum, type(Enum)):
          raise TypeError(
              "Expected Graphene Enum, but got: {!r}".format(sort_enum))
      self._registry_sort_enums[obj_type] = sort_enum


input_registry = None


def get_global_registry():
    global input_registry
    if not input_registry:
        input_registry = InputRegistry()
    return input_registry


class AnimationType(Enum):
  DIMENSION = "DimensionAnimation"
  COLOR = "ColorAnimation"


class DimensionType(Enum):
  LEFT = 'left'
  SIZE = 'size'
