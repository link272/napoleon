from .base import BaseMerger
from .json_decoder import JSONDecoder
from ..properties.base import recurse_iter_properties
from ..properties.container import List, Set, Map
from ..properties.instance import Instance
from ..properties.scalars import JSON, Float, Integer, Boolean, String, Decimal, UUID, DateTime
from ..tools.singleton import Undefined, is_define


class JSONMerger(BaseMerger):

    def __init__(self):
        super().__init__()
        self.decoder = JSONDecoder()

    def _dispatch_update(self, _property, root, source): # noqa
        if isinstance(_property, Instance):
            target = self._decode_instance(_property, root, source)
        elif isinstance(_property, (List, Set)):
            target = self._decode_collection(_property, root, source)
        elif isinstance(_property, Map):
            target = self._decode_mapping(_property, root, source)
        elif isinstance(_property, (Float, Integer, Boolean, String, Decimal, DateTime, UUID)):
            target = _property.from_primitive(source)
        elif isinstance(_property, JSON):
            target = source
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return target

    def _decode_instance(self, _property, root, source):
        instance = dict()
        for k, prop in recurse_iter_properties(_property.object_type):
            head = source.get(k, Undefined)
            base = getattr(root, k)
            if is_define(head):
                if head is None:
                    instance[k] = None
                elif base is None:
                    instance[k] = self.decoder._dispatch(_property, source)
                else:
                    instance[k] = self._dispatch_update(prop, base, head)
        return root.update(**instance)

    def _decode_collection(self, _property, base, root):
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
        return _property.type(res)

    def _decode_mapping(self, _property, base, root):
        for k2, v2 in base.items():
            if k2 in root:
                self._dispatch_update(_property.item_type, v2, root[k2])
            else:
                root[k2] = self.decoder._dispatch(_property.item_type, v2) # noqa
        return root
