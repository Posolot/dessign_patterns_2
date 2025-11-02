from Src.reposity import reposity
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model
from Src.Models.transaction_model import transaction_model
from Src.Core.validator import validator, argument_exception, operation_exception
import os
import json
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_item_model import receipt_item_model
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.category_dto import category_dto
from Src.Dtos.storage_dto import storage_dto
from Src.Dtos.transaction_dto import transaction_dto


class start_service:
    # Репозиторий
    __repo: reposity = reposity()

    # Рецепт по умолчанию
    __default_receipt: receipt_model

    # Словарь который содержит загруженные и инициализованные инстансы нужных объектов
    # Ключ - id записи, значение - abstract_model
    __cache = {}

    # Наименование файла (полный путь)
    __full_file_name: str = ""

    def __init__(self):
        self.__repo.initalize()

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(start_service, cls).__new__(cls)
        return cls.instance

        # Текущий файл

    @property
    def file_name(self) -> str:
        return self.__full_file_name

    # Полный путь к файлу настроек
    @file_name.setter
    def file_name(self, value: str):
        validator.validate(value, str)
        full_file_name = os.path.abspath(value)
        if os.path.exists(full_file_name):
            self.__full_file_name = full_file_name.strip()
        else:
            raise argument_exception(f'Не найден файл настроек {full_file_name}')

    # Загрузить настройки из Json файла
    def load(self) -> bool:
        """
        Загружает настройки из JSON файла.
        При первом запуске обновляет флаг first_start.
        Загружает все данные: default_receipt, storage, transaction.
        """
        if not self.__full_file_name:
            raise operation_exception("Не найден файл настроек!")

        try:
            with open(self.__full_file_name, 'r', encoding='utf-8') as file_instance:
                settings = json.load(file_instance)

            # Проверяем первый запуск
            if settings.get("first_start", True):
                settings["first_start"] = False
                with open(self.__full_file_name, 'w', encoding='utf-8') as file_instance:
                    json.dump(settings, file_instance, ensure_ascii=False, indent=4)

            # Загружаем default_receipt
            if "default_receipt" in settings:
                data = settings["default_receipt"]
                self.convert(data)

            # Загружаем склады
            if "storage" in settings:
                self.__convert_storages({"storage": settings["storage"]})

            # Загружаем транзакции
            if "transaction" in settings:
                self.__convert_transactions({"transaction": settings["transaction"]})

            return True

        except FileNotFoundError:
            raise operation_exception(f"Файл настроек не найден: {self.__full_file_name}")

        except json.JSONDecodeError as e:
            raise operation_exception(f"Ошибка чтения JSON ({self.__full_file_name}): {e}")

        except Exception as e:
            raise operation_exception(f"Ошибка загрузки настроек: {e}")

    # Сохранить элемент в репозитории
    def __save_item(self, key: str, dto, item):
        validator.validate(key, str)
        item.unique_code = dto.id
        self.__cache.setdefault(dto.id, item)
        self.__repo.data[key].append(item)

    # Загрузить единицы измерений
    def __convert_ranges(self, data: dict) -> bool:
        validator.validate(data, dict)
        ranges = data['ranges'] if 'ranges' in data else []
        if len(ranges) == 0:
            return False

        for range in ranges:
            dto = range_dto().create(range)
            item = range_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.range_key(), dto, item)

        return True

    # Загрузить группы номенклатуры
    def __convert_groups(self, data: dict) -> bool:
        validator.validate(data, dict)
        categories = data['categories'] if 'categories' in data else []
        if len(categories) == 0:
            return False

        for category in categories:
            dto = category_dto().create(category)
            item = group_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.group_key(), dto, item)

        return True

    # Загрузить номенклатуру
    def __convert_nomenclatures(self, data: dict) -> bool:
        validator.validate(data, dict)
        nomenclatures = data['nomenclatures'] if 'nomenclatures' in data else []
        if len(nomenclatures) == 0:
            return False

        for nomenclature in nomenclatures:
            dto = nomenclature_dto().create(nomenclature)
            item = nomenclature_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.nomenclature_key(), dto, item)

        return True

    def __convert_storages(self, data: dict) -> bool:
        validator.validate(data, dict)
        storages = data['storage'] if 'storage' in data else []
        if len(storages) == 0:
            return False

        for storage in storages:
            dto = storage_dto().create(storage)
            item = storage_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.storage_key(), dto, item)

        return True

    # Загрузить транзакции
    def __convert_transactions(self, data: dict) -> bool:
        validator.validate(data, dict)
        transactions = data.get('transaction', [])
        if len(transactions) == 0:
            return False

        for transaction in transactions:
            # Создаём DTO
            dto = transaction_dto().create(transaction)

            # Ищем связанные объекты в кэше
            storage = self.__cache.get(dto.storage_id)
            nomenclature = self.__cache.get(dto.nomenclature_id)
            range_obj = self.__cache.get(dto.range_id)

            if not storage:
                raise operation_exception(f"Не найден склад с id={dto.storage_id} для транзакции {dto.id}")
            if not nomenclature:
                raise operation_exception(f"Не найдена номенклатура с id={dto.nomenclature_id} для транзакции {dto.id}")
            if not range_obj:
                raise operation_exception(f"Не найдена единица измерения с id={dto.range_id} для транзакции {dto.id}")
            # Создаём модель транзакции с данными из DTO
            item = transaction_model.create(storage, nomenclature, dto.quantity,range_obj, dto.date_tr)
            item.unique_code = dto.id

            # Сохраняем в репозиторий
            self.__save_item(reposity.transaction_key(), dto, item)

        return True

    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)
        # 1 Созданим рецепт
        cooking_time = data['cooking_time'] if 'cooking_time' in data else ""
        portions = int(data['portions']) if 'portions' in data else 0
        name = data['name'] if 'name' in data else "НЕ ИЗВЕСТНО"
        self.__default_receipt = receipt_model.create(name, cooking_time, portions)

        # Загрузим шаги приготовления
        steps = data['steps'] if 'steps' in data else []
        for step in steps:
            if step.strip() != "":
                self.__default_receipt.steps.append(step)

        self.__convert_ranges(data)
        self.__convert_groups(data)
        self.__convert_nomenclatures(data)

        # Собираем рецепт
        compositions = data['composition'] if 'composition' in data else []
        for composition in compositions:
            # TODO: Заменить код через Dto
            namnomenclature_id = composition['nomenclature_id'] if 'nomenclature_id' in composition else ""
            range_id = composition['range_id'] if 'range_id' in composition else ""
            value = composition['value'] if 'value' in composition else ""
            nomenclature = self.__cache[namnomenclature_id] if namnomenclature_id in self.__cache else None
            range = self.__cache[range_id] if range_id in self.__cache else None
            item = receipt_item_model.create(nomenclature, range, value)
            self.__default_receipt.composition.append(item)

        # Сохраняем рецепт
        self.__repo.data[reposity.receipt_key()].append(self.__default_receipt)
        return True

    """
    Стартовый набор данных
    """

    @property
    def data(self):
        return self.__repo.data

    """
    Основной метод для генерации эталонных данных
    """

    def start(self):
        self.file_name = "Docs/settings.json"
        result = self.load()
        if not result:
            raise operation_exception("Невозможно сформировать стартовый набор данных!")