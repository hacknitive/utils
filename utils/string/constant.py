from enum import Enum


class EnumCaseStrategy(str, Enum):
    LOWER = 'LOWER'
    UPPER = 'UPPER'
    TITLE = "TITLE"
    PASCAL = "PASCAL"
    CAMEL = 'CAMEL'

