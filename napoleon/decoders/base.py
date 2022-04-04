import threading

from ..properties.instance import Instance


class BaseDecoder(object):

    def decode(self, source, cls):
        return self._dispatch(Instance(cls), source)

    def _dispatch(self, _property, source):
        raise NotImplementedError


class BaseMerger(object):

    def __init__(self):
        self._lock = threading.RLock()

    def decode_update(self, root, source):
        with self._lock:
            self._dispatch_update(Instance(root.__class__), root, source)

    def _dispatch_update(self, _property, root, source):
        raise NotImplementedError
