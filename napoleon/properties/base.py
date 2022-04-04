from ..tools.collection import get_child_class
from ..tools.singleton import Undefined, is_define


class Property(object):

    __slots__ = ("public_name", "private_name", "description", "_default", "nullable")

    def __init__(self,
                 *,
                 default=Undefined,
                 description=Undefined,
                 nullable=True):
        assert is_define(default)
        self.description = description
        self.nullable = nullable
        self._default = default

    @property
    def type(self):
        return Undefined

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError("None is not an allowed value for this field")
        if is_define(self.type) and (not isinstance(value, self.type) or value is not None):
            raise TypeError(f"{value} if not of type {self.type}")

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = hex(id(self))[1:]

    def __get__(self, instance, owner=None):
        """
        If instance is None than this is a class lookup, so we return the descriptor
        """
        return getattr(instance, self.private_name, self)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)

    @property
    def default(self):
        if callable(self._default):
            default = self._default()
        else:
            default = self._default
        return default
        
    def __str__(self):
        return self.__class__.__name__.capitalize()

    def __eq__(self, other):
        return isinstance(other, Property) and self.__class__ == other.__class__

    def __lt__(self, other):
        return isinstance(other, Property) and issubclass(self.__class__, other.__class__)


def iter_properties(cls):
    _properties = {u: v for u, v in vars(cls).items() if isinstance(v, Property)}  # noqa
    for parent in reversed(cls.mro()):
        if parent is not object:
            _properties.update({u: v for u, v in vars(parent).items() if isinstance(v, Property)})  # noqa
    return _properties.items()


def recurse_iter_properties(cls):
    for _cls in get_child_class(cls):
        for key, _prop in iter_properties(_cls):
            yield key, _prop


class PlaceHolder(Property):

    __slots__ = ()

    def __init__(self,
                 *,
                 default=None,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
