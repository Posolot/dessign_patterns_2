import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Any

from Src.Logics.osv_service import OSVReportService
from Src.Models.settings_model import settings_model
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.factory_convertor import factory_convertor
from Src.Core.abstract_logic import abstract_logic
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
class BlockPeriodCalculator(abstract_logic):

    def __init__(self, osv_service: OSVReportService, storage_file: str = ""):
        self.osv_service = osv_service
        self.saved_turnovers: Dict[Tuple[str, Optional[str]], Dict[str, Any]] = {}
        self.converter = factory_convertor()  # как в OSVReportService
        self.__file_name = ""
        observe_service.add(self)

        if storage_file:
            self.file_name = storage_file

    # ---------------------- FILE NAME -----------------------
    def handle(self, event: str, params):
        """
        Обработка уведомлений от observe_service.

        Реагируем на:
          - changed_block_datetime  -> пересчитать сохранённые обороты (всё до новой даты блокировки)
          - add_new_object, change_object, object_deleted -> выполнить пересчёт оборотов (чтобы учесть новые/изменённые/удалённые объекты)
        При успешном пересчёте — сохраняем (если file_name настроен).
        """
        super().handle(event, params)

        try:
            if event == event_type.changed_block_datetime():
                self.calculate_turnover_until_block()
                self.save()

            elif event in (
                    event_type.add_new_object(),
                    event_type.change_object(),
                    event_type.object_deleted()
            ):
                self.calculate_turnover_until_block()
                self.save()

            else:
                return

        except Exception as ex:
            try:
                self.set_exception(ex)
            except Exception:
                pass
            raise
    @property
    def file_name(self) -> str:
        return self.__file_name

    @file_name.setter
    def file_name(self, value: str):
        full = os.path.abspath(value)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if not os.path.exists(full):
            with open(full, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)
        self.__file_name = full

    # ---------------------- AGGREGATION -----------------------

    def _make_key(self, rec: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        n = rec.get("nomenclature")
        u = rec.get("unit")
        nid = getattr(n, "unique_code", None) if not isinstance(n, dict) else n.get("unique_code")
        uid = getattr(u, "unique_code", None) if not isinstance(u, dict) else u.get("unique_code")
        return nid, uid

    def _aggregate(self, lst: List[Dict[str, Any]]) -> Dict[Tuple[str, Optional[str]], Dict[str, Any]]:
        result = {}
        for rec in lst:
            key = self._make_key(rec)
            if key[0] is None:
                continue

            incoming = float(rec.get("incoming", 0) or 0)
            outgoing = float(rec.get("outgoing", 0) or 0)
            start_balance = float(rec.get("start_balance", 0) or 0)

            # нормализуем nomenclature и unit через converter
            nomenclature = rec.get("nomenclature")
            unit = rec.get("unit")
            if not isinstance(nomenclature, dict):
                nomenclature = self.converter.create(nomenclature)
            if unit and not isinstance(unit, dict):
                unit = self.converter.create(unit)

            if key not in result:
                result[key] = {
                    "nomenclature": nomenclature,
                    "unit": unit,
                    "start_balance": start_balance,
                    "incoming": incoming,
                    "outgoing": outgoing
                }
            else:
                result[key]["incoming"] += incoming
                result[key]["outgoing"] += outgoing

        return result

    def _merge(self, base: Dict, extra: Dict) -> Dict:
        for key, v in extra.items():
            if key in base:
                base[key]["incoming"] += v.get("incoming", 0)
                base[key]["outgoing"] += v.get("outgoing", 0)
            else:
                base[key] = v
        return base

    # ---------------------- LOAD / SAVE -----------------------

    def load(self) -> bool:
        if not self.__file_name:
            return False

        try:
            with open(self.__file_name, "r", encoding="utf-8") as f:
                data = json.load(f)

            result = {}
            for item in data:
                n = item.get("nomenclature")
                u = item.get("unit")
                nid = n.get("unique_code") if isinstance(n, dict) else None
                uid = u.get("unique_code") if isinstance(u, dict) else None

                if nid is None:
                    continue

                result[(nid, uid)] = {
                    "nomenclature": n,
                    "unit": u,
                    "start_balance": item.get("start_balance", 0),
                    "incoming": item.get("incoming", 0),
                    "outgoing": item.get("outgoing", 0)
                }

            self.saved_turnovers = result
            return True
        except:
            return False

    def save(self) -> bool:
        """
        Сохраняет данные с сериализацией через converter,
        как в OSVReportService.
        """
        if not self.__file_name:
            return False

        try:
            dto_list = []
            for rec in self.saved_turnovers.values():
                dto = {
                    "nomenclature": rec["nomenclature"] if isinstance(rec["nomenclature"], dict)
                    else self.converter.create(rec["nomenclature"]),
                    "unit": rec["unit"] if isinstance(rec["unit"], dict)
                    else (self.converter.create(rec["unit"]) if rec["unit"] else None),
                    "start_balance": rec["start_balance"],
                    "incoming": rec["incoming"],
                    "outgoing": rec["outgoing"]
                }
                dto_list.append(dto)

            with open(self.__file_name, "w", encoding="utf-8") as f:
                json.dump(dto_list, f, ensure_ascii=False)

            return True
        except:
            return False

    # ---------------------- MAIN LOGIC -----------------------

    def calculate_turnover_until_block(self, storage_id=None, dto=None) -> List[Dict[str, Any]]:
        block = settings_model.get_block_period().strftime("%Y-%m-%d")
        data = self.osv_service.generate("1900-01-01", block, storage_id, dto)
        self.saved_turnovers = self._aggregate(data)
        return list(self.saved_turnovers.values())

    def calculate_balance(self, date_end: datetime, storage_id=None, dto=None) -> List[Dict[str, Any]]:
        block = settings_model.get_block_period()
        block_end = block.strftime("%Y-%m-%d")
        after = (block + timedelta(days=1)).strftime("%Y-%m-%d")

        before = self._aggregate(self.osv_service.generate("1900-01-01", block_end, storage_id, dto))
        after_map = self._aggregate(self.osv_service.generate(after, date_end.strftime("%Y-%m-%d"), storage_id, dto))

        merged = self._merge(before, after_map)

        result = []
        for rec in merged.values():
            rec["end_balance"] = rec["start_balance"] + rec["incoming"] - rec["outgoing"]
            result.append(rec)

        return result
