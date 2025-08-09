from enum import Enum
from typing import Literal


class EnumOrderBy(str, Enum):
    A = "A"
    D = "D"

ORDER_BY_LITERAL = Literal[*sorted({i.value for i in EnumOrderBy})]


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


