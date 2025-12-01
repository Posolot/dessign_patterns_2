# reference_service_prototype.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from Src.Core.prototype import prototype
from Src.Core.validator import validator, operation_exception, argument_exception
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.reposity import reposity
from Src.Dtos.range_dto import range_dto
from Src.Dtos.category_dto import category_dto
from Src.Dtos.storage_dto import storage_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.storage_model import storage_model
from Src.Logics.response_json import response_json
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type


class reference_factory:
    """
    Фабрика для создания моделей из DTO
    """
    mapping = {
        "nomenclature_model": (nomenclature_dto, nomenclature_model),
        "range_model": (range_dto, range_model),
        "group_model": (category_dto, group_model),
        "storage_model": (storage_dto, storage_model)
    }

    @classmethod
    def resolve(cls, reference_type: str):
        t = (reference_type or "").lower()
        for k in cls.mapping:
            if t == k or t.startswith(k):
                return cls.mapping[k]
        return None


class reference_service():
    """
    Сервис работы со справочниками с использованием prototype и response_json
    """

    def __init__(self, factory: reference_factory = None):
        self._repo = reposity()
        self._factory = factory or reference_factory()
        self._json_builder = response_json()  # объект для build JSON

    def _map_type_to_repo_key(self, reference_type: str) -> str:
        repo = self._repo
        if "nomen" in reference_type:
            return repo.nomenclature_key()
        if "range" in reference_type or reference_type in ("unit", "units"):
            return repo.range_key()
        if "group" in reference_type or "category" in reference_type:
            return repo.group_key()
        if "stor" in reference_type or "warehouse" in reference_type:
            return repo.storage_key()

        raise argument_exception(f"Unknown reference type: {reference_type}")

    def get(self, reference_type: str, item_id: Optional[str] = None) -> List[Any]:
        """
        Получение элементов справочника.
        Возвращает сериализованный JSON через response_json
        (response_json.build сам создаёт событие convert_to_json).
        """
        key = self._map_type_to_repo_key(reference_type)
        proto = prototype(self._repo.data.get(key, []))

        if item_id:
            proto = prototype.filter(proto, [
                type("TempFilter", (), {"field_name": "unique_code", "value": item_id, "type": "EQUALS"})()
            ])

        # response_json.build формирует сериализованный результат и (по реализации) уже
        # генерирует событие convert_to_json.
        result = self._json_builder.build("json", proto.data)
        observe_service.create_event(event_type.convert_to_json(), result)
        return result

    def add(self, reference_type: str, dto) -> Any:
        """
        Добавление:
         - генерируем событие add_new_object с исходным dto (до создания)
         - создаём модель, сохраняем
         - генерируем событие added_new_object с сериализованным результатом (после)
        """
        validator.validate(dto, object)
        resolved = self._factory.resolve(reference_type)
        if not resolved:
            raise argument_exception("Unsupported reference type")
        dto_cls, model_cls = resolved
        validator.validate(dto, dto_cls)

        # Pre-event: попытка создания (до фактического создания)
        try:
            observe_service.create_event(event_type.add_new_object(), dto)
        except Exception:
            # не критично, просто игнорируем ошибки подписчиков
            pass

        key = self._map_type_to_repo_key(reference_type)
        instance = model_cls(**{k: getattr(dto, k) for k in dto.__dict__ if not k.startswith("_")})
        self._repo.data.setdefault(key, []).append(instance)

        # сериализованный результат
        try:
            serialized = self._json_builder.build("json", [instance])[0]
        except Exception:
            serialized = instance
        # Post-event: объект добавлен
        try:
            observe_service.create_event(event_type.added_new_object(), serialized)
        except Exception:
            pass

        return serialized

    def update(self, reference_type: str, item_id: str, partial_payload: Dict[str, Any]) -> Any:
        """
        Обновление:
         - обновляем объект
         - генерируем событие change_object с сериализованным результатом
        """
        key = self._map_type_to_repo_key(reference_type)
        proto = prototype(self._repo.data.get(key, []))

        target_proto = prototype.filter(proto, [
            type("TempFilter", (), {"field_name": "unique_code", "value": item_id, "type": "EQUALS"})()
        ])
        if not target_proto.data:
            raise operation_exception(f"Item {item_id} not found in {reference_type}")
        target = target_proto.data[0]

        # можно отправить pre-change event (по желанию) — но в этом коде посылаем post-change
        for k, v in (partial_payload or {}).items():
            if hasattr(target, k):
                setattr(target, k, v)

        try:
            serialized = self._json_builder.build("json", [target])[0]
        except Exception:
            serialized = target

        try:
            observe_service.create_event(event_type.change_object(), serialized)
        except Exception:
            pass

        return serialized

    def delete(self, reference_type: str, item_id: str) -> bool:
        """
        Удаление:
         - генерируем start_deletion_object перед удалением (с сериализованным объектом)
         - выполняем проверки (например, используется ли номенклатура)
         - удаляем
         - генерируем object_deleted после успеха (с тем же сериализованным объектом)
        """
        key = self._map_type_to_repo_key(reference_type)
        proto = prototype(self._repo.data.get(key, []))

        target_proto = prototype.filter(proto, [
            type("TempFilter", (), {"field_name": "unique_code", "value": item_id, "type": "EQUALS"})()
        ])
        if not target_proto.data:
            raise operation_exception(f"Item {item_id} not found in {reference_type}")

        target = target_proto.data[0]

        # сериализуем объект для событий (если возможно)
        try:
            serialized_target = self._json_builder.build("json", [target])[0]
        except Exception:
            serialized_target = target

        # pre-deletion event
        try:
            observe_service.create_event(event_type.start_deletion_object(), serialized_target)
        except Exception:
            pass

        # проверка использования номенклатуры
        if key == reposity.nomenclature_key():
            for r in self._repo.data.get(reposity.receipt_key(), []):
                try:
                    for comp in getattr(r, "composition", []):
                        if comp.get("nomenclature_id") == item_id:
                            raise operation_exception(f"Cannot delete nomenclature {item_id}: used in receipt {getattr(r, 'unique_code', None)}")
                except Exception:
                    pass
            for t in self._repo.data.get(reposity.transaction_key(), []):
                if getattr(t, "nomenclature_id", None) == item_id:
                    raise operation_exception(f"Cannot delete nomenclature {item_id}: used in transaction {getattr(t, 'unique_code', None)}")

        # собственно удаление
        self._repo.data[key] = [x for x in proto.data if getattr(x, "unique_code", None) != item_id]

        # post-deletion event
        try:
            observe_service.create_event(event_type.object_deleted(), serialized_target)
        except Exception:
            pass

        return True
