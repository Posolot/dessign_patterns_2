from Src.Models.company_model import company_model
from Src.Core.validator import validator, argument_exception
from Src.Core.response_formats import response_formats

######################################
# Модель настроек приложения
class settings_model:
    __company: company_model = None
    __default_response_format:str =  response_formats .json

    # Текущая организация
    @property
    def company(self) -> company_model:
        return self.__company
    
    @company.setter
    def company(self, value: company_model):
        validator.validate(value, company_model)
        self.__company = value


    @property
    def default_response_format(self) -> str:
        return self.__default_response_format

    # Формат ответа по умолчанию
    @default_response_format.setter
    def default_response_format(self, value:str):
        validator.validate(value, str)
        if value not in response_formats.list_all_formats():
            raise argument_exception("Некорректно указан тип формата!")
        
        self.__default_response_format = value


