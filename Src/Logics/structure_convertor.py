from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import argument_exception

class structure_converter(abstract_convertor):
    """
    Конвертер для структурированных типов: list, tuple, dict.
    Использует переданную фабрику для рекурсивной конвертации элементов.
    """

    def __init__(self, factory):
        if factory is None:
            raise argument_exception("Не передана фабрика для structure_converter")
        self.factory = factory

    def convert(self, value):
        if value is None:
            raise argument_exception("Передано пустое значение")

        if isinstance(value, (list, tuple)):
            return [self.factory.create(item) for item in value]

        elif isinstance(value, dict):
            return {k: self.factory.create(v) for k, v in value.items()}

        else:
            raise argument_exception(f"StructureConverter не поддерживает тип {type(value)}")
