from fastapi import HTTPException
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
