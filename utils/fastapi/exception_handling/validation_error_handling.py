from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.exceptions import RequestValidationError
from ..router import ProjectOrjsonResponse as Response

HTTP_422_UNPROCESSABLE_ENTITY = status.HTTP_422_UNPROCESSABLE_ENTITY


def prepare_handler_for_validation_errors_function(
    fast_api_app: FastAPI,
    message: str="Some fields are not valid.",
):

    async def handler_for_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> Response:
        exe_error = exc.errors()
        return Response(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            success=False,
            data=exe_error,
            message=message,
            )

    fast_api_app.exception_handler(RequestValidationError)(handler_for_validation_error)
