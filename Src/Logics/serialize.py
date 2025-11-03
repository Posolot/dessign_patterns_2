# Src/Core/serializer.py
from datetime import datetime
from Src.Core.common import common

def to_primitive(value):
    # None / простые типы
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    # datetime
    if isinstance(value, datetime):
        return value.isoformat()

    # списки/кортежи
    if isinstance(value, (list, tuple)):
        return [to_primitive(v) for v in value]

    # dict
    if isinstance(value, dict):
        return {k: to_primitive(v) for k, v in value.items()}

    # если есть to_dict() — используем и рекурсивно
    if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
        try:
            return to_primitive(value.to_dict())
        except Exception:
            pass

    # пробуем получить поля доменной модели через common.get_fields
    try:
        fields = common.get_fields(value)
    except Exception:
        fields = None

    if fields:
        result = {}
        for f in fields:
            v = getattr(value, f, None)
            result[f] = to_primitive(v)
        return result

    # пробуем __dict__ (DTO)
    if hasattr(value, "__dict__"):
        return {k.lstrip("_"): to_primitive(v) for k, v in value.__dict__.items()}

    return str(value)
