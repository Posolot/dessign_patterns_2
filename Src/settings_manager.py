from Src.Models.settings_model import settings_model
from Src.Core.validator import argument_exception
from Src.Core.validator import operation_exception
from Src.Core.validator import validator
from Src.Models.company_model import company_model
from Src.Core.common import common
from Src.Core.observe_service import observe_service
from Src.Core.abstract_logic import abstract_logic
from Src.Core.event_type import event_type
from Src.Dtos.logging_dto import logging_dto
import os
import json


class settings_manager(abstract_logic):
    """
    Менеджер настроек, работающий через DTO:
      - get_settings_dto() возвращает settings_dto
      - реагирует на event_type.reload_settings() и публикует DTO в шину
      - предоставляет привычные методы read_all/save_all/ensure_file
    """
    __full_file_name: str = ""
    __settings: settings_model = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        try:
            observe_service.add(self)
        except Exception as ex:
            try:
                self._inner_set_exception(ex)
            except Exception:
                pass

        self.set_default()

    @property
    def settings(self) -> settings_model:
        return self.__settings

    @property
    def file_name(self) -> str:
        return self.__full_file_name

    @file_name.setter
    def file_name(self, value: str):
        validator.validate(value, str)
        full_file_name = os.path.abspath(value)
        if os.path.exists(full_file_name):
            self.__full_file_name = full_file_name.strip()
        else:
            raise argument_exception(f"Не найден файл настроек {full_file_name}")

    def read_all(self) -> dict:
        if not self.__full_file_name:
            return {}
        try:
            with open(self.__full_file_name, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_all(self, data: dict) -> bool:
        validator.validate(data, dict)
        if not self.__full_file_name:
            raise operation_exception("Не задан file_name в settings_manager")

        try:
            dirpath = os.path.dirname(self.__full_file_name)
            if dirpath:
                os.makedirs(dirpath, exist_ok=True)
            with open(self.__full_file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as ex:
            self._inner_set_exception(ex)
            return False

    def ensure_file(self, path: str):
        """
        Создать файл если не существует и установить его как текущий settings file.
        """
        validator.validate(path, str)
        full = os.path.abspath(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if not os.path.exists(full):
            with open(full, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False)
        self.__full_file_name = full

    def load(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не найден файл настроек!")

        try:
            with open(self.__full_file_name, "r", encoding="utf-8") as file_instance:
                raw = json.load(file_instance)

                if isinstance(raw, dict):
                    if "company" in raw.keys():
                        data = raw["company"]
                        return self.convert(data)

                    if "response_format" in raw.keys():
                        try:
                            self.__settings.response_format = raw["response_format"]
                        except Exception:
                            raise operation_exception(f"{Exception}")
                return False
        except Exception:
            return False

    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        fields = common.get_fields(self.__settings.company)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))

        try:
            for key in matching_keys:
                setattr(self.__settings.company, key, data[key])
        except Exception as ex:
            self._inner_set_exception(ex)
            return False

        return True


    def get_logging_dto(self) -> logging_dto:
        " Возвращение DTO логгирования "
        return self.__settings.logging


    # Оработчик событий (реагируем на reload_settings)
    def handle(self, event: str, params):
        """
        Подписка на event_type.reload_settings():
          params может быть:
            - logging_dto -> применяем, сохраняем в файле и публикуем обновлённый settings_dto
            - None        -> перечитать DTO из файла и опубликовать
        """
        try:
            if event != event_type.reload_settings():
                return

            """ 1) Если пришёл logging_dto — применяем и сохраняем в файл"""
            if isinstance(params, logging_dto):
                try:
                    validator.validate(params, logging_dto)
                except Exception as ex:
                    self._inner_set_exception(ex)
                    return

                try:
                    self.__settings.logging = params
                except Exception as ex:
                    self._inner_set_exception(ex)
                    return

                # Подготовить сериализуемую структуру для raw["logging"]
                raw = self.read_all() or {}
                raw_logging = None

                try:
                    serialized = params.serialize()
                    if isinstance(serialized, list) and len(serialized) > 0 and isinstance(serialized[0], dict):
                        raw_logging = serialized[0]
                    elif isinstance(serialized, dict):
                        raw_logging = serialized
                    # положить в raw
                    try:
                        raw["logging"] = raw_logging
                    except Exception as ex:
                        raise operation_exception(ex)
                except Exception as ex:
                    self._inner_set_exception(ex)
                    return

                # Попытка записать raw в файл
                try:
                    raw_write = self.save_all(raw)
                    if not raw_write:
                        raise argument_exception("save_all returned False")
                except Exception as ex:
                    self._inner_set_exception(ex)
                    return

            """2) Параметр None (или другое) — перечитать файл и опубликовать DTO"""
            if params is None:
                try:
                    raw = self.read_all() or {}
                    logging_raw = raw.get("logging", {})
                    # обновляем DTO
                    if hasattr(self.__settings.logging, "update_from_dict"):
                        self.__settings.logging.update_from_dict({"logging": logging_raw})
                except Exception as ex:
                    self._inner_set_exception(ex)
        except Exception as ex:
            self._inner_set_exception(ex)
        return

    def set_default(self):
        # старая модель (для обратной совместимости)
        company = company_model()
        company.name = "Рога и копыта"
        company.inn = -1

        self.__settings = settings_model()
        self.__settings.company = company
        # дефолтный файл настроек (можно переопределить через file_name или через событие)
        self.__full_file_name = "Docs/settings.json"
