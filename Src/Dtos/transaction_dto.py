from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator
from datetime import datetime
# DTO для модели транзакции
# Пример структуры:
# {
#     "id": "d8c12a0f2b8841bfb4dc93cb12d22f85",
#     "date_tr": "2025-01-10 00:00:00",
#     "nomenclature_id": "0c101a7e5934415583a6d2c388fcc11a",
#     "storage_id": "1a2b3c4d000100020003000000000001",
#     "quantity": 50,
#     "range_id": "adb7510f687d428fa69726e53d3f65b7"
# }

class transaction_dto(abstact_dto):
    __date_tr: datetime = None
    __nomenclature_id: str = ""
    __storage_id: str = ""
    __quantity: float = 0
    __range_id: str = ""

    @property
    def date_tr(self) -> datetime:
        return self.__date_tr

    @date_tr.setter
    def date_tr(self, value):
        if isinstance(value, str) and value.strip():
            try:
                self.__date_tr = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"Некорректный формат даты: {value}")
        elif isinstance(value, datetime):
            self.__date_tr = value
        else:
            self.__date_tr = None

    @property
    def nomenclature_id(self) -> str:
        return self.__nomenclature_id
    @nomenclature_id.setter
    def nomenclature_id(self, value: str):
        self.__nomenclature_id = value

    @property
    def storage_id(self) -> str:
        return self.__storage_id
    @storage_id.setter
    def storage_id(self, value: str):
        self.__storage_id = value

    @property
    def quantity(self) -> float:
        return self.__quantity
    @quantity.setter
    def quantity(self, value: float):
        self.__quantity = value

    @property
    def range_id(self) -> str:
        return self.__range_id
    @range_id.setter
    def range_id(self, value: str):
        self.__range_id = value

    # Переопределяем create для явного присваивания полей
    def create(self, data) -> "transaction_dto":

        validator.validate(data, dict)

        # Базовые поля id (и name, если есть)
        for key in ["id", "name"]:
            if key in data:
                setattr(self, key, data[key])

        # Остальные поля явно
        self.date_tr = data.get("date_tr", "")
        self.nomenclature_id = data.get("nomenclature_id", "")
        self.storage_id = data.get("storage_id", "")
        self.quantity = data.get("quantity", 0)
        self.range_id = data.get("range_id", "")

        return self
