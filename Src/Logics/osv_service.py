from datetime import datetime
from fastapi import HTTPException
from Src.Models.transaction_model import transaction_model
from Src.Logics.factory_convertor import factory_convertor


class OSVReportService:
    """
    Сервис формирования отчёта "Оборотно-сальдовая ведомость" (ОСВ)
    по складу за указанный период.
    """

    def __init__(self, start_service_instance):
        self.start_service = start_service_instance
        self.converter = factory_convertor()

    def generate(self, date_start: str, date_end: str, storage_id: str):
        # 🔹 Проверяем корректность дат
        try:
            dt_start = datetime.strptime(date_start, "%Y-%m-%d")
            dt_end = datetime.strptime(date_end, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты, нужен YYYY-MM-DD")

        data = self.start_service.data
        transactions = data.get("transaction_model", [])
        nomenclatures = data.get("nomenclature_model", [])

        report = {}

        # 🔹 Инициализация отчёта по всем номенклатурам
        for n in nomenclatures:
            unit_obj = getattr(n, "range", None)
            key = (n.unique_code, getattr(unit_obj, "unique_code", None))

            report[key] = {
                "start_balance": 0.0,
                "nomenclature": self.converter.create(n),
                "unit": self.converter.create(unit_obj) if unit_obj else None,
                "incoming": 0.0,
                "outgoing": 0.0,
                "end_balance": 0.0
            }

        # 🔹 Обработка транзакций
        for t in transactions:
            if not isinstance(t, transaction_model):
                continue
            if not t.storage or getattr(t.storage, "unique_code", None) != storage_id:
                continue
            if not (dt_start <= t.date_tr <= dt_end):
                continue

            n = t.nomenclature
            r = t.range
            key = (n.unique_code, getattr(r, "unique_code", None))

            if key not in report:
                report[key] = {
                    "start_balance": 0.0,
                    "nomenclature": self.converter.create(n),
                    "unit": self.converter.create(r) if r else None,
                    "incoming": 0.0,
                    "outgoing": 0.0,
                    "end_balance": 0.0
                }

            qty = t.quantity * (1.0 / (getattr(r, "value", 1.0) if r else 1.0))
            if qty > 0:
                report[key]["incoming"] += qty
            else:
                report[key]["outgoing"] += abs(qty)

        # 🔹 Итоговые остатки
        for item in report.values():
            item["end_balance"] = item["start_balance"] + item["incoming"] - item["outgoing"]

        return list(report.values())