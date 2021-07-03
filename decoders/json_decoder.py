from ..properties.container import Collection, Map
from ..properties.instance import Instance
from ..properties.scalars import Blob, JSON, Symbol, Float, Integer, Boolean, String
from ..properties.base import recurse_iter_properties, PlaceHolder
from ..tools.singleton import Undefined, exist, is_define, Nothing
from .base import BaseDecoder


class JSONDecoder(BaseDecoder):

    def _dispatch(self, _property, source):
        if source is None:
            target = Nothing
        elif isinstance(_property, Instance):
            target = self._decode_instance(_property, source)
        elif isinstance(_property, Collection):
            target = self._decode_collection(_property, source)
        elif isinstance(_property, Map):
            target = self._decode_mapping(_property, source)
        elif isinstance(_property, (JSON, Float, Integer, Boolean, String)):
            target = _property.from_primitive(source)
        elif isinstance(_property, (Blob, Symbol)):
            target = _property.from_string(source)
        elif isinstance(_property, PlaceHolder):
            target = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return target

    def _decode_instance(self, _property, component):
        instance = dict()
        for k, prop in recurse_iter_properties(_property.object_type):
            source = component.get(k, Undefined)
            if is_define(source):
                instance[k] = self._dispatch(prop, source)
        cls = _property.infer_class(instance)
        return cls(**instance)

    def _decode_collection(self, _property, source):
        return _property._type(self._dispatch(_property.item_type, v) for v in source)

    def _decode_mapping(self, _property, source):
        return _property._type((k, self._dispatch(_property.item_type, v)) for k, v in source.items())
