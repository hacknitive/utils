from typing import (
    Annotated,
    Any,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from .route_permission_model import RoutePermission
from .prepare_method_and_path_and_regex import prepare_method_and_path_and_regex
from .constant import DATA_VISIBILITY_LITERAL


class Role(BaseModel):
    name: Annotated[str, Field(max_length=50)]
    description: Annotated[str, Field(max_length=1000)]
    data_visibility: DATA_VISIBILITY_LITERAL 

    routes_permissions: dict[
        Annotated[
            str,
            Field(max_length=500)
        ],
        RoutePermission,
    ]

    @field_validator('routes_permissions', mode='before')
    @classmethod
    def validate_and_enrich_routes(cls, v: Any) -> Any:
        """
        Validates that each key is in 'METHOD:path' format, normalizes the
        METHOD to uppercase, and enriches the value dictionary with method,
        path, and regex data before it becomes a RoutePermission model.
        """
        if not isinstance(v, dict):
            return v  # Let Pydantic handle the type error

        enriched_routes = {}
        for key, value in v.items():
            # 1. Validate Key Format
            if not isinstance(key, str) or ':' not in key:
                raise ValueError(
                    f"Invalid route format for key '{key}'. Expected 'METHOD:path'."
                )

            method_part, path_part = key.split(':', 1)
            if not method_part or not path_part:
                raise ValueError(
                    f"Invalid route format for key '{key}'. Method and path must not be empty."
                )

            # 2. Validate Value
            if not isinstance(value, dict):
                raise ValueError(
                    f"The value for route '{key}' must be a dictionary.")

            # 3. Prevent manual override of derived fields
            conflicting_keys = {'method', 'path',
                                'regex'}.intersection(value.keys())
            if conflicting_keys:
                raise ValueError(
                    f"Fields {conflicting_keys} for route '{key}' must not be provided manually; "
                    "they are derived from the dictionary key."
                )

            # 4. Enrich the value dictionary
            derived_data = prepare_method_and_path_and_regex(key)
            enriched_value = {**derived_data, **value}

            # 5. Use the normalized key and enriched value
            normalized_key = f"{method_part.upper()}:{path_part}"
            enriched_routes[normalized_key] = enriched_value

        return enriched_routes
