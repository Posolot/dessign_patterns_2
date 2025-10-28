import json
import unittest
from datetime import datetime, date

from Src.Logics.basic_convertor import basic_converter
from Src.Logics.datetime_convertor import datetime_converter
from Src.Logics.reference_conventor import reference_converter
from Src.Logics.structure_convertor import structure_converter
from Src.Logics.factory_convertor import factory_convertor
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import argument_exception


class TestConverters(unittest.TestCase):

    # region BASIC CONVERTER
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

    def test_basic_converter_none_raises(self):
        # Подготовка
        conv = basic_converter()
        value = None

        # Действие и Проверка
        with self.assertRaises(argument_exception):
            conv.convert(value)
    # endregion

    # region DATETIME CONVERTER
    def test_datetime_converter_valid(self):
        # Подготовка
        conv = datetime_converter()
        dt = datetime(2025, 10, 27, 21, 30, 0)

        # Действие
        result = conv.convert(dt)

        # Проверка
        self.assertEqual(result, {"value": "2025-10-27T21:30:00"})

    def test_datetime_converter_date_converts_to_datetime(self):
        # Подготовка
        conv = datetime_converter()
        d = date(2025, 10, 27)

        # Действие
        result = conv.convert(datetime.combine(d, datetime.min.time()))

        # Проверка
        self.assertEqual(result, {"value": "2025-10-27T00:00:00"})

    def test_datetime_converter_none_raises(self):
        # Подготовка
        conv = datetime_converter()
        dt = None

        # Действие и Проверка
        with self.assertRaises(argument_exception):
            conv.convert(dt)
    # endregion

    # region REFERENCE CONVERTER
    class TestModel(abstact_model):
        def __init__(self, name, value):
            super().__init__()
            self.name = name
            self.value = value

    def test_reference_converter_valid(self):
        # Подготовка
        conv = reference_converter()
        obj = self.TestModel("Test", 123)

        # Действие
        result = conv.convert(obj)

        # Проверка
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["value"], 123)

    def test_reference_converter_none_raises(self):
        # Подготовка
        conv = reference_converter()

        # Действие и Проверка
        with self.assertRaises(argument_exception):
            conv.convert(None)
    # endregion

    # region STRUCTURE CONVERTER
    def test_structure_converter_list(self):
        # Подготовка
        factory = factory_convertor()
        conv = structure_converter(factory)
        value = [1, "test", True]

        # Действие
        result = conv.convert(value)

        # Проверка
        self.assertEqual(result, [
            {"value": 1},
            {"value": "test"},
            {"value": True}
        ])

    def test_structure_converter_dict(self):
        # Подготовка
        factory = factory_convertor()
        conv = structure_converter(factory)
        value = {"a": 1, "b": "hello"}

        # Действие
        result = conv.convert(value)

        # Проверка
        self.assertEqual(result, {
            "a": {"value": 1},
            "b": {"value": "hello"}
        })


    def test_structure_converter_none_raises(self):
        # Подготовка
        factory = factory_convertor()
        conv = structure_converter(factory)

        # Действие и Проверка
        with self.assertRaises(argument_exception):
            conv.convert(None)
    # endregion

    # region FACTORY CONVERTOR
    def test_factory_convertor_basic_types(self):
        # Подготовка
        factory = factory_convertor()

        # Действие
        result_int = factory.create(10)
        result_str = factory.create("hi")

        # Проверка
        self.assertEqual(result_int, {"value": 10})
        self.assertEqual(result_str, {"value": "hi"})

    def test_factory_convertor_datetime(self):
        # Подготовка
        factory = factory_convertor()
        dt = datetime(2025, 10, 28, 14, 30)

        # Действие
        result = factory.create(dt)

        # Проверка
        self.assertEqual(result, {"value": "2025-10-28T14:30:00"})

    def test_factory_convertor_structure(self):
        # Подготовка
        factory = factory_convertor()
        data = {"a": 1, "b": [2, 3]}

        # Действие
        result = factory.create(data)

        # Проверка
        self.assertEqual(result, {
            "a": {"value": 1},
            "b": [{"value": 2}, {"value": 3}]
        })

    def test_factory_convertor_reference(self):
        # Подготовка
        factory = factory_convertor()
        obj = self.TestModel("Ref", 99)

        # Действие
        result = factory.create(obj)

        # Проверка
        self.assertEqual(result["name"], "Ref")
        self.assertEqual(result["value"], 99)

    def test_factory_convertor_none_raises(self):
        # Подготовка
        factory = factory_convertor()

        # Действие и Проверка
        with self.assertRaises(argument_exception):
            factory.create(None)
    # endregion


if __name__ == "__main__":
    unittest.main()
