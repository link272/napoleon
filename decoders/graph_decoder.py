from ..properties.container import Collection, Map
from ..properties.instance import Instance
from ..properties.scalars import Blob, JSON, UUID, DateTime, Float, Integer, Boolean, String
from ..properties.base import recurse_iter_properties, PlaceHolder
from ..tools.singleton import Undefined, Nothing, exist, is_define
from .base import BaseDecoder


class GraphQLDecoder(BaseDecoder):

    def __init__(self, model):
        self.model = model

    def _dispatch(self, _property, source):
        if source is None:
            target = None
        elif isinstance(_property, Instance):
            target = self._decode_instance(_property, source)
        elif isinstance(_property, Collection):
            target = self._decode_collection(_property, source)
        elif isinstance(_property, Map):
            target = self._decode_mapping(_property, source)
        elif isinstance(_property, (JSON, DateTime, UUID, Boolean, Integer, Float, String)):
            target = _property.from_primitive(source)
        elif isinstance(_property, Blob):
            target = _property.from_string(source)
        elif isinstance(_property, PlaceHolder):
            target = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return target

    def _decode_instance(self, _property, source):
        instance = dict()
        for k, prop in recurse_iter_properties(_property.object_type):
            head = getattr(source, k, Undefined)
            if is_define(head):
                instance[k] = self._dispatch(prop, head)
        cls = _property.infer_class(instance)
        return cls(**instance)

    def _decode_collection(self, _property, source):
        return _property._type(self._dispatch(_property.item_type, v) for v in source)

    def _decode_mapping(self, _property, source):
        name = str(_property.item_type) + "Map"
        _type, _prop = self.model.map_classes[name]
        return _property._type((item.key, self._dispatch(_prop, item.value)) for item in source)
