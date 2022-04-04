import importlib
import os
import signal
import sys
import time
import warnings

from napoleon.core.cmd.base import BaseCommandLine
from napoleon.core.cmd.default import CommandLine
from napoleon.core.daemon.base import BaseDaemon
from napoleon.core.log.base import BaseLogger
from napoleon.core.network.base import BaseClient, BaseInterface
from napoleon.core.path.base import BasePath
from napoleon.core.platform.base import BaseMachine
from napoleon.core.shared.config import Configurable
from napoleon.core.vault.base import BaseVault
from napoleon.decoders.json_decoder import JSONDecoder
from napoleon.properties import MutableSingleton, Instance, Map, String, PlaceHolder
from napoleon.properties.base import iter_properties
from napoleon.tools.collection import last
from napoleon.tools.io import load_yml, save_yml
from napoleon.tools.singleton import Undefined, is_define


class Application(Configurable, metaclass=MutableSingleton):

    cmd = Instance(BaseCommandLine)
    name = String("Napoleon")
    warning_filter: str = String("ignore")
    paths = Instance(BasePath)
    vault = Map(Instance(BaseVault))
    loggers = Map(Instance(BaseLogger))
    clients = Map(Instance(BaseClient))
    interfaces = Map(Instance(BaseInterface))
    daemons: dict = Map(Instance(BaseDaemon))
    platform = Instance(BaseMachine)
    _is_running = PlaceHolder()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        signal.signal(signal.SIGUSR1, self.reload)  # 10
        signal.signal(signal.SIGUSR2, self.terminate)  # 12

    def _build_internal(self):
        warnings.filterwarnings(self.warning_filter)

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
        self.shutdown()

    def shutdown(self):
        for daemon in self.daemons.values():
            daemon.shutdown()

    @classmethod
    def deserialize(cls, instance):
        """ Order matter here """
        _app = cls()
        decoder = JSONDecoder()
        for key, field in iter_properties(cls):
            part = instance.get(key, Undefined)
            if is_define(part):
                _app.update(**{key: decoder._dispatch(field, part)}) # noqa
        return _app

    @classmethod
    def configure(cls, cmd_class=CommandLine, context=Undefined):
        cmd = cmd_class.from_cmd(add_help=True)

        _context = context.copy() if is_define(context) else dict()

        _context["cwd"] = os.getcwd()
        _context["cmd"] = cmd.serialize()
        _context["env"] = dict(os.environ)

        _app = cls.from_config(cmd.template_path, cmd.config_path, _context)
        _app.cmd = cmd
        _app.platform = last(BaseMachine.__subclasses__()).from_platform()
        return _app

    @classmethod
    def load(cls, filepath):
        return cls.deserialize(load_yml(filepath))

    def dump(self, filepath):
        save_yml(filepath, self.serialize())
