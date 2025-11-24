from Src.Core.validator import validator
from Src.Dtos.field_filter_dto import field_filter_dto
from Src.Core.filter_type import filter_type
from Src.Core.filter_models import filter_model
from typing import Any, List

class prototype:
    """
    Универсальный прототип для всех доменных моделей.
    Поддерживает:
      - клонирование
      - фильтрацию через список field_filter_dto или через объект DTO (у которого есть .filters)
      - вложенные поля ('range.base.name', 'group.name' и т.д.)
      - фильтрацию по name и unique_code
      - фильтры типа EQUALS / LIKE
    """
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
        """
        Получение значения вложенного атрибута по нотации 'range.base.name'.
        Поддерживает dicts, objects и списки на любом уровне.
        """
        if obj is None or not path:
            return obj

        parts = path.split(".", 1)
        head = parts[0]
        tail = parts[1] if len(parts) > 1 else None

        # dict
        if isinstance(obj, dict):
            val = obj.get(head)
        # list/tuple -> рекурсивно собрать результаты
        elif isinstance(obj, (list, tuple)):
            results = []
            for item in obj:
                r = prototype._get_nested_attr(item, path)
                if r is not None:
                    results.append(r)
            return results if results else None
        else:
            # обычный объект
            val = getattr(obj, head, None)

        if tail is None:
            return val

        # если val - список — пробегаем по каждому элементу
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
        """
        Сравнивает candidate с фильтром ff (field_filter_dto).
        candidate может быть: простым значением или списком значений (тогда any).
        """
        # пустой кандидат — мимо
        if candidate is None:
            return False

        # если список — проверить любой элемент
        if isinstance(candidate, (list, tuple)):
            return any(prototype._match_value(c, ff) for c in candidate)

        cand_str = str(candidate).strip().lower()
        val_str = str(ff.value).strip().lower()

        # сравнить по enum filter_type
        if ff.type == filter_type.EQUALS:
            return cand_str == val_str
        elif ff.type == filter_type.LIKE:
            return val_str in cand_str
        else:
            # fallback (безопасно)
            return cand_str == val_str

    @staticmethod
    def filter_by_model(model: filter_model, data: dict) -> "prototype":
        validator.validate(data, dict)

        key = model.value
        return prototype(data.get(key, []))
    

    @staticmethod
    def filter(source: "prototype", filters) -> "prototype":
        """
        Фильтрует source.data по фильтрам.
        filters: может быть:
          - списком field_filter_dto
          - объектом DTO (у которого есть .filters)
        Возвращает новый prototype с отфильтрованными элементами.
        """
        validator.validate(source, prototype)

        # поддержка DTO (у которого есть атрибут filters)
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
                # отладочный вывод (при необходимости)
                print("DEBUG prototype._get_nested_attr:", ff.field_name, "=>", candidate, "ff.value:", ff.value)
                if not prototype._match_value(candidate, ff):
                    matched_all = False
                    break
            if matched_all:
                filtered.append(item)

        return source.clone(filtered)
