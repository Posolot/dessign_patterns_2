from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.validator import validator, argument_exception
from Src.Core.common import common


class reference_converter(abstract_convertor):
    """
    Конвертер ссылочных типов (Reference).
    Преобразует объект справочника в словарь по его публичным полям.
    """

    def convert(self, value):
        # Проверка на None
        if value is None:
            raise argument_exception("Передано пустое значение")

        # Проверка через валидатор на любой объект
        validator.validate(value, object)

        # Получаем список публичных полей объекта
        fields = common.get_fields(value)

        if not fields:
            raise argument_exception("Объект не имеет атрибутов для конвертации")

        # Формируем словарь по полям экземпляра
        result = {field: getattr(value, field, None) for field in fields}

        return result
