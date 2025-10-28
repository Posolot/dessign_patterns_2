from datetime import datetime
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import validator, argument_exception


class datetime_converter(abstract_convertor):
    """
    Конвертер для типа datetime в словарь.
    """

    def convert(self, value):
        # Проверка на None
        if value is None:
            raise argument_exception("Передано пустое значение")

        # Проверяем тип данных
        allowed_types = (datetime,)

        # Проверка корректности аргумента через validator
        validator.validate(value, allowed_types)

        # Возвращаем словарь с ISO-форматом даты и временем
        return {
            "value": value.isoformat()
        }
