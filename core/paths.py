from napoleon.core.special.path import FilePath
from napoleon.properties import AbstractObject, MutableSingleton, iter_properties
from napoleon.core.cmd import CMD
from napoleon.tools.regex import to_snake
from napoleon.tools.singleton import exist
from jinja2 import Template
from pathlib import Path
import yaml

ROOT_DIRECTORY = Path(__file__).parent.parent


class Paths(AbstractObject, metaclass=MutableSingleton):

    root = FilePath(default=ROOT_DIRECTORY, description="source directory")
    templates = FilePath(default=ROOT_DIRECTORY / Path("templates"), description="templates directory")
    static = FilePath(default=ROOT_DIRECTORY / Path("static"), description="static directory")
    data: Path = FilePath(default=Path.cwd(), description="data directory")
    temporary = FilePath(default=Path("/tmp"), description="temporary directory")
    log = FilePath(default=Path.cwd() / Path("logs"), description="log directory")
    config = FilePath(default=ROOT_DIRECTORY / Path("config"), description="config directory")
    docs = FilePath(default=ROOT_DIRECTORY / Path("docs"), description="docs filepath")

    def _build_internal(self):
        for key, field in iter_properties(self.__class__):
            if isinstance(field, FilePath):
                _path = getattr(self, key)
                if exist(_path):
                    _path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_config_filepath(cls, filepath, context):
        t = Template(filepath.read_text())
        context["CWD_DIR"] = str(Path.cwd())
        context["ROOT_DIR"] = str(ROOT_DIRECTORY)
        config = t.render(context)
        return cls.deserialize(yaml.safe_load(config))

    def build_data_filepath(self, stem, ext, bucket=""):
        parents = self.data / Path(to_snake(bucket))
        if not parents.exists():
            parents.mkdir(parents=True, exist_ok=True)
        return parents / Path(to_snake(stem) + "." + ext)


if exist(CMD.paths_config_file):
    PATHS = Paths.from_config_filepath(CMD.paths_config_file, CMD.serialize())
else:
    PATHS = Paths()
