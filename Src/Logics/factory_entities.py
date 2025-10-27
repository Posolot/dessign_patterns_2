from Src.Core.abstract_response import abstract_response
from Src.Logics.response_csv import response_csv
from Src.Logics.response_xml import response_xml
from Src.Logics.response_markdown import response_markdown
from Src.Logics.response_json import response_json
from Src.Core.validator import operation_exception
from Src.Core.validator import validator
from Src.settings_manager import settings_manager

class factory_entities:
    # Подключаем менеджер настроек
    __settings = settings_manager()

    # Соответствие форматов и классов
    __match = {
        "csv": response_csv,
        "json": response_json,
        "markdown": response_markdown,
        "xml": response_xml
    }

    # Получить нужный тип
    def create(self, _format: str) -> abstract_response:
        validator.validate(_format, str)
        format_upper = _format.strip().lower()
        if format_upper not in self.__match:
            raise operation_exception(f"Формат '{_format}' не поддерживается")

        return self.__match[format_upper]

    # Создать тип по умолчанию из настроек
    def create_default(self) -> abstract_response:
        """
        Создаёт экземпляр ответа на основе формата,
        указанного в settings_manager.settings.response_format
        """
        default_format = self.__settings.settings.response_format
        return self.create(default_format)
