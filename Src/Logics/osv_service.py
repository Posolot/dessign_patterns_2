from datetime import datetime
from fastapi import HTTPException
from typing import Optional, List, Set

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
            return (
                datetime.strptime(date_start, "%Y-%m-%d"),
                datetime.strptime(date_end, "%Y-%m-%d")
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты, нужен YYYY-MM-DD")

    def _validate_filters(self, dto: filter_dto):
        if not dto or not dto.filters:
            return

        for f in dto.filters:
            last = f.field_name.split(".")[-1]
            if last not in ALLOWED_LAST_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Фильтрация разрешена только по name и unique_code, но получено '{f.field_name}'"
                )

    def generate(self, date_start: str, date_end: str, storage_id: Optional[str],
                 dto: Optional[filter_dto] = None):

        dt_start, dt_end = self._parse_dates(date_start, date_end)
        self._validate_filters(dto)

        data = self.start_service.data
        transactions = data.get("transaction_model", [])
        nomenclatures = data.get("nomenclature_model", [])

        allowed_nomenclature_ids: Optional[Set[str]] = None

        if dto and dto.filters:
            model_proto = prototype.filter_by_model(dto.model, data)
            filtered_models = prototype.filter(model_proto, dto).data

            if dto.model == filter_model.NOMENCLATURE:
                allowed_nomenclature_ids = {m.unique_code for m in filtered_models}

            elif dto.model == filter_model.GROUP:
                group_ids = {g.unique_code for g in filtered_models}
                allowed_nomenclature_ids = {
                    n.unique_code for n in nomenclatures
                    if getattr(n.group, "unique_code", None) in group_ids
                }

            elif dto.model == filter_model.RANGE:
                range_ids = {r.unique_code for r in filtered_models}
                allowed_nomenclature_ids = {
                    n.unique_code for n in nomenclatures
                    if getattr(n.range, "unique_code", None) in range_ids
                }

            elif dto.model == filter_model.RECEIPT:
                receipt_ids = {r.unique_code for r in filtered_models}
                allowed_nomenclature_ids = {
                    n.unique_code for n in nomenclatures
                    if getattr(n.receipt, "unique_code", None) in receipt_ids
                }

        # -------------------------------------------------------------------
        # 2) Фильтруем транзакции → тоже через prototype
        # -------------------------------------------------------------------
        trans_proto = prototype(transactions)
        filtered_transactions = [
            t for t in trans_proto.data
            if (not storage_id or getattr(t.storage, "unique_code", None) == storage_id)
               and (dt_start <= t.date_tr <= dt_end)
        ]

        # фильтр по номенклатурам
        if allowed_nomenclature_ids is not None:
            filtered_transactions = [
                t for t in filtered_transactions
                if getattr(t.nomenclature, "unique_code", None) in allowed_nomenclature_ids
            ]

        # -------------------------------------------------------------------
        # 3) Формируем отчёт
        # -------------------------------------------------------------------
        report = {}

        for t in filtered_transactions:
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

            qty = t.quantity / (r.value if r and getattr(r, "value", None) else 1)

            if qty > 0:
                report[key]["incoming"] += qty
            else:
                report[key]["outgoing"] += abs(qty)

        # -------------------------------------------------------------------
        # Добавляем номенклатуры, по которым не было транзакций (пустые записи)
        # Только номенклатуры, разрешённые фильтром (если фильтр применён).
        # В качестве unit берём nomenclature.range если он есть, иначе None.
        # -------------------------------------------------------------------
        for n in nomenclatures:
            if allowed_nomenclature_ids is not None and n.unique_code not in allowed_nomenclature_ids:
                continue

            n_range = getattr(n, "range", None)
            key = (n.unique_code, getattr(n_range, "unique_code", None))

            if key not in report:
                report[key] = {
                    "start_balance": 0.0,
                    "nomenclature": self.converter.create(n),
                    "unit": self.converter.create(n_range) if n_range else None,
                    "incoming": 0.0,
                    "outgoing": 0.0,
                    "end_balance": 0.0
                }

        for item in report.values():
            item["end_balance"] = (
                    item["start_balance"] + item["incoming"] - item["outgoing"]
            )

        return list(report.values())
