import datetime
import time

from napoleon.core.decorator.base import MethodWrapper
from napoleon.core.decorator.property import MethodDecorator
from napoleon.properties import Integer, Float


class Timeout(Exception):

    pass


class Timer(MethodWrapper):

    timeout: int = Integer(60)
    delay: float = Float(3.)

    def __call__(self, *args, **kwargs):
        result = None
        timeout = datetime.datetime.now() + datetime.timedelta(seconds=self.timeout)
        while flag := datetime.datetime.now() < timeout:
            try:
                result = self.method(*args, **kwargs)
            except Exception as e:
                if flag:
                    time.sleep(self.delay)
                else:
                    raise e
            else:
                break
        return result


def timer(timer_class=Timer):
    def wrapper(method):
        return MethodDecorator(method,
                               timer_class,
                               default=timer_class)
    return wrapper
