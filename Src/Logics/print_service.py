import json
from datetime import datetime
from Src.Core.abstract_logic import abstract_logic
from Src.Core.observe_service import observe_service
from Src.Logics.response_json import response_json
from Src.settings_manager import settings_manager
import os

class print_service(abstract_logic):

    SETTINGS_FILE = "appsettings.json"

    def __init__(self):
        super().__init__()
        observe_service.add(self)

        self._serializer = response_json()
        self._sm = settings_manager()

    def handle(self, event: str, params):
        super().handle(event, params)
        timestamp = datetime.utcnow().isoformat()

        # Сериализация params
        try:
            payload = self._serializer.build("json", params if isinstance(params, list) else [params])
        except Exception as ex:
            self.set_exception(ex)
            raise

        # Загружаем, модифицируем и сохраняем в SETTINGS_FILE
        try:
            full_path = os.path.abspath(self.SETTINGS_FILE)

            # Чтение с защитой от пустого или повреждённого JSON
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                settings = {}

            settings.setdefault("print_logs", [])
            settings["print_logs"].append({
                "ts": timestamp,
                "event": event,
                "payload": payload
            })

            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

        except Exception as ex:
            try:
                self.set_exception(ex)
            except Exception:
                pass
            raise

