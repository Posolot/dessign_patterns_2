# Src/Logics/response_json.py
from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
from datetime import datetime
from Src.Logics.serialize import to_primitive

class response_json(abstract_response):
    def build(self, format: str, data: list):
        # возвращаем список словарей
        return [to_primitive(x) for x in data]
