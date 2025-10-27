import unittest
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.range_dto import range_dto

# Набор тестов для работы с Dto
class test_dtos(unittest.TestCase):

    # Проверить фабричный метод и загрузку данных в dto
    def test_notThrow_nomenclature_dto_create(self):
        # Подготовка
        data = { "name": "Пшеничная мука", "range_id":"a33dd457-36a8-4de6-b5f1-40afa6193346", "category_id":"7f4ecdab-0f01-4216-8b72-4c91d22b8918", "id":"0c101a7e-5934-4155-83a6-d2c388fcc11a"}
        dto = nomenclature_dto()

        # Действие
        result = dto.create(data)

        # Проверка
        assert result is not None
        assert len(dto.name) > 0


    # Проверить фабричный метод и загрузку данных в dto
    def test_notThrow_range_dto_create(self):
        # Подготовка
        data = { "name":"Грамм", 
                "id":"adb7510f-687d-428f-a697-26e53d3f65b7",
                "base_id":None,
                "value":1 }
        dto = range_dto()

        # Действие
        result = dto.create(data)

        # Проверка
        assert result is not None
        assert len(dto.name) > 0    


  
if __name__ == '__main__':
    unittest.main()  