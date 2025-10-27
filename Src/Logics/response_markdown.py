from Src.Core.abstract_response import abstract_response
from Src.Core.common import common

class response_markdown(abstract_response):
    """
    Реализация ответа в формате Markdown (таблица)
    """

    def _to_cell(self, value):
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, (list, tuple)):
            return " | ".join(self._to_cell(v) for v in value)
        v_name = getattr(value, "name", None)
        if v_name is not None:
            return str(v_name)
        v_code = getattr(value, "unique_code", None)
        if v_code is not None:
            return str(v_code)
        return str(value)

    def build(self, format: str, data: list) -> str:
        if not data:
            return ""

        item = data[0]
        fields = common.get_fields(item)

        # Заголовки таблицы
        header = "| " + " | ".join(fields) + " |\n"
        separator = "| " + " | ".join(["---" for _ in fields]) + " |\n"

        # Строки данных
        rows = ""
        for obj in data:
            row_cells = [self._to_cell(getattr(obj, f, None)) for f in fields]
            row = "| " + " | ".join(row_cells) + " |\n"
            rows += row

        return header + separator + rows