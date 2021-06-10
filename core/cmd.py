from napoleon.properties import AbstractObject, Boolean, MutableSingleton
from napoleon.core.special.hidden import HiddenString
from napoleon.core.special.path import FilePath, Path
from napoleon.tools.collection import first

from docopt import docopt

COMMAND_LINE = """Artemis
Usage:
  test.py [-c paths_config_file] [--allow_db]
  test.py --version

Options:
  -h --help
  -v --version
  -c paths_config_file --paths_config_file=paths_config_file
  -p password
  -k secret_key
  -d --allow_db"""


class CommandLine(AbstractObject, metaclass=MutableSingleton):

    paths_config_file = FilePath()
    allow_db = Boolean()
    version = Boolean()
    help = Boolean()
    secret_key = HiddenString()
    password = HiddenString("artemis")

    @classmethod
    def from_cmd(cls):
        args = dict()
        try:
            docopts = docopt(COMMAND_LINE)
        except:  # noqa
            pass
        else:
            for k, v in docopts.items():
                key = k.lstrip("-")
                if isinstance(v, list):
                    value = first(v)
                elif isinstance(v, int):
                    value = bool(v)
                else:
                    value = v
                if value:
                    args[key] = value
        return cls.deserialize(args)
