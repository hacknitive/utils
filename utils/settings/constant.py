from enum import Enum


class EnumRunMode(str, Enum):
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    DEVELOPMENT = "DEVELOPMENT"
    LOCAL = "LOCAL"
    TEST = "TEST"


ARGS_OF_TESTS = (
    "unittest",
    "pytest",
    "django test",
)
