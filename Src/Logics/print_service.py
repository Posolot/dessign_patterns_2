import json
from datetime import datetime
from Src.Core.abstract_logic import abstract_logic
from Src.Core.observe_service import observe_service
from Src.Logics.response_json import response_json
class print_service(abstract_logic):

    SETTINGS_FILE = "appsettings.json"

    def __init__(self):
        super().__init__()
        # Подключение в наблюдение
        observe_service.add(self)
        # Создаём объект response_json для сериализации
        self._serializer = response_json()

    def handle(self, event: str, params):
        """
        Обработка всех событий:
        Логирование в файл и appsettings.json через response_json
        """
        super().handle(event, params)

        timestamp = datetime.utcnow().isoformat()

        # Сериализация params через response_json
        try:
            payload = self._serializer.build("json", params)
        except Exception:
            payload = repr(params)

        # Загружаем текущие настройки
        try:
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    settings = json.loads(content)
                else:
                    settings = {}
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        if "print_logs" not in settings:
            settings["print_logs"] = []

        # Записываем событие
        settings["print_logs"].append({
            "ts": timestamp,
            "event": event,
            "payload": payload
        })

        # Сохраняем обратно
        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

