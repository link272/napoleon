import time

from napoleon.core.decorator.base import MethodWrapper
from napoleon.core.decorator.property import MethodDecorator
from napoleon.properties import Integer, Float


class Retrier(MethodWrapper):

    max_retry = Integer(3)
    delay: float = Float(3.)

    def __call__(self, *args, **kwargs):
        result = None
        count = 0
        while flag := count <= self.max_retry:
            try:
                result = self.method(*args, **kwargs)
            except Exception as e:  # noqa
                if flag:
                    time.sleep(self.delay)
                    count += 1
                else:
                    raise e
            else:
                break
        return result


def retry(retry_class=Retrier):
    def wrapper(method):
        return MethodDecorator(method,
                               retry_class,
                               default=retry_class)
    return wrapper
