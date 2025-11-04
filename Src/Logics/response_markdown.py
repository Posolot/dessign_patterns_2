from Src.Core.abstract_response import abstract_response
from Src.Logics.factory_convertor import factory_convertor

class response_markdown(abstract_response):
    def _to_cell(self, value):
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, (list, tuple)):
            return " | ".join(self._to_cell(v) for v in value)
        if isinstance(value, dict):
            return " | ".join(str(v) for v in value.values())
        return str(value)

    def build(self, format: str, data: list) -> str:
        if not data:
            return ""

        conv = factory_convertor()

        def primitiveize(value):
            if value is None or isinstance(value, (str, int, float, bool)):
                return value
            if isinstance(value, (list, tuple)):
                return [primitiveize(v) for v in value]
            if isinstance(value, dict):
                return {k: primitiveize(v) for k, v in value.items()}
            try:
                r = conv.create(value)
                return primitiveize(r)
            except Exception:
                return str(value)

        first_prim = primitiveize(conv.create(data[0]))

        if not isinstance(first_prim, dict):
            # одиночная колонка
            header = "| value |\n| --- |\n"
            rows = ""
            for obj in data:
                prim = primitiveize(conv.create(obj))
                rows += f"| {self._to_cell(prim)} |\n"
            return header + rows

        fields = list(first_prim.keys())
        header = "| " + " | ".join(fields) + " |\n"
        separator = "| " + " | ".join(["---"] * len(fields)) + " |\n"

        rows = ""
        for obj in data:
            prim = primitiveize(conv.create(obj))
            row_cells = [self._to_cell(prim.get(f)) for f in fields]
            rows += "| " + " | ".join(row_cells) + " |\n"

        return header + separator + rows
