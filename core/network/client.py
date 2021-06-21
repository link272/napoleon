from napoleon.core.vault.secret import Secret
from napoleon.core.special.alias import Alias
from napoleon.properties import AbstractObject, String, Integer, Float, Instance, PlaceHolder
from napoleon.core.utils.timer import Timer, timeout
from napoleon.tools.context import temporary_state
from napoleon.core.abstract import AbstractClient

import threading
import urllib3
import socket

urllib3.disable_warnings()


class ClientDownException(Exception):

    pass


class Client(AbstractClient):

    host = String("127.0.0.1")
    user = String()
    password = Secret()
    port = Integer(443)
    timer: Timer = Instance(Timer, default=Timer)
    socket_timeout: int = Float(5.)
    service_timeout: int = Float(3600)
    _active_flag = PlaceHolder()
    lock = PlaceHolder()

    def _build_internal(self):
        self._active_flag = threading.Event()
        self.lock = threading.RLock()

    @timeout
    def check_activity(self):
        self.is_active = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.socket_timeout)
        try:
            s.connect((self.host, self.port))
        except Exception as e:
            self.log.warning(f"{self.host}:{self.port} is down: {e}")
        else:
            self.is_active = True
        finally:
            s.close()
        return self.is_active

    @property
    def is_active(self):
        return self._active_flag.is_set()

    @is_active.setter
    def is_active(self, value):
        if value:
            self._active_flag.set()
        else:
            self._active_flag.clear()

    def wait_for_activity(self):
        if not self.is_active:
            if not self.timer.is_active:
                with temporary_state(self.timer, delay=self.service_timeout):
                    if not self.check_activity():
                        raise ClientDownException(f"Service: {self.name} is down since: {self.service_timeout} seconds")
            else:
                if self._active_flag.wait(timeout=self.service_timeout):
                    raise ClientDownException(f"Service: {self.name} is down since: {self.service_timeout} seconds")

    def __str__(self):
        return self.name


class Interface(AbstractObject):

    client = Alias(Client)
