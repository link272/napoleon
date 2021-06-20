from napoleon.properties import MutableSingleton, Instance, Map, String, PlaceHolder
from napoleon.core.trace import Logger
from napoleon.core.network.client import Client
from napoleon.core.storage.database import Database
from napoleon.core.utils.machine import Platform
from napoleon.core.cmd import CommandLine
from napoleon.core.utils.config import Configurable
from napoleon.core.special.path import FilePath
from napoleon.core.vault import Vault
from napoleon.core.daemon.base import Daemon
from napoleon.decoders.json_decoder import JSONDecoder
from jinja2 import Template

import sys
import importlib
import signal
import warnings
import time
from pathlib import Path
import yaml


class Application(Configurable, metaclass=MutableSingleton):

    name = String("Napoleon")
    tracers = Map(Instance(Logger))
    paths = Instance(FilePath())
    clients = Map(Instance(Client))
    databases = Map(Instance(Database))
    platform = Instance(Platform, default=Platform.from_platform)
    cmd = Instance(CommandLine)
    vault = Instance(Vault)
    warning_filter: str = String("ignore")
    daemons: dict = Map(Instance(Daemon))
    _is_running = PlaceHolder()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        signal.signal(signal.SIGUSR1, self.reload)  # 10
        signal.signal(signal.SIGUSR2, self.terminate)  # 12

    def _build_internal(self):
        warnings.filterwarnings(self.warning_filter)
        for path in self.paths.values():
            if not path.exists():
                path.mkdir(parents=True)

    def reload(self, signum, frame): # noqa
        self.log.info(f"Receiving signal {signum}, reloading")
        for name, module in sys.modules.copy().items():
            if name.startswith("core"):
                importlib.reload(module)

    def terminate(self, signum, frame): # noqa
        self.log.info(f"Receiving signal {signum}, stopping")
        self._is_running = False

    def run(self):
        for daemon in self.daemons.values():
            daemon.start()
        self._is_running = True
        while self._is_running:
            try:
                time.sleep(2)
            except KeyboardInterrupt:
                self._is_running = False
        for daemon in self.daemons.values():
            daemon.shutdown()

    @classmethod
    def deserialize(cls, instance):
        serialized_daemons = instance.pop("daemons", {})
        app = JSONDecoder().decode(instance, cls)
        for k, v in serialized_daemons.items():
            app.daemons[k] = JSONDecoder().decode(v, Daemon)
        return app

    @classmethod
    def from_cmd(cls, cmd_class=CommandLine):
        cmd = cmd_class.from_cmd(add_help=True)

        context = {"cwd": str(Path.cwd())} # noqa

        context["cmd"] = cmd.serialize()

        template = Template(cmd.paths_config_file.read_text())
        config = template.render(context)

        context["paths"] = yaml.safe_load(config)
        context["vault"] = Vault.from_base64_key(Path(context["paths"].get("vault").read_text()))

        app = cls.from_config(cls.__name__.lower(), context)
        return app
