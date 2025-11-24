from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator, argument_exception
from typing import List, Any, Dict, Optional
from Src.Dtos.field_filter_dto import field_filter_dto
from Src.Core.filter_models import filter_model   # enum моделей
from Src.Core.filter_type import filter_type
from Src.Core.prototype import prototype


class filter_dto(abstact_dto):
    __model: Optional[filter_model] = None
    __filters: List[field_filter_dto] = None

    def __init__(self):
        self.__filters = []
        self.__model = None

    @property
    def model(self) -> Optional[filter_model]:
        return self.__model

    @model.setter
    def model(self, m):
        if m is None:
            self.__model = None
            return

        if isinstance(m, str):
            try:
                m = filter_model(m.lower())
            except Exception:
                try:
                    m = filter_model[m.lower()]
                except Exception:
                    raise argument_exception("Неверный model для filter_dto")
        validator.validate(m, filter_model)
        self.__model = m

    @property
    def filters(self) -> List[field_filter_dto]:
        return self.__filters

    def add_filter(self, f: field_filter_dto):
        validator.validate(f, field_filter_dto)
        self.__filters.append(f)

    def add_filter_from_dict(self, fd: Dict[str, Any]):

        if not isinstance(fd, dict):
            raise argument_exception("filter must be a dict")

        ff = field_filter_dto()
        ff.field_name = fd.get("field_name")
        ff.value = fd.get("value")

        t = fd.get("type")
        if t is None:
            raise argument_exception("filter.type is required")

        if isinstance(t, str):
            try:
                t_enum = filter_type[t.strip().upper()]
            except Exception:
                # пробуем создать через value
                try:
                    t_enum = filter_type(t)
                except Exception:
                    raise argument_exception(f"Неверное значение type фильтра: {t}")
        else:
            t_enum = t

        validator.validate(t_enum, filter_type)
        ff.type = t_enum

        self.add_filter(ff)

    def clear_filters(self):
        self.__filters = []

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "filter_dto":
        """
        Ожидает структуру:
          {
            "model": "nomenclature_model"
            "filters": [ {field_name, value, type}, ... ]
          }
        """
        if d is None:
            return filter_dto()
        if not isinstance(d, dict):
            raise argument_exception("from_dict expects a dict")

        inst = filter_dto()
        if "model" in d and d["model"] is not None:
            inst.model = d["model"]

        if "filters" in d and d["filters"]:
            if not isinstance(d["filters"], list):
                raise argument_exception("filters must be a list")
            for f in d["filters"]:
                inst.add_filter_from_dict(f)

        return inst

    def apply(self, data: list) -> list:
        proto = prototype(data)
        filtered_proto = prototype.filter(proto, self)
        return filtered_proto.data
