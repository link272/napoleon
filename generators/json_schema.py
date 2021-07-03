from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import Float, Integer, String, JSON, Boolean, Blob, Symbol
from ..properties.base import PlaceHolder, recurse_iter_properties
from ..tools.singleton import is_define
from jsonschema import validate


class JSONSchema(object):

    def __init__(self, title="default"):
        self.title = title

    def generate_schema(self, _property):
        schema = self._dispatch(Instance(_property))
        schema["title"] = self.title
        schema["$schema"] = "http://json-schema.org/schema#"
        return schema

    def _dispatch(self, _property):
        if isinstance(_property, Instance):
            schema = self._build_instance_schema(_property)
        elif isinstance(_property, (List, Set)):
            schema = self._build_sequence_schema(_property)
        elif isinstance(_property, Map):
            schema = self._build_mapping_schema(_property)
        elif isinstance(_property, Integer):
            schema = self._build_numeric_schema(_property, "integer")
        elif isinstance(_property, Float):
            schema = self._build_numeric_schema(_property, "number")
        elif isinstance(_property, Boolean):
            schema = self._build_base_schema("boolean", _property)
        elif isinstance(_property, String):
            schema = self._build_string_schema(_property)
        elif isinstance(_property, JSON):
            schema = self._build_base_schema("object", _property)
        elif isinstance(_property, PlaceHolder):
            schema = self._build_base_schema("null", _property)
        elif isinstance(_property, Blob):
            schema = self._build_base_schema("string", _property)
        elif isinstance(_property, Symbol):
            schema = self._build_symbol_schema(_property)
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return schema

    def _build_base_schema(cls, _type, _property): # noqa
        if _property.nullable and _type != "null":
            schema = {"type": [_type, "null"]}
        else:
            schema = {"type": _type}
        if is_define(_property.description):
            schema["description"] = _property.description
        return schema

    def _build_instance_schema(self, instance):
        schema = self._build_base_schema("object", instance)
        properties = {}
        for key, _prop in recurse_iter_properties(instance.object_type):
            properties[key] = self._dispatch(_prop)
        schema["properties"] = properties
        schema["additionalProperties"] = False
        schema["propertyNames"] = {"type": "string", "pattern": "[a-z_][a-z0-9_]{1,30}$"}
        return schema

    def _build_sequence_schema(self, _property):
        schema = self._build_base_schema("array", _property)
        schema["items"] = self._dispatch(_property.item_type)
        if is_define(_property.nb_min):
            schema["minItems"] = _property.nb_min
        if is_define(_property.nb_max):
            schema["maxItems"] = _property.nb_max
        if is_define(_property.unique):
            schema["uniqueItems"] = _property.unique
        if is_define(_property.merge_on):
            schema["mergeStrategy"] = "arrayMergeById"
            schema["mergeOptions"] = {"idRef": "/" + _property.merge_on}
        return schema

    def _build_mapping_schema(self, _property):
        schema = self._build_base_schema("object", _property)
        if is_define(_property.nb_min):
            schema["minProperties"] = _property.nb_min
        if is_define(_property.nb_max):
            schema["maxProperties"] = _property.nb_max
        schema["propertyNames"] = {"type": "string", "pattern": "[a-z_][a-z0-9_]{2,30}$"}
        return schema

    def _build_numeric_schema(self, _property, _type):
        schema = self._build_base_schema(_type, _property)
        if is_define(_property.minimum):
            schema["minimum"] = _property.minimum
        if is_define(_property.maximum):
            schema["maximum"] = _property.maximum
        if is_define(_property.exclusive_minimum):
            schema["exclusiveMinimum"] = _property.exclusive_minimum
        if is_define(_property.exclusive_maximum):
            schema["exclusiveMaximum"] = _property.exclusive_maximum
        if is_define(_property.multiple_of):
            schema["multipleOf"] = _property.multiple_of
        return schema

    def _build_symbol_schema(self, _property):
        schema = self._build_base_schema("string", _property)
        if is_define(_property.format):
            schema["format"] = _property.format
        if is_define(_property.pattern):
            schema["format"] = _property.pattern
        return schema

    def _build_string_schema(self, _property):
        schema = self._build_symbol_schema(_property)
        if is_define(_property.enum):
            if len(_property.enum) == 1:
                schema["const"] = _property.enum[0]
            else:
                schema["enum"] = _property.enum
        if is_define(_property.min_length):
            schema["minLength"] = _property.min_length
        if is_define(_property.max_length):
            schema["maxLength"] = _property.max_length
        return schema

    def validate(self, struct, component):
        validate(struct, schema=self.generate_schema(component))
