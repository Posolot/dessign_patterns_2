import abc
from Src.Core.validator import validator, operation_exception

# Абстрактный класс для формирования ответов
class abstract_response(abc.ABC):
    # Сформировать нужный ответ
    @abc.abstractmethod
    def build(self, format: str, data: list) -> str:
        validator.validate(format, str)
        validator.validate(data, list)

        if len(data) == 0:
            raise operation_exception("Нет данных!")

        return ""