from napoleon.properties import UUID, DateTime, Set, String, Instance, PlaceHolder, Boolean
from napoleon.core.utils.config import Configurable
from napoleon.tools.regex import to_snake
from napoleon.core.tasks.graph_machine import GraphMachine
from napoleon.core.application import Application
import uuid
import pendulum
from pathlib import Path


class Context(Configurable):

    key = UUID(default=uuid.uuid4)
    created_at = DateTime(pendulum.now)
    tags: set = Set(String())
    resume_action = String()
    logger_name = String("default")
    engine: GraphMachine = Instance(GraphMachine)
    error_msg = String()

    def _build_internal(self):
        self.log.info(f"Context ID: {self.key}")

    @classmethod
    def exist(cls, key):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    @classmethod
    def load(cls, key):
        raise NotImplementedError

    def build_context_directory(self, bucket=""):
        parents = Application().paths["data"] / Path(str(self.key)) / Path(to_snake(bucket))
        if not parents.exists():
            parents.mkdir(parents=True, exist_ok=True)
        return parents

    def build_context_filepath(self, stem, ext, bucket=""):
        return self.build_context_directory(bucket=bucket) / Path(to_snake(stem) + "." + ext)

    def run(self):
        return self.engine.execute(self)
