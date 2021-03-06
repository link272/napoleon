import threading

from .base import Property

lock = threading.RLock()


class SlottedType(type):

    def __new__(mcs, name, bases, _dict): # noqa
        properties = {_name: _property for _name, _property in _dict.items() if isinstance(_property, Property)}
        setted_slot_names = mcs.get_all_slot_names(bases)  # noqa

        field_names = set(hex(id(prop))[1:] for prop in properties.values())

        new_slots = field_names - setted_slot_names

        if "_class_name" in new_slots:
            new_slots.remove("_class_name")

        if "__weakref__" not in setted_slot_names:  # noqa
            new_slots.add("__weakref__")  # noqa

        _dict["__slots__"] = new_slots
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
