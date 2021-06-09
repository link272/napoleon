from napoleon.properties import Alias, AbstractObject, String, Integer, Float, Instance, PlaceHolder, Boolean, List
from napoleon.core.utils.timer import Timer, timeout
from napoleon.core.vault import Secret
from napoleon.core.paths import PATHS, FilePath, Path
from napoleon.tools.context import temporary_state
from napoleon.core.tasks.graph_machine import BaseAction, EXIT, DEFAULT
from napoleon.tools.collection import empty

import threading
import urllib3
import socket

urllib3.disable_warnings()


CLIENTS = {}


class CheckService(BaseAction):

    client_names = List(String())
    timer = Instance(Timer, default=Timer)

    def execute(self, context):
        for name, client in CLIENTS.items():
            if empty(self.client_names) or name in self.client_names:
                with temporary_state(client, timer=self.timer):
                    if not client.check_activity():
                        self.log.error(f"Service {name} is down")
        return DEFAULT


class ServiceDownException(Exception):

    pass


class Client(AbstractObject):

    name = String("default")
    host = String("127.0.0.1")
    port = Integer(443)
    user = String()
    password = Secret()
    timer = Instance(Timer, default=Timer)
    socket_timeout: int = Float(5.)
    service_timeout: int = Float(3600)
    _active_flag = PlaceHolder()
    lock = PlaceHolder()

    def _build_internal(self):
        CLIENTS[self.name] = self
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
                        raise ServiceDownException(f"Service: {self.name} is down since: {self.service_timeout} seconds")
            else:
                if self._active_flag.wait(timeout=self.service_timeout):
                    raise ServiceDownException(f"Service: {self.name} is down since: {self.service_timeout} seconds")

    def __str__(self):
        return self.name
