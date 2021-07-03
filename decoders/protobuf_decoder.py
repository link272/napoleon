from ..properties.container import Collection, Map
from ..properties.instance import Instance
from ..properties.scalars import Blob, JSON, UUID, DateTime, Float, Integer, Boolean, String
from ..properties.base import recurse_iter_properties, PlaceHolder
from ..tools.singleton import Nothing, Undefined, exist, is_define
from .base import BaseDecoder
import pendulum


class ProtobufDecoder(BaseDecoder):

    def __init__(self, model):
        self.model = model

    def decode(self, bytes_message, cls):
        message = self.model.get_message_type(cls.__name__)()
        message.ParseFromString(bytes_message)
        _property = Instance(cls)
        return self._dispatch(Instance(cls), message)

    def _dispatch(self, _property, source):
        if not is_define(source):
            target = _property.system_default()
        elif isinstance(_property, Instance):
            target = self._decode_instance(_property, source)
        elif isinstance(_property, Collection):
            target = self._decode_collection(_property, source)
        elif isinstance(_property, Map):
            target = self._decode_mapping(_property, source)
        elif isinstance(_property, DateTime):
            target = pendulum.instance(source.ToDatetime())
        elif isinstance(_property, (Float, Integer, Boolean, String)):
            target = _property.from_primitive(source)
        elif isinstance(_property, (JSON, Blob, UUID)):
            target = _property.from_bytes(source)
        elif isinstance(_property, PlaceHolder):
            target = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return target

    def _decode_instance(self, _property, component):
        instance = dict()
        for k, prop in recurse_iter_properties(_property.object_type):
            base = getattr(component, k, Undefined)
            if is_define(base):
                head = self._dispatch(prop, base)
                if exist(head):
                    instance[k] = head
        cls = _property.infer_class(instance)
        return cls(**instance)

    def _decode_collection(self, _property, base):
        return _property._type([self._dispatch(_property.item_type, v) for v in base])

    def _decode_mapping(self, _property, base):
        name = str(_property.item_type) + "Map"
        _type, _prop = self.model.map_classes[name]
        return _property._type((item.key, self._dispatch(_prop, item.value)) for item in base)
