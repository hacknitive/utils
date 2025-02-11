from enum import Enum


class EnumOrderBy(str, Enum):
    A = "A"
    D = "D"


class EnumDatetimeDuration(str, Enum):
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    

MAP_ORDER_BY_SQL = {
    "A": "ASC",
    "D": "DESC"
}


