from pathlib import Path
from logging import Logger
from traceback import format_exc

from .remove_directory import  remove_directory
from .remove_file import remove_file


async def delete_by_keywords(
        keywords: tuple[str, ...],
        dir_path: Path,
        logger: Logger,
        ) -> None:
    for keyword in keywords:
        for item in dir_path.rglob("*"):
            if keyword in item.name:
                try:
                    if item.is_file():
                        await remove_file(path=str(item))
                    elif item.is_dir():
                        await remove_directory(path=str(item))
                    else:
                        logger.warning(
                        f"Item is neither a file nor a directory: %s",
                        item
                        )
                except Exception:
                    logger.warning(format_exc())

    return None
