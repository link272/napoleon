from napoleon.tools.singleton import Intrinsic, Undefined, Nothing
from napoleon.tools.collection import invert_map
from napoleon.properties.descriptor import Descriptor
from napoleon.properties import String, Set, Instance
from napoleon.core.application import Application


class Lazy(object):

    __slots__ = ("hidden_name", "map_attr_name")

    def __init__(self, name, map_attr_name):
        self.hidden_name = "_" + name
        self.map_attr_name = map_attr_name

    def __get__(self, instance, owner):
        _map = getattr(Application(), self.map_attr_name)
        return _map.get(getattr(instance, self.hidden_name), Nothing)

    def __set__(self, instance, value):
        setattr(instance, self.hidden_name, value)


class Alias(String, Descriptor):

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
        return "@" + str(self.item_type.__name__)

    def system_default(self):
        return Nothing

    def to_string(self, value):
        return invert_map(getattr(Application(), self.item_type.__name__.lower() + "s"))[value]

    def to_primitive(self, value):
        return self.to_string(value)


class LazySet(object):

    __slots__ = ("hidden_name", "map_attr_name")

    def __init__(self, name, map_attr_name):
        self.hidden_name = "_" + name
        self.map_attr_name = map_attr_name

    def __get__(self, instance, owner):
        _map = getattr(Application(), self.map_attr_name)
        return {key: _map.get(key) for key in getattr(instance, self.hidden_name)}

    def __set__(self, instance, value):
        setattr(instance, self.hidden_name, value)


class MapAlias(Set, Descriptor):

    __slots__ = ("item_class",)

    def __init__(self,
                 item_class,
                 *,
                 default=Intrinsic,
                 description=Undefined,
                 nullable=False):
        super().__init__(String(),
                         default=default,
                         description=description,
                         nullable=nullable)
        self.item_class = item_class

    def build_descriptor(self, name):
        return LazySet(name, self.item_class.__name__.lower() + "s")

    def __str__(self):
        return "@" + str(self.item_class.__name__)

    def to_string(self, values):
        _invert = invert_map(getattr(Application(), self.item_class.__name__.lower() + "s"))
        return [_invert[v] for v in values]

    def to_primitive(self, value):
        return self.to_string(value)
