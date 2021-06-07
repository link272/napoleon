from napoleon.properties import UUID, DateTime, Set, String, Instance, PlaceHolder, Boolean
from napoleon.core.paths import PATHS, Path
from napoleon.core.utils.config import Configurable
from napoleon.tools.regex import to_snake
from napoleon.core.tasks.graph_machine import GraphMachine
import uuid
import pendulum
import threading


class Context(Configurable):

    key = UUID(default=uuid.uuid4)
    created_at = DateTime(pendulum.now)
    tags: set = Set(String())
    resume_action = String()
    logger_name = String("default")
    engine: GraphMachine = Instance(GraphMachine)
    error_msg = String()
    is_threaded = Boolean()
    thread = PlaceHolder()

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
        parents = PATHS.data / Path(str(self.key)) / Path(to_snake(bucket))
        if not parents.exists():
            parents.mkdir(parents=True, exist_ok=True)
        return parents

    def build_context_filepath(self, stem, ext, bucket=""):
        return self.build_context_directory(bucket=bucket) / Path(to_snake(stem) + "." + ext)

    def run(self):
        status = False
        if self.is_threaded:
            self.thread = threading.Thread(target=self.engine.execute, args=(self,))
            self.thread.start()
            status = self.thread.is_alive()
        else:
            self.engine.execute(self)
        return status
