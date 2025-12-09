from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator, argument_exception
from Src.Logics.response_json import response_json
class logging_dto(abstact_dto):
    __min_level: str = "INFO"
    __mode: str = "file"
    __directory: str = "./Src/Logs"
    __format: str = "{date} [{level}] {message} {meta}"

    def __init__(self, min_level="INFO", mode="file",
                 directory="./Src/Logs",
                 format="{date} [{level}] {message} {meta}"):

        self.min_level = min_level
        self.mode = mode
        self.directory = directory
        self.format = format

    # ---------- PROPERTIES ----------
    @property
    def min_level(self):
        return self.__min_level

    @min_level.setter
    def min_level(self, v):
        validator.validate(v, str)
        v = v.strip()
        if not v:
            raise argument_exception("min_level пустой")
        self.__min_level = v.upper()

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, v):
        validator.validate(v, str)
        v = v.strip().lower()
        if v not in ("file", "console"):
            raise argument_exception("mode: file|console")
        self.__mode = v

    @property
    def directory(self):
        return self.__directory

    @directory.setter
    def directory(self, v):
        validator.validate(v, str)
        v = v.strip()
        if not v:
            raise argument_exception("directory пустой")
        self.__directory = v

    @property
    def format(self):
        return self.__format

    @format.setter
    def format(self, v):
        validator.validate(v, str)
        v = v.strip()
        if not v:
            raise argument_exception("format пустой")
        self.__format = v

    def serialize(self):
        r = response_json()
        result = r.build("", [self])
        print(result)
        return result

    def update_from_dict(self, raw: dict):
        """
        Обновляет DTO значениями из dict.
        """
        allowed = {"min_level", "mode", "directory", "format"}
        for key, value in raw.items():
            if key not in allowed:
                raise argument_exception(f"Неизвестное поле logging_dto: {key}")
            setattr(self, key, value)
        return self
