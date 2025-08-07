from typing import (
    Annotated,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
    model_validator
)

# from .constant import (
#     DATA_VISIBILITY_TYPE_LITERAL,
#     DataVisibilityTypeEnum,
# )

class AuthenticatedUser(BaseModel):
    user_pid: str
    session_pid: str
    role_pid: str

    permitted_request_fields: set[str]
    permitted_response_fields: set[str]

    data_visibility_filter_field: Optional[str]
    # data_visibility_type: DATA_VISIBILITY_TYPE_LITERAL

    data_access_level: Annotated[int, Field(ge=1, le=100)]

    # @model_validator(mode="after")
    # def check_data_visibility(self) -> "AuthenticatedUser":
    #     if self.data_visibility_type == DataVisibilityTypeEnum.ALL_DATA:
    #         if self.data_visibility_filter_field is not None:
    #             raise ValueError(
    #                 "When `data_visibility_type` is ALL_DATA, "
    #                 "`data_visibility_filter_field` must be None."
    #             )
    #     elif self.data_visibility_type == DataVisibilityTypeEnum.PERSONAL_DATA:
    #         if self.data_visibility_filter_field is None:
    #             raise ValueError(
    #                 "When `data_visibility_type` is PERSONAL_DATA, "
    #                 "`data_visibility_filter_field` must not be None."
    #             )
    #     return self
