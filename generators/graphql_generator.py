from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import Float, Integer, String, DateTime, JSON, UUID, Bytes, Boolean, Blob
from ..properties.metaclass import SlottedType
from ..properties.base import PlaceHolder, recurse_iter_properties
from ..tools.singleton import Nothing, Undefined, exist, is_define
from ..tools.collection import get_child_class
from ..properties.objects import AbstractObject
import graphene
import inspect
import typing
from functools import wraps


def graph_method(method):
    @wraps(method)
    def wrapper(root, *args, **kwargs):
        return method(root, *args, **kwargs)
    wrapper.is_graphql = True
    return wrapper


class GraphQLModel(object):

    def __init__(self):
        self.graph_classes = {}
        self.input_root = Undefined
        self.output_root = Undefined
        self.map_classes = {}

    def build_type_name(self, _cls, output=True): # noqa
        suffix = "Type" if output else "InputType"
        return _cls.__name__ + suffix

    def generate_output_model(self, root):
        self.output_root = self._dispatch(Instance(root), output=True)

    def generate_input_model(self, root):
        self.input_root = self._dispatch(Instance(root), output=False)

    def _dispatch(self, _property, output=True):
        if isinstance(_property, Instance):
            name = self.build_type_name(_property.object_type, output=output)
            if name not in self.graph_classes:
                _type = self._build_graph_type(_property.object_type, output=output)
                for cls in get_child_class(_property.object_type):
                    sub_name = self.build_type_name(cls, output=output)
                    self.graph_classes[sub_name] = _type
            _type = self.graph_classes[name]
        elif isinstance(_property, (List, Set)):
            _type = self._build_sequence_type(_property, output=output)
        elif isinstance(_property, Map):
            _type = self._build_mapping_type(_property, output=output)
        elif isinstance(_property, Integer):
            _type = graphene.types.scalars.BigInt
        elif isinstance(_property, Float):
            _type = graphene.Float
        elif isinstance(_property, DateTime):
            _type = graphene.DateTime
        elif isinstance(_property, Bytes):
            _type = graphene.Base64
        elif isinstance(_property, Boolean):
            _type = graphene.Boolean
        elif isinstance(_property, String):
            _type = graphene.String
        elif isinstance(_property, JSON):
            _type = graphene.JSONString
        elif isinstance(_property, UUID):
            _type = graphene.UUID
        elif isinstance(_property, Blob):
            _type = graphene.String
        elif isinstance(_property, PlaceHolder):
            _type = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return _type

    def _build_sequence_type(self, _property, output=True):
        return graphene.List(self._dispatch(_property.item_type, output=output))

    def _build_mapping_type(self, _property, output=True):
        kv_name = str(_property.item_type) + "Map"
        if kv_name not in self.map_classes:
            self.map_classes[kv_name] = (
                SlottedType(kv_name, (AbstractObject,), {"key": String(), "value": _property.item_type}),
                _property)
        return self._build_sequence_type(List(Instance(self.map_classes[kv_name][0])), output=output)

    def _build_graph_method(self, attrs, obj_class):
        for attr_name, method in inspect.getmembers(obj_class, predicate=inspect.isfunction):
            if getattr(method, "is_graphql", False):
                signature = typing.get_type_hints(method)
                return_type = signature.pop("return")
                method_args = {k: self._dispatch(v, output=True) for k, v in signature.items()}
                attrs[attr_name] = graphene.Field(self._dispatch(return_type, output=True), args=method_args)
                attrs["resolve_" + attr_name] = method

    def _build_graph_type(self, object_type, output=True):
        name = self.build_type_name(object_type, output=output)
        attr = {}
        meta = {
            "name": name
        }
        attr["Meta"] = type("Meta", (object,), meta)
        for key, _prop in recurse_iter_properties(object_type):
            attr_type = self._dispatch(_prop, output=output)
            if exist(attr_type):
                desc = _prop.description if is_define(_prop.description) else ""
                if output:
                    attr[key] = graphene.Field(attr_type,
                                               description=desc,
                                               required=False,
                                               default_value=None)
                else:
                    attr[key] = graphene.InputField(attr_type,
                                                    description=desc,
                                                    required=False,
                                                    default_value=Undefined)

        if output:
            self._build_graph_method(attr, object_type)
            _type = type(name, (graphene.ObjectType,), attr)
        else:
            _type = type(name, (graphene.InputObjectType,), attr)
        return _type
