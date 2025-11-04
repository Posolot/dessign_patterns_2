from Src.Core.abstract_response import abstract_response
from Src.Logics.factory_convertor import factory_convertor
from xml.sax.saxutils import escape

class response_xml(abstract_response):
    def _to_xml_fragment(self, tag, value, indent="    "):
        if value is None:
            return f"{indent}<{tag}></{tag}>\n"
        if isinstance(value, (str, int, float, bool)):
            return f"{indent}<{tag}>{escape(str(value))}</{tag}>\n"
        if isinstance(value, (list, tuple)):
            text = ""
            for v in value:
                text += self._to_xml_fragment(tag, v, indent)
            return text
        if isinstance(value, dict):
            text = f"{indent}<{tag}>\n"
            for k, v in value.items():
                text += self._to_xml_fragment(k, v, indent + "  ")
            text += f"{indent}</{tag}>\n"
            return text
        return f"{indent}<{tag}>{escape(str(value))}</{tag}>\n"

    def build(self, format: str, data: list) -> str:
        if not data:
            return "<items></items>"

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

        text = "<items>\n"
        for obj in data:
            text += "  <item>\n"
            primitive = primitiveize(conv.create(obj))
            if isinstance(primitive, dict):
                for key, value in primitive.items():
                    text += self._to_xml_fragment(key, value, indent="    ")
            else:
                text += self._to_xml_fragment("value", primitive, indent="    ")
            text += "  </item>\n"
        text += "</items>"
        return text
