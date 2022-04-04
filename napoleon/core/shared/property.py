from napoleon.core.shared.application import Application
from napoleon.properties import String, Map
from napoleon.tools.collection import invert_map
from napoleon.tools.singleton import Undefined


class Alias(String):

    """Alias for shared objects"""

    __slots__ = ("descriptor",)

    def __init__(self,
                 descriptor,
                 *,
                 default=None,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        assert isinstance(descriptor, Map)
        self.descriptor = descriptor

    @property
    def mapping(self):
        return getattr(Application(), self.descriptor.private_name)

    def __set__(self, instance, value):
        if value is None:
            setattr(instance, self.private_name, value)
        elif isinstance(value, str):
            setattr(instance, self.private_name, value)
        elif isinstance(value, self.descriptor.item_type):
            setattr(instance, self.private_name, invert_map(self.mapping)[value])
        else:
            raise ValueError(f"{value} is not an instance of ({self.descriptor.item_type}, str)")

    def __get__(self, instance, owner=None):
        value = getattr(instance, self.private_name)
        return self.mapping.get(value, None)

    def to_primitive(self, value):
        return invert_map(self.mapping)[value]

    def __delete__(self, instance):
        setattr(instance, self.private_name, None)

    def __eq__(self, other):
        return super().__eq__(other) and self.descriptor.item_type.issubclass(other.item_type)

    def __lt__(self, other):
        return super().__lt__(other) and self.descriptor.item_type.issubclass(other.item_type)

    def __str__(self):
        return "@" + str(self.descriptor.item_type.__name__)

    def to_bytes(self, value):
        return self.to_primitive(value).encode()
