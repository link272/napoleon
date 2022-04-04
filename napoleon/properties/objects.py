import logging

from .base import iter_properties
from .metaclass import SlottedType
from .scalars import String
from ..decoders.json_decoder import JSONDecoder
from ..encoders.hash_encoder import HashEncoder
from ..encoders.json_encoder import JSONEncoder


class ReadOnlyClassName(String):

    def __set_name__(self, owner, name):
        self.private_name = name
        self.public_name = name

    def __get__(self, instance, owner):
        return instance.__class__.__name__

    def __set__(self, instance, value):
        pass


class AbstractObject(object, metaclass=SlottedType):

    class_name = ReadOnlyClassName()
    log = logging

    def __init__(self, **kwargs):
        for key, _property in iter_properties(self.__class__): # noqa
            if key in kwargs:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, _property.default)
        self._check_internal()
        self._build_internal()

    def update(self, **kwargs):
        self._clean_internal()
        for key, field in iter_properties(self.__class__): # noqa
            if key in kwargs:
                self.__setattr__(key, kwargs[key])
        self._check_internal()
        self._build_internal()
        return self

    def _clean_internal(self):
        pass

    def _check_internal(self):
        pass

    def _build_internal(self):
        pass

    def hash(self):
        return HashEncoder().encode(self)

    def __del__(self):
        self._clean_internal()

    def copy(self):
        return self.__class__.deserialize(self.serialize())

    def serialize(self):
        return JSONEncoder().encode(self)

    @classmethod
    def deserialize(cls, instance):
        return JSONDecoder().decode(instance, cls)
