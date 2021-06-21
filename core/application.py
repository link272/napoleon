from napoleon.properties import MutableSingleton, Instance, Map, String, PlaceHolder, AbstractObject
from napoleon.core.abstract import AbstractVault, AbstractPlateform, AbstractCommandLine, AbstractTracer, \
    AbstractClient, AbstractDatabase, AbstractInterface, AbstractDaemon

from napoleon.core.utils.config import Configurable
from napoleon.core.utils.cmd import CommandLine
from napoleon.core.special.path import FilePath
from napoleon.decoders.json_decoder import JSONDecoder
from napoleon.tools.singleton import Undefined, is_define
from napoleon.properties.base import iter_properties
from napoleon.tools.io import load_yml, save_yml
from napoleon.tools.collection import first

import sys
import importlib
import signal
import warnings
import time
from pathlib import Path


class Application(Configurable, metaclass=MutableSingleton):

    cmd = Instance(AbstractCommandLine)
    name = String("Napoleon")
    warning_filter: str = String("ignore")
    paths = Map(FilePath())
    vault = Instance(AbstractVault)
    tracers = Map(Instance(AbstractTracer))
    clients = Map(Instance(AbstractClient))
    databases = Map(Instance(AbstractDatabase))
    interfaces = Map(Instance(AbstractInterface))
    daemons: dict = Map(Instance(AbstractDaemon))
    platform = Instance(AbstractPlateform)
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
        """ Order matter here """
        _app = cls()
        decoder = JSONDecoder()
        for key, field in iter_properties(cls):
            part = instance.get(key, Undefined)
            if is_define(part):
                _app.update({key: decoder(field, part)})
        return _app

    @classmethod
    def configure(cls, cmd_class=CommandLine, context=Undefined):
        cmd = cmd_class.from_cmd(add_help=True)

        _context = context.copy() if is_define(context) else dict()

        _context["cwd"] = str(Path.cwd())
        _context["root"] = str(Path(__file__.parent))
        _context["cmd"] = cmd.serialize()

        _app = cls.from_config(cmd.template_path, cmd.config_path, _context)
        _app.cmd = cmd
        _app.plateform = first(AbstractPlateform.__subclasses__()).from_platform()
        return _app

    @classmethod
    def load(cls, filepath):
        return cls.deserialize(load_yml(filepath))

    def dump(self, filepath):
        save_yml(filepath, self.serialize())


app = Application()
