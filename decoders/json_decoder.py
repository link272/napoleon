from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import Float, Integer, JSON, Boolean, Symbol
from ..properties.base import recurse_iter_properties, PlaceHolder
from ..tools.singleton import Undefined, exist, is_define, Nothing
from .base import BaseDecoder


class JSONDecoder(BaseDecoder):

    def _dispatch(self, _property, base):
        if not exist(base) or not is_define(base):
            head = _property.system_default()
        elif base is None:
            head = None
        elif isinstance(_property, Instance):
            head = self._decode_instance(_property, base)
        elif isinstance(_property, List):
            head = self._decode_sequence(_property, base)
        elif isinstance(_property, Map):
            head = self._decode_mapping(_property, base)
        elif isinstance(_property, (Float, Integer, Boolean, JSON)):
            head = base
        elif isinstance(_property, Symbol):
            head = _property.from_string(base)
        elif isinstance(_property, PlaceHolder):
            head = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return head

    def _decode_instance(self, _property, component):
        instance = dict()
        for k, prop in recurse_iter_properties(_property.object_type):
            base = component.get(k, Undefined)
            if is_define(base):
                head = self._dispatch(prop, base)
                if exist(head):
                    instance[k] = head
        cls = _property.infer_class(instance)
        return cls(**instance)

    def _decode_sequence(self, _property, base):
        return _property._type(self._dispatch(_property.item_type, v) for v in base)

    def _decode_mapping(self, _property, base):
        return _property._type((k, self._dispatch(_property.item_type, v)) for k, v in base.items())
