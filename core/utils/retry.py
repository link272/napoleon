from napoleon.properties import AbstractObject, Integer
from functools import wraps
import time


def retry(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        result = None
        count = 0
        retrier = args[0].retrier.copy()
        while count <= retrier.max_retry:
            if count < retrier.max_retry:
                try:
                    result = method(*args, **kwargs)
                except Exception:  # noqa
                    retrier.wait(count)
                    count += 1
                else:
                    break
            else:
                result = method(*args, **kwargs)
        return result
    return wrapper


class Retrier(AbstractObject):

    max_retry = Integer(3)
    delay = Integer(3)

    def wait(self, count):
        time.sleep(self.delay)
