from datetime import datetime
from Src.Models.company_model import company_model
from Src.Core.validator import validator
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
from Src.Dtos.logging_dto import logging_dto
from Src.Core.validator import argument_exception
# Модель настроек приложения
class settings_model:
    __company: company_model = None
    __response_format: str = "Json"
    __block_period: datetime = None
    __logging: logging_dto = None

    def __init__(self):
        # создаём экземпляр logging_dto по умолчанию
        self.__logging = logging_dto()
        self.__company = None
        self.__response_format = "Json"
        self.__block_period = None

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

    @property
    def logging(self):
        return self.__logging

    @logging.setter
    def logging(self, v):
        if not validator.validate(v, logging_dto):
            raise argument_exception("logging должен быть logging_dto")
        self.__logging = v

    # Дата блокировки
    @property
    def block_period(self) -> datetime:
        return self.__block_period

    @block_period.setter
    def block_period(self, value: datetime):
        validator.validate(value, datetime)
        self.__block_period = value
        observe_service.create_event(event_type.changed_block_datetime(), value)

    @staticmethod
    def get_block_period() -> datetime:
        instance = settings_model()
        if instance.block_period is None:
            return datetime(1900, 1, 1)  # значение по умолчанию
        return instance.block_period
