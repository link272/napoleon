import unittest
from napoleon import Application
from napoleon.core.cmd.base import BaseCommandLine
from napoleon.core.cmd.default import CommandLine
from napoleon import Decimal, Integer, Instance, String
from pathlib import Path
from unittest import mock
import argparse
import decimal
from tests.base import TestInstance, TestInstanceChild1, TestInstanceChild2


class TestSubCommand(BaseCommandLine):

    a6 = String()


class TestCommandLine(CommandLine):

    a3 = Decimal()
    a4 = Integer()
    a5 = Instance(TestSubCommand)

    @classmethod
    @mock.patch(
        'argparse.ArgumentParser.parse_known_args',
        return_value=(argparse.Namespace(
            config_path=Path.cwd() / Path("tests/config/custom_application.yml"),
            template_path=Path.cwd() / Path("tests/config/application.yml"),
            a3="3",
            a4="5",
            a5="a5",
            a6="test"
        ),
            None
        )
    )
    def from_cmd(cls, *args, **kwargs):
        return super().from_cmd(add_help=True)


class TestApplication(unittest.TestCase):

    def test_initialization(self):
        a = Application.configure(cmd_class=TestCommandLine)
        a.shutdown()

    def test_cmd(self):
        a = TestCommandLine.from_cmd()
        self.assertEqual(a.a3, decimal.Decimal('3'))
        self.assertEqual(a.a4, 5)
        self.assertEqual(a.a5.a6, "test")

    def test_config(self):
        app = Application.configure(cmd_class=TestCommandLine)

        test1 = {
            'c2': 'test_server'
        }

        field = Instance(TestInstance)
        class1 = field.infer_class(test1)
        self.assertEqual(class1, TestInstanceChild1)

        instance1 = class1(**test1)
        self.assertEqual(instance1.c2.scheme, "http")

        instance2 = TestInstanceChild2.deserialize({"c4": 'gAAAAABiR2COVX68v84GPMilkTlSuCi7AXvDvv46DhabZW-cvWAG0aH5xAGKdv_\
            HmD0zS3mlgJlTyAYgy2VoGv-nECXt2juac4MKLItJuX7O5f157EAZm44='})
        self.assertEqual(instance2.c4, "myverysecretpassword")

    def test_state_decorator(self):

        app = Application.configure(cmd_class=TestCommandLine)

        a1 = TestInstance()
        try:
            a1.checkpoint_method()
        except Exception as e:
            pass
        result = a1.checkpoint_method()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
