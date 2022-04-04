from functools import partial

from napoleon.core.decorator.base import MethodWrapper
from napoleon.properties.instance import Instance
from napoleon.tools.singleton import Undefined


class MethodDecorator(Instance):

    __slots__ = ("method",)

    def __init__(self,
                 method,
                 object_type,
                 *,
                 default=Undefined,
                 description=Undefined,
                 nullable=False):
        super().__init__(object_type,
                         default=default,
                         description=description,
                         nullable=nullable)
        assert issubclass(object_type, MethodWrapper)
        self.method = method

    def __set__(self, instance, value):
        value.method = partial(self.method, instance)
        setattr(instance, self.private_name, value)
