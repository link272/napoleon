from napoleon.properties import Blob
import numpy as np
from napoleon.tools.bson import to_bson, from_bson
from napoleon.tools.singleton import Nothing
import json


class Array(Blob):

    __slots__ = ()
    _type = np.array

    def system_default(self):
        return Nothing

    def to_string(self, value):
        return json.dumps(value.tolist())

    def from_string(self, value):
        return np.array(json.loads(value))

    def to_bytes(self, value):
        return to_bson(value.tolist())

    def from_bytes(self, value):
        return np.array(from_bson(value))

