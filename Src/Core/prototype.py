from Src.Core.validator import validator
from Src.Dtos.field_filter_dto import field_filter_dto
from Src.Core.filter_type import filter_type
from typing import Any, List

class prototype:
    __data: list = []

    @property
    def data(self):
        return self.__data

    def __init__(self, data: list):
        validator.validate(data, list)
        self.__data = data

    def clone(self, data: list = None) -> "prototype":
        inner_data = data if data is not None else self.__data
        return prototype(inner_data)

    @staticmethod
    def _get_nested_attr(obj: Any, path: str):
        if obj is None or not path:
            return obj

        parts = path.split(".", 1)
        head = parts[0]
        tail = parts[1] if len(parts) > 1 else None

        if isinstance(obj, dict):
            val = obj.get(head)
        elif isinstance(obj, (list, tuple)):
            results = []
            for item in obj:
                r = prototype._get_nested_attr(item, path)
                if r is not None:
                    results.append(r)
            return results if results else None
        else:
            val = getattr(obj, head, None)

        if tail is None:
            return val

        if isinstance(val, (list, tuple)):
            results = []
            for element in val:
                r = prototype._get_nested_attr(element, tail)
                if r is not None:
                    results.append(r)
            return results if results else None

        return prototype._get_nested_attr(val, tail)

    @staticmethod
    def _match_value(candidate, ff: field_filter_dto) -> bool:
        if candidate is None:
            return False

        if isinstance(candidate, (list, tuple)):
            return any(prototype._match_value(c, ff) for c in candidate)

        cand_str = str(candidate).strip().lower()
        val_str = str(ff.value).strip().lower()
        if ff.type == filter_type.EQUALS:
            return cand_str == val_str
        elif ff.type == filter_type.LIKE:
            return val_str in cand_str
        else:
            return cand_str == val_str

    @staticmethod
    def filter(source: "prototype", filters) -> "prototype":

        validator.validate(source, prototype)
        if hasattr(filters, "filters"):
            filters_list = filters.filters
        else:
            filters_list = filters

        validator.validate(filters_list, list)

        if not source.data:
            return source.clone([])

        filtered = []
        for item in source.data:
            matched_all = True
            for ff in filters_list:
                candidate = prototype._get_nested_attr(item, ff.field_name)
                if not prototype._match_value(candidate, ff):
                    matched_all = False
                    break
            if matched_all:
                filtered.append(item)

        return source.clone(filtered)
