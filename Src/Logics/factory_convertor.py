from datetime import datetime, date
from types import SimpleNamespace
from Src.Logics.basic_convertor import basic_converter
from Src.Logics.datetime_convertor import datetime_converter
from Src.Logics.reference_conventor import reference_converter
from Src.Core.abstract_model import abstact_model
from Src.Logics.structure_convertor import structure_converter
from Src.Core.validator import argument_exception

class factory_conventor:
    """
    Фабрика конверторов.
    Определяет тип входных данных и применяет соответствующий конвертер.
    Может обрабатывать одиночные объекты или списки.
    """

    def __init__(self):
        # Подключаем доступные конверторы
        self.__basic = basic_converter()
        self.__datetime = datetime_converter()
        self.__reference = reference_converter()

    def create(self, obj):
        """
        Формирует словарь (или список словарей) в зависимости от типа входных данных.
        """
        if obj is None:
            raise argument_exception("Невозможно конвертировать None")

        # Если список — обрабатываем каждый элемент рекурсивно
        if isinstance(obj, list):
            return [self.create(item) for item in obj]

        # Простые типы
        if isinstance(obj, (int, float, str, bool)):
            return self.__basic.convert(obj)

        # Дата или время
        if isinstance(obj, (datetime, date)):
            if isinstance(obj, date) and not isinstance(obj, datetime):
                # Преобразуем дату в datetime с 00:00:00
                obj = datetime(obj.year, obj.month, obj.day)
            return self.__datetime.convert(obj)

        # Ссылочные типы (модели, объекты)
        return self.__reference.convert(obj)