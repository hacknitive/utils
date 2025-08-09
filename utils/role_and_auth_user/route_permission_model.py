from pydantic import (
    BaseModel,
)

from .constant import METHODS_LITERAL

class RoutePermission(BaseModel):
    method: METHODS_LITERAL
    path: str
    regex: str
    permitted_request_fields: set[str]
    permitted_response_fields: set[str]
