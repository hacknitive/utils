from typing import Optional

from os import (
    makedirs,
    sep,
)
from pathlib import Path
from logging import (
    getLogger,
    Formatter,
    StreamHandler,
    Logger,
)
from logging.handlers import (
    SysLogHandler,
    TimedRotatingFileHandler,
)

from .constant import *


class PrepareLogger:
    def __init__(
        self,
        project_base_dir: str,
        name: str,
        level: EnumLogLevel,
        handlers: list[EnumLogHandler],
        format_: str = '{"time":"%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", '
        '"function": "%(funcName)s", "message": "%(message)s"}',
        timed_rotating_file_handler: Optional[dict] = None,
        syslog_handler: Optional[dict] = None,
        stream_handler: Optional[dict] = None,
    ) -> None:
        self.project_base_dir = project_base_dir
        self.name = name
        self.level = level.value.upper()
        self.handlers = handlers

        self.format = format_

        self.timed_rotating_file_handler = timed_rotating_file_handler or dict()
        self.syslog_handler_input = syslog_handler or dict()
        self.stream_handler_input = stream_handler or dict()

        self.file_path: str
        self.app_logger: Logger
        self.prepared_handlers = list()

    def perform(self) -> Logger:
        self._get_logger()
        self._set_level()
        self._prepare_handlers()
        self._set_formatter()
        self._add_handler_2_logger()
        return self.app_logger

    def _get_logger(self):
        self.app_logger = getLogger(self.name)

    def _set_level(self):
        self.app_logger.setLevel(self.level)

    def _prepare_handlers(self):
        if EnumLogHandler.FILE in self.handlers:
            self._prepare_file_handler()

        if EnumLogHandler.SYSLOG in self.handlers:
            self._prepare_syslog_handler()

        if EnumLogHandler.CONSOLE in self.handlers:
            self._prepare_console_handler()

    def _prepare_file_handler(self):
        self.file_path = (
            self.project_base_dir
            + sep
            + "logs"
            + sep
            + self.timed_rotating_file_handler["filename"]
        )

        self._create_parent_folders()

        handler = TimedRotatingFileHandler(
            **{
                **self.timed_rotating_file_handler,
                "filename": self.file_path,
            }
        )
        self.prepared_handlers.append(handler)

    def _create_parent_folders(self):
        log_dir = Path(self.file_path).resolve().parent

        makedirs(
            log_dir,
            exist_ok=True,
        )

    def _prepare_syslog_handler(self):
        handler = SysLogHandler(**self.syslog_handler_input)
        self.prepared_handlers.append(handler)

    def _prepare_console_handler(self):
        stream = STREAM_DICT[self.stream_handler_input.get("stream", EnumLogStream.STDOUT)]
        handler = StreamHandler(stream=stream)
        self.prepared_handlers.append(handler)

    def _set_formatter(self):
        for handler in self.prepared_handlers:
            handler.setFormatter(Formatter(fmt=self.format))

    def _add_handler_2_logger(self):
        for handler in self.prepared_handlers:
            self.app_logger.addHandler(handler)
