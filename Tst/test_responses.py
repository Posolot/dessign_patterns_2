import unittest
import json
import os
import xml.etree.ElementTree as ET

from Src.Logics.response_csv import response_csv
from Src.Logics.response_json import response_json
from Src.Logics.response_markdown import response_markdown
from Src.Logics.response_xml import response_xml
from Src.Logics.factory_entities import factory_entities
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.receipt_model import receipt_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Core.response_format import response_formats
from Src.Core.validator import validator
from Src.Core.abstract_response import abstract_response


class TestResponseFormats(unittest.TestCase):
    def setUp(self):
        self.output_dir = "tests/test_output"
        os.makedirs(self.output_dir, exist_ok=True)

        # Базовые сущности
        self.group = group_model()
        self.group.name = "Основная группа"

        self.unit = range_model().create("шт", 1, None)
        self.unit.name = "Штука"

        self.nomenclature1 = nomenclature_model.create("Товар 1", self.group, self.unit)
        self.nomenclature2 = nomenclature_model.create("Товар 2", self.group, self.unit)

        self.recipe = receipt_model.create("Рецепт 1", "Описание рецепта", 1)

    def save_to_file(self, content, filename):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    # ==== CSV ====
    def test_build_nomenclature_csv_contains_fields(self):
        response = response_csv()
        data = [self.nomenclature1, self.nomenclature2]
        result = response.build("CSV", data)
        path = self.save_to_file(result, "nomenclature.csv")

        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        self.assertIn("unique_code", result)
        self.assertIn("name", result)
        self.assertIn("Товар 1", result)

    # ==== Markdown ====
    def test_build_nomenclature_markdown_valid_table(self):
        response = response_markdown()
        data = [self.nomenclature1]
        result = response.build("Markdown", data)
        path = self.save_to_file(result, "nomenclature.md")

        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        self.assertIn("| group | name | range | unique_code |", result)

    # ==== JSON ====
    def test_build_nomenclature_json_valid(self):
        response = response_json()
        data = [self.nomenclature1]
        result = response.build("Json", data)
        path = self.save_to_file(result, "nomenclature.json")

        self.assertTrue(os.path.exists(path))
        parsed = json.loads(result)
        self.assertEqual(parsed[0]["name"], "Товар 1")

    # ==== XML ====
    def test_build_nomenclature_xml_contains_tags(self):
        response = response_xml()
        data = [self.nomenclature1]
        result = response.build("XML", data)
        path = self.save_to_file(result, "nomenclature.xml")

        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        self.assertIn("<name>Товар 1</name>", result)
        ET.fromstring(result)  # Проверка валидности XML

    # ==== Factory ====
    def test_factory_creates_valid_response_instance(self):
        factory = factory_entities()
        data = [self.group]

        for fmt in ["CSV", "Json", "Markdown", "XML"]:
            with self.subTest(format=fmt):
                cls = factory.create(fmt)
                instance = cls()
                validator.validate(instance, abstract_response)
                result = instance.build(fmt, data)
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)

    # ==== Проверка JSON для разных сущностей ====
    def test_build_group_json_contains_group_name(self):
        response = response_json()
        data = [self.group]
        result = response.build("Json", data)
        parsed = json.loads(result)
        self.assertEqual(parsed[0]["name"], "Основная группа")

    def test_build_unit_json_contains_unit_data(self):
        response = response_json()
        data = [self.unit]
        result = response.build("Json", data)
        parsed = json.loads(result)
        self.assertEqual(parsed[0]["name"], "Штука")
        self.assertEqual(parsed[0]["value"], 1)

    def test_build_recipe_json_contains_recipe_data(self):
        response = response_json()
        data = [self.recipe]
        result = response.build("Json", data)
        parsed = json.loads(result)
        self.assertEqual(parsed[0]["name"], "Рецепт 1")
        # self.assertEqual(parsed[0]["description"], "Описание рецепта")

    # ==== Проверка корректности всех форматов ====
    def test_all_formats_are_valid_and_nonempty(self):
        factory = factory_entities()
        formats = ["csv", "markdown", "json", "xml"]
        entities = {
            "groups": [self.group],
            "units": [self.unit],
            "nomenclature": [self.nomenclature1, self.nomenclature2],
            "recipes": [self.recipe]
        }

        for entity_name, items in entities.items():
            for fmt in formats:
                with self.subTest(entity=entity_name, format=fmt):
                    cls = factory.create(fmt)
                    instance = cls()
                    result = instance.build(fmt, items)
                    # if fmt == "markdown":
                    #     fmt = "md"
                    path = self.save_to_file(result, f"{entity_name}.{fmt}")
                    self.assertTrue(os.path.exists(path))
                    self.assertGreater(os.path.getsize(path), 0)
                    if fmt == "json":
                        json.loads(result)
                    elif fmt == "xml":
                        ET.fromstring(result)

if __name__ == '__main__':
    unittest.main()