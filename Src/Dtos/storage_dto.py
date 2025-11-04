from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator
# DTO для модели склада
# Пример:
# {
#     "id": "1a2b3c4d-0001-0002-0003-000000000001",
#     "name": "Главный склад",
#     "address": "г. Москва, ул. Промышленная, д. 5"
# }

class storage_dto(abstact_dto):
    __address: str = ""

    @property
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, value: str):
        self.__address = value

    # Переопределяем create, чтобы явно присваивать address
    def create(self, data) -> "storage_dto":

        validator.validate(data, dict)

        # Используем базовую логику для name и id
        super_fields = ['name', 'id']
        for key in super_fields:
            if key in data:
                setattr(self, key, data[key])

        # Явно присваиваем address
        if "address" in data:
            self.address = data["address"]
        else:
            self.address = ""

        return self