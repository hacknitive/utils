from typing import Optional 

from pydantic import BaseModel

from .response_schema import ResponseSchema
from .delete_by_pid_response import ModelDeleteByPidResponseWithSchema


class ModelDeleteBulkRequest(BaseModel):
    pids: tuple[str, ...]


class ModelDeleteBulkResponse(BaseModel):
    success: bool = True
    error: Optional[str] = None


class ModelDeleteBulkResponseWithSchema(ResponseSchema):
    data: dict[str, ModelDeleteByPidResponseWithSchema] = None
