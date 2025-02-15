from typing import Any

from pydantic import (
    BaseModel,
    model_validator,
)


class ModelUpdatePartiallyRequestValidation(BaseModel):

    @model_validator(mode='before')
    @classmethod
    def is_any_data_exist(cls, data: Any) -> Any:
        if data:
            return data
        raise ValueError("At least one field must be provided.")