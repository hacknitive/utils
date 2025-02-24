from typing import Callable
from datetime import datetime
from csv import DictReader, DictWriter
from io import (
    TextIOWrapper,
    StringIO,
    BytesIO,
)

from fastapi import (
    UploadFile,
    status,
)
from pydantic import BaseModel

from ....exception import ProjectBaseException


class CreateFromCsv:
    def __init__(
        self,
        file: UploadFile,
        core_func: Callable,
        core_func_kwargs: dict,
        request_model: type[BaseModel],
        response_model: type[BaseModel],
    ) -> None:
        self.file = file
        self.core_func = core_func
        self.core_func_kwargs = core_func_kwargs
        self.request_model = request_model
        self.response_model = response_model

        now = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        self.file_name = self.file.filename.rsplit(
            '.', 1)[0] + f"-Result-{now}.csv"

        self.reader: DictReader = None
        self.writer: DictWriter = None
        self.in_memory_file = StringIO()
        self.file_in_bytesio: BytesIO = None

    async def perform(self,):
        self.get_reader()
        self.get_writer()
        await self.core()
        self.get_bytesio()
        return self.create_result()

    def get_reader(self):
        self.reader = DictReader(TextIOWrapper(
            self.file.file,
            encoding='utf-8-sig',
        ))

    def get_writer(self):
        self.writer = DictWriter(
            self.in_memory_file,
            fieldnames=(
                *(i for i in self.request_model.__fields__.keys()),
                *(i for i in self.response_model.__fields__.keys()),
                'error',
            ),
        )

        self.writer.writeheader()

    async def do_for_each_line(
            self,
            line,
    ):
        try:
            model = self.request_model(**line)
            result = await self.core_func(model=model, **self.core_func_kwargs)
            if isinstance(result, list):
                for result_i in result:
                    self.writer.writerow({**line, **result_i, })
            else:
                self.writer.writerow({**line, **result})
        except Exception as e:
            error = getattr(e, 'error', None) or e

            result = {
                **line,
                'error': str(error).replace("\n", " #NEWLINE "),
            }

            self.writer.writerow({**result, **line})

    def get_bytesio(self):
        file_in_string = self.in_memory_file.getvalue()
        file_in_bytes = bytes(
            file_in_string,
            encoding='utf-8',
        )
        self.file_in_bytesio = BytesIO(file_in_bytes)

    async def core(self):
        try:
            for line in self.reader:
                await self.do_for_each_line(line)
        except Exception as e:
            error = getattr(e, 'error', None) or e
            error = str(error).replace("\n", " #NEWLINE ")

            raise ProjectBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                data=None,
                error=error,
                message=error,
            )

    def create_result(self,):
        return {
            'media_type': 'application/csv',
            'content': self.file_in_bytesio,
            'status_code': status.HTTP_200_OK,
            'headers': {"Content-Disposition": f"attachment; filename={self.file_name}"},
        }
