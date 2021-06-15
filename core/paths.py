from napoleon.core.special.path import FilePath
from napoleon.properties import AbstractObject, MutableSingleton, iter_properties
from napoleon.tools.regex import to_snake
from napoleon.tools.singleton import exist
from jinja2 import Template
from pathlib import Path
import yaml
import uuid
import shutil


class Paths(AbstractObject, metaclass=MutableSingleton):

    root = FilePath(default=Path(__file__).parent.parent, description="source directory")
    templates = FilePath(description="templates directory")
    static = FilePath(description="static directory")
    data: Path = FilePath(description="data directory")
    temporary = FilePath(default=Path("/tmp/" + str(uuid.uuid4())), description="temporary directory")
    log = FilePath(description="log directory")
    config = FilePath(description="config directory")
    docs = FilePath(description="docs directory")
    vault = FilePath(description="secret filepath")

    def _build_internal(self):
        for key, field in iter_properties(self.__class__):
            if isinstance(field, FilePath):
                _path = getattr(self, key)
                if exist(_path) and not _path.exists():
                    _path.mkdir(parents=True)

    @classmethod
    def from_config(cls, path, context):
        template = Template(path.read_text())
        context["cwd"] = str(Path.cwd())
        config = template.render(context)
        return cls.deserialize(yaml.safe_load(config))

    def build_data_filepath(self, stem, ext, bucket=""):
        parents = self.data / Path(to_snake(bucket))
        if not parents.exists():
            parents.mkdir(parents=True, exist_ok=True)
        return parents / Path(to_snake(stem) + "." + ext)
