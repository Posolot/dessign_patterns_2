from Src.Core.abstract_response import abstract_response
from Src.Logics.factory_convertor import factory_convertor

class response_json(abstract_response):
    def build(self, format: str, data: list):
        conv = factory_convertor()
        result = [conv.create(x) for x in data]
        return result
