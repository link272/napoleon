from ..properties import List, Set, Map, Instance, Float, Integer, DateTime, JSON, UUID, Boolean, Symbol,\
    iter_properties, PlaceHolder
from ..tools.singleton import Nothing, exist
from .base import BaseEncoder


class GraphQLEncoder(BaseEncoder):

    def __init__(self, model):
        self.model = model

    def _dispatch(self, _property, base):
        if isinstance(_property, Instance):
            head = self._encode_instance(_property, base)
        elif isinstance(_property, (List, Set)):
            head = self._encode_sequence(_property, base)
        elif isinstance(_property, Map):
            head = self._encode_mapping(_property, base)
        elif isinstance(_property, (Float, Integer, Boolean, JSON, DateTime, UUID)):
            head = base
        elif isinstance(_property, Symbol):
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
        type_name = self.model.build_type_name(component.__class__, output=True)
        return self.model.graph_classes[type_name](**instance)

    def _encode_sequence(self, _property, base):
        return [self._dispatch(_property.item_type, v) for v in base]

    def _encode_mapping(self, _property, base):
        name = _property.__class__.__name__ + "Map"
        _type = self.model.map_classes[name][0]
        return [self._dispatch(Instance(_type), _type(key=k, value=v)) for k, v in base.items()]
