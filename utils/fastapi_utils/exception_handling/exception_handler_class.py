from traceback import format_exc

from fastapi import Request 
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ExceptionHandler():
    def __init__(
            self,
            request: Request,
            exc: Exception,
            append_traceback_to_message: bool = False
    ) -> None:
        self.request = request
        self.exc = exc
        self.append_traceback_to_message = append_traceback_to_message

        self.status_code = None
        self.success = None
        self.data = None
        self.message = None
        self.headers = None
        self.error_traceback = None
        self.content = None

    async def perform(self,):
        await self.get_status_code()
        await self.get_success()
        await self.get_headers()
        await self.get_data()
        await self.get_message()
        await self.get_error_traceback()
        await self.perform_exception_logic()
        await self.prepare_content_to_respond()

        return JSONResponse(
            content=self.content,
            status_code=self.status_code,
            headers=self.headers,
        )


    async def get_status_code(self,):
        if isinstance(self.exc, RequestValidationError):
            self.status_code = 422
        else:
            self.status_code = getattr(self.exc, "status_code", 500)

    async def get_success(self,):
        self.success = getattr(self.exc, "success", False)

    async def get_headers(self,):
        self.headers = getattr(self.exc, "headers", None)

    async def get_data(self,):
        self.data = getattr(self.exc, "data", None)
        if self.data is None:
            try:
                self.data = self.exc.errors()
            except Exception:
                pass

    async def get_message(self,):
        message = getattr(self.exc, "message", None)
        if message is None:
            message = getattr(self.exc, "detail", None)
            if message is None:
                message = getattr(self.exc, "args", None)
                if message is None:
                    message = "Oops! Something went wrong!"
                else:
                    message = str(message)

        self.message = message

    async def get_error_traceback(self,):
        self.error_traceback = format_exc()

    async def perform_exception_logic(self) -> None:
        pass

    async def prepare_content_to_respond(self,):
        self.content = {
            "status_code": self.status_code,
            "success": self.success,
            "data": self.data,
            "message": self.message,
        }

        if self.append_traceback_to_message and self.error_traceback:
            self.content["message"] = (
                self.content["message"]
                + " - "
                + str(self.error_traceback)
            )
