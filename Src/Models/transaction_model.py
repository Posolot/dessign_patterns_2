from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model
from Src.Core.entity_model import entity_model
from Src.Dtos.transaction_dto import transaction_dto
from Src.Core.validator import validator
from datetime import datetime

class transaction_model(entity_model):

    __storage: storage_model
    __nomenclature: nomenclature_model
    __quantity: float = 0.0
    __unique_number: int = 0
    __range: range_model
    __date_tr: datetime

    def __init__(self):
        super().__init__()  # только инициализация базового класса

    @property
    def storage(self) -> storage_model:
        return self.__storage

    @storage.setter
    def storage(self, value: storage_model):
        validator.validate(value, storage_model)
        self.__storage = value

    @property
    def nomenclature(self) -> nomenclature_model:
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model):
        validator.validate(value, nomenclature_model)
        self.__nomenclature = value

    @property
    def quantity(self) -> float:
        return self.__quantity

    @quantity.setter
    def quantity(self, value: float):
        validator.validate(value, (int, float))
        self.__quantity = float(value)

    @property
    def range(self) -> range_model:
        return self.__range

    @range.setter
    def range(self, value: range_model):
        validator.validate(value, range_model)
        self.__range = value

    @property
    def date_tr(self):
        return self.__date_tr

    @date_tr.setter
    def date_tr(self, value):
        validator.validate(value, datetime)
        self.__date_tr = value

    @staticmethod
    def create(storage: storage_model,
               nomenclature: nomenclature_model,
               quantity: float,
               range: range_model,
               date_tr: datetime,
               ) -> 'transaction_model':
        transaction = transaction_model()
        transaction.storage = storage
        transaction.nomenclature = nomenclature
        transaction.quantity = quantity
        transaction.range = range
        transaction.date_tr = date_tr
        return transaction

    @staticmethod
    def from_dto(dto: transaction_dto, cache: dict):
        validator.validate(dto, transaction_dto)
        validator.validate(cache, dict)

        storage = cache[dto.storage_id] if dto.storage_id in cache else None
        nomenclature = cache[dto.nomenclature_id] if dto.nomenclature_id in cache else None
        range_obj = cache[dto.range_id] if dto.range_id in cache else None

        item = transaction_model.create(storage, nomenclature,dto.quantity, range_obj, dto.date_tr)
        item.unique_code = dto.id
        return item

    def to_dict(self):
        return {
            "id": self.unique_code,
            "date_tr": self.date_tr.isoformat() if self.date_tr else None,
            "quantity": self.quantity,
            "storage_id": self.storage.unique_code if self.storage else None,
            "nomenclature_id": self.nomenclature.unique_code if self.nomenclature else None,
            "range_id": self.range.unique_code if self.range else None,
        }