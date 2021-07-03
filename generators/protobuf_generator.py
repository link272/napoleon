import hashlib
from ..properties import Instance, List, Set, Map, Integer, Float, DateTime, Boolean, String, Bytes, SlottedType, Blob, JSON
from ..properties.base import recurse_iter_properties, PlaceHolder
from ..tools.singleton import Nothing, exist, is_define, Undefined
from ..properties.objects import AbstractObject
import subprocess
import importlib
import sys
from pathlib import Path


class ProtobufModel(object):

    base_tags = {
        "id": "1",
        "data": "2",
        "key": "3",
        "value": "4",
        "name": "5",
        "class_name": "6",
        "status": "7",
        "code": "8",
        "error": "9",
        "response": "10",
        "timestamp": "11",
        "token": "12",
    }

    def __init__(self, name="artemis"):
        self.name = name
        self.visited_classes = set()
        self.content = []
        self.map_classes = {}
        self.module = Undefined

    def get_message_type(self, name):
        if is_define(self.module):
            raise RuntimeError("Generation is not done yet")
        return getattr(self.module, name)

    def _generate_proto_tag(self, key, used):
        if key in self.base_tags:
            tag = self.base_tags.get(key)
        else:
            tag = str(int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2047 - 16) + 16)

        if tag in used:
            raise ValueError(f"Generated protobuf tag: {tag} is duplicated from key: {key}")
        else:
            used.add(tag)
        return tag

    def generate(self, cls, directory):
        self.content.append("syntax = \"proto3\";")
        self.content.append(f"package {self.name};")
        self.content.append("import \"google/protobuf/timestamp.proto\";")
        self._dispatch(Instance(cls))
        filepath = directory / Path(f"{self.name}.proto")
        filepath.write_text("\n".join(self.content))
        subprocess.run(f"protoc --proto_path={directory} --python_out={directory} {filepath}", shell=True)
        sys.path.append(str(directory))
        self.module = importlib.import_module(self.name + "_pb2")

    def _build_instance_schema(self, _property):
        name = _property.object_type.__name__
        if name not in self.visited_classes:
            self.visited_classes.add(name)
            msg = list()
            msg.append(" ".join(("message", name, "{")))
            used = set()
            for key, _prop in recurse_iter_properties(_property.object_type):
                tag = self._generate_proto_tag(key, used)
                _type = self._dispatch(_prop)
                if exist(_type):
                    field = "".join(["    ", _type, " ", key, " = ", tag, ";"])
                    msg.append(field)
            msg.append("}")
            protobuf_schema = "\n".join(msg)
            self.content.append(protobuf_schema)
        return name

    def _dispatch(self, _property):
        if isinstance(_property, Instance):
            name = _property.object_type.__name__
            if name not in self.visited_classes:
                _type = self._build_instance_schema(_property)
            _type = name
        elif isinstance(_property, (List, Set)):
            _type = "repeated " + self._dispatch(_property.item_type)
        elif isinstance(_property, Map):
            _type = self._build_mapping_type(_property)
        elif isinstance(_property, Integer):
            _type = "int64" if is_define(_property.minimum) and _property.minimum > 0 else "sint64" # noqa
        elif isinstance(_property, Float):
            _type = "double"
        elif isinstance(_property, DateTime):
            _type = "google.protobuf.Timestamp"
        elif isinstance(_property, Boolean):
            _type = "bool"
        elif isinstance(_property, String):
            _type = "string"
        elif isinstance(_property, (Blob, JSON, Bytes)):
            _type = "bytes"
        elif isinstance(_property, PlaceHolder):
            _type = Nothing
        else:
            raise RuntimeError(f"{_property} is not implemented")
        return _type

    def _build_mapping_type(self, _property):
        kv_name = str(_property.item_type) + "Map"
        if kv_name not in self.map_classes:
            self.map_classes[kv_name] = (
                SlottedType(kv_name, (AbstractObject,), {"key": String(), "value": _property.item_type}),
                _property)
        return self._dispatch(List(Instance(self.map_classes[kv_name][0])))
