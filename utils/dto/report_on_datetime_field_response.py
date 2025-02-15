from typing import Optional

from pydantic import BaseModel
from utils.dto import ResponseSchema


class ModelReportRegistrationResponse(BaseModel):
    datetime: Optional[str] = None
    count: Optional[int] = None


class ModelReportRegistrationResponseWithSchema(ResponseSchema):
    data: list[ModelReportRegistrationResponse] = list()
