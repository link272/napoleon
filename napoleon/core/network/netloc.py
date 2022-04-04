import socket

import urllib3

from napoleon.core.decorator.timer import timer
from napoleon.core.network.base import BaseClient
from napoleon.properties import String, Integer, Float

urllib3.disable_warnings()


class NetworkLocalization(BaseClient):

    host = String("127.0.0.1")
    port = Integer(443)
    socket_timeout: int = Float(5.)

    @timer()
    def check_remote(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.socket_timeout)
        try:
            s.connect((self.host, self.port))
        except Exception as e:
            s.close()
            raise e
