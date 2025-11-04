import unittest
from datetime import datetime
from Src.start_service import start_service
from Src.Logics.osv_service import OSVReportService

class TestOSVReportService(unittest.TestCase):

    def setUp(self):
        # Подготовка: загрузка данных через start_service (без запуска сервера)
        self.service = start_service()
        self.service.file_name = "Docs/settings.json"
        self.service.load()
        self.report_service = OSVReportService(self.service)
        self.data = self.service.data

    def test_osv_basic_structure(self):
        # Подготовка
        date_start = "2025-01-01"
        date_end = "2025-02-28"
        storage_list = self.data.get("storage_model", [])
        self.assertTrue(storage_list, "Нет складов для теста")
        storage_id = storage_list[0].unique_code

        # Действие
        report = self.report_service.generate(date_start, date_end, storage_id)

        # Проверка
        self.assertIsInstance(report, list, "Ожидается список записей в отчёте")
        self.assertTrue(len(report) > 0, "Отчёт должен содержать хотя бы одну запись")
        sample = report[0]
        for key in ("nomenclature", "unit", "start_balance", "incoming", "outgoing", "end_balance"):
            self.assertIn(key, sample, f"В записи отчёта нет ключа '{key}'")

        self.assertIsInstance(sample["incoming"], (int, float))
        self.assertIsInstance(sample["outgoing"], (int, float))
        self.assertIsInstance(sample["end_balance"], (int, float))

    def test_osv_incoming_outgoing_values_for_known_items(self):
        # Подготовка
        date_start = "2025-01-01"
        date_end = "2025-02-28"
        storage_list = self.data.get("storage_model", [])
        self.assertTrue(storage_list, "Нет складов для теста")
        storage_id = storage_list[0].unique_code

        # Действие
        report = self.report_service.generate(date_start, date_end, storage_id)

        # Проверка
        # Ищем записи по уникальному коду номенклатуры (из исходных данных)
        # Ожидаем: для муки (0c101a7e...) incoming == 5 (5000 г => 5 кг), для сахара outgoing == 1 (−1000 г => 1 кг)
        flour_code = "0c101a7e-5934-4155-83a6-d2c388fcc11a"
        sugar_code = "39d9349d-28fa-4c7b-ad92-5c5fc7cf93da"

        flour_entry = next((e for e in report if e["nomenclature"].get("unique_code") == flour_code), None)
        sugar_entry = next((e for e in report if e["nomenclature"].get("unique_code") == sugar_code), None)

        self.assertIsNotNone(flour_entry, "Не найден отчёт по Пшеничной муке")
        self.assertIsNotNone(sugar_entry, "Не найден отчёт по Сахару")

        # Точные проверки (числа могут быть float)
        self.assertAlmostEqual(flour_entry["incoming"], 5.0, places=6, msg="Неверный приход для муки")
        self.assertAlmostEqual(sugar_entry["outgoing"], 1.0, places=6, msg="Неверный расход для сахара")

    def test_invalid_date_format_raises(self):
        # Подготовка
        bad_date_start = "2025/01/01"  # неверный формат
        bad_date_end = "2025-02-28"
        storage_list = self.data.get("storage_model", [])
        storage_id = storage_list[0].unique_code if storage_list else "unknown"

        # Действие / Проверка
        with self.assertRaises(Exception):
            self.report_service.generate(bad_date_start, bad_date_end, storage_id)


if __name__ == "__main__":
    unittest.main()
