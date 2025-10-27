from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
import json

class response_json(abstract_response):
    """
    Реализация ответа в формате JSON
    """

    def _to_primitive(self, value):
        # Примитивы
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        # Списки/кортежи
        if isinstance(value, (list, tuple)):
            return [self._to_primitive(v) for v in value]
        # Если объект модели — используем common.get_fields, чтобы взять правильные свойства
        try:
            fields = common.get_fields(value)
        except Exception:
            fields = None

        if fields:
            result = {}
            for f in fields:
                v = getattr(value, f, None)
                result[f] = self._to_primitive(v)
            return result

        # Фоллбек: пробуем __dict__ (на случай простого DTO)
        if hasattr(value, "__dict__"):
            return {k: self._to_primitive(v) for k, v in value.__dict__.items()}

        # Иначе приводим к строке
        return str(value)

    def build(self, format: str, data: list) -> str:
        return json.dumps([self._to_primitive(x) for x in data], ensure_ascii=False, indent=2)