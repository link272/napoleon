from .base import BaseDecoder
from ..properties.base import recurse_iter_properties, PlaceHolder
from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import JSON, Float, Integer, Boolean, String, Decimal, DateTime, Bytes, UUID
from ..tools.singleton import Undefined, is_define


class JSONDecoder(BaseDecoder):

    def _dispatch(self, _property, source):
        if isinstance(_property, Instance):
            target = self._decode_instance(_property, source)
        elif isinstance(_property, (List, Set)):
            target = self._decode_collection(_property, source)
        elif isinstance(_property, Map):
            target = self._decode_mapping(_property, source)
        elif isinstance(_property, (Float, Integer, Boolean, String, Decimal, DateTime, UUID)):
            target = _property.from_primitive(source)
        elif isinstance(_property, Bytes):
            target = _property.from_primitive(source.encode())
        elif isinstance(_property, JSON):
            target = source
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return target

    def _decode_instance(self, _property, component):
        instance = dict()
        for k, prop in recurse_iter_properties(_property.object_type):
            if isinstance(prop, PlaceHolder):
                continue
            source = component.get(k, Undefined)
            if is_define(source):
                if source is None:
                    instance[k] = None
                else:
                    instance[k] = self._dispatch(prop, source)
        cls = _property.infer_class(instance)
        return cls(**instance)

    def _decode_collection(self, _property, source):
        return _property.type(self._dispatch(_property.item_type, v) for v in source)

    def _decode_mapping(self, _property, source):
        return _property.type((k, self._dispatch(_property.item_type, v)) for k, v in source.items())
