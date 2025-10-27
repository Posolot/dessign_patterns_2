

"""
Типы форматов данных для вывода данных Api
"""
class response_formats:

    """
    Формат ответа csv
    """
    @staticmethod
    def csv() -> str:
        return "csv"
    
    """
    Формат ответа json
    """
    @staticmethod
    def json() -> str:
        return "json"
    
    """
    Формат ответа markdown
    """
    @staticmethod
    def markdown() -> str:
        return "markdown"
    
    """
    Статический метод возвращает список всех поддерживаемых форматов данных
    """

    @staticmethod
    def get_all_formats() -> list:
        return ["scv", "excel", "json", "markdown"]