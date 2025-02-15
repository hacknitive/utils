from enum import Enum


class EnumOrderBy(str, Enum):
    A = "A"
    D = "D"


class EnumDatetimeDuration(str, Enum):
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    

MAP_ORDER_BY_SQL = {
    "A": "ASC",
    "D": "DESC"
}

MAP_ORDER_BY_MQL = {
    "A": +1,
    "D": -1
}


