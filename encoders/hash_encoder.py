from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import Float, Integer, Boolean, Symbol, UUID
from ..properties.base import PlaceHolder, iter_properties
from ..tools.singleton import Nothing, exist, is_define
from .base import BaseEncoder
import hashlib


class HashEncoder(BaseEncoder):

    def encode(self, instance):
        _hash = hashlib.sha256()
        self._dispatch(Instance(instance.__class__), instance, _hash)
        return _hash.hexdigest()

    def _dispatch(self, _property, base, _hash): # noqa
        if isinstance(_property, Instance):
            self._encode_instance(_property, base, _hash)
        elif isinstance(_property, (List, Set)):
            self._encode_sequence(_property, base, _hash)
        elif isinstance(_property, Map):
            self._encode_mapping(_property, base, _hash)
        elif isinstance(_property, (Float, Integer, Boolean)):
            _hash.update(str(base).encode())
        elif isinstance(_property, UUID):
            _hash.update(base.bytes)
        elif isinstance(_property, Symbol):
            _hash.update(_property.to_string(base).encode())
        elif isinstance(_property, PlaceHolder):
            pass
        else:
            raise RuntimeError(f"{_property} is not implemented")

    def _encode_instance(self, _property, component, _hash):
        for k, prop in iter_properties(component.__class__):
            base = getattr(component, k, Nothing)
            if base:
                self._dispatch(prop, base, _hash)

    def _encode_sequence(self, _property, base, _hash):
        for v in base:
            self._dispatch(_property.item_type, v, _hash)

    def _encode_mapping(self, _property, base, _hash):
        for k, v in base.items():
            _hash.update(k.encode())
            self._dispatch(_property.item_type, v, _hash)
