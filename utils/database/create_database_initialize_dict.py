from pathlib import Path


def create_database_initialize_dict(
        directory_path: Path,
        pattern: str = "*.sql"
) -> dict:
    initialize_dict = {}

    for file in directory_path.glob(pattern=pattern):
        if file.is_file():
            with open(file, 'r', encoding='utf-8') as file:
                initialize_dict[file.name] = file.read()

    return initialize_dict
