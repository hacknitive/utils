from enum import Enum
from typing import Literal


class AuthenticationTypeEnum(str, Enum):
    AUTHENTICATED = "AUTHENTICATED"
    ANONYMOUS = "ANONYMOUS"

AUTHENTICATION_TYPE_LITERAL = Literal[*sorted({i.value for i in AuthenticationTypeEnum})]


class MethodsEnum(str, Enum):
    GET = "GET",
    POST = "POST",
    PUT = "PUT",
    DELETE = "DELETE",
    PATCH = "PATCH",
    OPTIONS = "OPTIONS",
    HEAD = "HEAD",

METHODS_SET = {i.value for i in MethodsEnum}
METHODS_LITERAL = Literal[*sorted({i.value for i in MethodsEnum})]


class DataVisibilityEnum(str, Enum):
    PERSONAL = "PERSONAL",
    ALL = "ALL",

DATA_VISIBILITY_SET = {i.value for i in DataVisibilityEnum}
DATA_VISIBILITY_LITERAL = Literal[*sorted(DATA_VISIBILITY_SET)]