from .base import Property
from ..tools.singleton import Undefined, is_define


class Container(Property):

    __slots__ = ("nb_min", "nb_max", "item_type", "merge_on")

    def __init__(self,
                 item_type,
                 *,
                 nb_min=Undefined,
                 nb_max=Undefined,
                 merge_on=Undefined,
                 default=Undefined,
                 description="",
                 nullable=False):
        super().__init__(default=default if is_define(default) else self.type,
                         description=description,
                         nullable=nullable)
        self.nb_min = nb_min
        self.nb_max = nb_max
        self.item_type = item_type
        self.merge_on = merge_on

    def validate(self, value):
        super().validate(value)
        if is_define(self.nb_min) and len(value) < self.nb_min:
            raise ValueError("Validation error")
        if is_define(self.nb_max) and len(value) > self.nb_max:
            raise ValueError("Validation error")

    def __eq__(self, other):
        return super().__eq__(other) and self.item_type == other.item_type

    def __lt__(self, other):
        return super().__lt__(other) and self.item_type <= other.item_type

    def __str__(self):
        return str(self.item_type) + "[]"


class List(Container):

    unique = False
    __slots__ = ()

    @property
    def type(self):
        return list

    def validate(self, value):
        super().validate(value)
        for item in value:
            self.item_type.validate(item)


class Set(Container):

    unique = True
    __slots__ = ()

    @property
    def type(self):
        return set

    def validate(self, value):
        super().validate(value)
        for item in value:
            self.item_type.validate(item)

class Map(Container):  # noqa

    __slots__ = ()

    @property
    def type(self):
        return dict

    def validate(self, value):
        super().validate(value)
        for item in value.values:
            self.item_type.validate(item)
