from ..properties.instance import Instance


class BaseEncoder(object):

    def encode(self, instance):
        return self._dispatch(Instance(instance.__class__), instance)

    def _dispatch(self, _property, base):
        raise NotImplemented
