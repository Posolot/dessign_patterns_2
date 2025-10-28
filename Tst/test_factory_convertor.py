import unittest
from datetime import datetime, date
from types import SimpleNamespace
from Src.Core.validator import argument_exception
from Src.Logics.factory_convertor import factory_conventor
from Src.Models.range_model import range_model

class test_convert_factory(unittest.TestCase):

    def setUp(self):
        self.factory = factory_conventor()

    # Простейшие типы
    def test_basic_types(self):
        self.assertEqual(self.factory.create(42), {"value": 42})
        self.assertEqual(self.factory.create(3.14), {"value": 3.14})
        self.assertEqual(self.factory.create("hello"), {"value": "hello"})
        self.assertEqual(self.factory.create(True), {"value": True})

    # Дата и время
    def test_datetime(self):
        dt = datetime(2025, 10, 27, 14, 5, 30)
        self.assertEqual(self.factory.create(dt), {"value": "2025-10-27T14:05:30"})

        d = date(2025, 10, 27)
        self.assertEqual(self.factory.create(d), {"value": "2025-10-27T00:00:00"})

    # Ссылочные объекты
    def test_reference_object(self):
        obj = SimpleNamespace(id=1, name="Test")
        self.assertEqual(self.factory.create(obj), {"id": 1, "name": "Test"})

    # Списки
    def test_list_of_mixed_types(self):
        dt = datetime(2025, 10, 27, 14, 5, 30)
        obj = SimpleNamespace(id=1, name="Test")
        data = [42, "abc", dt, obj]

        expected = [
            {"value": 42},
            {"value": "abc"},
            {"value": "2025-10-27T14:05:30"},
            {"id": 1, "name": "Test"}
        ]
        self.assertEqual(self.factory.create(data), expected)

    # Проверка None
    def test_none_raises(self):
        with self.assertRaises(argument_exception):
            self.factory.create(None)


if __name__ == "__main__":
    unittest.main()