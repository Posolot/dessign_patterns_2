"""
Типы событий
"""
class event_type:

    """
    Событие - сформирован Json
    """
    @staticmethod
    def convert_to_json() -> str:
        return "convert_to_json"


    """
    Событие - добавление нового объекта
    """
    @staticmethod
    def add_new_object() -> str:
        return "add_new_object"

    """
    Событие - объект добавлен
    """
    @staticmethod
    def added_new_object() -> str:
        return "added_new_object"

    """
    Событие - измненение существующего объекта
    """
    @staticmethod
    def change_object() -> str:
        return "change_object"

    """
    Событие - удаление существующего объекта объекта
    """
    @staticmethod
    def start_deletion_object() -> str:
        return "start_deletion_object"

    """
    Событие - объект удален
    """
    @staticmethod
    def object_deleted() -> str:
        return "object_deleted"

    """
    Событие - смена даты блокировки
    """
    @staticmethod
    def changed_block_datetime() -> str:
        return "changed_block_datetime"

    """
    События логирования
    """
    @staticmethod
    def log() -> str:
        return "log"

    @staticmethod
    def log_debug() -> str:
        return "LOG_DEBUG"

    @staticmethod
    def log_info() -> str:
        return "LOG_INFO"

    @staticmethod
    def log_error() -> str:
        return "LOG_ERROR"

    """
    Перезагрузка настроек
    """
    @staticmethod
    def reload_settings() -> str:
        return "reload_settings"

    """
    Получить список всех событий
    """
    @staticmethod
    def events() -> list:
        result = []
        methods = [method for method in dir(event_type) if
                    callable(getattr(event_type, method)) and not method.startswith('__') and method != "events"]
        for method in methods:
            key = getattr(event_type, method)()
            result.append(key)

        return result