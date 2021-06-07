from ..tools.singleton import Intrinsic, Undefined, UndefinedType, Nothing, NothingType
from ..tools.collection import get_child_class


class Property(object):

    __slots__ = ("description", "default", "nullable")
    _type = UndefinedType

    def __init__(self,
                 *,
                 default=Intrinsic,
                 description=Undefined,
                 nullable=False):

        self.description = description
        self.default = default
        self.nullable = nullable

    def initialize_default(self):
        if callable(self.default):
            default = self.default()
        elif self.default is Intrinsic:
            default = self.system_default()
        else:
            default = self.default
        return default

    def system_default(self):
        raise NotImplementedError
        
    def __str__(self):
        return self.__class__.__name__.capitalize()

    def __eq__(self, other):
        return isinstance(other, Property) and self.__class__ == other.__class__

    def __lt__(self, other):
        return isinstance(other, Property) and issubclass(self.__class__, other.__class__)


def iter_properties(cls):
    _properties = cls.__properties__.copy()  # noqa
    for parent in reversed(cls.mro()):
        if parent is not object:
            _properties.update(parent.__properties__)  # noqa
    return _properties.items()


def recurse_iter_properties(cls):
    for _cls in get_child_class(cls):
        for key, _prop in iter_properties(_cls):
            yield key, _prop


class PlaceHolder(Property):

    _type = NothingType
    __slots__ = ()

    def system_default(self):
        return Nothing
