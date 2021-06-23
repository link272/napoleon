from functools import wraps
from napoleon.properties import AbstractObject, Integer, PlaceHolder
from napoleon.tools.singleton import Nothing, exist
import threading


def timeout(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        flag = False
        timer = args[0].timer.copy()
        with timer:
            while not timer.is_timed_out():
                flag = method(*args, **kwargs)
                if not flag:
                    timer.wait()
                else:
                    break
        return flag
    return wrapper


class Timer(AbstractObject):

    delay: int = Integer(60)
    period: int = Integer(5)
    _is_timed_out = PlaceHolder()
    _internal_clock = PlaceHolder()

    def _build_internal(self):
        self._is_timed_out = threading.Event()

    def _check_internal(self):
        assert self.period < self.delay

    def is_timed_out(self):
        return self._is_timed_out.is_set()

    def wait(self):
        self._is_timed_out.wait(self.period)

    @property
    def is_active(self):
        return exist(self._internal_clock) and self._internal_clock.is_alive()

    def __enter__(self):
        self._is_timed_out.clear()
        self._internal_clock = threading.Timer(self.delay, self._is_timed_out.set)
        self._internal_clock.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.is_timed_out():
            self._internal_clock.cancel()
        self._internal_clock = Nothing
