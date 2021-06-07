from ..properties.instance import Instance
import threading


class BaseDecoder(object):

    def decode(self, component, cls):
        return self._dispatch(Instance(cls), component)

    def _dispatch(self, _property, base):
        raise NotImplementedError


class BaseMerger(object):

    def __init__(self):
        self._lock = threading.RLock()

    def decode_update(self, base, head):
        with self._lock:
            self._dispatch_update(Instance(base.__class__), head, base)

    def _dispatch_update(self, _property, base, root):
        raise NotImplementedError
