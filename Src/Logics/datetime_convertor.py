from datetime import datetime
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import validator, argument_exception


class datetime_converter(abstract_convertor):
    def convert(self, value):
        if value is None:
            raise argument_exception("Передано пустое значение")

        allowed_types = (datetime,)
        validator.validate(value, allowed_types)

        return value.isoformat()

