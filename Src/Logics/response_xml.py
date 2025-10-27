from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
from xml.sax.saxutils import escape

class response_xml(abstract_response):
    """
    Реализация ответа в формате XML
    """

    def _to_xml_fragment(self, tag, value, indent="    "):
        """
        Возвращает xml-фрагмент для тега и значения.
        Если value - примитив, возвращает <tag>value</tag>
        Если value - dict, возвращает вложенные теги
        """
        if value is None:
            return f"{indent}<{tag}></{tag}>\n"

        # Примитив
        if isinstance(value, (str, int, float, bool)):
            return f"{indent}<{tag}>{escape(str(value))}</{tag}>\n"

        # Списки -> повторяющиеся теги
        if isinstance(value, (list, tuple)):
            text = ""
            for v in value:
                text += self._to_xml_fragment(tag, v, indent)
            return text

        # Словарь / объект -> вложенные теги
        if isinstance(value, dict):
            text = f"{indent}<{tag}>\n"
            for k, v in value.items():
                text += self._to_xml_fragment(k, v, indent + "  ")
            text += f"{indent}</{tag}>\n"
            return text

        # Фоллбек
        return f"{indent}<{tag}>{escape(str(value))}</{tag}>\n"


    def _to_primitive(self, value):
        # Аналогично json: примитивы, списки, объекты через common.get_fields -> dict
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, (list, tuple)):
            return [self._to_primitive(v) for v in value]

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

        if hasattr(value, "__dict__"):
            return {k: self._to_primitive(v) for k, v in value.__dict__.items()}

        return str(value)


    def build(self, format: str, data: list) -> str:
        if not data:
            return "<items></items>"

        text = "<items>\n"
        for obj in data:
            text += "  <item>\n"
            fields = common.get_fields(obj)
            for f in fields:
                value = getattr(obj, f, None)
                primitive = self._to_primitive(value)
                text += self._to_xml_fragment(f, primitive, indent="    ")
            text += "  </item>\n"
        text += "</items>"
        return text