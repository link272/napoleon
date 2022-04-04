import unittest
from tests.base import TestScalar, TestContainer, NOW


class TestProperties(unittest.TestCase):

    def test_initialisation(self):
        a = TestScalar()
        self.assertDictEqual(
            a.serialize(),
            {
                'a1': False,
                'a2': 0.5,
                'a3': 4,
                'a4': '',
                'a5': 'dGVzdA==',
                'a6': '3',
                'retryable_method': {'class_name': 'Retrier', 'max_retry': 3, 'delay': 3.0},
                'a7': NOW.isoformat(),
                'a8': None,
                'a9': {},
                'class_name': 'TestScalar'
            }
        )

    def test_copy(self):
        a1 = TestContainer(b1=[TestScalar()], b2=["1", "2"])
        a2 = a1.copy()
        self.assertEqual(a1.hash(), a2.hash())

    def test_equality(self):
        a1 = TestScalar()
        a1.a3 = 5
        a2 = TestScalar(a3=5)
        self.assertEqual(a1.hash(), a2.hash())

    def test_retry_decorator(self):
        a1 = TestScalar()
        a1.retryable_method.delay = 0.
        try:
            a1.retryable_method()
        except:
            pass
        self.assertEqual(a1.a3, 12)


if __name__ == '__main__':
    unittest.main()
