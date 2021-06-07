from .base import Property
from ..tools.singleton import Intrinsic, Undefined


class Container(Property):

    __slots__ = ("nb_min", "nb_max", "item_type", "merge_on")

    def __init__(self,
                 item_type,
                 *,
                 nb_min=Undefined,
                 nb_max=Undefined,
                 merge_on=Undefined,
                 default=Intrinsic,
                 description=Undefined,
                 nullable=False):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.nb_min = nb_min
        self.nb_max = nb_max
        self.item_type = item_type
        self.merge_on = merge_on

    def __eq__(self, other):
        return super().__eq__(other) and self.item_type == other.item_type

    def __lt__(self, other):
        return super().__lt__(other) and self.item_type <= other.item_type

    def __str__(self):
        return str(self.item_type) + "[]"

    def system_default(self):
        return self._type()


class List(Container):

    unique = False
    __slots__ = ()
    _type = list


class Set(List):  # noqa

    unique = True
    __slots__ = ()
    _type = set


class Map(Container):  # noqa

    __slots__ = ()
    _type = dict
