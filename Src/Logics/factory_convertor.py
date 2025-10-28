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
    Определяет тип входных данных и применяет соответствующий конвертер.
    Может обрабатывать одиночные объекты или списки.
    """

    def __init__(self):
        self.__basic = basic_converter()
        self.__datetime = datetime_converter()
        self.__reference = reference_converter()
        # Передаём фабрику (self) в structure_converter
        self.__structure = structure_converter(self)

    def create(self, obj):
        if obj is None:
            raise argument_exception("Невозможно конвертировать None")

        if isinstance(obj, list):
            return [self.create(item) for item in obj]

        if isinstance(obj, (int, float, str, bool)):
            return self.__basic.convert(obj)

        if isinstance(obj, (datetime, date)):
            if isinstance(obj, date) and not isinstance(obj, datetime):
                obj = datetime(obj.year, obj.month, obj.day)
            return self.__datetime.convert(obj)

        if isinstance(obj, (list, tuple, dict)):
            return self.__structure.convert(obj)

        return self.__reference.convert(obj)
