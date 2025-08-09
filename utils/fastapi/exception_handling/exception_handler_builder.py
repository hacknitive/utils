from typing import  Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from utils.settings import EnumRunMode

from .exception_handler_class import ExceptionHandlerClass


def exception_handler_builder(
        perform_exception_logic_func: Callable,
        run_mode: EnumRunMode,
) -> Callable:
    
    async def handle_exception(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        exception_handler_obj = ExceptionHandlerClass(
            request=request,
            exc=exc,
            perform_exception_logic_func=perform_exception_logic_func,
            run_mode=run_mode,
        )

        return await exception_handler_obj.perform()

    return handle_exception
