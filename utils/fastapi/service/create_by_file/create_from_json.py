from typing import Callable
from datetime import datetime
from json import load, dumps
from io import (
    BytesIO,
)

from fastapi.encoders import jsonable_encoder
from fastapi import (
    UploadFile,
    status,
)
from pydantic import BaseModel


class CreateFromJson:
    def __init__(
            self,
        file: UploadFile,
        core_func: Callable,
        core_func_kwargs: dict,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
        unacceptable_file_format_exception: type[Exception] | Exception,
    ) -> None:
        self.file = file
        self.core_func = core_func
        self.core_func_kwargs = core_func_kwargs
        self.request_model = request_model
        self.response_model = response_model
        self.unacceptable_file_format_exception = unacceptable_file_format_exception

        now = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        self.file_name = self.file.filename.rsplit(
            '.', 1)[0] + f"-Result-{now}.json"

        self.file_in_bytesio: BytesIO = None
        self.results = list()

    async def perform(self,):
        await self.core()
        self.get_bytesio()
        return self.create_result()

    async def core(self,):
        data = load(self.file.file)
        for data_i in data:
            try:
                await self.do_for_each_data(data_i=data_i)

            except Exception as e:
                error = getattr(e, 'error', None) or e
                result = {
                    **data_i,
                    'error': str(error).replace("\n", " #NEWLINE "),
                }

                self.results.append({**result, **data_i})

    async def do_for_each_data(
            self,
            data_i,
    ):
        model = self.request_model(**data_i)
        result = await self.core_func(model=model)
        if isinstance(result, list):
            for result_i in result:
                self.results.append({**data_i, **result_i})
        else:
            self.results.append({**data_i, **result})

    def get_bytesio(self):
        results = jsonable_encoder(self.results)
        file_in_string = dumps(results)
        file_in_bytes = bytes(
            file_in_string,
            encoding='utf-8',
        )
        self.file_in_bytesio = BytesIO(file_in_bytes)

    def create_result(self,):
        return {
            'media_type': 'application/json',
            'content': self.file_in_bytesio,
            'status_code': status.HTTP_200_OK,
            'headers': {"Content-Disposition": f"attachment; filename={self.file_name}"},
        }
