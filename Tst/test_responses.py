from Src.start_service import start_service
from Src.Logics.markdown_response import markdown_response
from Src.reposity import reposity
import unittest

# Набор тестов для проверки формирования данных
# в разных форматах
class test_responses(unittest.TestCase):

    # Проверить формирование Markdown 
    def test_markdown_response_build(self):
        # Подготовка
        service = start_service()
        service.start()
        response = markdown_response()


        # Действие
        result = response.build(service.data[ reposity.nomenclature_key ] )

        # Проверка
        assert len(result) > 0
        print(result)

  
if __name__ == '__main__':
    unittest.main()  