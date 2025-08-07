from enum import Enum
from typing import (
    Literal,
)

0
class AuthenticationTypeEnum(str, Enum):
    AUTHENTICATED = "AUTHENTICATED"
    ANONYMOUS = "ANONYMOUS"


AUTHENTICATION_TYPE_LITERAL = Literal[*sorted({i.value for i in AuthenticationTypeEnum})]

