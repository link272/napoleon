from ..properties.container import Collection, Map
from ..properties.instance import Instance
from ..properties.scalars import Blob, JSON, Symbol, Float, Integer, Boolean, String
from ..properties.base import recurse_iter_properties, PlaceHolder
from ..tools.singleton import Nothing, Undefined, exist, is_define
from .base import BaseMerger
from .json_decoder import JSONDecoder


class JSONMerger(BaseMerger):

    def __init__(self):
        super().__init__()
        self.decoder = JSONDecoder()

    def _dispatch_update(self, _property, root, source):
        if source is None:
            target = None
        elif not exist(root):
            target = self.decoder._dispatch(_property, root, source) # noqa
        elif isinstance(_property, Instance):
            target = self._decode_instance(_property, root, source)
        elif isinstance(_property, Collection):
            target = self._decode_collection(_property, root, source)
        elif isinstance(_property, Map):
            target = self._decode_mapping(_property, root, source)
        elif isinstance(_property, (JSON, Float, Integer, Boolean, String)):
            target = _property.from_primitive(source)
        elif isinstance(_property, (Blob, Symbol)):
            target = _property.from_string(source)
        elif isinstance(_property, PlaceHolder):
            target = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return target

    def _decode_instance(self, _property, root, source):
        instance = dict()
        for k, prop in recurse_iter_properties(_property.object_type):
            head = source.get(k, Undefined)
            base = getattr(root, k, Nothing)
            if is_define(head):
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
        return _property._type(res)

    def _decode_mapping(self, _property, base, root):
        for k2, v2 in base.items():
            if k2 in root:
                self._dispatch_update(_property.item_type, v2, root[k2])
            else:
                root[k2] = self.decoder._dispatch(_property.item_type, v2) # noqa
        return root
