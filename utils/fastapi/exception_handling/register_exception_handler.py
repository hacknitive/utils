from typing import (
    Type,
    Callable,
)

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ...exception import ProjectBaseException


EXCEPTIONS = (
    ProjectBaseException,
    HTTPException,
    StarletteHTTPException,
    RequestValidationError,
    *range(500, 510),
)


def register_exception_handler(
        app: FastAPI,
        exception_handler_func: Callable,
        exceptions: tuple[Type[Exception | int]] = EXCEPTIONS,
) -> None:

    for exception in exceptions:
        app.exception_handler(exception)(exception_handler_func)

    return None
