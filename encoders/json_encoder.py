from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import Float, Integer, JSON, Boolean, String, Blob, Symbol
from ..properties.base import PlaceHolder, iter_properties
from ..tools.singleton import Nothing, exist
from .base import BaseEncoder


class JSONEncoder(BaseEncoder):

    def _dispatch(self, _property, base):
        if isinstance(_property, Instance):
            head = self._encode_instance(_property, base)
        elif isinstance(_property, (List, Set)):
            head = self._encode_sequence(_property, base)
        elif isinstance(_property, Map):
            head = self._encode_mapping(_property, base)
        elif isinstance(_property, (Float, Integer, Boolean, JSON, String)):
            head = _property.to_primitive(base)
        elif isinstance(_property, (Blob, Symbol)):
            head = _property.to_string(base)
        elif isinstance(_property, PlaceHolder):
            head = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return head

    def _encode_instance(self, _property, component):
        instance = dict()
        for k, prop in iter_properties(component.__class__):
            base = getattr(component, k, Nothing)
            if exist(base):
                head = self._dispatch(prop, base)
                if exist(head):
                    instance[k] = head
        return instance

    def _encode_sequence(self, _property, base):
        return [self._dispatch(_property.item_type, v) for v in base]

    def _encode_mapping(self, _property, base):
        return {k: self._dispatch(_property.item_type, v) for k, v in base.items()}
