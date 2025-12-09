from Src.Core.abstract_logic import abstract_logic
from Src.Core.observe_service import observe_service
from Src.Core import log_levels
from datetime import datetime
import os, sys
import json
from Src.Dtos.logging_dto import logging_dto
from Src.Core.event_type import event_type
class logging_service(abstract_logic):
    def __init__(self, sm):
        """
        sm — уже созданный settings_manager (singleton)
        """
        self._sm = sm

        # Инициализация с текущим logging_dto
        self._apply_from_dto(self._sm.settings.logging)
        # Подписка на шину
        try:
            observe_service.add(self)
        except Exception:
            self._inner_set_exception(Exception("Cannot subscribe to observe_service"))

    def _apply_from_dto(self, dto: logging_dto):
        """
        Применяем настройки из DTO в логгер
        """
        if not isinstance(dto, logging_dto):
            return
        try:
            self.level = getattr(log_levels, dto.min_level.upper(), log_levels.INFO)
            self.mode = dto.mode.lower()
            self.log_dir = os.path.abspath(dto.directory)
            self.format = dto.format
        except Exception as ex:
            self._inner_set_exception(ex)

    def reload_settings(self):
        """
        Создаёт событие reload_settings для шины
        """
        observe_service.create_event(event_type.reload_settings(), "reload")

    def handle(self, event: str, params):
        """
        Обработка лог-событий:
          - события 'LOG_*' или 'log'
        """
        try:
            # --- 1) События логирования ---
            if isinstance(event, str) and (event.startswith("LOG_") or event == "log"):
                self._process_log(event, params)
                return
        except Exception as ex:
            self._inner_set_exception(ex)


    def _process_log(self, event, params):
        """
        Внутренний метод обработки события логирования
        """
        try:
            if event.startswith("LOG_"):
                level = event[4:].upper()
                if isinstance(params, dict):
                    msg = params.get("message", "")
                    meta = params.get("meta")
                elif isinstance(params, str):
                    msg = params
                    meta = None
                else:
                    msg = str(params)
                    meta = None
            elif event == "log":
                if isinstance(params, dict):
                    level = (params.get("level") or "INFO").upper()
                    msg = params.get("message", "")
                    meta = params.get("meta")
                else:
                    level = "INFO"
                    msg = str(params)
                    meta = None
            else:
                return

            # фильтр по уровню из текущего logging_dto
            lvl_num = getattr(log_levels, level, log_levels.INFO)
            if lvl_num < getattr(self, "level", log_levels.INFO):
                return

            # записываем
            self._write(level, msg, meta)
        except Exception as ex:
            try:
                self._inner_set_exception(ex)
            except Exception:
                pass

    def _write(self, level, message, meta):
        """
        Запись строки лога
        """
        try:
            now = datetime.utcnow()
            date_str = now.strftime("%Y-%m-%d %H:%M:%S")
            meta_str = ""
            if meta is not None:
                try:
                    meta_str = json.dumps(meta, ensure_ascii=False)
                except Exception:
                    meta_str = str(meta)

            line = (
                self.format.replace("{date}", date_str)
                           .replace("{level}", level)
                           .replace("{message}", str(message))
                           .replace("{meta}", meta_str)
            )

            # вывод
            if getattr(self, "mode", "file") == "console":
                sys.stdout.write(line + "\n")
                sys.stdout.flush()
                return

            # файл
            log_dir = getattr(self, "log_dir", os.path.join(os.getcwd(), "logs"))
            os.makedirs(log_dir, exist_ok=True)
            file_log_name = os.path.join(log_dir, "app.log")
            with open(file_log_name, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        except Exception as ex:
            # fallback: stderr
            try:
                ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                sys.stderr.write(f"{ts} [ERROR] Logging write failed: {ex}\n")
                sys.stderr.write(f"{ts} [{level}] {message}\n")
                sys.stderr.flush()
            except:
                pass
            try:
                self._inner_set_exception(ex)
            except:
                pass


def emit(level, message, meta=None):
    payload = {"level": level, "message": message}
    if meta is not None:
        payload["meta"] = meta
    observe_service.create_event("log", payload)
