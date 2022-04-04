import json
import uuid
from pathlib import Path

from napoleon.core.decorator.base import MethodWrapper
from napoleon.core.decorator.property import MethodDecorator
from napoleon.core.shared.application import Application
from napoleon.properties import UUID, JSON


class BaseCheckpoint(MethodWrapper):

    context: dict = JSON()

    def exist(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def save(self, json_string):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        result = None
        if self.exist():
            self.context = json.loads(self.load())
        try:
            result = self.method(*args, **kwargs)
        except Exception as e:
            if self.context:
                self.save(json.dumps(self.context))
            raise e
        else:
            self.delete()
        finally:
            self.context.clear()
        return result


class TemporaryFileCheckpoint(BaseCheckpoint):

    key = UUID(default=uuid.uuid4)

    def delete(self):
        self.build_checkpoint_filepath().unlink(missing_ok=True)

    def build_checkpoint_filepath(self):
        return Application().paths.temporary / Path(str(self.key) + ".json")

    def exist(self):
        return self.build_checkpoint_filepath().exists()

    def load(self):
        return self.build_checkpoint_filepath().read_text()

    def save(self, json_string):
        self.build_checkpoint_filepath().write_text(json_string)


def checkpoint(save_class=TemporaryFileCheckpoint):
    def wrapper(method):
        return MethodDecorator(method,
                               BaseCheckpoint,
                               default=save_class)
    return wrapper
