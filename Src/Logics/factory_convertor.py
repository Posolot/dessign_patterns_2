from datetime import datetime, date
from Src.Logics.basic_convertor import basic_converter
from Src.Logics.datetime_convertor import datetime_converter
from Src.Logics.reference_conventor import reference_converter
from Src.Core.abstract_model import abstact_model
from Src.Logics.structure_convertor import structure_converter
from Src.Core.validator import argument_exception

class factory_convertor:
    """
    Фабрика конверторов.
    Использует маппинг типов -> конвертеры; порядок в маппинге важен (специфичные типы раньше общих).
    """

    def __init__(self):
        self.__basic = basic_converter()
        self.__datetime = datetime_converter()
        self.__reference = reference_converter()
        self.__structure = structure_converter(self)

        # маппинг типов -> экземпляры конвертеров
        self.__match = {
            bool: self.__basic,
            int: self.__basic,
            float: self.__basic,
            str: self.__basic,
            datetime: self.__datetime,
            date: self.__datetime,
            list: self.__structure,
            tuple: self.__structure,
            dict: self.__structure,
            object: self.__reference
        }

    def create(self, obj):
        if obj is None:
            raise argument_exception("Невозможно конвертировать None")
        for typ, converter in self.__match.items():
            # isinstance учтёт наследование (поэтому порядок важен)
            if isinstance(obj, typ):
                # Особая логика для date (если это не datetime) — приводим к datetime, как в оригинале
                if typ is date and not isinstance(obj, datetime):
                    obj = datetime(obj.year, obj.month, obj.day)

                if hasattr(converter, "convert"):
                    return converter.convert(obj)

                if callable(converter):
                    return converter(obj)

                raise TypeError("Неправильный тип конвертера в __match")

        raise argument_exception("Не найден подходящий конвертер")
