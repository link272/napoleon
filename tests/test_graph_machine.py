import unittest
from napoleon.core.task.base import BaseContext


class TestContext(BaseContext):

    @classmethod
    def exist(cls, key):
        return False

    def save(self):
        pass

    @classmethod
    def load(cls, key):
        raise NotImplementedError


class TestGraphMachine(unittest.TestCase):

    def test_run(self):
        config = {
            "actions": [
                {
                    "config": {
                        "test": "ok1"
                    },
                    "executable": "tests.tasks.task.SimpleAction1",
                    "name": "A1"
                },
                {
                    "config": {
                        "test": "ok2"
                    },
                    "executable": "tests.tasks.task.SimpleAction1",
                                  "name": "A2"
                }

            ],
            "transitions": [
                {
                    "previous": "A1",
                    "next": "A2"
                }
            ]

        }
        c = TestContext.deserialize({"engine": config})
        c.run()
        self.assertEqual(c.error_msg, "ok2")
