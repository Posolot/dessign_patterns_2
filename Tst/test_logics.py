import unittest
from Src.Logics.response_csv import response_scv
from Src.Models.group_model import group_model
from Src.Logics.factory_entities import factory_entities
from Src.Core.response_format import response_formats
from Src.Core.validator import validator
from Src.Core.abstract_response import abstract_response

# Тесты для проверки логики 
class test_logics(unittest.TestCase):

    # Проверим формирование CSV
    def test_notNone_response_csv_buld():
        # Подготовка
        response = response_scv()
        data = []
        entity = group_model.create( "test" )
        data.append( entity )

        # Дейстие
        result = response.create( "csv", data)

        # Проверка
        assert result is not None


    def test_notNone_factory_create():
        # Подготовка
        factory = factory_entities()
        data = []
        entity = group_model.create( "test" )
        data.append( entity )

        # Действие
        logic = factory.create( response_formats.csv )

        # Проверка
        assert logic is not None
        instance =  eval(logic) # logic()
        validator.validate( instance,  abstract_response)
        text =    instance.build(  response_formats.csv , data )
        assert len(text) > 0 



        
  
if __name__ == '__main__':
    unittest.main()   
