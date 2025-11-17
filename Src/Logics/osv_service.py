# Src/Logics/osv_service.py

from datetime import datetime
from fastapi import HTTPException
from typing import Optional, Set, List

from Src.Models.transaction_model import transaction_model
from Src.Logics.factory_convertor import factory_convertor
from Src.Core.prototype import prototype
from Src.Dtos.filter_dto import filter_dto
from Src.Core.filter_models import filter_model


ALLOWED_LAST_FIELDS = {"name", "unique_code"}


class OSVReportService:

    def __init__(self, start_service_instance):
        self.start_service = start_service_instance
        self.converter = factory_convertor()

    def _parse_dates(self, date_start: str, date_end: str):
        try:
            dt_start = datetime.strptime(date_start, "%Y-%m-%d")
            dt_end = datetime.strptime(date_end, "%Y-%m-%d")
            return dt_start, dt_end
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты, нужен YYYY-MM-DD")


    def _validate_filters(self, dto: filter_dto):
        if not dto or not dto.filters:
            return

        for f in dto.filters:
            field_path = f.field_name.strip()
            last = field_path.split(".")[-1]

            if last not in ALLOWED_LAST_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Фильтрация разрешена только по name и unique_code, но получено '{field_path}'"
                )

    def generate(
            self,
            date_start: str,
            date_end: str,
            storage_id: Optional[str],
            dto: Optional[filter_dto] = None):

        dt_start, dt_end = self._parse_dates(date_start, date_end)
        self._validate_filters(dto)

        data = self.start_service.data
        transactions: List[transaction_model] = data.get("transaction_model", [])
        nomenclatures = data.get("nomenclature_model", [])
        ranges = data.get("range_model", [])
        groups = data.get("group_model", [])
        receipts = data.get("receipt_model", [])

        allowed_nomenclature_ids: Optional[Set[str]] = None
        allowed_storage_ids: Optional[Set[str]] = None
        allowed_range_ids: Optional[Set[str]] = None


        transactions_prefiltered = False

        if isinstance(dto, filter_dto) and dto.filters:
            mapping = {
                filter_model.NOMENCLATURE: ("nomenclature_model", nomenclatures),
                filter_model.RANGE: ("range_model", ranges),
                filter_model.GROUP: ("group_model", groups),
                filter_model.RECEIPT: ("receipt_model", receipts),
            }

            if dto.model:
                key, dataset = mapping.get(dto.model, (None, None))
                if dataset is not None:
                    proto = prototype(dataset)
                    filtered_models = prototype.filter(proto, dto).data

                    if key == "nomenclature_model":
                        allowed_nomenclature_ids = {n.unique_code for n in filtered_models}
                    elif key == "range_model":
                        allowed_range_ids = {r.unique_code for r in filtered_models}
                    elif key == "group_model":
                        allowed_group_ids = {g.unique_code for g in filtered_models}
                        allowed_nomenclature_ids = {
                            n.unique_code
                            for n in nomenclatures
                            if getattr(n.group, "unique_code", None) in allowed_group_ids
                        }
                else:
                    proto = prototype(transactions)
                    transactions = prototype.filter(proto, dto).data
                    transactions_prefiltered = True

            else:
                found = False
                for model_enum, (keyname, dataset) in mapping.items():
                    if not dataset:
                        continue
                    proto = prototype(dataset)
                    filtered_models = prototype.filter(proto, dto).data
                    if filtered_models:
                        found = True
                        if model_enum == filter_model.NOMENCLATURE:
                            allowed_nomenclature_ids = {n.unique_code for n in filtered_models}
                        elif model_enum == filter_model.RANGE:
                            allowed_range_ids = {r.unique_code for r in filtered_models}
                        elif model_enum == filter_model.GROUP:
                            allowed_group_ids = {g.unique_code for g in filtered_models}
                            allowed_nomenclature_ids = {
                                n.unique_code
                                for n in nomenclatures
                                if getattr(n.group, "unique_code", None) in allowed_group_ids
                            }
                        break

                if not found:
                    proto = prototype(transactions)
                    transactions = prototype.filter(proto, dto).data
                    transactions_prefiltered = True

        if allowed_nomenclature_ids is not None:
            nom_list = [n for n in nomenclatures if n.unique_code in allowed_nomenclature_ids]
        elif transactions_prefiltered:
            tx_nom_codes = {getattr(t.nomenclature, "unique_code", None) for t in transactions if
                            getattr(t, "nomenclature", None)}
            nom_list = [n for n in nomenclatures if n.unique_code in tx_nom_codes]
        else:
            nom_list = nomenclatures

        report = {}
        for n in nom_list:
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

        filtered_transactions = [
            t for t in transactions
            if (not storage_id or getattr(t.storage, "unique_code", None) == storage_id)
               and (allowed_storage_ids is None or getattr(t.storage, "unique_code", None) in allowed_storage_ids)
               and (allowed_nomenclature_ids is None or getattr(t.nomenclature, "unique_code",
                                                                None) in allowed_nomenclature_ids)
               and (allowed_range_ids is None or getattr(t.range, "unique_code", None) in allowed_range_ids)
               and (dt_start <= t.date_tr <= dt_end)
        ]

        for t in filtered_transactions:
            n = t.nomenclature
            r = t.range
            key = (n.unique_code, getattr(r, "unique_code", None))

            if key not in report:
                if allowed_nomenclature_ids is not None:
                    continue
                report[key] = {
                    "start_balance": 0.0,
                    "nomenclature": self.converter.create(n),
                    "unit": self.converter.create(r) if r else None,
                    "incoming": 0.0,
                    "outgoing": 0.0,
                    "end_balance": 0.0
                }

            qty = t.quantity / (r.value if r and r.value else 1)
            if qty > 0:
                report[key]["incoming"] += qty
            else:
                report[key]["outgoing"] += abs(qty)

        for item in report.values():
            item["end_balance"] = item["start_balance"] + item["incoming"] - item["outgoing"]

        # Возвращаем список значений отчёта
        return list(report.values())





