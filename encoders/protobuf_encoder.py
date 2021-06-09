from ..properties.container import List, Set, Map, Container
from ..properties.instance import Instance
from ..properties.scalars import Float, Integer, Boolean, Bytes, DateTime, String
from ..properties.base import PlaceHolder, iter_properties
from ..tools.singleton import Nothing, exist
from .base import BaseEncoder


class ProtobufEncoder(BaseEncoder):

    def __init__(self, model, deterministic=True):
        self.model = model
        self.deterministic = deterministic

    def encode(self, instance):
        message = super().encode(instance)
        return message.SerializeToString(deterministic=self.deterministic)

    def _dispatch(self, _property, base):
        if isinstance(_property, Instance):
            head = self._encode_instance(_property, base)
        elif isinstance(_property, (List, Set)):
            head = self._encode_sequence(_property, base)
        elif isinstance(_property, Map):
            head = self._encode_mapping(_property, base)
        elif isinstance(_property, (Float, Integer, Boolean, DateTime)):
            head = base
        elif isinstance(_property, Bytes):
            head = _property.to_bytes(base)
        elif isinstance(_property, String):
            head = _property.to_string(base)
        elif isinstance(_property, PlaceHolder):
            head = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return head

    def _encode_instance(self, _property, component):
        message_type = self.model.get_message_type(component.__class__.__name__)
        instance = message_type()
        for k, prop in iter_properties(component.__class__):
            base = getattr(component, k, Nothing)
            if exist(base):
                head = self._dispatch(prop, base)
                if exist(head):
                    if isinstance(prop, Container):
                        getattr(instance, k).extend(head)
                    elif isinstance(prop, DateTime):
                        getattr(instance, k).FromDatetime(head)
                    else:
                        setattr(instance, k, head)
        return instance

    def _encode_sequence(self, _property, base):
        return [self._dispatch(_property.item_type, v) for v in base]

    def _encode_mapping(self, _property, base):
        name = str(_property.item_type) + "Map"
        _type = self.model.map_classes[name][0]
        return [self._dispatch(Instance(_type), _type(key=k, value=v)) for k, v in base.items()]
