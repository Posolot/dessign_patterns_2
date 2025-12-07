from Src.Core.abstract_logic import abstract_logic
from Src.Core.observe_service import observe_service
from Src.Core import log_levels
from datetime import datetime
import os, sys
import json

class logging_service(abstract_logic):
    def __init__(self, sm):
        """
        sm — уже созданный settings_manager (singleton)
        """

        self.level = "INFO"
        self.mode = "file"
        self.log_dir = os.path.join(os.getcwd(), "Src", "Logs")
        self.format = "{date} [{level}] {message} {meta}"

        if sm is None:
            raise ValueError("settings_manager instance is required")
        self._sm = sm

        """
        Добавление как наблюдателя
        """
        self.reload_settings()
        try:
            observe_service.add(self)
        except Exception:
            self._inner_set_exception(Exception("Cannot subscribe to observe_service"))


    def reload_settings(self):
        try:
            raw = self._sm.read_all() or {}
        except Exception as ex:
            self._inner_set_exception(ex)
            raw = {}

        try:
            cfg = raw.get("logging")
            if cfg is None:
                cfg = {
                    "min_level": self.level,
                    "mode": self.mode,
                    "directory": self.log_dir,
                    "format": self.format
                }
                raw["logging"] = cfg
                try:
                    self._sm.save_all(raw)
                except Exception as ex_save:
                    self._inner_set_exception(ex_save)

            # применяем настройки
            level_name = cfg.get("min_level", "INFO")
            self.level = getattr(log_levels, level_name.upper(), log_levels.INFO)
            self.mode = str(cfg.get("mode", "file")).lower()
            self.log_dir = os.path.abspath(cfg.get("directory", self.log_dir))
            self.format = cfg.get("format", self.format)

        except Exception as ex:
            self._inner_set_exception(ex)

    def handle(self, event: str, params):
        """
        Обработка лог-событий:
          - события вида 'LOG_DEBUG', 'LOG_INFO', 'LOG_ERROR'
          - событие 'log' с payload dict {'level','message','meta'}
        """
        try:
            # распарсить вход
            if isinstance(event, str) and event.startswith("LOG_"):
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

            # фильтрация по уровню
            lvl_num = getattr(log_levels, level, log_levels.INFO)
            min_level = getattr(self, "level", log_levels.INFO)
            if lvl_num < min_level:
                return

            try:
                self._write(level, msg, meta)
            except Exception as ex:
                # fallback: вывести в stderr и зафиксировать внутреннюю ошибку
                try:
                    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    sys.stderr.write(f"{ts} [ERROR] Logging write failed: {ex}\n")
                    sys.stderr.write(f"{ts} [{level}] {msg}\n")
                    sys.stderr.flush()
                except Exception:
                    pass
                try:
                    self._inner_set_exception(ex)
                except Exception:
                    pass

        except Exception as ex:
            # защита от любых неожиданных ошибок в обработчике
            try:
                self._inner_set_exception(ex)
            except Exception:
                pass

    def _write(self, level, message, meta):
        """
        Запись строки лога.
        При ошибках переходит в stderr и фиксирует исключения через _inner_set_exception.
        """
        try:
            now = datetime.utcnow()
            date_str = now.strftime("%Y-%m-%d %H:%M:%S")
            meta_str = ""
            if meta is not None:
                try:
                    meta_str = json.dumps(meta, ensure_ascii=False)
                except Exception:
                    try:
                        meta_str = str(meta)
                    except Exception:
                        meta_str = "<unserializable-meta>"

            # Готовим строку
            line = (
                self.format.replace("{date}", date_str)
                .replace("{level}", level)
                .replace("{message}", str(message))
                .replace("{meta}", meta_str)
            )

            """
            Console
            """
            if getattr(self, "mode", "file") == "console":
                try:
                    sys.stdout.write(line + "\n")
                    sys.stdout.flush()
                    return
                except Exception as ex:
                    try:
                        sys.stderr.write(f"{date_str} [ERROR] Failed to write to stdout: {ex}\n")
                        sys.stderr.flush()
                    except:
                        pass
                    try:
                        self._inner_set_exception(ex)
                    except:
                        pass
                    return
            """
            File
            """
            log_dir = getattr(self, "log_dir", os.path.join(os.getcwd(), "logs"))
            file_log_name = os.path.join(log_dir, "app.log")
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as ex:
                self.mode = "console"
                try:
                    self._inner_set_exception(ex)
                except:
                    pass
                try:
                    sys.stderr.write(f"{date_str} [ERROR] Cannot create directory '{log_dir}': {ex}\n")
                    sys.stderr.flush()
                except:
                    pass
                return

            try:
                with open(file_log_name, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                return
            except Exception as ex:
                self.mode = "console"
                try:
                    self._inner_set_exception(ex)
                except:
                    pass
                try:
                    sys.stderr.write(f"{date_str} [ERROR] Cannot write to file '{file_log_name}': {ex}\n")
                    sys.stderr.write(line + "\n")
                    sys.stderr.flush()
                except:
                    pass

        except Exception as ex:
            "Проверка падения логгера"
            try:
                ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                sys.stderr.write(f"{ts} [ERROR] Unexpected logging failure: {ex}\n")
                sys.stderr.flush()
            except:
                pass
            try:
                self._inner_set_exception(ex)
            except:
                pass

def emit(level, message, meta=None):
    payload = {'level': level, 'message': message}
    if meta is not None: payload['meta'] = meta
    observe_service.create_event('log', payload)
