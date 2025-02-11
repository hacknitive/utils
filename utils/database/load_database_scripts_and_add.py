from pathlib import Path
from typing import Literal
from logging import Logger


def load_database_scripts_and_add(
        this_file_path: Path | str,
        sqls: dict[str, list],
        logger: Logger,
        extension: Literal["sql", "mql"] = "sql",
        script_directory_name: str = "sql",
) -> None:

    for key, value in sqls.items():
        path = Path(this_file_path).resolve(
        ).parents[0] / script_directory_name / f"{key}.{extension}"

        if not path.exists():
            logger.info("Path is not exist to load: %s", str(path))
            continue
            
        with open(path, "r", encoding="utf-8") as handler:
            sql_lines = handler.readlines()

        sqls = list()
        for sql_line in sql_lines: 
            if not sql_line.startswith("--"):
                if sql_line.endswith("\n"):
                    sql_line = sql_line[:-1]

                if sql_line:
                    sqls.append(sql_line)


        if sqls:
            value.extend(sqls)

    return None
