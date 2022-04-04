import unittest
from tests.base import TestScalar, TestContainer
from napoleon.generators.json_schema import JSONSchema


class TestJSONSchema(unittest.TestCase):

    def test_initialisation(self):
        a = TestContainer(b1=[TestScalar()], b2=["1", "2"])
        serialized_a = a.serialize()

        generator = JSONSchema(TestContainer)
        generator.validate(serialized_a)


if __name__ == '__main__':
    unittest.main()