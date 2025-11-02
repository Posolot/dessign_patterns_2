from Src.Core.entity_model import entity_model
from Src.Core.validator import validator
from Src.Dtos.storage_dto import storage_dto
"""
Модель склада (Storage)
"""
class storage_model(entity_model):
    __address: str = ""

    def __init__(self, name: str = "", address: str = ""):
        super().__init__(name)
        self.__address = address

    @property
    def address(self) -> str:
        return self.__address.strip()

    @address.setter
    def address(self, value: str):
        validator.validate(value, str, 255)
        self.__address = value.strip()

    @staticmethod
    def create(name: str, address: str):
        validator.validate(name, str)
        validator.validate(address, str)

        item = storage_model()
        item.name = name
        item.address = address
        return item
    @staticmethod
    def from_dto(dto: storage_dto, cache: dict):
        validator.validate(dto, storage_dto)
        validator.validate(cache, dict)

        item = storage_model.create(dto.name, dto.address)
        item.unique_code = dto.id
        return item