from .base import Property
from .alias import Alias
from ..tools.singleton import Nothing
import threading

lock = threading.RLock()


class Lazy(object):

    __slots__ = ("hash_map", "hidden_name")

    def __init__(self, hash_map, name):
        self.hash_map = hash_map
        self.hidden_name = "_" + name

    def __get__(self, instance, owner):
        return self.hash_map.get(getattr(instance, self.hidden_name), Nothing)

    def __set__(self, instance, value):
        setattr(instance, self.hidden_name, value)


class SlottedType(type):

    def __new__(mcs, name, bases, _dict): # noqa
        properties = {_name: _property for _name, _property in _dict.items() if isinstance(_property, Property)}
        setted_slot_names = mcs.get_all_slot_names(bases)  # noqa

        field_names = set(properties.keys())

        new_slots = field_names - setted_slot_names

        if "__weakref__" not in setted_slot_names:  # noqa
            new_slots.add("__weakref__")  # noqa

        if "class_name" not in setted_slot_names:
            new_slots.add("class_name")

        _dict["__slots__"] = new_slots
        _dict["__properties__"] = properties

        for _name in field_names:
            if isinstance(properties[_name], Alias):
                _dict[_name] = Lazy(properties[_name].item_map, _name)
                _dict["__slots__"].remove(_name)
                _dict["__slots__"].add("_" + _name)
            else:
                _dict.pop(_name)

        return super().__new__(mcs, name, bases, _dict)

    @classmethod
    def get_all_slot_names(mcs, bases): # noqa
        names = set()
        for base in bases:
            if base is not object:
                for _cls in base.mro():
                    sub_names = set(_cls.__dict__.get("__slots__", set()))
                    names.update(sub_names)
        return names


class Singleton(SlottedType):
    
    _instances = {}

    def __call__(cls, *args, **kwargs): # noqa
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MutableSingleton(SlottedType):

    _instances = {}

    def __call__(cls, *args, **kwargs): # noqa
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(MutableSingleton, cls).__call__(*args, **kwargs)
        elif args or kwargs:
            with lock:
                cls._instances[cls].update(*args, **kwargs)
        else:
            pass
        return cls._instances[cls]
