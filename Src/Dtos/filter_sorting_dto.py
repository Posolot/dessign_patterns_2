from Src.Dtos.filter_dto import filter_dto
from typing import List, Dict, Any, Optional
from Src.Dtos.filter_dto import filter_dto
from Src.Core.validator import validator
from Src.Core.prototype import prototype

class filter_sorting_dto:
    __filters = []
    __sorting = []

    def __init__(self):
        self.filters: filter_dto = filter_dto()
        self.sorting: List[str] = []

    @staticmethod
    def from_dict(d: Optional[Dict[str, Any]]) -> "filter_sorting_dto":
        inst = filter_sorting_dto()
        if not d:
            return inst

        if "filters" in d and d["filters"] is not None:
            if isinstance(d["filters"], dict):
                inst.filters = filter_dto.from_dict(d["filters"])
            elif isinstance(d["filters"], list):
                fd = filter_dto()
                for f in d["filters"]:
                    fd.add_filter_from_dict(f)
                inst.filters = fd
            else:
                raise ValueError("filters must be dict or list")

        # sorting
        if "sorting" in d and d["sorting"] is not None:
            if not isinstance(d["sorting"], list):
                raise ValueError("sorting must be a list of field names")
            inst.sorting = [str(x) for x in d["sorting"]]

        return inst

    def apply(self, data: list) -> list:
        validator.validate(data, list)
        result = self.filters.apply(data) if self.filters and self.filters.filters else data[:]

        if not self.sorting:
            return result

        for key in reversed(self.sorting):
            result.sort(key=lambda item: prototype._get_nested_attr(item, key) or "")

        return result


    # {
    #     "filters":
    #     [
    #         {
    #             "field_name":"name",
    #             "value":"Пщеничная мука",
    #             "type":"LIKE"
    #         },
    #
    #         {
    #             "field_name":"range_name",
    #             "value":"кг",
    #             "type":"EQUALS"
    #         }
    #     ],
    #     "sorting":[
    #         "range_name"
    #     ]
    # }