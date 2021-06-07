from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import Float, Integer, Boolean, Bytes, DateTime, String
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

    def _dispatch(self, _property, base):
        if base is None or not exist(base) or not is_define(base):
            head = _property.system_default()
        elif isinstance(_property, Instance):
            head = self._decode_instance(_property, base)
        elif isinstance(_property, Set):
            head = self._decode_set(_property, base)
        elif isinstance(_property, List):
            head = self._decode_list(_property, base)
        elif isinstance(_property, Map):
            head = self._decode_mapping(_property, base)
        elif isinstance(_property, (Float, Integer, Boolean, DateTime)):
            head = base
        elif isinstance(_property, DateTime):
            head = pendulum.instance(base.ToDatetime())
        elif isinstance(_property, Bytes):
            head = _property.from_bytes(base)
        elif isinstance(_property, String):
            head = _property.from_string(base)
        elif isinstance(_property, PlaceHolder):
            head = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return head

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

    def _decode_set(self, _property, base):
        return {self._dispatch(_property.item_type, v) for v in base}

    def _decode_list(self, _property, base):
        return [self._dispatch(_property.item_type, v) for v in base]

    def _decode_mapping(self, _property, base):
        name = _property.__class__.__name__ + "Map"
        _type, _prop = self.model.map_classes[name]
        return {item.key: self._dispatch(_prop, item.value) for item in base}
