from Src.Core.abstract_response import abstract_response
from Src.Core.common import common

class response_csv(abstract_response):

    def _to_cell(self, value):
        # Примитивы
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        # Списки -> склеим через |
        if isinstance(value, (list, tuple)):
            return "|".join(self._to_cell(v) for v in value)
        # Объекты моделей -> попробуем взять name или unique_code или преобразовать в dict и взять значения
        v_name = getattr(value, "name", None)
        if v_name is not None:
            return str(v_name)
        v_code = getattr(value, "unique_code", None)
        if v_code is not None:
            return str(v_code)
        # Фоллбек — строка
        return str(value)

    # Сформировать CSV
    def build(self, format: str, data: list):
        if not data:
            return ""

        # Шапка
        item = data[0]
        fields = common.get_fields(item)
        header = ";".join(fields) + "\n"

        # Строки данных
        rows = ""
        for obj in data:
            cells = []
            for field in fields:
                value = getattr(obj, field, None)
                cells.append(self._to_cell(value))
            rows += ";".join(cells) + "\n"

        return header + rows