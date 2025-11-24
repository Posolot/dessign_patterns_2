from Src.Core.prototype import prototype
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto



class prototype_report(prototype):
    @staticmethod
    def filter_by_nomenclature(source:prototype, nomenclature: nomenclature_model) -> prototype:
        validator.validate(source, prototype)
        validator.validate(nomenclature, nomenclature_model)

        result = []
        for item in source.data:
            if item.nomenclature == nomenclature:
                result.append(item)

        return source.clone(result)

    @staticmethod
    def filter(source: prototype, filter: filter_dto) -> prototype:
        validator.validate(source, prototype)
        result = prototype.filter(source.data, filter)
        return source.clone(result)

