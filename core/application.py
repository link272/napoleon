from napoleon.properties import MutableSingleton, Instance, Map, String
from napoleon.core.trace import Logger, LOGGERS
from napoleon.core.network.client import CLIENTS, Client
from napoleon.core.storage.database import DATABASES, Database
from napoleon.core.utils.machine import Platform, PLATFORM
from napoleon.core.cmd import CommandLine, CMD
from napoleon.core.utils.config import Configurable
from napoleon.core.paths import Paths, PATHS
from napoleon.core.vault import Vault, VAULT
from napoleon.core.daemon.base import Daemon
from napoleon.decoders.json_decoder import JSONDecoder
import sys
import importlib
import signal
import warnings
import time


class Application(Configurable, metaclass=MutableSingleton):

    name = String("Napoleon")
    tracers = Map(Instance(Logger), default=LOGGERS)
    paths = Instance(Paths, default=PATHS)
    clients = Map(Instance(Client), default=CLIENTS)
    databases = Map(Instance(Database), default=DATABASES)
    platform = Instance(Platform, default=PLATFORM)
    cmd = Instance(CommandLine, default=CMD)
    vault = Instance(Vault, default=VAULT)
    warning_filter: str = String("ignore")
    daemons: dict = Map(Instance(Daemon))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        signal.signal(signal.SIGUSR1, self.reload)  # 12

    def _build_internal(self):
        warnings.filterwarnings(self.warning_filter)

    def _clean_internal(self):
        self.shutdown()

    def reload(self, signum, frame): # noqa
        self.log.info(f"Receiving signal {signum}, reloading")
        for name, module in sys.modules.copy().items():
            if name.startswith("core") and not name.startswith("core.share.schema"):
                importlib.reload(module)

    def shutdown(self):
        for daemon in self.daemons.values():
            daemon.shutdown()

    def start(self):
        for daemon in self.daemons.values():
            daemon.start()

    def run(self):
        self.start()
        loop = True
        while loop:
            try:
                time.sleep(2)
            except KeyboardInterrupt:
                loop = False
        self.shutdown()

    @classmethod
    def deserialize(cls, instance):
        serialized_daemons = instance.pop("daemons")
        app = JSONDecoder().decode(instance, cls)
        for k, v in serialized_daemons.items():
            app.daemons[k] = JSONDecoder().decode(v, Daemon)
        return app
