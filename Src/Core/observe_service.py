from typing import Any, List
from Src.Core.abstract_logic import abstract_logic

class observe_service:
    """
    Централизованный реестр наблюдателей.
    - Не добавляет два подписчика одного класса по умолчанию.
    - Итерирует по копии списка при уведомлении.
    """
    handlers: List[abstract_logic] = []

    @classmethod
    def add(cls, instance: abstract_logic, allow_multiple_of_same_class: bool = False):
        if instance is None:
            return
        if not isinstance(instance, abstract_logic):
            return
        if instance in cls.handlers:
            return
        if not allow_multiple_of_same_class:
            for h in cls.handlers:
                if isinstance(h, instance.__class__):
                    return
        cls.handlers.append(instance)

    @classmethod
    def delete(cls, instance: abstract_logic):
        if instance is None:
            return
        if not isinstance(instance, abstract_logic):
            return
        try:
            cls.handlers.remove(instance)
        except ValueError:
            pass

    @classmethod
    def create_event(cls, event: str, params):
        exceptions = []
        for instance in list(cls.handlers):
            try:
                instance.handle(event, params)
            except Exception as ex:
                exceptions.append(ex)
        if exceptions:
            raise Exception(f"Errors in observers: {exceptions}")
