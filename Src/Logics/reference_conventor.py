from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import argument_exception
from Src.Core.common import common


class reference_converter(abstract_convertor):

    def __init__(self, factory):
        if factory is None:
            raise argument_exception("Не передана фабрика для reference_converter")
        self.factory = factory

    def convert(self, value):
        if value is None:
            raise argument_exception("Передано пустое значение")

        fields = common.get_fields(value)
        if not fields:
            raise argument_exception("Объект не имеет атрибутов для конвертации")

        result = {}
        for field in fields:
            temp = getattr(value, field, None)
            if temp is None or isinstance(temp, (int, float, str, bool)):
                result[field] = temp
                continue
            result[field] = self.factory.create(temp)

        return result
