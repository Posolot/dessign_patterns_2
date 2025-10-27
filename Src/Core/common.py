from Src.Core.entity_model import entity_model
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import argument_exception

# Набор статических общих методов
class common:

    """
    Получить список наименований всех моделей
    """
    @staticmethod
    def get_models() -> list:
        result = []
        for  inheritor in entity_model.__subclasses__():
            result.append(inheritor.__name__)

        return result    


    """
    Получить полный список полей любой модели
        - is_common = True - исключить из списка словари и списки
    """
    @staticmethod
    def get_fields(source, is_common: bool = False) -> list:
        if source is None:
            raise argument_exception("Некорректно переданы аргументы!")
            # Все атрибуты объекта, кроме приватных
        items = list(filter(lambda x: not x.startswith("_"), dir(source)))
        # vars(source) возвращает все атрибуты экземпляра
        result = []
        for item in items:
            try:
                value = getattr(source, item)
            except AttributeError:
                continue
                # Опционально фильтруем сложные типы
            if is_common and isinstance(value, (dict, list)):
                continue

                # Добавляем, если это поле экземпляра или property
            if not callable(value):
                result.append(item)

        return result
