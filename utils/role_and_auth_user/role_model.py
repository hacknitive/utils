from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

from .route_permission_model import RoutePermission


class Role(BaseModel):
    name: Annotated[str, Field(max_length=50)]
    description: Annotated[str, Field(max_length=1000)]

    route_permissions: dict[
        Annotated[
            str,
            Field(max_length=500)
        ],
        RoutePermission,
    ]
