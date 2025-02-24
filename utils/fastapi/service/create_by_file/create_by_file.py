from typing import Callable

from fastapi import (
    UploadFile,
)
from pydantic import BaseModel


from .create_from_csv import CreateFromCsv
from .create_from_json import CreateFromJson


async def create_by_file(
        file: UploadFile,
        core_func: Callable,
        core_func_kwargs: dict,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
        unacceptable_file_format_exception: type[Exception] | Exception,
) -> dict:
    if file.content_type == 'text/csv':
        return await CreateFromCsv(
            file=file,
            core_func=core_func,
            core_func_kwargs=core_func_kwargs,
            request_model=request_model,    
            response_model=response_model,
        ).perform()

    elif file.content_type == 'application/json':
        return await CreateFromJson(
            file=file,
            core_func=core_func,
            core_func_kwargs=core_func_kwargs,
            request_model=request_model,    
            response_model=response_model,
        ).perform()
    
    else:
        raise unacceptable_file_format_exception

