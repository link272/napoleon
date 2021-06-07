from napoleon.properties import AbstractObject, Boolean, Integer, Float, String, List
import numpy as np


class DType(AbstractObject):

    name = String()


class BaseFloat(DType):

    minimum: float = Float()
    maximum: float = Float()
    step: float = Float()
    default: float = Float()

    def _check_internal(self):
        assert self.minimum <= self.maximum

    def universe(self):
        return np.arange(self.minimum, self.maximum, step=self.step).tolist()


class BaseInteger(DType):

    minimum: int = Integer()
    maximum: int = Integer()
    step: int = Integer()
    default: int = Integer()

    def _check_internal(self):
        assert self.minimum <= self.maximum

    def universe(self):
        return list(range(self.minimum, self.maximum, step=self.step))


class BaseLabel(DType):

    labels: list = List(String())
    default: str = String()

    def universe(self):
        return self.symbols.copy()


class BaseBoolean(DType):

    default: bool = Boolean()

    def universe(self): # noqa
        return [False, True]
