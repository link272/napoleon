import argparse

from napoleon.properties import AbstractObject
from napoleon.properties import Map, List, Set, Boolean, String, Integer, Float, Decimal, UUID, DateTime, Instance
from napoleon.properties.base import iter_properties
from napoleon.tools.singleton import is_define


class BaseCommandLine(AbstractObject):

    @classmethod
    def from_cmd(cls, add_help=False):
        parser = argparse.ArgumentParser(add_help=add_help)
        cls.build_parser(parser)
        namespace, _ = parser.parse_known_args()
        base = vars(namespace)
        return cls.decode_parser(base)

    @classmethod
    def build_parser(cls, parser):
        for key, field in iter_properties(cls):
            if key == "class_name":
                continue
            _help = field.description if is_define(field.description) else None
            if isinstance(field, (String, Decimal, DateTime, UUID, Integer, Float, Boolean)):
                parser.add_argument("--" + key,
                                    metavar="",
                                    action='store',
                                    default=field.default,
                                    type=field.type,
                                    dest=key,
                                    help=_help)
            elif isinstance(field, (Map, List, Set)):
                if not isinstance(field.item_type, (String, Decimal, DateTime, UUID, Integer, Float, Boolean)):
                    RuntimeError(f"Command line container item has to be a scalar, non bytes, but is a {field}")
                parser.add_argument("--" + key,
                                    metavar="",
                                    action='store',
                                    nargs="*",
                                    default=field.default,
                                    type=field.item_type.type,
                                    dest=key,
                                    help=_help)
            elif isinstance(field, Instance):
                parser.add_argument(key,
                                    metavar="",
                                    action='store',
                                    default=None,
                                    type=str,
                                    help=_help)
                field.object_type.build_parser(parser)
            else:
                RuntimeError(f"Command line field cannot a {field}")

    @classmethod
    def decode_parser(cls, base):
        instance = {}
        for key, field in iter_properties(cls):
            if key in base and base[key] is not None:
                if isinstance(field, Map):
                    _map = dict()
                    for i in base[key]:
                        i1, i2 = i.split("=")
                        _map[i1] = field.item_type.from_string(i2)
                    instance[key] = _map
                elif isinstance(field, (Set, List)):
                    instance[key] = field.type(field.item_type.from_primitive(i) for i in base[key])
                elif isinstance(field, Instance):
                    instance[key] = field.object_type.decode_parser(base)
                else:
                    instance[key] = field.from_primitive(base[key])

        return cls(**instance)

