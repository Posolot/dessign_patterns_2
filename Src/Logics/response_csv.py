from Src.Core.abstract_response import abstract_response
from Src.Core.common import common


class response_scv(abstract_response):

    # Сформировать CSV
    def create(self, format:str, data: list):
        text = super().create(format, data)

        # Шапка
        item = data [ 0 ]
        fields = common.get_fields( item )
        for field in fields:
            text += f"{field};"

        # Данные

        return text    

