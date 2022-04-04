from napoleon.properties import AbstractObject, String, PlaceHolder, Map, Bytes, Boolean, Decimal,\
    DateTime, UUID, List, Float, Set, Instance, Integer, JSON
import pendulum
from napoleon.core.decorator.retry import retry
from napoleon.core.decorator.state import checkpoint
from napoleon.core.log.property import Log
from napoleon.core.shared.property import Alias
from napoleon.core.network.base import BaseClient
from napoleon.core.vault.property import Secret
from napoleon.core.shared.application import Application


NOW = pendulum.now()


class TestScalar(AbstractObject):

    a1 = Boolean()
    a2 = Float(minimum=0.0, maximum=1.0, default=lambda: 0.5)
    a3 = Integer(maximum=10, minimum=2, multiple_of=2, default=4)
    a4 = String()
    a5 = Bytes(default=b"test")
    a6 = Decimal(default=3)
    a7 = DateTime(default=NOW)
    a8 = UUID()
    a9 = JSON()

    @retry()
    def retryable_method(self):
        self.a3 += 2
        raise Exception()


class TestContainer(AbstractObject):

    b1 = List(Instance(TestScalar))
    b2 = Set(String())
    b3 = Map(Integer())


class TestInstance(AbstractObject):

    c1 = Log()

    @checkpoint()
    def checkpoint_method(self):
        for i in range(self.checkpoint_method.context.get("i", 0), 10):
            self.checkpoint_method.context["i"] = i
            if i == 3 and not self.checkpoint_method.context.get("except", False):
                self.checkpoint_method.context["except"] = True
                raise Exception()
        return True


class TestInstanceChild1(TestInstance):

    c2 = Alias(Application.clients)


class TestInstanceChild2(TestInstance):

    c3 = PlaceHolder(default=Ellipsis)
    c4 = Secret()
