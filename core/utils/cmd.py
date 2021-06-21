from napoleon.properties import String, Map, List, Set
from napoleon.core.special.path import FilePath, Path
from napoleon.properties.base import iter_properties
from napoleon.properties.scalars import Scalar
from napoleon.properties.container import Container
from napoleon.tools.singleton import is_define
from napoleon.core.abstract import AbstractCommandLine

import argparse


class CommandLine(AbstractCommandLine):

    config_path = FilePath(Path.cwd() / Path("config/application.yml"), description="env-related config file")
    template_path = FilePath(Path.cwd() / Path("templates/application.yml"), description="generic config file")
    environment = String("local")
    vars = Map(String())

    @classmethod
    def from_cmd(cls, add_help=False):
        parser = argparse.ArgumentParser(add_help=add_help)
        for key, field in iter_properties(cls):
            if key == "class_name":
                continue
            _help = field.description if is_define(field.description) else None
            if isinstance(field, Scalar):
                parser.add_argument("--" + key, metavar="", action='store', default=field.default, type=str, dest=key, help=_help)
            elif isinstance(field, Container):
                if not isinstance(field.item_type, Scalar):
                    RuntimeError(f"Command line container item has to be a scalar type {field.item_type}")
                parser.add_argument("--" + key, metavar="", action='store', nargs="*", default=[], type=str, dest=key, help=_help)
            else:
                RuntimeError(f"Command line field has to be a container or a scalar {field}")

        namespace, _ = parser.parse_known_args()
        base = vars(namespace)
        instance = {}

        for key, field in iter_properties(cls):
            if key in base and base[key] is not None:
                if isinstance(field, Map):
                    _map = dict()
                    for i in base[key]:
                        i1, i2 = i.split("=")
                        _map[i1] = field.item_type.from_string(i2)
                    instance[key] = _map
                elif isinstance(field, Set):
                    instance[key] = {field.item_type.from_string(i) for i in base[key]}
                elif isinstance(field, List):
                    instance[key] = [field.item_type.from_string(i) for i in base[key]]
                else:
                    instance[key] = field.from_string(base[key])

        return cls(**instance)
