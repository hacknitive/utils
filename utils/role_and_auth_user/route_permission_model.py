from pydantic import (
    BaseModel,
)

from .constant import ACCESS_TYPE_LITERAL


class RoutePermission(BaseModel):
    access_type: ACCESS_TYPE_LITERAL
    permitted_request_fields: set[str]
    permitted_response_fields: set[str]
