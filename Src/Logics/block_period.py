import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from Src.Logics.osv_service import OSVReportService
from Src.Models.settings_model import settings_model
from Src.Dtos.filter_dto import filter_dto


class BlockPeriodCalculator:

    def __init__(self, osv_service: OSVReportService, storage_file: str = "saved_turnovers.json"):
        self.osv_service = osv_service
        self.storage_file = storage_file
        self.saved_turnovers: Dict[Tuple[str, Optional[str]], Dict] = {}  # ключ: (nomenclature, range)
        self.load_saved_turnovers()


    def save_to_file(self):
        """Сохраняет текущие обороты в JSON файл"""
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(list(self.saved_turnovers.values()), f, default=str, ensure_ascii=False)

    def load_saved_turnovers(self):
        """Загружает обороты из файла. Если файла нет — создаёт пустой."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.saved_turnovers = {
                        (t["nomenclature"]["unique_code"], t["unit"]["unique_code"] if t["unit"] else None): t
                        for t in loaded
                    }
            except Exception:
                # Если файл пустой или повреждён, создаём пустую структуру
                self.saved_turnovers = {}
        else:
            # создаём пустой файл
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump([], f)
            self.saved_turnovers = {}


    def calculate_turnover_until_block(self, storage_id: Optional[str] = None, dto: Optional[filter_dto] = None):
        """Расчет оборотов с 1900-01-01 до даты блокировки и сохранение"""
        block_date = settings_model.get_block_period().strftime("%Y-%m-%d")

        turnovers = self.osv_service.generate(
            date_start="1900-01-01",
            date_end=block_date,
            storage_id=storage_id,
            dto=dto
        )

        self.saved_turnovers = {
            (t["nomenclature"]["unique_code"], t["unit"]["unique_code"] if t["unit"] else None): t
            for t in turnovers
        }

        self.save_to_file()  # сохраняем в файл
    def calculate_balance(self, date_end: datetime,
                          storage_id: Optional[str] = None, dto: Optional[filter_dto] = None) -> List[Dict]:
        """Расчет остатков с учетом даты блокировки"""
        block_date = settings_model.get_block_period().strftime("%Y-%m-%d")

        # 1. Берем сохраненные обороты до блокировки
        report = dict(self.saved_turnovers)

        # 2. Рассчитываем обороты с даты блокировки до date_end
        new_turnovers = self.osv_service.generate(
            date_start=block_date,
            date_end=date_end.strftime("%Y-%m-%d"),
            storage_id=storage_id,
            dto=dto
        )

        # 3. Объединяем с сохраненными
        for t in new_turnovers:
            key = (t["nomenclature"]["unique_code"], t["unit"]["unique_code"] if t["unit"] else None)
            if key in report:
                report[key]["incoming"] += t["incoming"]
                report[key]["outgoing"] += t["outgoing"]
            else:
                report[key] = t

        # 4. Считаем конечный баланс
        final_report = []
        for t in report.values():
            t["end_balance"] = t["incoming"] - t["outgoing"]
            final_report.append(t)

        return final_report
