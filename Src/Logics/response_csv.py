from Src.Core.abstract_response import abstract_response
from Src.Logics.serialize import to_primitive

class response_csv(abstract_response):
    """
    Реализация ответа в формате CSV через serialize (to_primitive)
    """

    def _to_cell(self, value):
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, (list, tuple)):
            return "|".join(self._to_cell(v) for v in value)
        if isinstance(value, dict):
            return "|".join(str(v) for v in value.values())
        return str(value)

    def build(self, format: str, data: list):
        if not data:
            return ""

        first = to_primitive(data[0])
        header = ";".join(first.keys()) + "\n"

        rows = ""
        for obj in data:
            primitive = to_primitive(obj)
            cells = [self._to_cell(v) for v in primitive.values()]
            rows += ";".join(cells) + "\n"

        return header + rows
