from pathlib import Path

from napoleon.core.shared.application import Application
from napoleon.core.shared.config import Configurable
from napoleon.tools.io import load_yml, save_yml
from napoleon.tools.regex import to_snake


class FileContext(Configurable):

    def _build_internal(self):
        self.log.info(f"Context ID: {self.key}")

    @classmethod
    def exist(cls, key):
        return (Application().paths.data / Path(str(key)) / Path(str(key) + ".yml")).exists()

    @classmethod
    def load(cls, key):
        return cls.deserialize(load_yml(Application().paths.data / Path(str(key)) / Path(CONTEXT_FILENAME)))

    def save(self):
        save_yml(Application().paths.data / Path(str(self.key)) / Path(CONTEXT_FILENAME), self.serialize())

    def build_context_directory(self, bucket=""):
        parents = Application().paths.data / Path(str(self.key)) / Path(to_snake(bucket))
        if not parents.exists():
            parents.mkdir(parents=True, exist_ok=True)
        return parents

    def build_context_filepath(self, stem, ext, bucket=""):
        return self.build_context_directory(bucket=bucket) / Path(to_snake(stem) + "." + ext)
