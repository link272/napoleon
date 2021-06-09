from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import Float, Integer, JSON, Boolean, Symbol
from ..properties.base import recurse_iter_properties, PlaceHolder
from ..tools.singleton import Nothing, Undefined, exist, is_define
from .base import BaseMerger
from .json_decoder import JSONDecoder


class JSONMerger(BaseMerger):

    def __init__(self):
        super().__init__()
        self.decoder = JSONDecoder()

    def _dispatch_update(self, _property, base, root):
        if root is None or not exist(root) or not is_define(root):
            head = self.decoder._dispatch(_property, base) # noqa
        elif root is None or not exist(root) or not is_define(root):
            head = _property.system_default()
        elif isinstance(_property, Instance):
            head = self._decode_instance(_property, base, root)
        elif isinstance(_property, List):
            head = self._decode_list(_property, base, root)
        elif isinstance(_property, Set):
            head = self._decode_set(_property, base, root)
        elif isinstance(_property, Map):
            head = self._decode_mapping(_property, base, root)
        elif isinstance(_property, (Float, Integer, Boolean, JSON)):
            head = base
        elif isinstance(_property, Symbol):
            head = _property.from_string(base)
        elif isinstance(_property, PlaceHolder):
            head = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return head

    def _decode_instance(self, _property, component, root):
        instance = dict()
        for k, prop in recurse_iter_properties(_property.object_type):
            base = component.get(k, Undefined)
            attr = getattr(root, k, Nothing)
            if is_define(base):
                head = self._dispatch_update(prop, base, attr)
                if exist(head):
                    instance[k] = head
        return root.update(**instance)

    def _decode_list(self, _property, base, root):
        if isinstance(_property.item_type, Instance):
            for v1 in root:
                k1 = getattr(v1, _property.merge_on)
                found = False
                for v2 in base:
                    k2 = v2.get(_property.merge_on)
                    if k1 == k2:
                        self._dispatch_update(_property.item_type, v2, v1)
                        found = True
                if not found:
                    root.append(self.decoder._dispatch(_property.item_type, v2)) # noqa
            res = root
        else:
            res = self.decoder._dispatch(_property, base) # noqa
        return res

    def _decode_set(self, _property, base, root):
        return set(self._decode_list(_property, base, root))

    def _decode_mapping(self, _property, base, root):
        for k2, v2 in base.items():
            if k2 in root:
                self._dispatch_update(_property.item_type, v2, root[k2])
            else:
                root[k2] = self.decoder._dispatch(_property.item_type, v2) # noqa
        return root
