import uuid

import pendulum

from napoleon.core.log.property import Log
from napoleon.core.shared.config import Configurable
from napoleon.core.task.graph_machine import GraphMachine
from napoleon.properties import UUID, DateTime, Set, String, Instance


class BaseContext(Configurable):
    """
    A context goes from a graph platform action to another, it contains all the data
    """

    key = UUID(default=uuid.uuid4)
    created_at = DateTime(default=pendulum.now)
    tags: set = Set(String())
    resume_action = String()
    log = Log()
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

    def run(self):
        return self.engine.execute(self)
