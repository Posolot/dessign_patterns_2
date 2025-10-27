from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import argument_exception

class structure_converter(abstract_convertor):
    """
    Конвертер для структурированных типов: list, tuple, dict.
    Использует convert_factory для рекурсивной конвертации элементов.
    """

    def convert(self, value):
        if value is None:
            raise argument_exception("Передано пустое значение")

        # Локальный импорт чтобы избежать циклической зависимости
        from Src.Logics.factory_convertor import factory_convertor
        factory = factory_convertor()

        if isinstance(value, (list, tuple)):
            # Рекурсивно конвертируем каждый элемент
            return [factory.convert(item) for item in value]

        elif isinstance(value, dict):
            # Рекурсивно конвертируем каждое значение словаря
            return {k: factory.convert(v) for k, v in value.items()}

        else:
            raise argument_exception(f"StructureConverter не поддерживает тип {type(value)}")
