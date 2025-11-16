from Src.Core.abstract_response import abstract_response
from Src.Logics.factory_convertor import factory_convertor

class response_json(abstract_response):
    def build(self, format: str, data: list):
        conv = factory_convertor()

        # def primitiveize(value):
        #     # Простые типы
        #     if value is None or isinstance(value, (str, int, float, bool)):
        #         return value
        #     # Списки/кортежи
        #     if isinstance(value, (list, tuple)):
        #         return [primitiveize(v) for v in value]
        #     # Словари
        #     if isinstance(value, dict):
        #         return {k: primitiveize(v) for k, v in value.items()}
        #     # Пробуем конвертировать через фабрику
        #     try:
        #         print(value)
        #         r = conv.create(value)
        #         return primitiveize(r)
        #     except Exception:
        #         return str(value)

        return [conv.create(x) for x in data]
