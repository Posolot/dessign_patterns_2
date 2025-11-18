from enum import Enum


class filter_type(str, Enum):
    EQUALS = "EQUALS"
    LIKE = "LIKE"
