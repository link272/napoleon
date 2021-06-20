from ..tools.singleton import Intrinsic, Undefined, Nothing
from ..tools.collection import invert_map
from .scalars import String


class Lazy(object):

    __slots__ = ("hash_map_ref", "hidden_name")

    def __init__(self, hash_map_ref, name):
        self.hash_map_ref = hash_map_ref
        self.hidden_name = "_" + name

    def __get__(self, instance, owner):
        return self.hash_map_ref().get(getattr(instance, self.hidden_name), Nothing)

    def __set__(self, instance, value):
        setattr(instance, self.hidden_name, value)


class Alias(String):

    def __init__(self,
                 item_type,
                 hash_map_ref,
                 *,
                 default=Intrinsic,
                 description=Undefined,
                 nullable=False):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.hash_map_ref = hash_map_ref
        self.item_type = item_type

    def __eq__(self, other):
        return super().__eq__(other) and self.item_type.issubclass(other.item_type)

    def __lt__(self, other):
        return super().__lt__(other) and self.item_type.issubclass(other.item_type)

    def __str__(self):
        return "@" + str(self.item_type)

    def system_default(self):
        return Nothing

    def to_string(self, value):
        return invert_map(self.hash_map_ref())[value]

    def from_string(self, value):
        return value
