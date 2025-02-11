from typing import (
    Optional,
    Sequence,
)

from pydantic import BaseModel
from starlette.responses import Response
from starlette.background import BackgroundTask
from orjson import dumps
from fastapi.encoders import jsonable_encoder


class ProjectOrjsonResponse(Response):
    media_type = "application/json"

    def __init__(  # noqa
            self,
            status_code: int = 200,
            success: bool = True,
            data: None | dict | list | BaseModel = None,
            error: str | dict | list | None | Sequence = None,

            headers: Optional[dict[str, str]] = None,
            background: Optional[BackgroundTask] = None,
    ):
        self.status_code = status_code
        self.success = success
        self.data = data
        self.error = error

        self.background = background
        self.body = self.render()
        self.init_headers(headers)
   
    def render(self, content=None) -> bytes:
        return dumps(self.prepare_content())

    def prepare_content(self):
        return jsonable_encoder({
            "status_code": self.status_code,
            "success": self.success,
            "data": self.data,
            "error": self.error
        })
