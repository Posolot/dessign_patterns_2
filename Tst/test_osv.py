import unittest
from Src.start_service import start_service
from Src.Models.transaction_model import transaction_model
from Src.Core.common import common
from Src.Logics.response_json import response_json
from datetime import datetime

class TestTransactionModel(unittest.TestCase):

    def setUp(self):
        # Инициализация start_service без блокировки
        self.service = start_service()
        self.service.file_name = "Docs/settings.json"
        self.service.load()
        self.data = self.service.data

        tx_list = self.data.get("transaction_model", [])
        self.tx = tx_list[0] if tx_list else None

    def test_transaction_to_dict(self):
        # Подготовка
        # Действие
        tx_dict = self.tx.to_dict()
        # Проверка
        self.assertIn("id", tx_dict)
        self.assertIn("date_tr", tx_dict)
        self.assertIn("quantity", tx_dict)
        self.assertIn("storage_id", tx_dict)
        self.assertIn("nomenclature_id", tx_dict)
        self.assertIn("range_id", tx_dict)


    def test_osv_report_creation(self):
        # Подготовка
        date_start = datetime.strptime("2025-01-01", "%Y-%m-%d")
        date_end = datetime.strptime("2025-02-28", "%Y-%m-%d")
        # Берем один склад из данных
        storage_ids = [s.unique_code for s in self.data.get("storage_model", [])]
        self.assertTrue(storage_ids, "Нет складов для теста")
        storage_id = storage_ids[0]

        # Действие: формируем отчет ОСВ вручную
        transactions = self.data.get("transaction_model", [])
        nomenclatures = self.data.get("nomenclature_model", [])
        ranges = {r.unique_code: r for r in self.data.get("range_model", [])}

        result = {}
        for n in nomenclatures:
            n_name = getattr(n, "name", "Неизвестно")
            range_id = getattr(n, "range_id", None)  # безопасно
            unit = getattr(ranges.get(range_id), "name", "—") if range_id else "—"
            key = (n.unique_code, unit)
            result[key] = {
                "nomenclature": n_name,
                "unit": unit,
                "start_balance": 0.0,
                "incoming": 0.0,
                "outgoing": 0.0,
                "end_balance": 0.0
            }

        for t in transactions:
            if not isinstance(t, transaction_model):
                continue
            if not t.storage or t.storage.unique_code != storage_id:
                continue
            if not (date_start <= t.date_tr <= date_end):
                continue

            n = t.nomenclature
            r = t.range
            unit = getattr(r, "name", "—") if r else "—"
            key = (n.unique_code, unit)

            if key not in result:
                # создаём запись, если её нет
                result[key] = {
                    "nomenclature": getattr(n, "name", "Неизвестно"),
                    "unit": unit,
                    "start_balance": 0.0,
                    "incoming": 0.0,
                    "outgoing": 0.0,
                    "end_balance": 0.0
                }

            qty = t.quantity * (1.0 / (r.value if r and hasattr(r, "value") else 1.0))
            if qty > 0:
                result[key]["incoming"] += qty
            else:
                result[key]["outgoing"] += abs(qty)

        # Конечные остатки
        for item in result.values():
            item["end_balance"] = item["start_balance"] + item["incoming"] - item["outgoing"]

        # Проверка
        self.assertTrue(result, "Отчет ОСВ пустой")
        for item in result.values():
            self.assertIn("nomenclature", item)
            self.assertIn("unit", item)
            self.assertIn("start_balance", item)
            self.assertIn("incoming", item)
            self.assertIn("outgoing", item)
            self.assertIn("end_balance", item)

if __name__ == "__main__":
    unittest.main()
