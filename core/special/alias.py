from napoleon.tools.singleton import Intrinsic, Undefined, Nothing
from napoleon.tools.collection import invert_map
from napoleon.properties.descriptor import Descriptor
from napoleon.core.application import app


class Lazy(object):

    __slots__ = ("hidden_name", "map_attr_name")

    def __init__(self, name, map_attr_name):
        self.hidden_name = "_" + name
        self.map_attr_name = map_attr_name

    def __get__(self, instance, owner):
        _map = getattr(app, self.map_attr_name)
        return _map.get(getattr(instance, self.hidden_name), Nothing)

    def __set__(self, instance, value):
        setattr(instance, self.hidden_name, value)


class Alias(Descriptor):

    __slots__ = ("item_type",)

    def __init__(self,
                 item_type,
                 *,
                 default=Intrinsic,
                 description=Undefined,
                 nullable=False):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.item_type = item_type

    def build_descriptor(self, name):
        return Lazy(name, self.item_type.__name__.lower() + "s")

    def __eq__(self, other):
        return super().__eq__(other) and self.item_type.issubclass(other.item_type)

    def __lt__(self, other):
        return super().__lt__(other) and self.item_type.issubclass(other.item_type)

    def __str__(self):
        return "@" + str(self.item_type)

    def system_default(self):
        return Nothing

    def to_string(self, value):
        return invert_map(getattr(app, self.item_type.__name__.lower() + "s"))[value]

    def from_string(self, value):
        return value
