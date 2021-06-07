from .base import Property, recurse_iter_properties
from ..tools.singleton import Undefined, Intrinsic, Nothing
from ..tools.collection import leave_one_out, first, get_child_class, empty


class Instance(Property):

    __slots__ = ("object_type",)
    _type = object

    def __init__(self,
                 object_type,
                 *,
                 default=Intrinsic,
                 description=Undefined,
                 nullable=False):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.object_type = object_type

    def __eq__(self, other):
        return super().__eq__(other) and self.object_type == other.object_type

    def __lt__(self, other):
        return super().__eq__(other) and issubclass(self.object_type, other.object_type)

    def __str__(self):
        return self.object_type.__name__

    def system_default(self):
        return Nothing

    def infer_class(self, instance):
        if len(get_child_class(self.object_type)) == 1:
            candidate = self.object_type
        else:
            candidates = {_cls for _cls in get_child_class(self.object_type) if _cls.__name__ == instance.get("class_name", None)}
            if not candidates:
                candidates = self.search_class(instance)
            if len(candidates) != 1:
                raise RuntimeError(f"No unique candidate for object: {self.object_type.__name__}, {instance}, {get_child_class(self.object_type)}")
            else:
                candidate = first(candidates)
        return candidate

    def search_class(self, instance):
        candidates = set()
        instance_properties = set(instance.keys())
        for one_out, others in leave_one_out(get_child_class(self.object_type, include_parent=False)):
            others_properties = [{key for key, value in recurse_iter_properties(_cls)} for _cls in others]
            if not empty(others_properties):
                set_others_properties = set.union(*others_properties)
                if not instance_properties.issubset(set_others_properties):
                    candidates.add(one_out)
        return candidates
