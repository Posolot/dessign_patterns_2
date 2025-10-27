import unittest
import json
from datetime import datetime
from Src.Logics.basic_convertor import basic_converter
from Src.Logics.datetime_convertor import datetime_converter
from Src.Logics.reference_conventor import reference_converter
from Src.Core.abstract_model  import abstact_model
from Src.Core.validator import argument_exception


class TestConverters(unittest.TestCase):

    # Тест basic_converter
    def test_basic_converter_int(self):
        # Подготовка
        conv = basic_converter()
        value = 42

        # Действие
        result = conv.convert(value)

        # Проверка
        self.assertEqual(result, {"value": 42})

    def test_basic_converter_str(self):
        # Подготовка
        conv = basic_converter()
        value = "hello"

        # Действие
        result = conv.convert(value)

        # Проверка
        self.assertEqual(result, {"value": "hello"})

    def test_basic_converter_none(self):
        # Подготовка
        conv = basic_converter()
        value = None

        # Действие и Проверка
        with self.assertRaises(argument_exception):
            conv.convert(value)


    # Тест datetime_converter
    def test_datetime_converter(self):
        # Подготовка
        conv = datetime_converter()
        dt = datetime(2025, 10, 27, 21, 30, 0)

        # Действие
        result = conv.convert(dt)

        # Проверка
        self.assertEqual(result, {"value": "2025-10-27T21:30:00"})

    def test_datetime_converter_none(self):
        # Подготовка
        conv = datetime_converter()
        dt = None

        # Действие и Проверка
        with self.assertRaises(argument_exception):
            conv.convert(dt)


    # Тест reference_converter
    class TestModel(abstact_model):
        def __init__(self, name, value):
            super().__init__()
            self.name = name
            self.value = value

    def test_reference_converter(self):
        # Подготовка
        conv = reference_converter()
        obj = self.TestModel("Test", 123)

        # Действие
        result = conv.convert(obj)

        # Проверка
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["value"], 123)

    def test_reference_converter_none(self):
        # Подготовка
        conv = reference_converter()
        obj = None

        # Действие и Проверка
        with self.assertRaises(argument_exception):
            conv.convert(obj)


if __name__ == "__main__":
    unittest.main()
