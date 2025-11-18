from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator, argument_exception
from Src.Core.filter_type import filter_type

class field_filter_dto(abstact_dto):
    __field_name: str = ""
    __value = None
    __type: filter_type = filter_type.EQUALS

    @property
    def field_name(self) -> str:
        return self.__field_name

    @field_name.setter
    def field_name(self, v: str):
        validator.validate(v, str)
        v = v.strip()
        if not v:
            raise argument_exception("field_name не может быть пустым")
        self.__field_name = v

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, v):
        self.__value = v

    @property
    def type(self) -> filter_type:
        return self.__type

    @type.setter
    def type(self, t):
        if isinstance(t, str):
            try:
                t = filter_type[t.strip().upper()]
            except KeyError:
                raise argument_exception(f"Неверный filter_type: {t}")
        validator.validate(t, filter_type)
        self.__type = t
