import hashlib

from .base import BaseEncoder
from ..properties.base import PlaceHolder, iter_properties
from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import Scalar


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
        elif isinstance(_property, Scalar):
            _hash.update(_property.to_bytes(base))
        else:
            raise RuntimeError(f"{_property} is not implemented")

    def _encode_instance(self, _property, component, _hash):
        for k, prop in iter_properties(component.__class__):
            if isinstance(prop, PlaceHolder):
                continue
            base = getattr(component, k)
            if base is None:
                _hash.update(b"None")
            else:
                self._dispatch(prop, base, _hash)

    def _encode_sequence(self, _property, base, _hash):
        for v in sorted(list(base)):
            self._dispatch(_property.item_type, v, _hash)

    def _encode_mapping(self, _property, base, _hash):
        for k, v in base.items():
            _hash.update(k.encode())
            self._dispatch(_property.item_type, v, _hash)
