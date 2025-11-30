# observe_service.py
import json
from datetime import datetime
from typing import Any, Dict

SETTINGS_FILE = "appsettings.json"

class observe_service:

    _subscribers = {}

    @classmethod
    def subscribe(cls, event_name: str, callback):
        """
        Подписка на событие
        """
        if event_name not in cls._subscribers:
            cls._subscribers[event_name] = []
        cls._subscribers[event_name].append(callback)

    @classmethod
    def create_event(cls, event_name: str, payload: Dict[str, Any]):
        """
        Создание события и уведомление всех подписчиков
        """
        for cb in cls._subscribers.get(event_name, []):
            try:
                cb(payload)
            except Exception as e:
                print(f"Observer callback error: {e}")

        # Записываем изменения в настройки
        cls._write_to_settings(event_name, payload)

    @staticmethod
    def _write_to_settings(event_name: str, payload: Dict[str, Any]):
        """
        Логирование событий в appsettings.json
        """
        try:
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            except FileNotFoundError:
                settings = {}

            if "events" not in settings:
                settings["events"] = []

            settings["events"].append({
                "event": event_name,
                "payload": payload,
                "ts": datetime.utcnow().isoformat()
            })

            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error writing to settings: {e}")
