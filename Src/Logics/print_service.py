import json
from datetime import datetime
from Src.Core.abstract_logic import abstract_logic
from Src.Core.observe_service import observe_service
from Src.Logics.response_json import response_json
from Src.settings_manager import settings_manager

class print_service(abstract_logic):

    SETTINGS_FILE = "appsettings.json"

    def __init__(self):
        super().__init__()
        # Подключение в наблюдение
        observe_service.add(self)

        # Создаём объект response_json для сериализации
        self._serializer = response_json()

        # settings_manager singleton
        self._sm = settings_manager()
        # Убедимся, что settings файл существует и настроен
        try:
            self._sm.ensure_file(self.SETTINGS_FILE)
        except Exception as ex:
            # если не удалось — фиксируем и пробрасываем
            self.set_exception(ex)
            raise

    def handle(self, event: str, params):
        """
        Обработка всех событий:
        Логирование в settings через settings_manager
        """
        super().handle(event, params)

        timestamp = datetime.utcnow().isoformat()

        # Сериализация params через response_json
        try:
            payload = self._serializer.build("json", params if isinstance(params, list) else [params])
        except Exception as ex:
            # сохраняем причину в объекте и пробрасываем
            self.set_exception(ex)
            raise

        # Работа через settings_manager: читаем, модифицируем, сохраняем
        try:
            settings = self._sm.read_all() or {}
            settings.setdefault("print_logs", [])
            settings["print_logs"].append({
                "ts": timestamp,
                "event": event,
                "payload": payload
            })

            ok = self._sm.save_all(settings)
            if not ok:
                raise RuntimeError("Не удалось сохранить settings через settings_manager.save_all")
        except Exception as ex:
            # фиксируем и пробрасываем
            try:
                self.set_exception(ex)
            except Exception:
                pass
            raise
