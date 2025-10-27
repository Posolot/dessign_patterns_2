from Src.Models.company_model import company_model
from Src.Core.validator import validator


######################################
# Модель настроек приложения
class settings_model:
    __company: company_model = None
    __response_format: str = "Json"

    # Текущая организация
    @property
    def company(self) -> company_model:
        return self.__company

    @company.setter
    def company(self, value: company_model):
        validator.validate(value, company_model)
        self.__company = value

    # Добавление формата в модель настроек
    @property
    def response_format(self) -> str:
        return self.__response_format

    @response_format.setter
    def response_format(self, value: str):
        allowed_formats = ["CSV", "Markdown", "Json", "XML"]
        validator.validate(value, str)
        if value not in allowed_formats:
            raise ValueError(f"Некорректный формат ответа: {value}. Допустимые значения: {allowed_formats}")
        self.__response_format = value