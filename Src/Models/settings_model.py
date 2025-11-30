from datetime import datetime
from Src.Models.company_model import company_model
from Src.Core.validator import validator



# Модель настроек приложения
class settings_model:
    __company: company_model = None
    __response_format: str = "Json"
    __block_period: datetime = None

    # Текущая организация
    @property
    def company(self) -> company_model:
        return self.__company

    @company.setter
    def company(self, value: company_model):
        validator.validate(value, company_model)
        self.__company = value

    # Формат ответа
    @property
    def response_format(self) -> str:
        return self.__response_format

    @response_format.setter
    def response_format(self, value: str):
        allowed_formats = ["CSV", "Markdown", "Json", "XML"]
        validator.validate(value, str)
        if value not in allowed_formats:
            raise ValueError(
                f"Некорректный формат ответа: {value}. Допустимые значения: {allowed_formats}"
            )
        self.__response_format = value

    # Дата блокировки
    @property
    def block_period(self) -> datetime:
        return self.__block_period

    @block_period.setter
    def block_period(self, value: datetime):
        validator.validate(value, datetime)
        self.__block_period = value

    @staticmethod
    def get_block_period() -> datetime:
        instance = settings_model()
        if instance.block_period is None:
            return datetime(1900, 1, 1)  # значение по умолчанию
        return instance.block_period
